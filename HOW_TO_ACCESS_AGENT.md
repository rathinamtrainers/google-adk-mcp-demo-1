# How to Access Your AI Agent

Your AI agent is **live and operational**! Here's how to access it:

---

## 🎯 Quick Access Methods

| Method | Difficulty | Best For |
|--------|-----------|----------|
| **Interactive Chat** | ⭐ Easy | Quick testing & demos |
| **Python Script** | ⭐⭐ Medium | Integration & automation |
| **Web Console** | ⭐ Easy | Visual interface & monitoring |
| **REST API** | ⭐⭐⭐ Advanced | Production applications |

---

## 🚀 Method 1: Interactive Chat (Easiest!)

### Start chatting with your agent right now:

```bash
cd /home/agenticai/google-adk-mcp/agent

# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS=/home/agenticai/agentic-ai-batch-2025-bb06223e6daf.json

# Start interactive chat
.venv/bin/python3 chat_with_agent.py
```

**Example conversation:**
```
You: Hi! I'm buying 3 items at $29.99 each. What's the total?
Agent: The total for 3 items at $29.99 each is $89.97.

You: I have a 15% discount code. What's my new total?
Agent: With a 15% discount on $89.97, you save $13.50. Your final price would be $76.47.

You: exit
Agent: Goodbye! Have a great day!
```

---

## 💻 Method 2: Python Code

### A. Quick Test Script

```bash
cd /home/agenticai/google-adk-mcp/agent
export GOOGLE_APPLICATION_CREDENTIALS=/home/agenticai/agentic-ai-batch-2025-bb06223e6daf.json

# Run pre-built tests
.venv/bin/python3 test_deployed_agent.py
```

### B. Write Your Own Script

Create a file called `my_agent_query.py`:

```python
from vertexai.agent_engines import AgentEngine
import vertexai

# Initialize Vertex AI
vertexai.init(
    project="agentic-ai-batch-2025",
    location="us-central1",
    staging_bucket="gs://agentic-ai-batch-2025-staging"
)

# Load your agent
agent = AgentEngine(
    resource_name="projects/740202511174/locations/us-central1/reasoningEngines/8601228775440515072"
)

# Ask questions
questions = [
    "What is 10 plus 5?",
    "Calculate 20% of 150",
    "I'm buying 5 items at $12 each. What's the total?"
]

for question in questions:
    response = agent.query(input=question)
    print(f"Q: {question}")
    print(f"A: {response['output']}\n")
```

Run it:
```bash
python3 my_agent_query.py
```

---

## 🌐 Method 3: Web Console

### Access through Google Cloud Console:

1. **Open this link:**
   ```
   https://console.cloud.google.com/vertex-ai/reasoning-engines?project=agentic-ai-batch-2025
   ```

2. **Find your agent:**
   - Look for Reasoning Engine ID: `8601228775440515072`
   - Name: Based on customer-support-agent

3. **Click on the agent** to view details

4. **Use the Query interface:**
   - Enter your question
   - Click "Query" or press Enter
   - View the response

5. **Try these test queries:**
   - "What is 5 plus 3?"
   - "Calculate 15% of 100"
   - "I'm buying 3 items at $29.99. What's the total?"

**Direct link to Vertex AI:**
https://console.cloud.google.com/vertex-ai?project=agentic-ai-batch-2025

---

## 🔧 Method 4: REST API

### Using cURL:

```bash
# Get access token
TOKEN=$(gcloud auth application-default print-access-token)

# Query the agent
curl -X POST \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/740202511174/locations/us-central1/reasoningEngines/8601228775440515072:query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "What is 7 times 8?"
  }'
```

### Using Python Requests:

```python
import requests
from google.auth import default
from google.auth.transport.requests import Request

# Get credentials
credentials, project = default()
credentials.refresh(Request())

# API endpoint
url = "https://us-central1-aiplatform.googleapis.com/v1/projects/740202511174/locations/us-central1/reasoningEngines/8601228775440515072:query"

# Headers
headers = {
    "Authorization": f"Bearer {credentials.token}",
    "Content-Type": "application/json"
}

# Query
data = {
    "input": "Calculate 25% of 80"
}

# Make request
response = requests.post(url, headers=headers, json=data)
result = response.json()

print(result['output'])
```

### Using Node.js/JavaScript:

```javascript
const { GoogleAuth } = require('google-auth-library');

async function queryAgent(question) {
  const auth = new GoogleAuth({
    scopes: 'https://www.googleapis.com/auth/cloud-platform'
  });

  const client = await auth.getClient();
  const token = await client.getAccessToken();

  const url = 'https://us-central1-aiplatform.googleapis.com/v1/projects/740202511174/locations/us-central1/reasoningEngines/8601228775440515072:query';

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token.token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ input: question })
  });

  const result = await response.json();
  return result.output;
}

// Usage
queryAgent("What is 10 + 5?").then(console.log);
```

---

## 📱 Method 5: Build a Web App

### Simple Flask Web App:

```python
from flask import Flask, request, jsonify
from vertexai.agent_engines import AgentEngine
import vertexai

app = Flask(__name__)

# Initialize agent
vertexai.init(
    project="agentic-ai-batch-2025",
    location="us-central1",
    staging_bucket="gs://agentic-ai-batch-2025-staging"
)

agent = AgentEngine(
    resource_name="projects/740202511174/locations/us-central1/reasoningEngines/8601228775440515072"
)

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    response = agent.query(input=user_message)
    return jsonify({'response': response['output']})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

---

## 🎓 Example Use Cases

### 1. Customer Support Chatbot

```python
# Customer asks about order total
response = agent.query(
    input="A customer wants to buy 3 shirts at $24.99 each. What's the total?"
)
print(response['output'])
# Output: The total for 3 shirts at $24.99 each is $74.97
```

### 2. Discount Calculator

```python
# Customer has a discount code
response = agent.query(
    input="Customer has a $150 order and a 20% discount code. What's the final price?"
)
print(response['output'])
# Output: With a 20% discount on $150, they save $30. Final price is $120.
```

### 3. Bulk Calculations

```python
# Multiple items with different prices
response = agent.query(
    input="Calculate: 2 items at $15.99, 3 items at $9.50, and 1 item at $29.99. What's the total?"
)
print(response['output'])
```

---

## 🔑 Important Information

### Agent Resource Name (save this!):
```
projects/740202511174/locations/us-central1/reasoningEngines/8601228775440515072
```

### Project Details:
- **Project ID**: `agentic-ai-batch-2025`
- **Location**: `us-central1`
- **Model**: Gemini 2.0 Flash
- **Staging Bucket**: `gs://agentic-ai-batch-2025-staging`

### MCP Server:
```
https://mcp-calculator-server-oyhyp5p3ua-uc.a.run.app
```

---

## 📝 Sample Test Queries

Try these questions with your agent:

**Simple Math:**
- "What is 5 plus 3?"
- "Calculate 12 times 8"
- "What's 100 divided by 4?"

**Percentages:**
- "Calculate 15% of 100"
- "What's 25% of 80?"
- "Find 10% of 250"

**Customer Support Scenarios:**
- "I'm buying 3 items at $29.99 each. What's the total?"
- "I have a $120 order with a 15% discount. What's my final price?"
- "Calculate the cost of 5 units at $18.50 each"

**Advanced:**
- "What's the square root of 144?"
- "Calculate 2 to the power of 8"
- "If I buy 4 items at $25.50 and get 20% off, what do I pay?"

---

## 🛠️ Troubleshooting

### Error: "Permission denied"
```bash
# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS=/home/agenticai/agentic-ai-batch-2025-bb06223e6daf.json
```

### Error: "Module not found"
```bash
# Activate virtual environment
cd /home/agenticai/google-adk-mcp/agent
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

### Error: "Agent not found"
Make sure you're using the correct resource name:
```
projects/740202511174/locations/us-central1/reasoningEngines/8601228775440515072
```

---

## 📊 Monitoring Usage

### View Logs:
```bash
# Agent logs
gcloud logging read \
  "resource.type=aiplatform.googleapis.com/ReasoningEngine" \
  --limit=50 \
  --project=agentic-ai-batch-2025
```

### Check Costs:
```
https://console.cloud.google.com/billing?project=agentic-ai-batch-2025
```

### Monitor in Console:
```
https://console.cloud.google.com/vertex-ai/reasoning-engines?project=agentic-ai-batch-2025
```

---

## 🎯 Quick Command Reference

```bash
# Interactive chat
cd /home/agenticai/google-adk-mcp/agent
export GOOGLE_APPLICATION_CREDENTIALS=/home/agenticai/agentic-ai-batch-2025-bb06223e6daf.json
.venv/bin/python3 chat_with_agent.py

# Run tests
.venv/bin/python3 test_deployed_agent.py

# Single query
.venv/bin/python3 -c "
from vertexai.agent_engines import AgentEngine
import vertexai
vertexai.init(project='agentic-ai-batch-2025', location='us-central1', staging_bucket='gs://agentic-ai-batch-2025-staging')
agent = AgentEngine(resource_name='projects/740202511174/locations/us-central1/reasoningEngines/8601228775440515072')
print(agent.query(input='What is 10 + 5?')['output'])
"
```

---

## ✅ Summary

**Easiest Method:** Use `chat_with_agent.py` for interactive conversations

**Best for Development:** Use Python scripts with the SDK

**Best for Production:** Use REST API with proper authentication

**Best for Monitoring:** Use Vertex AI Console

Your agent is ready to use **right now**! Start with the interactive chat and explore from there.

---

**Need help? Check these docs:**
- Full deployment guide: `AGENT_DEPLOYED.md`
- Project overview: `README.md`
- Quick reference: `QUICK_REFERENCE.md`
