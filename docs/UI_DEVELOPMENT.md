# UI Development Guide

**Complete Guide to the Streamlit User Interface**

---

## Table of Contents

1. [Streamlit Basics](#streamlit-basics)
2. [UI Architecture](#ui-architecture)
3. [Code Structure](#code-structure)
4. [Key Patterns](#key-patterns)
5. [Customization Guide](#customization-guide)
6. [Advanced Features](#advanced-features)

---

## Streamlit Basics

### What is Streamlit?

**Streamlit** is a Python framework for building web applications with minimal code.

**Key advantage:** Write Python, get a web app - no HTML/CSS/JavaScript required!

```python
# This is a complete Streamlit app:
import streamlit as st

st.title("Hello World")
name = st.text_input("Your name")
st.write(f"Hello, {name}!")
```

### Why Streamlit for This Project?

**Pros:**
- ✅ Python-only (no frontend skills needed)
- ✅ Fast development
- ✅ Built-in components (chat, buttons, inputs)
- ✅ Session state management
- ✅ Auto-refresh on code changes

**Cons:**
- ❌ Limited customization vs React
- ❌ Not ideal for complex SPAs
- ❌ Python backend only

---

## UI Architecture

### File Structure

```
ui/
├── app.py              # Main application (235 lines)
├── config.py           # Configuration constants (64 lines)
├── utils.py            # Helper functions (177 lines)
├── styles.css          # Custom styling (145 lines)
├── requirements.txt    # Dependencies
├── run.sh              # Launch script
└── README.md           # Documentation
```

### Component Diagram

```
┌────────────────────────────────────────────┐
│  app.py (Main Application)                 │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │  Sidebar                             │ │
│  │  - Theme toggle                      │ │
│  │  - Quick calc buttons                │ │
│  │  - Sample queries                    │ │
│  │  - Export functionality              │ │
│  │  - Statistics                        │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │  Main Area                           │ │
│  │  - Chat messages                     │ │
│  │  - Chat input                        │ │
│  │  - Title and header                  │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  Uses: config.py, utils.py, styles.css    │
└────────────────────────────────────────────┘
```

---

## Code Structure

### app.py Walkthrough

**File:** `ui/app.py` (235 lines)

#### 1. Page Configuration (Lines 14-19)

```python
st.set_page_config(
    page_title=config.PAGE_TITLE,        # Browser tab title
    page_icon=config.APP_ICON,           # Browser tab icon
    layout="wide",                        # Use full width
    initial_sidebar_state="expanded"      # Sidebar visible
)
```

**Purpose:** Configure browser appearance before any content loads

#### 2. Initialize Agent (Lines 28-44)

```python
def initialize_agent():
    """Initialize the Vertex AI agent"""
    # Set credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.GOOGLE_APPLICATION_CREDENTIALS

    # Initialize Vertex AI
    vertexai.init(
        project=config.PROJECT_ID,
        location=config.LOCATION,
        staging_bucket=config.STAGING_BUCKET
    )

    # Load agent
    agent = AgentEngine(resource_name=config.AGENT_RESOURCE_NAME)

    # Store in session state
    st.session_state.agent = agent
    st.session_state.agent_initialized = True
```

**Purpose:** Connect to deployed Vertex AI agent (done once per session)

#### 3. Query Agent (Lines 47-59)

```python
def query_agent(user_input: str) -> str:
    """Query the AI agent with user input"""
    try:
        with st.spinner("Agent is thinking..."):     # Show loading spinner
            response = st.session_state.agent.query(input=user_input)
            return response.get("output", "No response received.")
    except Exception as e:
        return f"Error querying agent: {str(e)}"
```

**Purpose:** Send query to agent and get response

#### 4. Render Sidebar (Lines 62-174)

```python
def render_sidebar():
    """Render the sidebar with controls"""
    with st.sidebar:
        # Theme toggle
        dark_mode = st.toggle("Dark Mode", value=st.session_state.dark_mode)

        # Quick calculator buttons
        for calc in config.QUICK_CALCULATIONS:
            if st.button(calc["label"], key=f"calc_{calc['label']}"):
                utils.add_message("user", calc["query"])
                response = query_agent(calc["query"])
                utils.add_message("assistant", response)
                st.rerun()  # Refresh to show new messages

        # Export functionality
        text_data = utils.export_chat_to_text(st.session_state.messages)
        st.download_button("Download as TXT", data=text_data, ...)
```

**Key functions:**
- `st.toggle()`: On/off switch
- `st.button()`: Clickable button
- `st.download_button()`: Download file button
- `st.rerun()`: Refresh page to update display

#### 5. Render Chat Interface (Lines 177-226)

```python
def render_chat_interface():
    """Render the main chat interface"""
    # Display existing messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            st.caption(f"_{message.get('timestamp', '')}_")

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        utils.add_message("user", prompt)

        # Display immediately
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get and display agent response
        response = query_agent(prompt)
        utils.add_message("assistant", response)

        with st.chat_message("assistant"):
            st.markdown(response)

        st.rerun()  # Refresh
```

**Key Streamlit components:**
- `st.chat_message()`: Chat bubble UI
- `st.chat_input()`: Chat text input box
- `:=` (walrus operator): Assign and check in one line

---

### config.py Walkthrough

**File:** `ui/config.py` (64 lines)

```python
# Project Configuration
PROJECT_ID = "agentic-ai-batch-2025"
LOCATION = "us-central1"
AGENT_RESOURCE_NAME = "projects/.../reasoningEngines/..."

# UI Configuration
APP_TITLE = "AI Customer Support Agent"
APP_ICON = "🤖"

# Quick Calculations
QUICK_CALCULATIONS = [
    {"label": "Add 10 + 5", "query": "What is 10 plus 5?"},
    # ... more
]

# Sample Queries
SAMPLE_QUERIES = [
    "I'm buying 3 items at $29.99 each. What's the total?",
    # ... more
]
```

**Purpose:** Central location for all configuration constants

---

### utils.py Walkthrough

**File:** `ui/utils.py` (177 lines)

**Key functions:**

#### 1. Session State Management

```python
def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "agent_initialized" not in st.session_state:
        st.session_state.agent_initialized = False
```

**Session state:**
- Persists data across reruns
- Like cookies but server-side
- Accessed via `st.session_state.variable_name`

#### 2. Message Management

```python
def add_message(role: str, content: str):
    """Add a message to session state"""
    message = {
        "role": role,              # "user" or "assistant"
        "content": content,        # Message text
        "timestamp": format_timestamp()
    }
    st.session_state.messages.append(message)
```

#### 3. Export Functions

```python
def export_chat_to_text(messages: List[Dict]) -> str:
    """Export chat history to plain text"""
    lines = ["AI Agent Chat History", "=" * 70]

    for i, msg in enumerate(messages, 1):
        lines.append(f"[{i}] {msg['role'].upper()}")
        lines.append(msg['content'])
        lines.append("")

    return "\n".join(lines)

def export_chat_to_json(messages: List[Dict]) -> str:
    """Export chat history to JSON"""
    export_data = {
        "exported_at": format_timestamp(),
        "messages": messages
    }
    return json.dumps(export_data, indent=2)
```

---

## Key Patterns

### Pattern 1: Session State Management

**Problem:** Streamlit reruns entire script on every interaction

**Solution:** Store data in session state

```python
# Initialize once
if "counter" not in st.session_state:
    st.session_state.counter = 0

# Use and modify
st.write(f"Counter: {st.session_state.counter}")

if st.button("Increment"):
    st.session_state.counter += 1
    st.rerun()
```

### Pattern 2: Conditional Rerun

**When to rerun:**
```python
if st.button("Click me"):
    st.session_state.data = "new value"
    st.rerun()  # Refresh to show new value
```

**When NOT to rerun:**
```python
# Streamlit auto-reruns on user interaction
name = st.text_input("Name")  # No need to manually rerun
st.write(f"Hello {name}")     # Updates automatically
```

### Pattern 3: Loading States

```python
with st.spinner("Loading..."):
    # Long operation
    result = api_call()

st.success("Done!")
```

### Pattern 4: Error Handling

```python
try:
    result = risky_operation()
    st.success("Success!")
except Exception as e:
    st.error(f"Error: {str(e)}")
```

---

## Customization Guide

### Add a New Quick Button

**Step 1:** Edit `ui/config.py`

```python
QUICK_CALCULATIONS = [
    # ... existing buttons
    {"label": "Calculate 20% tip", "query": "What's 20% of 45?"},
]
```

**Step 2:** No other changes needed! Button appears automatically.

### Change Theme Colors

**Edit `ui/config.py`:**

```python
LIGHT_THEME = {
    "primaryColor": "#1f77b4",  # Change to your color
    "backgroundColor": "#ffffff",
    "textColor": "#262730",
}
```

### Add Custom CSS

**Edit `ui/styles.css`:**

```css
/* Custom button style */
.stButton > button {
    background-color: #your-color;
    border-radius: 20px;
}
```

### Add New Feature: Message Search

**Step 1:** Add search box to sidebar (`ui/app.py`)

```python
def render_sidebar():
    # ... existing code

    # Add search
    search_term = st.text_input("Search messages")

    if search_term:
        filtered = [
            msg for msg in st.session_state.messages
            if search_term.lower() in msg["content"].lower()
        ]
        st.write(f"Found {len(filtered)} messages")
        for msg in filtered:
            st.text(msg["content"][:100])
```

**Step 2:** Test

```bash
cd ui
./run.sh
```

---

## Advanced Features

### Feature 1: Conversation Memory

**Store conversation context:**

```python
def get_conversation_context():
    """Get recent messages as context"""
    recent = st.session_state.messages[-5:]  # Last 5 messages
    context = "\n".join([f"{m['role']}: {m['content']}" for m in recent])
    return context

# Use in query
context = get_conversation_context()
enhanced_query = f"Context:\n{context}\n\nNew question: {user_input}"
response = agent.query(input=enhanced_query)
```

### Feature 2: Message Reactions

**Add thumbs up/down:**

```python
def render_message_with_reactions(message, index):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        col1, col2 = st.columns([1, 10])
        with col1:
            if st.button("👍", key=f"up_{index}"):
                st.session_state.messages[index]["reaction"] = "up"
                st.rerun()
        with col2:
            if st.button("👎", key=f"down_{index}"):
                st.session_state.messages[index]["reaction"] = "down"
                st.rerun()
```

### Feature 3: Voice Input (using browser API)

```python
# Add to ui/app.py
from streamlit_webrtc import webrtc_streamer

def voice_input():
    ctx = webrtc_streamer(key="speech")
    if ctx.audio_receiver:
        # Process audio and convert to text
        pass
```

### Feature 4: Multi-session Support

**Store different conversation threads:**

```python
if "sessions" not in st.session_state:
    st.session_state.sessions = {"default": []}
    st.session_state.current_session = "default"

session_name = st.selectbox(
    "Select conversation",
    options=list(st.session_state.sessions.keys())
)

st.session_state.current_session = session_name
messages = st.session_state.sessions[session_name]
```

---

## Debugging Tips

### View Session State

```python
# Add to sidebar for debugging
with st.expander("Debug: Session State"):
    st.write(st.session_state)
```

### Log Messages

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"User query: {user_input}")
logger.info(f"Agent response: {response}")
```

### Check Agent Connection

```python
def test_agent_connection():
    try:
        response = st.session_state.agent.query(input="Hello")
        st.success("Agent connected!")
        return True
    except Exception as e:
        st.error(f"Agent connection failed: {e}")
        return False
```

---

## Performance Optimization

### Caching Expensive Operations

```python
@st.cache_data
def load_configuration():
    """Cache config loading"""
    return config.QUICK_CALCULATIONS

@st.cache_resource
def get_agent():
    """Cache agent initialization"""
    return AgentEngine(resource_name=config.AGENT_RESOURCE_NAME)
```

### Minimize Reruns

```python
# Bad: Reruns on every interaction
if st.button("Click"):
    st.rerun()

# Good: Only rerun when necessary
if st.button("Click"):
    st.session_state.clicked = True
    # Streamlit auto-reruns on button click
```

---

## Summary

**Key Takeaways:**

1. **Streamlit = Python → Web App**
2. **Session state** persists data across reruns
3. **st.rerun()** refreshes the page
4. **Configuration in config.py** for easy customization
5. **Utilities in utils.py** for reusable functions
6. **Custom CSS** for styling

**Important Files:**
- `ui/app.py:28-44` - Agent initialization
- `ui/app.py:47-59` - Agent querying
- `ui/app.py:62-174` - Sidebar rendering
- `ui/app.py:177-226` - Chat interface
- `ui/utils.py` - Helper functions
- `ui/config.py` - Configuration

**Next Steps:**
- Experiment with customizations
- Add new features
- Try different Streamlit components
- Read [Streamlit docs](https://docs.streamlit.io)
