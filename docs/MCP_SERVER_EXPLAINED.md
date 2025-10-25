# MCP Server Explained

**Complete Guide to Understanding the MCP Calculator Server**

---

## Table of Contents

1. [What is MCP?](#what-is-mcp)
2. [Server Architecture](#server-architecture)
3. [Code Walkthrough](#code-walkthrough)
4. [Tool Implementation](#tool-implementation)
5. [HTTP Transport Layer](#http-transport-layer)
6. [Deployment](#deployment)
7. [Testing](#testing)
8. [Extending the Server](#extending-the-server)

---

## What is MCP?

### Model Context Protocol

**MCP** (Model Context Protocol) is a standardized protocol for AI models to interact with external tools and services.

**Think of it like this:**
```
Without MCP:
  AI: "I need to calculate 10 + 5"
  Developer: "Let me write custom integration code..."

With MCP:
  AI: "I need the add tool"
  MCP Server: "Here's the add tool and how to use it"
  AI: "add(10, 5)"
  MCP Server: "Result: 15"
```

### Why MCP?

**Benefits:**
1. **Standardization:** All AI systems can use the same tools
2. **Discoverability:** Tools self-describe their capabilities
3. **Type Safety:** JSON Schema validates inputs
4. **Reusability:** One MCP server works with multiple AI models

### MCP Components

```
┌─────────────────────────────────────────┐
│  AI Model (Gemini, GPT, Claude, etc.)  │
│  "I need to do calculations"            │
└─────────────────┬───────────────────────┘
                  │
                  │ MCP Protocol
                  ▼
┌─────────────────────────────────────────┐
│  MCP Server                             │
│  ┌───────────────────────────────────┐ │
│  │  Tool Registry                    │ │
│  │  "Here are available tools"       │ │
│  └───────────────┬───────────────────┘ │
│                  │                      │
│  ┌───────────────▼───────────────────┐ │
│  │  Tool Executor                    │ │
│  │  "Execute requested tool"         │ │
│  └───────────────┬───────────────────┘ │
│                  │                      │
│  ┌───────────────▼───────────────────┐ │
│  │  Tool Implementations             │ │
│  │  - add()                          │ │
│  │  - subtract()                     │ │
│  │  - multiply()                     │ │
│  │  - etc.                           │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

---

## Server Architecture

### Two-Layer Design

Our MCP server has **two layers**:

```
┌──────────────────────────────────────────┐
│  Layer 2: HTTP/SSE Transport             │
│  (http_server.py)                        │
│  - FastAPI web server                    │
│  - REST API endpoints                    │
│  - Cloud Run compatible                  │
└──────────────┬───────────────────────────┘
               │
               │ Function calls
               ▼
┌──────────────────────────────────────────┐
│  Layer 1: MCP Protocol                   │
│  (calculator_server.py)                  │
│  - Tool definitions                      │
│  - Tool execution logic                  │
│  - Business logic                        │
└──────────────────────────────────────────┘
```

**Why two layers?**

**Layer 1 (calculator_server.py):**
- Pure MCP implementation
- Defines tools according to MCP spec
- Could work with any MCP transport (stdio, HTTP, etc.)

**Layer 2 (http_server.py):**
- Makes Layer 1 accessible over HTTP
- Enables Cloud Run deployment
- Adds REST API endpoints for easy testing

### File Structure

```
mcp-server/
├── src/
│   ├── calculator_server.py    # Layer 1: MCP tools
│   └── http_server.py           # Layer 2: HTTP wrapper
├── Dockerfile                   # Container definition
├── requirements.txt             # Python dependencies
└── README.md                    # Documentation
```

---

## Code Walkthrough

### calculator_server.py (Layer 1)

**File:** `mcp-server/src/calculator_server.py`

#### Imports and Setup (Lines 1-15)

```python
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server.stdio import stdio_server
```

**What these do:**
- `Server`: Main MCP server class
- `Tool`: Data structure for tool definitions
- `TextContent`: Response format for tool results
- `stdio_server`: Standard I/O transport (used for direct MCP communication)

```python
app = Server("calculator-mcp-server")
```

**What this does:**
- Creates an MCP server instance
- Name: "calculator-mcp-server"
- This object will handle all MCP protocol operations

#### Tool Registration (Lines 18-144)

**Pattern: Decorator-based registration**

```python
@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available calculator tools."""
    return [Tool(...), Tool(...), ...]
```

**What this does:**
- `@app.list_tools()`: Decorator tells MCP server "this function lists tools"
- Returns a list of `Tool` objects
- Each `Tool` describes one calculator function

**Example Tool Definition (add):**

```python
Tool(
    name="add",                          # Tool identifier
    description="Add two numbers together",  # What it does
    inputSchema={                         # JSON Schema for inputs
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
        "required": ["a", "b"]            # Both parameters required
    }
)
```

**Understanding inputSchema:**
- Based on [JSON Schema](https://json-schema.org/)
- Describes expected input format
- AI models use this to call tools correctly
- Validates inputs automatically

**Why this matters:**
```
AI sees tool definition:
  "add" takes two numbers "a" and "b"

AI generates proper call:
  add(a=10, b=5)  ✓ Correct

Not:
  add(10, 5, 3)   ✗ Wrong (too many args)
  add(a="10")     ✗ Wrong (wrong type)
```

#### Tool Execution (Lines 147-220)

```python
@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool execution."""
```

**What this does:**
- `@app.call_tool()`: Decorator tells MCP server "this executes tools"
- `name`: Which tool to execute
- `arguments`: Dictionary of parameters
- Returns list of `TextContent` objects

**Example: Add tool implementation**

```python
if name == "add":
    result = arguments["a"] + arguments["b"]  # Do calculation
    return [TextContent(
        type="text",
        text=f"Result: {arguments['a']} + {arguments['b']} = {result}"
    )]
```

**Line-by-line:**
1. Check if tool name is "add"
2. Extract `a` and `b` from arguments dictionary
3. Perform addition: `a + b`
4. Format result as human-readable text
5. Wrap in `TextContent` object
6. Return as list (MCP protocol requirement)

**Error Handling Example (divide):**

```python
elif name == "divide":
    if arguments["b"] == 0:                    # Check for division by zero
        return [TextContent(
            type="text",
            text="Error: Division by zero is not allowed"
        )]
    result = arguments["a"] / arguments["b"]   # Safe to divide
    return [TextContent(
        type="text",
        text=f"Result: {arguments['a']} ÷ {arguments['b']} = {result}"
    )]
```

**Why error handling matters:**
- Prevents server crashes
- Provides helpful error messages to AI
- AI can retry with valid inputs

#### Main Function (Lines 223-234)

```python
async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )
```

**What this does:**
- Sets up stdio (standard input/output) transport
- Runs the MCP server
- Used for direct MCP protocol communication (not HTTP)

**Note:** We don't use this in production (we use HTTP instead), but it's useful for local testing with MCP clients.

---

### http_server.py (Layer 2)

**File:** `mcp-server/src/http_server.py`

#### Setup (Lines 1-50)

```python
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
```

**What these do:**
- `FastAPI`: Modern Python web framework
- `JSONResponse`: Return JSON data
- `CORSMiddleware`: Enable cross-origin requests

```python
app = FastAPI(
    title="MCP Calculator Server",
    description="Calculator tools exposed via MCP over HTTP",
    version="1.0.0",
    lifespan=lifespan
)
```

**What this does:**
- Creates FastAPI application
- Sets metadata (title, description, version)
- Registers lifespan handler for startup/shutdown

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**What this does:**
- Enables CORS (Cross-Origin Resource Sharing)
- Allows requests from any origin (`*`)
- Necessary for web browsers to access API

#### Health Check Endpoints (Lines 62-75)

```python
@app.get("/")
async def root():
    return {
        "status": "healthy",
        "service": "MCP Calculator Server",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**What these do:**
- `/`: Root endpoint, returns service info
- `/health`: Health check for Cloud Run
- Both return JSON
- Cloud Run pings `/health` to verify service is running

#### List Tools Endpoint (Lines 78-98)

```python
@app.get("/tools")
async def list_tools():
    try:
        tools = await list_tools_handler()  # Call Layer 1
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
```

**What this does:**
1. Client requests `GET /tools`
2. Server calls `list_tools_handler()` (from Layer 1)
3. Converts MCP `Tool` objects to JSON dictionaries
4. Returns list of all available tools
5. If error occurs, returns 500 status with error message

**Example response:**
```json
{
  "tools": [
    {
      "name": "add",
      "description": "Add two numbers together",
      "inputSchema": {
        "type": "object",
        "properties": {
          "a": {"type": "number", "description": "First number"},
          "b": {"type": "number", "description": "Second number"}
        },
        "required": ["a", "b"]
      }
    },
    ...
  ]
}
```

#### Execute Tool Endpoint (Lines 101-125)

```python
@app.post("/tools/{tool_name}")
async def call_tool(tool_name: str, request: Request):
    try:
        body = await request.json()
        arguments = body.get("arguments", {})

        # Execute tool via Layer 1
        result = await call_tool_handler(tool_name, arguments)

        return {
            "tool": tool_name,
            "result": [
                {
                    "type": r.type,
                    "text": r.text
                }
                for r in result
            ]
        }
    except Exception as e:
        logger.error(f"Error calling tool {tool_name}: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
```

**What this does:**
1. Client POSTs to `/tools/add` with JSON body
2. Extract `arguments` from request body
3. Call `call_tool_handler(tool_name, arguments)` (from Layer 1)
4. Convert `TextContent` objects to JSON dictionaries
5. Return result
6. If error occurs, return 500 status with error message

**Example request:**
```http
POST /tools/add HTTP/1.1
Content-Type: application/json

{
  "arguments": {
    "a": 10,
    "b": 5
  }
}
```

**Example response:**
```json
{
  "tool": "add",
  "result": [
    {
      "type": "text",
      "text": "Result: 10 + 5 = 15"
    }
  ]
}
```

---

## Tool Implementation

### Adding a New Tool

**Step-by-step guide to add a `modulo` tool:**

#### Step 1: Add Tool Definition

In `calculator_server.py`, add to the `list_tools()` function:

```python
Tool(
    name="modulo",
    description="Calculate remainder when first number is divided by second number",
    inputSchema={
        "type": "object",
        "properties": {
            "a": {
                "type": "number",
                "description": "Dividend"
            },
            "b": {
                "type": "number",
                "description": "Divisor (cannot be zero)"
            }
        },
        "required": ["a", "b"]
    }
)
```

#### Step 2: Add Tool Handler

In `calculator_server.py`, add to the `call_tool()` function:

```python
elif name == "modulo":
    if arguments["b"] == 0:
        return [TextContent(
            type="text",
            text="Error: Modulo by zero is not allowed"
        )]
    result = arguments["a"] % arguments["b"]
    return [TextContent(
        type="text",
        text=f"Result: {arguments['a']} mod {arguments['b']} = {result}"
    )]
```

#### Step 3: Test Locally

```bash
# Start server
cd mcp-server
python -m uvicorn src.http_server:app --reload

# Test tool listing
curl http://localhost:8000/tools

# Test tool execution
curl -X POST http://localhost:8000/tools/modulo \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"a": 10, "b": 3}}'

# Expected: {"tool": "modulo", "result": [{"type": "text", "text": "Result: 10 mod 3 = 1"}]}
```

#### Step 4: Rebuild and Redeploy

```bash
# Rebuild Docker image
gcloud builds submit --tag us-central1-docker.pkg.dev/agentic-ai-batch-2025/mcp-servers/mcp-calculator:latest

# Redeploy to Cloud Run (done automatically by Cloud Run)
# Test in production
curl https://mcp-calculator-server-oyhyp5p3ua-uc.a.run.app/tools/modulo \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"a": 10, "b": 3}}'
```

---

## HTTP Transport Layer

### Why HTTP Instead of stdio?

**stdio (Standard Input/Output):**
```
✓ Direct MCP protocol communication
✓ Efficient for local clients
✗ Not suitable for web deployment
✗ Can't scale horizontally
✗ No REST API
```

**HTTP:**
```
✓ Works with Cloud Run
✓ RESTful API for easy testing
✓ Horizontal scaling
✓ Standard web protocols
✗ Slight overhead (negligible)
```

### API Endpoints

| Method | Endpoint | Purpose | Request Body | Response |
|--------|----------|---------|--------------|----------|
| GET | `/` | Service info | None | Service metadata |
| GET | `/health` | Health check | None | `{"status": "healthy"}` |
| GET | `/tools` | List all tools | None | Array of tool definitions |
| POST | `/tools/{tool_name}` | Execute tool | `{"arguments": {...}}` | Tool result |

### Authentication

**Current:** Public access (for testing)
**Production:** Should require authentication

```python
# Add to http_server.py
from fastapi import HTTPBearer, Depends

security = HTTPBearer()

@app.post("/tools/{tool_name}")
async def call_tool(
    tool_name: str,
    request: Request,
    token: str = Depends(security)  # Require bearer token
):
    # Validate token
    # ...
```

---

## Deployment

### Docker Container

**File:** `mcp-server/Dockerfile`

```dockerfile
# Multi-stage build for smaller image
FROM python:3.11-slim as builder
# ... install dependencies

FROM python:3.11-slim
# ... copy files and run
CMD ["uvicorn", "src.http_server:app", "--host", "0.0.0.0", "--port", "8080"]
```

### Cloud Run Deployment

**Automatic scaling configuration:**
- Min instances: 0 (scale to zero)
- Max instances: 10
- Concurrency: 80 requests per container
- CPU: 1 vCPU
- Memory: 512 MB

**URL:** https://mcp-calculator-server-oyhyp5p3ua-uc.a.run.app

---

## Testing

### Local Testing

```bash
# Start server
cd mcp-server
python -m uvicorn src.http_server:app --reload

# Test in browser
http://localhost:8000

# Test with curl
curl http://localhost:8000/tools
curl -X POST http://localhost:8000/tools/add \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"a": 10, "b": 5}}'
```

### Production Testing

```bash
# Use provided test script
cd /home/agenticai/google-adk-mcp
./scripts/test-mcp-server.sh

# Or test manually
MCP_URL="https://mcp-calculator-server-oyhyp5p3ua-uc.a.run.app"

curl $MCP_URL/health
curl $MCP_URL/tools
curl -X POST $MCP_URL/tools/add \
  -H "Content-Type: application/json" \
  -d '{"arguments": {"a": 10, "b": 5}}'
```

---

## Extending the Server

### Ideas for New Tools

1. **Advanced Math:**
   - `logarithm(base, value)`
   - `trigonometry(function, angle)`
   - `factorial(n)`

2. **Unit Conversion:**
   - `convert_temperature(value, from_unit, to_unit)`
   - `convert_length(value, from_unit, to_unit)`
   - `convert_currency(amount, from_currency, to_currency)`

3. **Data Operations:**
   - `average(numbers)`
   - `median(numbers)`
   - `standard_deviation(numbers)`

4. **String Operations:**
   - `concatenate(strings)`
   - `reverse(text)`
   - `count_words(text)`

### Pattern for Complex Tools

For tools that need external APIs:

```python
import httpx

Tool(
    name="convert_currency",
    description="Convert currency using live exchange rates",
    inputSchema={
        "type": "object",
        "properties": {
            "amount": {"type": "number"},
            "from_currency": {"type": "string"},
            "to_currency": {"type": "string"}
        },
        "required": ["amount", "from_currency", "to_currency"]
    }
)

# Handler
elif name == "convert_currency":
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.exchangerate.com/convert",
            params={
                "from": arguments["from_currency"],
                "to": arguments["to_currency"],
                "amount": arguments["amount"]
            }
        )
        result = response.json()["result"]
        return [TextContent(
            type="text",
            text=f"Result: {arguments['amount']} {arguments['from_currency']} = {result} {arguments['to_currency']}"
        )]
```

---

## Summary

**Key Takeaways:**

1. **MCP is a standard protocol** for AI tools
2. **Two-layer architecture:** MCP core + HTTP wrapper
3. **Tool definition:** Name, description, JSON Schema
4. **Tool execution:** Extract args, compute, return TextContent
5. **HTTP wrapper:** Makes tools accessible via REST API
6. **Cloud Run deployment:** Serverless, auto-scaling
7. **Easy to extend:** Add new tools by following pattern

**File Reference:**
- `mcp-server/src/calculator_server.py:18-144` - Tool definitions
- `mcp-server/src/calculator_server.py:147-220` - Tool execution
- `mcp-server/src/http_server.py:78-98` - List tools API
- `mcp-server/src/http_server.py:101-125` - Execute tool API

**Next Steps:**
- Read `docs/AGENT_ENGINE_EXPLAINED.md` to understand how the agent calls these tools
- Try adding a new tool following the pattern
- Experiment with different tool types
