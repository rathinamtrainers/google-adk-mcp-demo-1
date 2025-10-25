# 🧪 AI Agent Testing Guide

Complete guide to running and testing your deployed AI agent.

---

## ⚡ Quick Start (30 seconds)

```bash
cd /home/agenticai/google-adk-mcp/agent
./run_agent.sh
```

**Choose an option:**
1. Interactive Chat (talk to the agent)
2. Run Automated Tests (5 test queries)
3. Single Query (ask one question)

---

## 🎯 Testing Methods

### Method 1: Easy Menu Script ⭐ (Recommended)

```bash
cd /home/agenticai/google-adk-mcp/agent
./run_agent.sh
```

This gives you a menu with 3 options to test your agent.

---

### Method 2: Interactive Chat 💬

**Best for:** Playing around and testing different questions

```bash
cd /home/agenticai/google-adk-mcp/agent
export GOOGLE_APPLICATION_CREDENTIALS=/home/agenticai/agentic-ai-batch-2025-bb06223e6daf.json
.venv/bin/python3 chat_with_agent.py
```

**Example conversation:**
```
You: Hi! What is 10 plus 5?
Agent: 10 plus 5 is 15.

You: Calculate 20% of 250
Agent: 20% of 250 is 50.

You: I'm buying 3 shirts at $24.99 each. What's the total?
Agent: The total for 3 shirts at $24.99 each is $74.97.

You: exit
Agent: Goodbye! Have a great day!
```

---

### Method 3: Automated Test Suite 🤖

**Best for:** Verifying all features work correctly

```bash
cd /home/agenticai/google-adk-mcp/agent
export GOOGLE_APPLICATION_CREDENTIALS=/home/agenticai/agentic-ai-batch-2025-bb06223e6daf.json
.venv/bin/python3 test_deployed_agent.py
```

**What it tests:**
- ✅ Simple addition
- ✅ Percentage calculations
- ✅ Discount calculations
- ✅ Square root
- ✅ Price calculations

---

### Method 4: Single Command Query

**Best for:** Quick one-off questions

```bash
cd /home/agenticai/google-adk-mcp/agent
export GOOGLE_APPLICATION_CREDENTIALS=/home/agenticai/agentic-ai-batch-2025-bb06223e6daf.json

.venv/bin/python3 -c "
from vertexai.agent_engines import AgentEngine
import vertexai

vertexai.init(
    project='agentic-ai-batch-2025',
    location='us-central1',
    staging_bucket='gs://agentic-ai-batch-2025-staging'
)

agent = AgentEngine(
    resource_name='projects/740202511174/locations/us-central1/reasoningEngines/8601228775440515072'
)

response = agent.query(input='What is 7 times 8?')
print(response['output'])
"
```

---

### Method 5: Custom Python Script

Create a file `my_test.py`:

```python
from vertexai.agent_engines import AgentEngine
import vertexai

# Initialize
vertexai.init(
    project="agentic-ai-batch-2025",
    location="us-central1",
    staging_bucket="gs://agentic-ai-batch-2025-staging"
)

# Load agent
agent = AgentEngine(
    resource_name="projects/740202511174/locations/us-central1/reasoningEngines/8601228775440515072"
)

# Your custom tests
my_questions = [
    "What is 100 divided by 5?",
    "Calculate 30% of 90",
    "I want to buy 6 items at $15.50 each. Total?"
]

for q in my_questions:
    response = agent.query(input=q)
    print(f"Q: {q}")
    print(f"A: {response['output']}\n")
```

Run it:
```bash
python3 my_test.py
```

---

## 📋 Sample Test Queries

### Basic Math
```
- "What is 5 plus 3?"
- "Calculate 12 times 7"
- "What's 100 divided by 4?"
- "Subtract 15 from 50"
```

### Percentages
```
- "Calculate 15% of 100"
- "What's 25% of 80?"
- "Find 10% of 250"
- "Calculate 5% of 1000"
```

### Customer Support Scenarios
```
- "I'm buying 3 items at $29.99 each. What's the total?"
- "I have a $120 order with a 15% discount. What's my final price?"
- "Calculate the cost of 5 units at $18.50 each"
- "If I order 10 products at $12.99, how much is that?"
```

### Advanced Calculations
```
- "What's the square root of 144?"
- "Calculate 2 to the power of 8"
- "What's the square root of 225?"
- "Calculate 5 raised to the power of 3"
```

### Complex Scenarios
```
- "I'm buying 4 items at $25.50 and get 20% off. What do I pay?"
- "Calculate: 3 items at $15, 2 items at $20, and apply 10% discount"
- "Order of $200 with 25% discount, then 8% tax. Final total?"
```

---

## 🎭 Test Scenarios by Use Case

### E-commerce Customer Support

**Scenario 1: Simple Purchase**
```
You: "Hi! I want to buy 3 t-shirts at $19.99 each."
Agent: "The total for 3 t-shirts at $19.99 each is $59.97."
```

**Scenario 2: Discount Applied**
```
You: "I have a cart worth $150 and a 20% discount code. What will I pay?"
Agent: "With a 20% discount on $150, you save $30. Your final price is $120."
```

**Scenario 3: Bulk Order**
```
You: "We need 25 units at $8.50 per unit for our office."
Agent: "The total cost for 25 units at $8.50 each is $212.50."
```

### Financial Calculations

**Scenario 1: Tip Calculator**
```
You: "My bill is $85. What's a 18% tip?"
Agent: "18% of $85 is $15.30."
```

**Scenario 2: Savings**
```
You: "If I save $50 per week for 12 weeks, how much will I have?"
Agent: "Saving $50 per week for 12 weeks gives you $600."
```

### Educational Math Help

**Scenario 1: Homework Help**
```
You: "Can you help me? What's the square root of 169?"
Agent: "The square root of 169 is 13."
```

**Scenario 2: Word Problem**
```
You: "If a train travels at 60 mph for 3.5 hours, how far does it go?"
Agent: [Uses multiply] "At 60 mph for 3.5 hours, the train travels 210 miles."
```

---

## ✅ Expected Test Results

When you run tests, you should see:

### Test 1: Addition ✅
```
Query: What is 5 plus 3?
Expected: 5 plus 3 is 8.
Tool Used: add
```

### Test 2: Percentage ✅
```
Query: Calculate 15% of 100
Expected: 15% of 100 is 15.
Tool Used: percentage
```

### Test 3: Discount Calculation ✅
```
Query: $120 order with 15% discount. Final price?
Expected: Final price is $102.
Tools Used: percentage, subtract
```

### Test 4: Square Root ✅
```
Query: What's the square root of 64?
Expected: The square root of 64 is 8.
Tool Used: sqrt
```

### Test 5: Multiplication ✅
```
Query: 4 items at $25.50 each?
Expected: Total is $102.00.
Tool Used: multiply
```

---

## 🔍 Verifying Tools Are Working

To verify each calculator tool works:

### 1. Add Tool
```bash
Query: "What is 10 + 5?"
Expected: Uses add tool, returns 15
```

### 2. Subtract Tool
```bash
Query: "Subtract 8 from 20"
Expected: Uses subtract tool, returns 12
```

### 3. Multiply Tool
```bash
Query: "Calculate 7 times 9"
Expected: Uses multiply tool, returns 63
```

### 4. Divide Tool
```bash
Query: "Divide 100 by 5"
Expected: Uses divide tool, returns 20
```

### 5. Percentage Tool
```bash
Query: "Calculate 25% of 80"
Expected: Uses percentage tool, returns 20
```

### 6. Square Root Tool
```bash
Query: "What's the square root of 225?"
Expected: Uses sqrt tool, returns 15
```

### 7. Power Tool
```bash
Query: "Calculate 3 to the power of 4"
Expected: Uses power tool, returns 81
```

---

## 🐛 Troubleshooting

### Issue: "Module not found" error

**Solution:**
```bash
cd /home/agenticai/google-adk-mcp/agent
source .venv/bin/activate
```

### Issue: "Permission denied" error

**Solution:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/home/agenticai/agentic-ai-batch-2025-bb06223e6daf.json
```

### Issue: Script not executable

**Solution:**
```bash
chmod +x run_agent.sh
chmod +x chat_with_agent.py
chmod +x test_deployed_agent.py
```

### Issue: "Agent not responding"

**Solution:**
Check MCP server is running:
```bash
curl https://mcp-calculator-server-oyhyp5p3ua-uc.a.run.app/health
```

---

## 📊 Performance Testing

### Response Time Test

```python
import time
from vertexai.agent_engines import AgentEngine
import vertexai

vertexai.init(
    project="agentic-ai-batch-2025",
    location="us-central1",
    staging_bucket="gs://agentic-ai-batch-2025-staging"
)

agent = AgentEngine(
    resource_name="projects/740202511174/locations/us-central1/reasoningEngines/8601228775440515072"
)

# Test response time
queries = ["What is 5 + 3?"] * 5

for i, query in enumerate(queries, 1):
    start = time.time()
    response = agent.query(input=query)
    elapsed = time.time() - start
    print(f"Query {i}: {elapsed:.2f}s")
```

### Concurrent Requests Test

```python
import concurrent.futures

def query_agent(question):
    response = agent.query(input=question)
    return response['output']

questions = [
    "What is 10 + 5?",
    "Calculate 20% of 100",
    "What's 8 times 7?",
    "Square root of 81?",
    "15 - 6 = ?"
]

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(query_agent, questions))

for q, r in zip(questions, results):
    print(f"Q: {q}\nA: {r}\n")
```

---

## 📈 Load Testing

For production readiness, test with increasing loads:

```python
import time

# Simulate 100 queries
for i in range(100):
    response = agent.query(input=f"What is {i} + 1?")
    print(f"Query {i+1}/100 completed")
    time.sleep(0.1)  # Rate limiting
```

---

## 🎯 Success Criteria

Your agent is working correctly if:

- ✅ All 5 automated tests pass
- ✅ Interactive chat responds naturally
- ✅ All 7 calculator tools work
- ✅ Response time < 5 seconds
- ✅ No error messages
- ✅ Calculations are accurate
- ✅ Agent personality is friendly and helpful

---

## 📝 Test Report Template

After testing, document your results:

```
=== AI AGENT TEST REPORT ===

Date: [DATE]
Tester: [YOUR NAME]

Tests Performed:
[ ] Automated test suite
[ ] Interactive chat
[ ] Custom queries
[ ] Performance testing

Results:
- Total queries: ___
- Successful: ___
- Failed: ___
- Average response time: ___ seconds

Tools Tested:
[ ] Add
[ ] Subtract
[ ] Multiply
[ ] Divide
[ ] Percentage
[ ] Square Root
[ ] Power

Issues Found:
[List any issues]

Notes:
[Additional observations]

Status: [ ] Pass [ ] Fail
```

---

## 🚀 Next Steps After Testing

Once testing is complete:

1. **Document Results** - Save test results for reference
2. **Share with Team** - Demonstrate agent capabilities
3. **Integrate** - Add to your application
4. **Monitor** - Set up logging and alerts
5. **Optimize** - Adjust based on usage patterns

---

## 📞 Quick Help

**All scripts location:**
```
/home/agenticai/google-adk-mcp/agent/
```

**Quick commands:**
```bash
# Interactive chat
./run_agent.sh

# Automated tests
.venv/bin/python3 test_deployed_agent.py

# Single query
.venv/bin/python3 -c "..." (see Method 4 above)
```

**Agent Resource Name:**
```
projects/740202511174/locations/us-central1/reasoningEngines/8601228775440515072
```

---

**Ready to test? Start with `./run_agent.sh` for the easiest experience! 🎉**
