# AI Agent Deployment Guide

Complete guide for deploying the Customer Support Agent to Vertex AI Agent Engine.

## 📊 Deployment Options Comparison

| Method | Complexity | Automation | Best For | Time Required |
|--------|------------|------------|----------|---------------|
| **🥇 Python ADK (Recommended)** | Medium | ✅ Full | Production, CI/CD | 10-15 min |
| **🥈 Vertex AI Console** | Low | ❌ Manual | Quick testing | 5-10 min |
| **🥉 gcloud CLI** | Medium | ⚠️ Partial | Scripts | Not yet available |
| **Terraform** | High | ✅ Full | IaC workflows | Not yet supported |

---

## 🥇 **Option 1: Python ADK Deployment (RECOMMENDED)**

### Why Choose This?
- ✅ Fully automated and reproducible
- ✅ Integrates with CI/CD pipelines
- ✅ Version-controllable
- ✅ Official Google support
- ✅ Can test locally before deployment

### Prerequisites

1. **Install Python packages:**
   ```bash
   pip install google-cloud-aiplatform[agent_engines,langchain]>=1.112 requests
   ```

2. **Verify IAM permissions:**
   ```bash
   # Your service account needs:
   # - roles/aiplatform.user
   # - roles/storage.admin (for Cloud Storage)
   ```

3. **Enable required APIs:**
   ```bash
   gcloud services enable aiplatform.googleapis.com storage.googleapis.com \
     --project=agentic-ai-batch-2025
   ```

### Deployment Steps

#### Quick Deploy

```bash
cd /home/agenticai/google-adk-mcp/agent

# Install dependencies
pip install google-cloud-aiplatform[agent_engines,langchain]>=1.112 requests

# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS=/home/agenticai/agentic-ai-batch-2025-bb06223e6daf.json

# Deploy the agent
python3 deploy_agent_programmatic.py
```

#### Test Locally First (Recommended)

```bash
# Test agent locally before deploying
python3 deploy_agent_programmatic.py --test-local
```

#### Deploy to Vertex AI

```bash
# Deploy to production
python3 deploy_agent_programmatic.py
```

### What It Does

1. ✅ Initializes Vertex AI client
2. ✅ Tests MCP server connectivity
3. ✅ Creates agent with 7 calculator tools
4. ✅ Deploys to Vertex AI Agent Engine
5. ✅ Runs a test query
6. ✅ Returns the agent resource name

### Expected Output

```
======================================================================
Deploying Customer Support Agent to Vertex AI Agent Engine
======================================================================

Project: agentic-ai-batch-2025
Location: us-central1
MCP Server: https://mcp-calculator-server-oyhyp5p3ua-uc.a.run.app
Agent Name: customer-support-agent

1. Initializing Vertex AI client...
2. Testing MCP server connectivity...
   ✅ MCP server is healthy: {'status': 'healthy'}
3. Creating agent with calculator tools...
   Tools: add, subtract, multiply, divide, percentage, sqrt, power
   ✅ Agent created locally

4. Deploying to Vertex AI Agent Engine...
   This may take a few minutes...

   ✅ Agent deployed successfully!

   Resource Name: projects/740202511174/locations/us-central1/reasoningEngines/1234567890

5. Testing deployed agent...
   Query: Hi! I'm buying 3 items at $29.99 each. What's the total?
   Response: The total for 3 items at $29.99 each is $89.97

======================================================================
DEPLOYMENT COMPLETE!
======================================================================

Agent Resource Name:
  projects/740202511174/locations/us-central1/reasoningEngines/1234567890

You can now interact with the agent in:
  - Vertex AI Console
  - Via API using the resource name
  - Programmatically with remote_agent.query()
```

### How to Use the Deployed Agent

#### Via Python

```python
from vertexai import agent_engines
import vertexai

vertexai.init(project="agentic-ai-batch-2025", location="us-central1")

# Load the deployed agent
remote_agent = agent_engines.LangchainAgent.get(
    resource_name="projects/740202511174/locations/us-central1/reasoningEngines/YOUR_ID"
)

# Query the agent
response = remote_agent.query(
    input="I have a 15% discount on a $120 order. What's my final price?"
)
print(response)
```

#### Via Vertex AI Console

Navigate to:
```
https://console.cloud.google.com/vertex-ai/reasoning-engines?project=agentic-ai-batch-2025
```

Find your deployed agent and interact with it.

### Troubleshooting

**Error: ImportError: No module named 'vertexai'**
```bash
pip install --upgrade google-cloud-aiplatform[agent_engines,langchain]>=1.112
```

**Error: Permission denied**
```bash
# Grant required roles
gcloud projects add-iam-policy-binding agentic-ai-batch-2025 \
  --member="serviceAccount:customer-support-agent-sa@agentic-ai-batch-2025.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

**Error: MCP server not responding**
```bash
# Test MCP server
curl https://mcp-calculator-server-oyhyp5p3ua-uc.a.run.app/health
```

---

## 🥈 **Option 2: Vertex AI Console (Manual)**

### When to Use
- Quick testing
- First-time exploration
- Non-technical users

### Steps

1. **Navigate to Vertex AI**
   ```
   https://console.cloud.google.com/vertex-ai/agent-builder?project=agentic-ai-batch-2025
   ```

2. **Create New Agent**
   - Click "Create Agent" or "New Agent"
   - Name: `customer-support-agent`
   - Display Name: `Customer Support Agent`

3. **Configure Model**
   - Model: Gemini 2.0 Flash
   - Temperature: 0.7
   - Top P: 0.95
   - Max tokens: 2048

4. **Add System Instructions**
   Copy from: `/home/agenticai/google-adk-mcp/agent/prompts/system_prompt.txt`

5. **Configure Tools/Functions**

   For each calculator tool, add a function definition:

   **Example for "add" tool:**
   ```json
   {
     "name": "add",
     "description": "Add two numbers together",
     "parameters": {
       "type": "object",
       "properties": {
         "a": {"type": "number", "description": "First number"},
         "b": {"type": "number", "description": "Second number"}
       },
       "required": ["a", "b"]
     }
   }
   ```

   Configure endpoint:
   - URL: `https://mcp-calculator-server-oyhyp5p3ua-uc.a.run.app/tools/add`
   - Method: POST
   - Body: `{"arguments": {"a": ${a}, "b": ${b}}}`

   Repeat for all 7 tools: add, subtract, multiply, divide, power, sqrt, percentage

6. **Set Service Account**
   ```
   customer-support-agent-sa@agentic-ai-batch-2025.iam.gserviceaccount.com
   ```

7. **Deploy & Test**
   - Click "Deploy"
   - Test in the built-in chat interface

### Pros & Cons

✅ **Pros:**
- Visual interface
- No coding required
- Quick to test

❌ **Cons:**
- Manual process (not automated)
- Hard to version control
- Not reproducible
- Time-consuming for updates

---

## 🥉 **Option 3: gcloud CLI**

### Status
⚠️ **Not yet available** - Vertex AI Agent Engine doesn't have full gcloud CLI support yet.

### Future Syntax (When Available)
```bash
# Expected future syntax
gcloud ai agent-engines create \
  --project=agentic-ai-batch-2025 \
  --location=us-central1 \
  --display-name="Customer Support Agent" \
  --config=agent_config.yaml
```

---

## 🎯 **Recommended Workflow**

### For Development & Testing
1. Test locally with `deploy_agent_programmatic.py --test-local`
2. Deploy to Vertex AI with `deploy_agent_programmatic.py`
3. Test in Vertex AI Console

### For Production
1. Use Python ADK deployment script
2. Integrate into CI/CD pipeline
3. Version control your agent configuration
4. Set up monitoring and logging

---

## 📋 **Post-Deployment Checklist**

After deploying your agent:

- [ ] Test with sample queries
- [ ] Verify all calculator tools work
- [ ] Check response quality
- [ ] Set up monitoring
- [ ] Configure logging
- [ ] Set up alerts for errors
- [ ] Document the resource name
- [ ] Update team documentation

---

## 🧪 **Test Queries**

Use these to verify your deployed agent:

1. **Simple calculation:**
   ```
   "What is 5 plus 3?"
   Expected: Uses add tool, returns 8
   ```

2. **Price calculation:**
   ```
   "I'm buying 3 items at $29.99 each. What's the total?"
   Expected: Uses multiply tool, returns $89.97
   ```

3. **Discount calculation:**
   ```
   "I have a 15% discount code on a $120 order. What's my final price?"
   Expected: Uses percentage and subtract tools, returns $102
   ```

4. **Complex calculation:**
   ```
   "What's the square root of 144?"
   Expected: Uses sqrt tool, returns 12
   ```

---

## 💰 **Cost Considerations**

| Component | Cost | Notes |
|-----------|------|-------|
| Agent Engine | Based on queries | ~$0.001-0.01 per query |
| Model (Gemini) | Token-based | ~$0.075 per 1M input tokens |
| MCP Server | Minimal | Already covered by Cloud Run |
| Storage | Minimal | Agent artifacts storage |

**Estimated Monthly Cost:**
- Low usage (100 queries/day): $3-10
- Medium usage (1000 queries/day): $30-100
- High usage (10000 queries/day): $300-1000

---

## 🔗 **Useful Links**

- **Vertex AI Console:** https://console.cloud.google.com/vertex-ai?project=agentic-ai-batch-2025
- **Agent Engine Docs:** https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine
- **ADK Documentation:** https://google.github.io/adk-docs/
- **MCP Server:** https://mcp-calculator-server-oyhyp5p3ua-uc.a.run.app

---

## 🎉 **Summary**

**Best Choice:** Use `deploy_agent_programmatic.py` for automated, reproducible deployments.

**Quick Start:**
```bash
cd /home/agenticai/google-adk-mcp/agent
pip install google-cloud-aiplatform[agent_engines,langchain]>=1.112 requests
export GOOGLE_APPLICATION_CREDENTIALS=/home/agenticai/agentic-ai-batch-2025-bb06223e6daf.json
python3 deploy_agent_programmatic.py
```

That's it! Your agent will be deployed and ready to use.
