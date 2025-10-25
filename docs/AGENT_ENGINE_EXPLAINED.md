# Agent Engine Explained

**Complete Guide to Vertex AI Agent Engine and Google ADK**

---

## Table of Contents

1. [What is Vertex AI Agent Engine?](#what-is-vertex-ai-agent-engine)
2. [Agent Architecture](#agent-architecture)
3. [Deployment Code Walkthrough](#deployment-code-walkthrough)
4. [How Tool Calling Works](#how-tool-calling-works)
5. [Agent Configuration](#agent-configuration)
6. [Testing the Agent](#testing-the-agent)
7. [Advanced Topics](#advanced-topics)

---

## What is Vertex AI Agent Engine?

### Overview

**Vertex AI Agent Engine** is Google's managed service for deploying AI agents that can use tools and reason about tasks.

**Think of it as:**
```
Agent Engine = LLM (Gemini) + Tool Calling + Orchestration + Managed Hosting
```

### Key Components

```
┌─────────────────────────────────────────┐
│  Vertex AI Agent Engine                 │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  Gemini 2.0 Flash Model           │ │
│  │  - Natural language understanding  │ │
│  │  - Reasoning capabilities          │ │
│  │  - Response generation             │ │
│  └─────────────┬─────────────────────┘ │
│                │                        │
│  ┌─────────────▼─────────────────────┐ │
│  │  Agent Orchestrator                │ │
│  │  - Tool selection                  │ │
│  │  - Execution planning              │ │
│  │  - Result synthesis                │ │
│  └─────────────┬─────────────────────┘ │
│                │                        │
│  ┌─────────────▼─────────────────────┐ │
│  │  Tool Registry                     │ │
│  │  - add(), subtract(), multiply()   │ │
│  │  - divide(), percentage()          │ │
│  │  - sqrt(), power()                 │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Why Use Agent Engine?

**Benefits:**
1. **Fully Managed:** Google handles infrastructure, scaling, updates
2. **Built-in Tool Calling:** Native support for function calling
3. **State-of-the-art Model:** Gemini 2.0 Flash
4. **Auto-scaling:** Handles 1 to 1000s of users
5. **Integrated Monitoring:** Cloud Logging and Monitoring

**Alternatives (and why we didn't use them):**
- **LangChain + self-hosting:** More work, need to manage servers
- **OpenAI Assistants API:** Vendor lock-in, not GCP-native
- **Custom agent code:** Requires ML expertise, harder to scale

---

## Agent Architecture

### ReAct Pattern (Reasoning + Acting)

Our agent follows the **ReAct pattern**:

```
1. OBSERVE: Receive user query
   ↓
2. REASON: Understand what needs to be done
   ↓
3. ACT: Use tools to get information
   ↓
4. OBSERVE: Get tool results
   ↓
5. REASON: Synthesize information
   ↓
6. RESPOND: Generate natural language response
```

**Example:**

```
User: "I'm buying 3 items at $29.99 each. What's the total?"

1. OBSERVE:
   Input: "I'm buying 3 items at $29.99 each. What's the total?"

2. REASON:
   Agent thinks: "This is a multiplication problem: 3 × $29.99"
   Agent decides: "I need to use the multiply tool"

3. ACT:
   Agent calls: multiply(a=3, b=29.99)

4. OBSERVE:
   Tool returns: "Result: 3 × 29.99 = 89.97"

5. REASON:
   Agent synthesizes: "The calculation is complete, 89.97 is the total"

6. RESPOND:
   Agent says: "The total for 3 items at $29.99 each is $89.97."
```

### Agent Components

**File:** `agent/deploy_agent_programmatic.py`

```
deploy_agent_programmatic.py
├── Tool Wrappers (lines 32-161)
│   ├── add()
│   ├── subtract()
│   ├── multiply()
│   ├── divide()
│   ├── percentage()
│   ├── sqrt()
│   └── power()
│
├── System Instructions (lines 165-188)
│   └── Agent personality and guidelines
│
└── Deployment Logic (lines 191-284)
    ├── Initialize Vertex AI
    ├── Create agent
    ├── Deploy to Agent Engine
    └── Test deployed agent
```

---

## Deployment Code Walkthrough

### Tool Wrapper Pattern

**Why wrap MCP tools?**

The MCP server exposes HTTP endpoints, but Vertex AI Agent Engine expects Python functions. We create **wrapper functions** that bridge this gap.

**Pattern:**

```python
def tool_name(param1: type, param2: type) -> str:
    """
    Tool description for the AI model.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Result description
    """
    # Make HTTP request to MCP server
    response = requests.post(
        f"{MCP_SERVER_URL}/tools/tool_name",
        json={"arguments": {"param1": param1, "param2": param2}},
        timeout=10
    )

    # Extract and return result
    result = response.json()
    return result["result"][0]["text"]
```

**Example: add() function**

```python
def add(a: float, b: float) -> str:
    """Add two numbers together.

    Args:
        a: First number
        b: Second number

    Returns:
        Result of addition
    """
    response = requests.post(
        f"{MCP_SERVER_URL}/tools/add",
        json={"arguments": {"a": a, "b": b}},
        timeout=10
    )
    result = response.json()
    return result["result"][0]["text"]
```

**What happens:**
1. Agent decides to call `add(10, 5)`
2. Wrapper function makes HTTP POST to MCP server
3. MCP server executes calculation
4. Wrapper returns "Result: 10 + 5 = 15"
5. Agent uses this in response generation

### System Instructions

**File:** `agent/deploy_agent_programmatic.py:165-188`

```python
SYSTEM_INSTRUCTION = """You are a helpful and friendly customer support agent...

Your responsibilities include:
- Answering customer questions about products, orders, and policies
- Helping customers with calculations (pricing, discounts, taxes, shipping costs)
- Providing clear and accurate information
...
"""
```

**Why this matters:**
- Defines agent personality
- Sets behavioral guidelines
- Specifies when to use tools
- Establishes response style

**Customization:**
Edit this string to change agent behavior:
- More formal: "You are a professional financial advisor..."
- More casual: "You're a friendly shopping buddy..."
- Different domain: "You are a math tutor helping students..."

### Agent Creation

**File:** `agent/deploy_agent_programmatic.py:226-235`

```python
agent = agent_engines.LangchainAgent(
    model="gemini-2.0-flash-exp",              # Which LLM to use
    tools=[add, subtract, multiply, ...],      # Available tools
    system_instruction=SYSTEM_INSTRUCTION,     # Personality
    model_kwargs={                             # Model parameters
        "temperature": 0.7,                    # Creativity (0-1)
        "top_p": 0.95,                         # Nucleus sampling
        "max_output_tokens": 2048,             # Max response length
    }
)
```

**Parameters explained:**

| Parameter | Value | Effect |
|-----------|-------|--------|
| `model` | `gemini-2.0-flash-exp` | Which Gemini model (flash = faster/cheaper) |
| `tools` | List of functions | Tools agent can use |
| `system_instruction` | String | Agent personality/guidelines |
| `temperature` | 0.7 | Higher = more creative, Lower = more deterministic |
| `top_p` | 0.95 | Nucleus sampling (diversity of vocabulary) |
| `max_output_tokens` | 2048 | Maximum response length |

### Deployment to Vertex AI

**File:** `agent/deploy_agent_programmatic.py:244-251`

```python
remote_agent = agent_engines.create(
    agent_engine=agent,                       # Agent to deploy
    requirements=[                            # Python dependencies
        "google-cloud-aiplatform[agent_engines,langchain]>=1.112",
        "requests>=2.31.0"
    ],
    display_name=AGENT_NAME,                  # Name in console
)
```

**What happens during deployment:**

```
1. Package agent code
   ├── Tool wrapper functions
   ├── System instructions
   ├── Model configuration
   └── Dependencies

2. Upload to Cloud Storage
   └── gs://agentic-ai-batch-2025-staging/

3. Create Reasoning Engine resource
   └── Vertex AI provisions infrastructure

4. Return resource name
   └── projects/740202511174/locations/us-central1/reasoningEngines/8601228775440515072
```

**Deployment takes:** ~2-5 minutes

---

## How Tool Calling Works

### End-to-End Flow

```
┌─────────────────────────────────────────────────────┐
│ 1. User Query                                        │
│    "What is 10 + 5?"                                 │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 2. Agent Receives Query                             │
│    agent.query(input="What is 10 + 5?")             │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 3. Gemini Processes Input                           │
│    Model analyzes: "This needs addition"            │
│    Model output:                                     │
│    {                                                 │
│      "tool_to_call": "add",                          │
│      "parameters": {"a": 10, "b": 5}                 │
│    }                                                 │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 4. Agent Executes Tool                              │
│    result = add(a=10, b=5)                           │
│      ↓                                               │
│    HTTP POST to MCP Server                           │
│      ↓                                               │
│    Returns: "Result: 10 + 5 = 15"                    │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 5. Gemini Generates Response                        │
│    Input: Tool result + original query              │
│    Output: "10 plus 5 equals 15."                   │
└──────────────────┬──────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────┐
│ 6. Return to User                                   │
│    {"output": "10 plus 5 equals 15."}               │
└─────────────────────────────────────────────────────┘
```

### Multi-Step Tool Calling

For complex queries, agent may call multiple tools:

```
User: "I have a $120 order with a 15% discount. What's my final price?"

Step 1: Calculate discount
  └── percentage(number=120, percent=15) → "Result: 15% of 120 = 18"

Step 2: Subtract discount
  └── subtract(a=120, b=18) → "Result: 120 - 18 = 102"

Step 3: Generate response
  └── "With a 15% discount on $120, you save $18. Your final price is $102."
```

---

## Agent Configuration

### Configuration Files

**1. System Prompt**

**File:** `agent/prompts/system_prompt.txt`

```
You are a helpful and friendly customer support agent...
```

**Modify this to change:**
- Agent personality
- Response style
- Domain knowledge
- Tool usage guidelines

**2. Agent Config**

**File:** `agent/agent_config.yaml`

```yaml
agent_name: "customer-support-agent"
model: "gemini-2.0-flash-exp"
temperature: 0.7
max_output_tokens: 2048

tools:
  - name: "add"
    description: "Add two numbers"
  - name: "subtract"
    description: "Subtract numbers"
  # ... more tools

examples:
  - input: "What is 10 + 5?"
    output: "10 plus 5 equals 15."
```

### Model Parameters

| Parameter | Range | Recommendation | Effect |
|-----------|-------|----------------|--------|
| **temperature** | 0.0 - 1.0 | 0.7 for chat, 0.2 for precise tasks | Higher = more creative |
| **top_p** | 0.0 - 1.0 | 0.95 | Nucleus sampling threshold |
| **top_k** | 1 - 40 | 40 | Number of tokens to consider |
| **max_output_tokens** | 1 - 8192 | 2048 | Maximum response length |

**Examples:**

```python
# Creative agent (storytelling, brainstorming)
model_kwargs={"temperature": 0.9, "top_p": 0.95}

# Precise agent (calculations, data extraction)
model_kwargs={"temperature": 0.2, "top_p": 0.9}

# Balanced agent (customer support)
model_kwargs={"temperature": 0.7, "top_p": 0.95}
```

---

## Testing the Agent

### Local Testing

```bash
cd /home/agenticai/google-adk-mcp/agent

# Test locally before deployment
python deploy_agent_programmatic.py --test-local
```

### Interactive Chat

```bash
# Chat with deployed agent
python chat_with_agent.py
```

### Automated Tests

```bash
# Run test suite
python test_deployed_agent.py
```

**Test file:** `agent/test_deployed_agent.py`

```python
test_queries = [
    "What is 5 plus 3?",                              # Simple addition
    "Calculate 15% of 100",                            # Percentage
    "$120 order with 15% discount. Final price?",     # Multi-step
    "What's the square root of 64?",                   # Square root
    "4 items at $25.50 each?",                         # Multiplication
]

for query in test_queries:
    response = agent.query(input=query)
    print(f"Q: {query}")
    print(f"A: {response['output']}\n")
```

---

## Advanced Topics

### Redeploying Updated Agent

```bash
cd /home/agenticai/google-adk-mcp/agent

# Make changes to:
# - Tool functions
# - System instructions
# - Model parameters

# Redeploy
python deploy_agent_programmatic.py

# New resource name will be generated
# Update UI config.py with new resource name
```

### Adding New Tools

**Step 1:** Create wrapper function

```python
def new_tool(param1: type, param2: type) -> str:
    """Tool description."""
    response = requests.post(
        f"{MCP_SERVER_URL}/tools/new_tool",
        json={"arguments": {"param1": param1, "param2": param2}},
        timeout=10
    )
    return response.json()["result"][0]["text"]
```

**Step 2:** Add to tools list

```python
agent = agent_engines.LangchainAgent(
    model="gemini-2.0-flash-exp",
    tools=[add, subtract, ..., new_tool],  # Add here
    system_instruction=SYSTEM_INSTRUCTION,
)
```

**Step 3:** Update system instructions

```python
SYSTEM_INSTRUCTION = """...
You have access to these tools:
- ...
- new_tool: Description of new tool
"""
```

**Step 4:** Redeploy

```bash
python deploy_agent_programmatic.py
```

### Monitoring Agent Performance

**View logs:**
```bash
gcloud logging read \
  "resource.type=aiplatform.googleapis.com/ReasoningEngine" \
  --limit=50 \
  --project=agentic-ai-batch-2025
```

**Metrics to monitor:**
- Response time
- Tool call frequency
- Error rate
- Token usage

### Cost Optimization

**Strategies:**
1. **Use flash model:** `gemini-2.0-flash-exp` is cheaper than `gemini-pro`
2. **Lower temperature:** Reduces token usage slightly
3. **Shorter system instructions:** Fewer input tokens
4. **Cache common queries:** At application level

**Cost breakdown:**
```
Agent query cost = Model inference + Tool calls + Storage

Typical query:
- Model inference: ~$0.005
- Tool calls (HTTP): negligible
- Storage: ~$0.000001

Total per query: ~$0.005
```

---

## Summary

**Key Takeaways:**

1. **Agent Engine is fully managed** - Google handles infrastructure
2. **Tool wrappers** connect Agent Engine to MCP server
3. **System instructions** define agent personality
4. **ReAct pattern** enables multi-step reasoning
5. **Easy to extend** with new tools
6. **Monitoring and logging** built-in

**Important Files:**
- `agent/deploy_agent_programmatic.py` - Deployment script
- `agent/prompts/system_prompt.txt` - Agent personality
- `agent/chat_with_agent.py` - Interactive testing
- `agent/test_deployed_agent.py` - Automated tests

**Resource Name:**
```
projects/740202511174/locations/us-central1/reasoningEngines/8601228775440515072
```

**Next Steps:**
- Read `docs/UI_DEVELOPMENT.md` for UI integration
- Experiment with different system instructions
- Try adding custom tools
- Monitor agent performance in production
