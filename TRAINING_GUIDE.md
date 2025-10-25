# Complete Training Guide - AI Agent with MCP Server

**Comprehensive Documentation for Learning and Training**

Version: 1.0
Last Updated: October 2025
Difficulty Level: Intermediate to Advanced

---

## Table of Contents

1. [Introduction & Overview](#1-introduction--overview)
2. [Prerequisites Knowledge](#2-prerequisites-knowledge)
3. [Project Architecture](#3-project-architecture)
4. [Component Deep Dive](#4-component-deep-dive)
5. [Code Walkthroughs](#5-code-walkthroughs)
6. [Deployment Process](#6-deployment-process)
7. [Testing & Validation](#7-testing--validation)
8. [Common Patterns & Best Practices](#8-common-patterns--best-practices)
9. [Troubleshooting Guide](#9-troubleshooting-guide)
10. [Hands-On Exercises](#10-hands-on-exercises)

---

## 1. Introduction & Overview

### 1.1 What This Project Does

This project demonstrates a complete **AI agent system** that can perform calculations through natural conversation. It consists of three main parts:

1. **MCP Server** - A calculator service with 7 mathematical tools
2. **AI Agent** - An intelligent agent powered by Gemini 2.0 Flash
3. **Web UI** - A user-friendly interface built with Streamlit

**Real-world example:**
```
User: "I'm buying 3 items at $29.99 each. What's my total?"
Agent: [Uses multiply tool: 3 × 29.99]
Agent: "The total for 3 items at $29.99 each is $89.97."
```

### 1.2 Why This Architecture?

**Key Design Decisions:**

1. **Separation of Concerns**
   - MCP Server: Pure business logic (calculations)
   - AI Agent: Decision-making and natural language
   - UI: User interaction

2. **Cloud-Native Deployment**
   - Scalable: Handles 1 or 1000 users
   - Cost-effective: Pay only for what you use
   - Managed: Google handles infrastructure

3. **Model Context Protocol (MCP)**
   - Standard way for AI to use tools
   - Reusable across different AI systems
   - Easy to extend with new tools

### 1.3 Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **AI Model** | Gemini 2.0 Flash | Natural language understanding |
| **Agent Framework** | Google ADK | Agent orchestration |
| **Tool Protocol** | MCP (Model Context Protocol) | Tool communication |
| **MCP Server** | Python + FastAPI | HTTP/SSE tool server |
| **Container** | Docker | Packaging |
| **Compute** | Cloud Run | Serverless hosting |
| **Agent Hosting** | Vertex AI Agent Engine | Managed agent runtime |
| **IaC** | Terraform | Infrastructure as code |
| **UI** | Streamlit | Web interface |

### 1.4 Learning Path

**Recommended order for understanding this project:**

```
Week 1: Understand MCP Server
├── What is MCP?
├── How tools are defined
├── HTTP/SSE transport layer
└── Testing tools locally

Week 2: Understand AI Agent
├── How Vertex AI Agent Engine works
├── Tool calling mechanism
├── Agent reasoning process
└── Deployment process

Week 3: Understand Infrastructure
├── Terraform basics
├── Cloud Run deployment
├── Artifact Registry
└── IAM and permissions

Week 4: Understand UI & Integration
├── Streamlit basics
├── Vertex AI SDK usage
├── Session management
└── End-to-end testing
```

---

## 2. Prerequisites Knowledge

### 2.1 Required Knowledge

**Essential (Must Know):**
- Python programming (functions, classes, async/await)
- HTTP basics (GET, POST, JSON)
- Command line / terminal usage
- Git basics

**Recommended (Should Know):**
- RESTful API concepts
- Docker basics
- Cloud computing concepts
- Web development basics

**Nice to Have:**
- Terraform
- Google Cloud Platform
- AI/ML concepts
- FastAPI framework

### 2.2 Concepts You'll Learn

By the end of this training, you'll understand:
- Model Context Protocol (MCP)
- Tool calling for AI agents
- Vertex AI Agent Engine
- Cloud Run deployment
- Infrastructure as Code with Terraform
- AI agent orchestration
- Streaming Server-Sent Events (SSE)

### 2.3 Tools You'll Need

**Required Software:**
```bash
- Python 3.10+
- Git
- Docker
- gcloud CLI
- Terraform
- A code editor (VS Code recommended)
```

**Optional but Helpful:**
```bash
- Postman (API testing)
- Docker Desktop
- Terraform extension for VS Code
```

---

## 3. Project Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        USER                                  │
│                          │                                   │
│                          ▼                                   │
│              ┌──────────────────────┐                       │
│              │   Streamlit UI       │                       │
│              │   (localhost:8501)   │                       │
│              └──────────┬───────────┘                       │
│                         │                                    │
└─────────────────────────┼────────────────────────────────────┘
                          │
                          │ HTTPS/API
                          │
┌─────────────────────────▼────────────────────────────────────┐
│              Google Cloud (us-central1)                       │
│                                                               │
│  ┌─────────────────────────────────────────────────┐        │
│  │         Vertex AI Agent Engine                  │        │
│  │  ┌────────────────────────────────────────┐    │        │
│  │  │  Gemini 2.0 Flash Model                │    │        │
│  │  │  - Understands natural language         │    │        │
│  │  │  - Decides which tools to use           │    │        │
│  │  │  - Generates responses                  │    │        │
│  │  └────────────────────────────────────────┘    │        │
│  │                                                  │        │
│  │  ┌────────────────────────────────────────┐    │        │
│  │  │  Agent Logic (Python ADK)              │    │        │
│  │  │  - Tool definitions                     │    │        │
│  │  │  - System instructions                  │    │        │
│  │  │  - Tool calling implementation          │    │        │
│  │  └──────────────┬─────────────────────────┘    │        │
│  └─────────────────┼──────────────────────────────┘        │
│                    │                                         │
│                    │ HTTP POST                               │
│                    │                                         │
│  ┌─────────────────▼──────────────────────────────┐        │
│  │         Cloud Run Service                      │        │
│  │  ┌────────────────────────────────────────┐   │        │
│  │  │  MCP Server (FastAPI)                  │   │        │
│  │  │  - Receives tool call requests         │   │        │
│  │  │  - Routes to calculator functions      │   │        │
│  │  │  - Returns results                      │   │        │
│  │  └────────────────────────────────────────┘   │        │
│  │                                                 │        │
│  │  ┌────────────────────────────────────────┐   │        │
│  │  │  Calculator Tools                      │   │        │
│  │  │  - add(a, b)                           │   │        │
│  │  │  - subtract(a, b)                      │   │        │
│  │  │  - multiply(a, b)                      │   │        │
│  │  │  - divide(a, b)                        │   │        │
│  │  │  - percentage(num, percent)            │   │        │
│  │  │  - sqrt(number)                        │   │        │
│  │  │  - power(base, exponent)               │   │        │
│  │  └────────────────────────────────────────┘   │        │
│  └─────────────────────────────────────────────── ┘        │
│                                                               │
│  ┌──────────────────────────────────────────────┐          │
│  │     Cloud Storage Bucket                      │          │
│  │     gs://agentic-ai-batch-2025-staging        │          │
│  │     - Agent artifacts                         │          │
│  │     - Dependencies                            │          │
│  └──────────────────────────────────────────────┘          │
└───────────────────────────────────────────────────────────── ┘
```

### 3.2 Request Flow Diagram

```
User Input: "What is 10 + 5?"
     │
     │ [1] User types in Streamlit UI
     ▼
┌──────────────────────┐
│  Streamlit UI        │
│  app.py line 208     │
│  agent.query(input=) │
└──────┬───────────────┘
       │
       │ [2] HTTPS POST to Vertex AI API
       │     {input: "What is 10 + 5?"}
       ▼
┌──────────────────────────────┐
│  Vertex AI Agent Engine      │
│  Receives query              │
└──────┬───────────────────────┘
       │
       │ [3] Gemini model processes input
       │     Identifies: need to use "add" tool
       ▼
┌──────────────────────────────┐
│  Agent Tool Calling Logic    │
│  Prepares tool call:         │
│  {tool: "add", args: {a:10, b:5}}
└──────┬───────────────────────┘
       │
       │ [4] HTTP POST to MCP Server
       │     POST /tools/add
       │     {arguments: {a: 10, b: 5}}
       ▼
┌──────────────────────────────┐
│  Cloud Run MCP Server        │
│  http_server.py line 89      │
│  Receives tool call          │
└──────┬───────────────────────┘
       │
       │ [5] Routes to calculator
       ▼
┌──────────────────────────────┐
│  Calculator Function         │
│  calculator_server.py        │
│  result = 10 + 5 = 15        │
└──────┬───────────────────────┘
       │
       │ [6] Returns result
       │     {result: [{text: "Result: 10 + 5 = 15"}]}
       ▼
┌──────────────────────────────┐
│  Vertex AI Agent Engine      │
│  Receives tool result        │
└──────┬───────────────────────┘
       │
       │ [7] Gemini generates natural response
       │     "10 plus 5 equals 15."
       ▼
┌──────────────────────────────┐
│  Streamlit UI                │
│  Displays response to user   │
└──────────────────────────────┘
```

### 3.3 Directory Structure Explained

```
google-adk-mcp/
│
├── mcp-server/                    # MCP Calculator Server
│   ├── src/
│   │   ├── calculator_server.py   # Tool definitions (MCP protocol)
│   │   └── http_server.py         # HTTP/SSE wrapper (FastAPI)
│   ├── Dockerfile                 # Container image definition
│   ├── requirements.txt           # Python dependencies
│   └── README.md                  # MCP server documentation
│
├── terraform/                     # Infrastructure as Code
│   ├── main.tf                    # All GCP resources
│   ├── variables.tf               # Configurable parameters
│   ├── outputs.tf                 # Export values
│   └── terraform.tfvars           # Actual values (not in git)
│
├── agent/                         # AI Agent Files
│   ├── deploy_agent_programmatic.py  # Deployment script
│   ├── chat_with_agent.py         # Interactive chat CLI
│   ├── test_deployed_agent.py     # Automated tests
│   ├── run_agent.sh               # Menu launcher
│   ├── agent_config.yaml          # Agent configuration
│   └── prompts/
│       └── system_prompt.txt      # Agent personality
│
├── ui/                            # Streamlit Web Interface
│   ├── app.py                     # Main Streamlit app
│   ├── config.py                  # Configuration
│   ├── utils.py                   # Helper functions
│   ├── styles.css                 # Custom styling
│   ├── requirements.txt           # UI dependencies
│   ├── run.sh                     # Launch script
│   └── README.md                  # UI documentation
│
├── scripts/                       # Automation Scripts
│   ├── deploy.sh                  # Full deployment
│   └── test-mcp-server.sh         # MCP testing
│
├── docs/                          # Training Documentation
│   └── [detailed guides]
│
└── Documentation Files
    ├── README.md                  # Project overview
    ├── SETUP.md                   # Setup instructions
    ├── TESTING_GUIDE.md           # Testing guide
    ├── TRAINING_GUIDE.md          # This file
    └── [other guides]
```

### 3.4 Data Flow

**Query Processing Steps:**

1. **Input Reception**
   - User types message in UI
   - UI validates and packages input
   - Sends to Vertex AI via SDK

2. **Agent Processing**
   - Agent receives query
   - Gemini model analyzes intent
   - Determines if tools needed
   - Plans which tools to call

3. **Tool Execution**
   - Agent calls MCP server endpoint
   - MCP server executes calculation
   - Returns structured result
   - Agent receives tool output

4. **Response Generation**
   - Agent synthesizes information
   - Gemini generates natural language
   - Response sent back to UI
   - UI displays to user

5. **State Management**
   - UI stores message in session
   - Adds to conversation history
   - Updates statistics
   - Ready for next query

---

## 4. Component Deep Dive

### 4.1 MCP Server

**Purpose:** Provides calculator tools via HTTP/SSE protocol

**Key Files:**
- `mcp-server/src/calculator_server.py` - Tool implementations
- `mcp-server/src/http_server.py` - FastAPI HTTP wrapper

**Detailed Documentation:** See `docs/MCP_SERVER_EXPLAINED.md`

### 4.2 AI Agent

**Purpose:** Orchestrates tool calls and generates intelligent responses

**Key Files:**
- `agent/deploy_agent_programmatic.py` - Agent deployment
- `agent/agent_config.yaml` - Configuration
- `agent/prompts/system_prompt.txt` - Personality

**Detailed Documentation:** See `docs/AGENT_ENGINE_EXPLAINED.md`

### 4.3 Infrastructure

**Purpose:** Provisions all cloud resources

**Key Files:**
- `terraform/main.tf` - Resource definitions
- `terraform/variables.tf` - Parameters
- `terraform/outputs.tf` - Export values

**Detailed Documentation:** See `docs/DEPLOYMENT_EXPLAINED.md`

### 4.4 User Interface

**Purpose:** Provides web-based chat interface

**Key Files:**
- `ui/app.py` - Main Streamlit application
- `ui/config.py` - Settings
- `ui/utils.py` - Helpers

**Detailed Documentation:** See `docs/UI_DEVELOPMENT.md`

---

## 5. Code Walkthroughs

**Detailed code explanations are in:**
- `docs/CODE_WALKTHROUGH.md` - Line-by-line code analysis

**What's covered:**
- MCP tool definition pattern
- FastAPI endpoint handlers
- Agent deployment code
- Streamlit session state management
- Terraform resource blocks

---

## 6. Deployment Process

**Step-by-step deployment guide:**
See `docs/DEPLOYMENT_EXPLAINED.md`

**Topics covered:**
- Setting up GCP project
- Authenticating with service account
- Running Terraform
- Building Docker images
- Deploying to Cloud Run
- Deploying agent to Vertex AI
- Testing deployed services

---

## 7. Testing & Validation

**Testing strategy:**
1. Unit testing individual components
2. Integration testing MCP + Agent
3. End-to-end testing via UI
4. Load testing for scale

**Test files:**
- `agent/test_deployed_agent.py`
- `scripts/test-mcp-server.sh`

**Detailed guide:** See `TESTING_GUIDE.md`

---

## 8. Common Patterns & Best Practices

### 8.1 MCP Tool Definition Pattern

```python
# Pattern: Define tool schema
Tool(
    name="function_name",           # Snake case
    description="What it does",     # Clear description
    inputSchema={                   # JSON Schema
        "type": "object",
        "properties": {
            "param": {"type": "type", "description": "..."}
        },
        "required": ["param"]
    }
)

# Pattern: Implement tool handler
@app.call_tool()
async def call_tool(name: str, arguments: Any):
    if name == "function_name":
        result = do_calculation(arguments["param"])
        return [TextContent(type="text", text=f"Result: {result}")]
```

### 8.2 Error Handling Pattern

```python
try:
    # Main logic
    result = operation()
except SpecificError as e:
    # Handle specific error
    return error_response(str(e))
except Exception as e:
    # Catch all fallback
    log_error(e)
    return generic_error_response()
```

### 8.3 Configuration Management

```python
# Use environment variables for secrets
CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# Use config files for constants
from config import PROJECT_ID, LOCATION

# Never hardcode credentials in code
```

---

## 9. Troubleshooting Guide

### Common Issues and Solutions

**Issue: "Module not found"**
- Solution: Activate virtual environment, reinstall dependencies

**Issue: "Permission denied"**
- Solution: Set GOOGLE_APPLICATION_CREDENTIALS

**Issue: "Agent not responding"**
- Solution: Check MCP server health endpoint

**Complete guide:** See `TROUBLESHOOTING.md`

---

## 10. Hands-On Exercises

### Exercise 1: Add a New Calculator Tool
**Difficulty:** Beginner
**Time:** 30 minutes

Task: Add a `modulo(a, b)` tool to the MCP server

Steps:
1. Edit `mcp-server/src/calculator_server.py`
2. Add tool definition
3. Add tool handler
4. Rebuild Docker image
5. Redeploy to Cloud Run
6. Test with agent

### Exercise 2: Customize Agent Personality
**Difficulty:** Beginner
**Time:** 15 minutes

Task: Make the agent more formal/casual

Steps:
1. Edit `agent/prompts/system_prompt.txt`
2. Redeploy agent
3. Test conversation tone

### Exercise 3: Add Export Feature to UI
**Difficulty:** Intermediate
**Time:** 1 hour

Task: Add PDF export for chat history

Steps:
1. Add PDF library to `ui/requirements.txt`
2. Create export function in `ui/utils.py`
3. Add button in `ui/app.py`
4. Test export functionality

### Exercise 4: Implement Rate Limiting
**Difficulty:** Advanced
**Time:** 2 hours

Task: Add rate limiting to MCP server

Steps:
1. Add rate limiting middleware to FastAPI
2. Track requests per IP
3. Return 429 when limit exceeded
4. Test with load testing tool

---

## Additional Resources

### Documentation Files
- `README.md` - Project overview
- `SETUP.md` - Initial setup
- `TESTING_GUIDE.md` - Testing procedures
- `HOW_TO_ACCESS_AGENT.md` - Access methods
- `QUICK_REFERENCE.md` - Command reference

### Detailed Technical Docs (in docs/ folder)
- `ARCHITECTURE_DEEP_DIVE.md` - Architecture details
- `MCP_SERVER_EXPLAINED.md` - MCP server internals
- `AGENT_ENGINE_EXPLAINED.md` - Agent Engine details
- `UI_DEVELOPMENT.md` - UI development guide
- `DEPLOYMENT_EXPLAINED.md` - Deployment process
- `CODE_WALKTHROUGH.md` - Code analysis

### External Resources
- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [Google Agent Development Kit Docs](https://cloud.google.com/vertex-ai/docs)
- [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/docs/generative-ai/agent-engine)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Terraform GCP Provider](https://registry.terraform.io/providers/hashicorp/google)
- [Streamlit Documentation](https://docs.streamlit.io)

---

## Training Completion Checklist

After completing this training, you should be able to:

- [ ] Explain what MCP is and why it's used
- [ ] Describe the architecture of the entire system
- [ ] Identify where each component runs (local vs cloud)
- [ ] Read and understand the MCP server code
- [ ] Read and understand the agent deployment code
- [ ] Read and understand the Streamlit UI code
- [ ] Read and understand the Terraform configuration
- [ ] Deploy the entire system from scratch
- [ ] Add a new tool to the MCP server
- [ ] Modify the agent's behavior
- [ ] Customize the UI
- [ ] Debug common issues
- [ ] Test all components
- [ ] Explain the request flow
- [ ] Understand cost implications

---

## Next Steps

1. **Read the detailed documentation** in the `docs/` folder
2. **Complete the hands-on exercises** to reinforce learning
3. **Experiment with modifications** to deepen understanding
4. **Build your own tools** extending this architecture
5. **Share knowledge** by training others

---

**Questions or Issues?**

If you encounter problems during training:
1. Check the troubleshooting section
2. Review relevant detailed documentation
3. Examine the code with line numbers provided
4. Test components individually
5. Document your findings for others

---

**Happy Learning!**

This project demonstrates modern AI agent architecture using industry-standard tools and best practices. Mastering this will prepare you for building production AI systems.
