"""
HTTP Server wrapper for FastMCP Calculator Server
Provides simple REST endpoints for Cloud Run deployment
"""
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import the FastMCP server and tool functions
from calculator_server import server as mcp_server, add, subtract, multiply, divide, power, sqrt, percentage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Map tool names to functions
TOOL_FUNCTIONS = {
    "add": add,
    "subtract": subtract,
    "multiply": multiply,
    "divide": divide,
    "power": power,
    "sqrt": sqrt,
    "percentage": percentage
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    logger.info("Starting MCP Calculator HTTP Server")
    yield
    logger.info("Shutting down MCP Calculator HTTP Server")


# Create FastAPI app
app = FastAPI(
    title="MCP Calculator Server",
    description="Calculator tools exposed via simple REST API",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "MCP Calculator Server",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check for Cloud Run."""
    return {"status": "healthy"}


@app.get("/tools")
async def list_tools():
    """List available calculator tools."""
    try:
        # Get tools from FastMCP server
        tools_list = mcp_server.list_tools()

        return {
            "tools": [
                {
                    "name": tool["name"],
                    "description": tool["description"],
                    "inputSchema": tool.get("inputSchema", {})
                }
                for tool in tools_list
            ]
        }
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/tools/{tool_name}")
async def call_tool(tool_name: str, request: Request):
    """Execute a specific tool."""
    try:
        body = await request.json()
        arguments = body.get("arguments", {})

        logger.info(f"Calling tool: {tool_name} with arguments: {arguments}")

        # Get the tool function
        tool_func = TOOL_FUNCTIONS.get(tool_name)
        if not tool_func:
            return JSONResponse(
                status_code=404,
                content={"error": f"Tool '{tool_name}' not found"}
            )

        # Call the tool function directly
        result = tool_func(**arguments)

        return {
            "tool": tool_name,
            "result": result
        }

    except TypeError as e:
        logger.error(f"Invalid arguments for tool {tool_name}: {e}")
        return JSONResponse(
            status_code=400,
            content={"error": f"Invalid arguments: {str(e)}"}
        )
    except Exception as e:
        logger.error(f"Error calling tool {tool_name}: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/execute")
async def execute_tool(request: Request):
    """Execute tool with full MCP-style request."""
    try:
        body = await request.json()
        tool_name = body.get("name")
        arguments = body.get("arguments", {})

        if not tool_name:
            return JSONResponse(
                status_code=400,
                content={"error": "Tool name is required"}
            )

        logger.info(f"Executing tool: {tool_name} with arguments: {arguments}")

        # Get the tool function
        tool_func = TOOL_FUNCTIONS.get(tool_name)
        if not tool_func:
            return JSONResponse(
                status_code=404,
                content={"error": f"Tool '{tool_name}' not found"}
            )

        # Call the tool function directly
        result = tool_func(**arguments)

        return {
            "tool": tool_name,
            "result": result
        }

    except TypeError as e:
        logger.error(f"Invalid arguments: {e}")
        return JSONResponse(
            status_code=400,
            content={"error": f"Invalid arguments: {str(e)}"}
        )
    except Exception as e:
        logger.error(f"Error executing tool: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting HTTP server on port {port}")
    uvicorn.run(
        "http_server:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
