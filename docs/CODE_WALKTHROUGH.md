# Code Walkthrough

**Line-by-Line Analysis of Key Code Sections**

---

## Table of Contents

1. [MCP Server Code](#mcp-server-code)
2. [Agent Deployment Code](#agent-deployment-code)
3. [Streamlit UI Code](#streamlit-ui-code)
4. [Terraform Configuration](#terraform-configuration)

---

## MCP Server Code

### calculator_server.py - Tool Definition

**File:** `mcp-server/src/calculator_server.py:18-39`

```python
1 @app.list_tools()
2 async def list_tools() -> list[Tool]:
3     """List available calculator tools."""
4     return [
5         Tool(
6             name="add",
7             description="Add two numbers together",
8             inputSchema={
9                 "type": "object",
10                 "properties": {
11                     "a": {
12                         "type": "number",
13                         "description": "First number"
14                     },
15                     "b": {
16                         "type": "number",
17                         "description": "Second number"
18                     }
19                 },
20                 "required": ["a", "b"]
21             }
22         ),
        # ... more tools
```

**Line-by-line:**

- **Line 1:** `@app.list_tools()` - Decorator that registers this function with the MCP server. When a client asks "what tools are available?", this function is called.

- **Line 2:** `async def list_tools()` - Async function because MCP uses async/await pattern for I/O operations.

- **Line 2:** `-> list[Tool]` - Type hint indicating this returns a list of Tool objects.

- **Line 5-22:** `Tool(...)` - Creates a Tool object (from MCP SDK) that describes one calculator function.

- **Line 6:** `name="add"` - Unique identifier for this tool. AI models use this name when calling the tool.

- **Line 7:** `description=...` - Human-readable description. AI models read this to understand when to use the tool.

- **Line 8-21:** `inputSchema={...}` - JSON Schema definition of expected inputs. This is crucial for:
  - AI models to generate correct function calls
  - Automatic input validation
  - Documentation generation

- **Line 9:** `"type": "object"` - The input is a JSON object (dictionary in Python).

- **Line 10-19:** `"properties": {...}` - Defines each parameter:
  - `"a"`: First parameter
  - `"b"`: Second parameter

- **Line 12:** `"type": "number"` - Parameter type must be a number (int or float).

- **Line 13:** `"description": "First number"` - Helps AI understand what this parameter is for.

- **Line 20:** `"required": ["a", "b"]` - Both parameters are mandatory.

### calculator_server.py - Tool Execution

**File:** `mcp-server/src/calculator_server.py:147-156`

```python
1 @app.call_tool()
2 async def call_tool(name: str, arguments: Any) -> list[TextContent | ImageContent | EmbeddedResource]:
3     """Handle tool execution."""
4     try:
5         if name == "add":
6             result = arguments["a"] + arguments["b"]
7             return [TextContent(
8                 type="text",
9                 text=f"Result: {arguments['a']} + {arguments['b']} = {result}"
10             )]
```

**Line-by-line:**

- **Line 1:** `@app.call_tool()` - Decorator that registers this as the tool execution handler. When a tool is called, this function routes to the correct implementation.

- **Line 2:** `name: str` - Which tool to execute (e.g., "add", "subtract").

- **Line 2:** `arguments: Any` - Dictionary of parameters (e.g., `{"a": 10, "b": 5}`).

- **Line 2:** `-> list[TextContent | ImageContent | EmbeddedResource]` - Return type: list of content objects. Tools can return text, images, or embedded resources.

- **Line 4:** `try:` - Error handling block to catch any exceptions during execution.

- **Line 5:** `if name == "add":` - Check which tool was requested.

- **Line 6:** `result = arguments["a"] + arguments["b"]` - Actual calculation. `arguments` is a dictionary, so we access parameters by key.

- **Line 7-10:** Return structured response:
  - **Line 7:** Return a list (MCP protocol requires a list even for single items)
  - **Line 7:** `TextContent(...)` - Wrap result in TextContent object
  - **Line 8:** `type="text"` - Indicates this is text content
  - **Line 9:** `text=f"Result: ..."` - Formatted result string with calculation details

**Why format as "Result: 10 + 5 = 15"?**
- Provides context to the AI model
- AI can use this to generate natural language responses
- Helps with debugging (see what calculation was performed)

### http_server.py - FastAPI Wrapper

**File:** `mcp-server/src/http_server.py:101-125`

```python
1 @app.post("/tools/{tool_name}")
2 async def call_tool(tool_name: str, request: Request):
3     """Execute a specific tool."""
4     try:
5         body = await request.json()
6         arguments = body.get("arguments", {})
7
8         # Execute tool via MCP handler
9         result = await call_tool_handler(tool_name, arguments)
10
11        return {
12            "tool": tool_name,
13            "result": [
14                {
15                    "type": r.type,
16                    "text": r.text
17                }
18                for r in result
19            ]
20        }
21    except Exception as e:
22        logger.error(f"Error calling tool {tool_name}: {e}")
23        return JSONResponse(
24            status_code=500,
25            content={"error": str(e)}
26        )
```

**Line-by-line:**

- **Line 1:** `@app.post("/tools/{tool_name}")` - FastAPI route decorator. Creates POST endpoint at `/tools/{tool_name}` where `{tool_name}` is a path parameter.

- **Line 2:** `tool_name: str` - Extracted from URL path (e.g., `/tools/add` → `tool_name="add"`).

- **Line 2:** `request: Request` - FastAPI Request object containing HTTP request data.

- **Line 5:** `await request.json()` - Parse JSON body from HTTP request. `await` because reading request body is async.

- **Line 6:** `arguments = body.get("arguments", {})` - Extract `arguments` key from body. If missing, use empty dict `{}`.

**Example request body:**
```json
{
  "arguments": {
    "a": 10,
    "b": 5
  }
}
```

- **Line 9:** `await call_tool_handler(tool_name, arguments)` - Call the MCP tool execution handler (from calculator_server.py).

- **Line 11-20:** Build HTTP response:
  - **Line 12:** Include tool name for reference
  - **Line 13-19:** Convert `TextContent` objects to JSON dictionaries
  - **Line 18:** `for r in result` - List comprehension to process each result item

- **Line 21-26:** Error handling:
  - **Line 22:** Log error for debugging
  - **Line 23-26:** Return 500 status code with error message

---

## Agent Deployment Code

### Tool Wrapper Pattern

**File:** `agent/deploy_agent_programmatic.py:32-48`

```python
1 def add(a: float, b: float) -> str:
2     """Add two numbers together.
3
4     Args:
5         a: First number
6         b: Second number
7
8     Returns:
9         Result of addition
10    """
11    response = requests.post(
12        f"{MCP_SERVER_URL}/tools/add",
13        json={"arguments": {"a": a, "b": b}},
14        timeout=10
15    )
16    result = response.json()
17    return result["result"][0]["text"]
```

**Line-by-line:**

- **Line 1:** Function signature. **Important:** Vertex AI reads this signature to understand:
  - Function name: `add`
  - Parameters: `a` and `b`, both floats
  - Return type: string

- **Lines 2-10:** Docstring. **Important:** Vertex AI reads this to understand:
  - What the function does
  - What each parameter means
  - What it returns
  - This becomes the "tool description" for the AI model

- **Line 11-15:** HTTP request to MCP server:
  - **Line 11:** `requests.post(...)` - Make HTTP POST request
  - **Line 12:** Endpoint: `{MCP_SERVER_URL}/tools/add`
  - **Line 13:** Request body: `{"arguments": {"a": a, "b": b}}`
  - **Line 14:** `timeout=10` - Fail if no response in 10 seconds

- **Line 16:** Parse JSON response from MCP server.

**MCP Server returns:**
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

- **Line 17:** Extract the text:
  - `result["result"]` - Get the "result" array
  - `[0]` - Get first item
  - `["text"]` - Get the "text" field
  - Returns: `"Result: 10 + 5 = 15"`

**Why this pattern?**

The wrapper bridges two systems:
```
Vertex AI Agent → Python function → HTTP request → MCP Server → HTTP response → Python return → Vertex AI Agent
```

### Agent Creation and Deployment

**File:** `agent/deploy_agent_programmatic.py:202-252`

```python
1 # Initialize Vertex AI
2 vertexai.init(
3     project=PROJECT_ID,
4     location=LOCATION,
5     staging_bucket=f"gs://{PROJECT_ID}-staging"
6 )
7
8 # Create agent with calculator tools
9 agent = agent_engines.LangchainAgent(
10    model="gemini-2.0-flash-exp",
11    tools=[add, subtract, multiply, divide, percentage, sqrt, power],
12    system_instruction=SYSTEM_INSTRUCTION,
13    model_kwargs={
14        "temperature": 0.7,
15        "top_p": 0.95,
16        "max_output_tokens": 2048,
17    }
18 )
19
20 # Deploy to Vertex AI Agent Engine
21 remote_agent = agent_engines.create(
22    agent_engine=agent,
23    requirements=[
24        "google-cloud-aiplatform[agent_engines,langchain]>=1.112",
25        "requests>=2.31.0"
26    ],
27    display_name=AGENT_NAME,
28 )
```

**Line-by-line:**

- **Lines 2-6:** Initialize Vertex AI SDK:
  - **Line 3:** Set GCP project
  - **Line 4:** Set region (where agent will run)
  - **Line 5:** Set Cloud Storage bucket for artifacts

- **Lines 9-18:** Create agent locally:
  - **Line 10:** `model="gemini-2.0-flash-exp"` - Which LLM to use
    - `flash` = faster and cheaper than `pro`
    - `exp` = experimental/latest version

  - **Line 11:** `tools=[...]` - List of Python functions agent can call
    - Vertex AI inspects each function:
      - Reads function signature
      - Reads docstring
      - Creates tool schema automatically

  - **Line 12:** `system_instruction` - Agent personality and guidelines

  - **Lines 13-17:** Model parameters:
    - **Line 14:** `temperature=0.7` - Randomness (0=deterministic, 1=creative)
    - **Line 15:** `top_p=0.95` - Nucleus sampling (diversity)
    - **Line 16:** `max_output_tokens=2048` - Maximum response length

- **Lines 21-28:** Deploy agent to cloud:
  - **Line 22:** `agent_engine=agent` - Agent to deploy
  - **Lines 23-26:** `requirements=[...]` - Python packages needed
    - These are installed in the cloud environment
    - Agent runs in isolated container with these packages
  - **Line 27:** `display_name` - Human-readable name for UI

**What happens during deployment:**
```
1. Package agent code (functions, instructions, config)
2. Upload to Cloud Storage bucket
3. Create container image with dependencies
4. Deploy container to Vertex AI Agent Engine
5. Return resource name for accessing agent
```

---

## Streamlit UI Code

### Session State Initialization

**File:** `ui/utils.py:91-102`

```python
1 def initialize_session_state():
2     """Initialize Streamlit session state variables"""
3     if "messages" not in st.session_state:
4         st.session_state.messages = []
5
6     if "agent_initialized" not in st.session_state:
7         st.session_state.agent_initialized = False
8
9     if "dark_mode" not in st.session_state:
10        st.session_state.dark_mode = False
11
12    if "query_count" not in st.session_state:
13        st.session_state.query_count = 0
```

**Line-by-line:**

- **Line 3:** `if "messages" not in st.session_state:` - Check if "messages" key exists
  - **Why:** Streamlit reruns entire script on every interaction
  - **Need:** Persist data across reruns
  - **Solution:** `st.session_state` (like cookies but server-side)

- **Line 4:** Initialize empty list for chat messages

**Pattern explanation:**
```python
# First run:
"messages" not in st.session_state → True
st.session_state.messages = [] → Initialize

# Button clicked, script reruns:
"messages" not in st.session_state → False (already exists)
Skip initialization, use existing list
```

This pattern ensures variables are created once and persist across interactions.

### Agent Query Function

**File:** `ui/app.py:47-59`

```python
1 def query_agent(user_input: str) -> str:
2     """Query the AI agent with user input"""
3     try:
4         with st.spinner("Agent is thinking..."):
5             response = st.session_state.agent.query(input=user_input)
6             return response.get("output", "No response received.")
7     except Exception as e:
8         return f"Error querying agent: {str(e)}"
```

**Line-by-line:**

- **Line 4:** `with st.spinner("Agent is thinking..."):`
  - Displays animated spinner with message
  - Shown while code block executes
  - Automatically removed when block finishes

- **Line 5:** `st.session_state.agent.query(input=user_input)`
  - `st.session_state.agent` - Agent object from initialization
  - `.query(input=user_input)` - Call agent with user's message
  - This makes HTTP request to Vertex AI
  - Returns dictionary with agent response

**Response structure:**
```python
{
  "output": "10 plus 5 equals 15.",
  "metadata": {...}
}
```

- **Line 6:** `response.get("output", "No response received.")`
  - Extract "output" key
  - If key missing, return default message
  - Safe navigation (won't crash if malformed response)

- **Line 7-8:** Error handling
  - Catches any exception (network errors, authentication failures, etc.)
  - Returns error message as string (displayed to user)

### Chat Interface Rendering

**File:** `ui/app.py:195-226`

```python
1 if prompt := st.chat_input("Type your message here..."):
2     # Add user message
3     utils.add_message("user", prompt)
4
5     # Display user message immediately
6     with st.chat_message("user"):
7         st.markdown(prompt)
8         st.caption(f"_{utils.format_timestamp()}_")
9
10    # Get agent response
11    response = query_agent(prompt)
12    utils.add_message("assistant", response)
13
14    # Display assistant message
15    with st.chat_message("assistant"):
16        st.markdown(response)
17        st.caption(f"_{utils.format_timestamp()}_")
18
19    st.rerun()  # Refresh to update sidebar stats
```

**Line-by-line:**

- **Line 1:** `if prompt := st.chat_input("Type your message here..."):`
  - **Walrus operator** `:=` - Assign and check in one line
  - Equivalent to:
    ```python
    prompt = st.chat_input("Type your message here...")
    if prompt:
    ```
  - `st.chat_input()` - Streamlit's chat input widget (bottom of screen)
  - Returns user's text when they press Enter
  - Returns `None` (falsy) if no input yet

- **Line 3:** `utils.add_message("user", prompt)`
  - Store user message in session state
  - Persists across reruns

- **Lines 6-8:** Display user message:
  - **Line 6:** `with st.chat_message("user"):` - Creates user-styled chat bubble
  - **Line 7:** `st.markdown(prompt)` - Display message text (supports markdown)
  - **Line 8:** `st.caption(...)` - Display timestamp in small text

- **Line 11:** Get response from agent (may take 2-4 seconds)

- **Line 12:** Store assistant response in session state

- **Lines 15-17:** Display assistant message (similar to user message)

- **Line 19:** `st.rerun()` - Refresh entire page
  - Updates sidebar statistics
  - Adds new messages to history
  - Resets chat input box

**Flow diagram:**
```
User types → st.chat_input() returns text → Add to session → Display → Query agent → Add response → Display → Rerun
```

---

## Terraform Configuration

### Cloud Run Service Resource

**File:** `terraform/main.tf:98-155`

```terraform
1 resource "google_cloud_run_v2_service" "mcp_server" {
2   name     = var.mcp_server_name
3   location = var.region
4
5   template {
6     service_account = google_service_account.mcp_server_sa.email
7
8     containers {
9       image = "${var.region}-docker.pkg.dev/${var.project_id}/${var.artifact_registry_repository}/mcp-calculator:latest"
10
11      ports {
12        container_port = 8080
13      }
14
15      resources {
16        limits = {
17          cpu    = "1"
18          memory = "512Mi"
19        }
20        cpu_idle = true
21      }
22    }
23
24    scaling {
25      min_instance_count = 0
26      max_instance_count = 10
27    }
28  }
29
30  lifecycle {
31    ignore_changes = [
32      template[0].containers[0].image
33    ]
34  }
35 }
```

**Line-by-line:**

- **Line 1:** `resource "google_cloud_run_v2_service" "mcp_server"`
  - Create Google Cloud Run service
  - Type: `google_cloud_run_v2_service` (gen2)
  - Local name: `mcp_server` (for referencing in Terraform)

- **Lines 2-3:** Basic configuration
  - **Line 2:** Service name in GCP
  - **Line 3:** Region (us-central1)

- **Line 5:** `template {` - Service revision template (defines how to run)

- **Line 6:** Service account for authentication/authorization

- **Lines 8-22:** Container configuration:
  - **Line 9:** Docker image URL
    - Format: `REGION-docker.pkg.dev/PROJECT/REPO/IMAGE:TAG`
    - Example: `us-central1-docker.pkg.dev/my-project/mcp-servers/mcp-calculator:latest`

  - **Lines 11-13:** Port configuration
    - Container listens on port 8080
    - Cloud Run routes HTTP to this port

  - **Lines 15-21:** Resource limits
    - **Line 17:** Max 1 vCPU per container
    - **Line 18:** Max 512MB RAM per container
    - **Line 20:** `cpu_idle = true` - Allow CPU throttling when idle (enables scale-to-zero)

- **Lines 24-27:** Scaling configuration:
  - **Line 25:** `min_instance_count = 0` - Scale to zero (no idle cost!)
  - **Line 26:** `max_instance_count = 10` - Max 10 containers

**Scaling behavior:**
```
0 requests → 0 instances (no cost)
1 request  → 1 instance spins up (~2-3s cold start)
100 requests → 2-3 instances (auto-scale)
1000 requests → 10 instances (max reached)
No requests for 15 min → Scale back to 0
```

- **Lines 30-34:** Lifecycle configuration:
  - **Line 32:** `ignore_changes = [template[0].containers[0].image]`
  - **Why:** Allow manual Docker image updates without Terraform detecting "drift"
  - **Effect:** Can run `gcloud builds submit` without Terraform trying to "fix" it

**Without this:**
```
1. Deploy with Terraform (image v1)
2. Manually push image v2
3. Terraform plan → "Drift detected! Will revert to v1"
```

**With this:**
```
1. Deploy with Terraform (image v1)
2. Manually push image v2
3. Terraform plan → "No changes needed"
```

---

## Summary

**Key patterns learned:**

1. **MCP Tool Pattern**: Tool definition + Tool execution
2. **Wrapper Pattern**: Bridge Vertex AI ↔ MCP HTTP
3. **Session State**: Persist data across Streamlit reruns
4. **Async/Await**: Handle I/O operations efficiently
5. **Error Handling**: Try/except with fallback responses
6. **Terraform Lifecycle**: Manage resource updates

**Code references:**
- MCP tool: `mcp-server/src/calculator_server.py:18-156`
- HTTP wrapper: `mcp-server/src/http_server.py:101-125`
- Agent wrapper: `agent/deploy_agent_programmatic.py:32-48`
- Agent deploy: `agent/deploy_agent_programmatic.py:202-252`
- UI initialization: `ui/utils.py:91-102`
- UI chat: `ui/app.py:195-226`
- Terraform Cloud Run: `terraform/main.tf:98-155`

**Understanding these patterns prepares you to:**
- Add new MCP tools
- Modify agent behavior
- Customize UI features
- Adjust infrastructure configuration
