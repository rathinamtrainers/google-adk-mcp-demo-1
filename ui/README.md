# AI Agent Chat - Streamlit UI

A beautiful, interactive web interface for chatting with your AI Customer Support Agent deployed on Vertex AI Agent Engine.

---

## Features

- **Interactive Chat Interface** - Natural conversation with your AI agent
- **Quick Calculator Buttons** - One-click access to common calculations
- **Response History** - View, export, and manage chat history
- **Dark/Light Mode Toggle** - Choose your preferred theme
- **Real-time Statistics** - Track messages and queries
- **Export Functionality** - Download conversations as TXT or JSON
- **Sample Queries** - Pre-loaded customer support scenarios

---

## Quick Start

### Option 1: Use the Launch Script (Easiest)

```bash
cd /home/agenticai/google-adk-mcp/ui
./run.sh
```

The script will:
1. Create a virtual environment (if needed)
2. Install dependencies
3. Set up credentials
4. Launch the Streamlit app

The UI will automatically open in your browser at `http://localhost:8501`

### Option 2: Manual Setup

```bash
# Navigate to UI directory
cd /home/agenticai/google-adk-mcp/ui

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS=/home/agenticai/agentic-ai-batch-2025-bb06223e6daf.json

# Run the app
streamlit run app.py
```

---

## Usage

### Main Chat Interface

1. **Type your message** in the chat input at the bottom
2. **Press Enter** to send
3. **View response** from the AI agent with timestamp
4. **Continue the conversation** naturally

### Quick Calculator Buttons

Located in the sidebar, click any button to instantly:
- Add numbers (10 + 5)
- Calculate percentages (15% of 100)
- Multiply (7 × 8)
- Find square roots (√144)
- Divide (100 ÷ 5)
- Calculate powers (2³)

### Sample Queries

Expand the "Sample Customer Support Queries" section to:
- View example questions
- Click "Send" to test customer support scenarios

### Export Chat History

1. View statistics (user/agent message counts)
2. Click **"Download as TXT"** for plain text export
3. Click **"Download as JSON"** for structured data export

### Clear Chat History

Click **"Clear Chat History"** in the sidebar to start fresh.

### Theme Toggle

Use the **"Dark Mode"** toggle in the sidebar to switch between light and dark themes.

---

## File Structure

```
ui/
├── app.py              # Main Streamlit application
├── config.py           # Configuration settings
├── utils.py            # Helper functions
├── styles.css          # Custom CSS styling
├── requirements.txt    # Python dependencies
├── run.sh              # Launch script
└── README.md           # This file
```

---

## Configuration

Edit `config.py` to customize:

- **Agent resource name** - Your Vertex AI agent identifier
- **Project settings** - GCP project ID, location, bucket
- **Quick calculations** - Add/remove calculator buttons
- **Sample queries** - Customize example questions
- **UI appearance** - App title, icon, colors
- **Chat settings** - Max history, default greeting

---

## Features in Detail

### 1. Chat Interface

- **Message bubbles** with user/agent distinction
- **Timestamps** for each message
- **Smooth scrolling** for long conversations
- **Loading indicator** while agent processes queries

### 2. Quick Calculations

Pre-configured buttons for:
```python
QUICK_CALCULATIONS = [
    {"label": "Add 10 + 5", "query": "What is 10 plus 5?"},
    {"label": "Calculate 15% of 100", "query": "Calculate 15% of 100"},
    {"label": "Multiply 7 × 8", "query": "What is 7 times 8?"},
    {"label": "Square root of 144", "query": "What's the square root of 144?"},
    {"label": "Divide 100 ÷ 5", "query": "What is 100 divided by 5?"},
    {"label": "Calculate 2³", "query": "Calculate 2 to the power of 3"},
]
```

### 3. Sample Customer Support Queries

Pre-loaded scenarios:
- Shopping cart calculations
- Discount applications
- Bulk order pricing
- Unit pricing
- Percentage questions

### 4. Export Formats

**Text Export Example:**
```
======================================================================
AI Agent Chat History
Exported: 2025-10-26 14:30:00
======================================================================

[1] USER - 2025-10-26 14:25:00
What is 10 plus 5?

[2] ASSISTANT - 2025-10-26 14:25:02
10 plus 5 equals 15.
```

**JSON Export Example:**
```json
{
  "exported_at": "2025-10-26 14:30:00",
  "total_messages": 2,
  "messages": [
    {
      "role": "user",
      "content": "What is 10 plus 5?",
      "timestamp": "2025-10-26 14:25:00"
    },
    {
      "role": "assistant",
      "content": "10 plus 5 equals 15.",
      "timestamp": "2025-10-26 14:25:02"
    }
  ]
}
```

### 5. Statistics Display

Real-time metrics:
- User message count
- Agent response count
- Total queries executed
- Conversation length

---

## Customization

### Add Custom Quick Calculations

Edit `config.py`:

```python
QUICK_CALCULATIONS = [
    {"label": "Your Label", "query": "Your query to agent"},
    # Add more...
]
```

### Modify Theme Colors

Edit `config.py`:

```python
LIGHT_THEME = {
    "primaryColor": "#1f77b4",
    "backgroundColor": "#ffffff",
    "secondaryBackgroundColor": "#f0f2f6",
    "textColor": "#262730",
}
```

### Change Default Greeting

Edit `config.py`:

```python
DEFAULT_GREETING = "Your custom greeting message here!"
```

### Add Custom CSS

Edit `styles.css` to modify:
- Message bubble styling
- Button appearance
- Colors and spacing
- Typography
- Animations

---

## Troubleshooting

### Issue: "Module not found" error

**Solution:**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall requirements
pip install -r requirements.txt
```

### Issue: "Failed to initialize agent"

**Solution:**
```bash
# Check credentials file exists
ls -l /home/agenticai/agentic-ai-batch-2025-bb06223e6daf.json

# Set credentials explicitly
export GOOGLE_APPLICATION_CREDENTIALS=/home/agenticai/agentic-ai-batch-2025-bb06223e6daf.json
```

### Issue: "Port already in use"

**Solution:**
```bash
# Use a different port
streamlit run app.py --server.port=8502

# Or kill existing process
pkill -f streamlit
```

### Issue: Blank page or errors

**Solution:**
1. Check browser console for JavaScript errors
2. Clear browser cache
3. Try a different browser
4. Restart the Streamlit server

### Issue: Slow responses

**Possible causes:**
- Agent cold start (first query after idle period)
- Network latency
- Complex calculations requiring multiple tool calls

**Solutions:**
- Wait for first query to warm up agent
- Check internet connection
- Monitor Vertex AI logs for performance issues

---

## Development

### Running in Development Mode

```bash
# Watch for file changes and auto-reload
streamlit run app.py --server.runOnSave=true
```

### Adding New Features

1. **New utility function** → Add to `utils.py`
2. **New configuration** → Add to `config.py`
3. **New UI component** → Add to `app.py`
4. **New styling** → Add to `styles.css`

### Testing Locally

```bash
# Test with sample queries
python3 -c "
import config
import utils

utils.initialize_session_state()
for query in config.SAMPLE_QUERIES:
    print(f'Testing: {query}')
"
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│         Streamlit UI (app.py)           │
│  - Chat interface                       │
│  - Quick buttons                        │
│  - History management                   │
└─────────────┬───────────────────────────┘
              │
              │ agent.query()
              ▼
┌─────────────────────────────────────────┐
│     Vertex AI Agent Engine              │
│  - Gemini 2.0 Flash model               │
│  - Agent reasoning                      │
│  - Tool selection                       │
└─────────────┬───────────────────────────┘
              │
              │ HTTP requests
              ▼
┌─────────────────────────────────────────┐
│   MCP Server (Cloud Run)                │
│  - Calculator tools                     │
│  - add, subtract, multiply, etc.        │
└─────────────────────────────────────────┘
```

---

## Performance Tips

1. **Keep agent warm** - Regular queries prevent cold starts
2. **Clear history periodically** - Better performance with fewer messages
3. **Use quick buttons** - Pre-formatted queries are faster
4. **Export regularly** - Don't let history grow too large

---

## Security Notes

- **Credentials** - Never commit service account JSON files
- **Local only** - This UI is designed for local development
- **Public deployment** - Requires additional authentication setup
- **Environment variables** - Use `.env` files for production

---

## Support & Resources

### Documentation
- Main project: `/home/agenticai/google-adk-mcp/README.md`
- Testing guide: `/home/agenticai/google-adk-mcp/TESTING_GUIDE.md`
- Agent access: `/home/agenticai/google-adk-mcp/HOW_TO_ACCESS_AGENT.md`

### Important Links
- **Streamlit Docs**: https://docs.streamlit.io
- **Vertex AI Docs**: https://cloud.google.com/vertex-ai/docs
- **Agent Console**: https://console.cloud.google.com/vertex-ai/reasoning-engines?project=agentic-ai-batch-2025

### Configuration Details
- **Project ID**: `agentic-ai-batch-2025`
- **Location**: `us-central1`
- **Agent ID**: `8601228775440515072`
- **MCP Server**: `https://mcp-calculator-server-oyhyp5p3ua-uc.a.run.app`

---

## Roadmap

Potential future enhancements:
- [ ] User authentication
- [ ] Multi-session support
- [ ] Conversation search
- [ ] Voice input/output
- [ ] Mobile responsive design
- [ ] Cloud deployment guide
- [ ] API key management
- [ ] Rate limiting
- [ ] Advanced analytics
- [ ] Custom tool integration

---

## License

Part of the Google Agent Development Kit MCP Server project.

---

## Quick Commands Reference

```bash
# Start the UI
./run.sh

# Manual start
streamlit run app.py

# Different port
streamlit run app.py --server.port=8502

# Development mode
streamlit run app.py --server.runOnSave=true

# Stop the server
Ctrl+C

# Kill all Streamlit processes
pkill -f streamlit

# Check virtual environment
source .venv/bin/activate
pip list
```

---

**Ready to chat? Run `./run.sh` and start talking to your AI agent!**
