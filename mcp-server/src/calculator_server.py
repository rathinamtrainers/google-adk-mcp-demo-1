"""
MCP Server for Calculator Operations
Provides basic math operations as tools for AI agents
Uses FastMCP with streamable-http transport for Cloud Run deployment
"""
import logging
import math
import os
from typing import Any
from mcp.server.fastmcp import FastMCP

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server (port will be set in __main__)
server = FastMCP(
    name="calculator-mcp-server",
    debug=False
)


@server.tool()
def add(a: float, b: float) -> dict[str, Any]:
    """Add two numbers together

    Args:
        a: First number
        b: Second number

    Returns:
        Dictionary with the result and operation details
    """
    result = a + b
    logger.info(f"add({a}, {b}) = {result}")
    return {
        "operation": "addition",
        "input_a": a,
        "input_b": b,
        "result": result,
        "text": f"Result: {a} + {b} = {result}"
    }


@server.tool()
def subtract(a: float, b: float) -> dict[str, Any]:
    """Subtract second number from first number

    Args:
        a: First number (minuend)
        b: Second number (subtrahend)

    Returns:
        Dictionary with the result and operation details
    """
    result = a - b
    logger.info(f"subtract({a}, {b}) = {result}")
    return {
        "operation": "subtraction",
        "input_a": a,
        "input_b": b,
        "result": result,
        "text": f"Result: {a} - {b} = {result}"
    }


@server.tool()
def multiply(a: float, b: float) -> dict[str, Any]:
    """Multiply two numbers together

    Args:
        a: First number
        b: Second number

    Returns:
        Dictionary with the result and operation details
    """
    result = a * b
    logger.info(f"multiply({a}, {b}) = {result}")
    return {
        "operation": "multiplication",
        "input_a": a,
        "input_b": b,
        "result": result,
        "text": f"Result: {a} × {b} = {result}"
    }


@server.tool()
def divide(a: float, b: float) -> dict[str, Any]:
    """Divide first number by second number

    Args:
        a: Numerator
        b: Denominator (cannot be zero)

    Returns:
        Dictionary with the result or error message
    """
    if b == 0:
        logger.warning(f"divide({a}, {b}) - Division by zero attempted")
        return {
            "operation": "division",
            "error": "Division by zero is not allowed",
            "text": "Error: Division by zero is not allowed"
        }

    result = a / b
    logger.info(f"divide({a}, {b}) = {result}")
    return {
        "operation": "division",
        "input_a": a,
        "input_b": b,
        "result": result,
        "text": f"Result: {a} ÷ {b} = {result}"
    }


@server.tool()
def power(base: float, exponent: float) -> dict[str, Any]:
    """Raise first number to the power of second number

    Args:
        base: Base number
        exponent: Exponent

    Returns:
        Dictionary with the result and operation details
    """
    result = base ** exponent
    logger.info(f"power({base}, {exponent}) = {result}")
    return {
        "operation": "power",
        "base": base,
        "exponent": exponent,
        "result": result,
        "text": f"Result: {base}^{exponent} = {result}"
    }


@server.tool()
def sqrt(number: float) -> dict[str, Any]:
    """Calculate square root of a number

    Args:
        number: Number to calculate square root of (must be non-negative)

    Returns:
        Dictionary with the result or error message
    """
    if number < 0:
        logger.warning(f"sqrt({number}) - Negative number attempted")
        return {
            "operation": "square_root",
            "error": "Cannot calculate square root of a negative number",
            "text": "Error: Cannot calculate square root of a negative number"
        }

    result = math.sqrt(number)
    logger.info(f"sqrt({number}) = {result}")
    return {
        "operation": "square_root",
        "input": number,
        "result": result,
        "text": f"Result: √{number} = {result}"
    }


@server.tool()
def percentage(number: float, percent: float) -> dict[str, Any]:
    """Calculate percentage of a number

    Args:
        number: The number to calculate percentage of
        percent: The percentage value

    Returns:
        Dictionary with the result and operation details
    """
    result = (number * percent) / 100
    logger.info(f"percentage({number}, {percent}) = {result}")
    return {
        "operation": "percentage",
        "number": number,
        "percent": percent,
        "result": result,
        "text": f"Result: {percent}% of {number} = {result}"
    }


# Helper function to create FastAPI app with health endpoint
def create_app():
    """Create FastAPI app with MCP server and health endpoint"""
    import uvicorn
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse

    # Create a new FastAPI app
    app = FastAPI(title="Calculator MCP Server")

    # Add health check endpoint for Cloud Run
    @app.get("/health")
    async def health_check():
        """Health check endpoint for Cloud Run"""
        return JSONResponse({"status": "healthy", "service": "calculator-mcp-server"})

    # Add the MCP endpoint - server.run() will handle the routing internally
    # We need to integrate FastMCP's routes into this app
    # For now, let's try using server._get_asgi_app() if it exists
    try:
        mcp_app = server._get_asgi_app()
        app.mount("/", mcp_app)
    except AttributeError:
        # If that doesn't work, we'll need to manually create the routes
        logger.warning("Could not mount MCP app automatically")

    return app


# Main entry point for Cloud Run deployment
if __name__ == "__main__":
    import uvicorn

    # Get port from environment (Cloud Run sets this)
    port = int(os.environ.get("PORT", 8080))

    # Try the simple approach first: just add custom route handler before running
    # Check if we can access server's internal app
    if hasattr(server, 'get_asgi_app'):
        app = server.get_asgi_app()

        # Add health endpoint
        @app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "calculator-mcp-server"}

        logger.info(f"🚀 MCP Calculator Server running on http://0.0.0.0:{port}")
        logger.info(f"📊 Available tools: add, subtract, multiply, divide, power, sqrt, percentage")
        logger.info(f"❤️  Health check endpoint: /health")

        uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    else:
        # Fallback to standard server.run() - we'll need to fix health check differently
        server.settings.host = "0.0.0.0"
        server.settings.port = port

        logger.info(f"🚀 MCP Calculator Server running on http://0.0.0.0:{port}")
        logger.info(f"📊 Available tools: add, subtract, multiply, divide, power, sqrt, percentage")
        logger.warning("⚠️  No health endpoint available - using default MCP endpoints only")

        server.run(transport="streamable-http")
