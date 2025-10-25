"""
MCP Server for Calculator Operations
Provides basic math operations as tools for AI agents
"""
import asyncio
import math
from typing import Any

from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server.stdio import stdio_server


# Create server instance
app = Server("calculator-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available calculator tools."""
    return [
        Tool(
            name="add",
            description="Add two numbers together",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="subtract",
            description="Subtract second number from first number",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number (minuend)"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number (subtrahend)"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="multiply",
            description="Multiply two numbers together",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="divide",
            description="Divide first number by second number",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "Numerator"
                    },
                    "b": {
                        "type": "number",
                        "description": "Denominator (cannot be zero)"
                    }
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="power",
            description="Raise first number to the power of second number",
            inputSchema={
                "type": "object",
                "properties": {
                    "base": {
                        "type": "number",
                        "description": "Base number"
                    },
                    "exponent": {
                        "type": "number",
                        "description": "Exponent"
                    }
                },
                "required": ["base", "exponent"]
            }
        ),
        Tool(
            name="sqrt",
            description="Calculate square root of a number",
            inputSchema={
                "type": "object",
                "properties": {
                    "number": {
                        "type": "number",
                        "description": "Number to calculate square root of (must be non-negative)"
                    }
                },
                "required": ["number"]
            }
        ),
        Tool(
            name="percentage",
            description="Calculate percentage of a number",
            inputSchema={
                "type": "object",
                "properties": {
                    "number": {
                        "type": "number",
                        "description": "The number to calculate percentage of"
                    },
                    "percent": {
                        "type": "number",
                        "description": "The percentage value"
                    }
                },
                "required": ["number", "percent"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool execution."""
    try:
        if name == "add":
            result = arguments["a"] + arguments["b"]
            return [TextContent(
                type="text",
                text=f"Result: {arguments['a']} + {arguments['b']} = {result}"
            )]

        elif name == "subtract":
            result = arguments["a"] - arguments["b"]
            return [TextContent(
                type="text",
                text=f"Result: {arguments['a']} - {arguments['b']} = {result}"
            )]

        elif name == "multiply":
            result = arguments["a"] * arguments["b"]
            return [TextContent(
                type="text",
                text=f"Result: {arguments['a']} × {arguments['b']} = {result}"
            )]

        elif name == "divide":
            if arguments["b"] == 0:
                return [TextContent(
                    type="text",
                    text="Error: Division by zero is not allowed"
                )]
            result = arguments["a"] / arguments["b"]
            return [TextContent(
                type="text",
                text=f"Result: {arguments['a']} ÷ {arguments['b']} = {result}"
            )]

        elif name == "power":
            result = arguments["base"] ** arguments["exponent"]
            return [TextContent(
                type="text",
                text=f"Result: {arguments['base']}^{arguments['exponent']} = {result}"
            )]

        elif name == "sqrt":
            if arguments["number"] < 0:
                return [TextContent(
                    type="text",
                    text="Error: Cannot calculate square root of a negative number"
                )]
            result = math.sqrt(arguments["number"])
            return [TextContent(
                type="text",
                text=f"Result: √{arguments['number']} = {result}"
            )]

        elif name == "percentage":
            result = (arguments["number"] * arguments["percent"]) / 100
            return [TextContent(
                type="text",
                text=f"Result: {arguments['percent']}% of {arguments['number']} = {result}"
            )]

        else:
            return [TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
