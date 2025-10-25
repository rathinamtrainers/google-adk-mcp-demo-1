"""
HTTP/SSE Server wrapper for MCP Calculator Server
Enables Cloud Run deployment with HTTP transport
"""
import asyncio
import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from calculator_server import list_tools as get_tools, call_tool as execute_tool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server instance
mcp_server = Server("calculator-mcp-server")

# Register handlers
@mcp_server.list_tools()
async def list_tools_handler() -> list[Tool]:
    return await get_tools()

@mcp_server.call_tool()
async def call_tool_handler(name: str, arguments: dict) -> list[TextContent | ImageContent | EmbeddedResource]:
    return await execute_tool(name, arguments)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    logger.info("Starting MCP Calculator HTTP Server")
    yield
    logger.info("Shutting down MCP Calculator HTTP Server")


# Create FastAPI app
app = FastAPI(
    title="MCP Calculator Server",
    description="Calculator tools exposed via MCP over HTTP",
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
        tools = await list_tools_handler()
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema
                }
                for tool in tools
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

        result = await call_tool_handler(tool_name, arguments)

        # Convert result to JSON-serializable format
        response = {
            "tool": tool_name,
            "result": [
                {
                    "type": content.type,
                    "text": content.text if hasattr(content, 'text') else str(content)
                }
                for content in result
            ]
        }

        return response

    except Exception as e:
        logger.error(f"Error calling tool {tool_name}: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/execute")
async def execute_tool_batch(request: Request):
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

        result = await call_tool_handler(tool_name, arguments)

        return {
            "tool": tool_name,
            "result": [
                {
                    "type": content.type,
                    "text": content.text if hasattr(content, 'text') else str(content)
                }
                for content in result
            ]
        }

    except Exception as e:
        logger.error(f"Error executing tool: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(
        "http_server:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
