"""
Configuration file for the Streamlit AI Agent Chat UI
"""
import os

# Google Cloud Configuration
PROJECT_ID = "agentic-ai-batch-2025"
LOCATION = "us-central1"
STAGING_BUCKET = f"gs://{PROJECT_ID}-staging"

# Agent Resource Name
AGENT_RESOURCE_NAME = "projects/740202511174/locations/us-central1/reasoningEngines/8601228775440515072"

# MCP Server URL (for reference)
MCP_SERVER_URL = "https://mcp-calculator-server-oyhyp5p3ua-uc.a.run.app"

# Service Account Credentials
GOOGLE_APPLICATION_CREDENTIALS = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS",
    "/home/agenticai/agentic-ai-batch-2025-bb06223e6daf.json"
)

# UI Configuration
APP_TITLE = "AI Customer Support Agent"
APP_ICON = "🤖"
PAGE_TITLE = "AI Agent Chat"

# Quick Calculator Options
QUICK_CALCULATIONS = [
    {"label": "Add 10 + 5", "query": "What is 10 plus 5?"},
    {"label": "Calculate 15% of 100", "query": "Calculate 15% of 100"},
    {"label": "Multiply 7 × 8", "query": "What is 7 times 8?"},
    {"label": "Square root of 144", "query": "What's the square root of 144?"},
    {"label": "Divide 100 ÷ 5", "query": "What is 100 divided by 5?"},
    {"label": "Calculate 2³", "query": "Calculate 2 to the power of 3"},
]

# Sample Customer Support Queries
SAMPLE_QUERIES = [
    "I'm buying 3 items at $29.99 each. What's the total?",
    "I have a $120 order with a 15% discount. What's my final price?",
    "Calculate the cost of 5 units at $18.50 each",
    "If I order 10 products at $12.99, how much is that?",
    "What's 25% of 80?",
]

# Chat Configuration
MAX_HISTORY_ITEMS = 100
DEFAULT_GREETING = "Hello! I'm your AI customer support assistant. I can help you with calculations, pricing, discounts, and more. How can I assist you today?"

# Theme Configuration
LIGHT_THEME = {
    "primaryColor": "#1f77b4",
    "backgroundColor": "#ffffff",
    "secondaryBackgroundColor": "#f0f2f6",
    "textColor": "#262730",
}

DARK_THEME = {
    "primaryColor": "#1f77b4",
    "backgroundColor": "#0e1117",
    "secondaryBackgroundColor": "#262730",
    "textColor": "#fafafa",
}
