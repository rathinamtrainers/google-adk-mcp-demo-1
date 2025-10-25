"""
Utility functions for the Streamlit AI Agent Chat UI
"""
import json
from datetime import datetime
from typing import List, Dict
import streamlit as st


def format_timestamp() -> str:
    """Format current timestamp for display"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def export_chat_to_text(messages: List[Dict[str, str]]) -> str:
    """
    Export chat history to plain text format

    Args:
        messages: List of message dictionaries with 'role' and 'content'

    Returns:
        Formatted text string
    """
    lines = [
        "=" * 70,
        "AI Agent Chat History",
        f"Exported: {format_timestamp()}",
        "=" * 70,
        ""
    ]

    for i, msg in enumerate(messages, 1):
        role = msg["role"].upper()
        content = msg["content"]
        timestamp = msg.get("timestamp", "")

        lines.append(f"[{i}] {role} - {timestamp}")
        lines.append(content)
        lines.append("")

    lines.append("=" * 70)
    return "\n".join(lines)


def export_chat_to_json(messages: List[Dict[str, str]]) -> str:
    """
    Export chat history to JSON format

    Args:
        messages: List of message dictionaries with 'role' and 'content'

    Returns:
        JSON string
    """
    export_data = {
        "exported_at": format_timestamp(),
        "total_messages": len(messages),
        "messages": messages
    }
    return json.dumps(export_data, indent=2)


def get_message_count(messages: List[Dict[str, str]]) -> Dict[str, int]:
    """
    Count messages by role

    Args:
        messages: List of message dictionaries

    Returns:
        Dictionary with counts by role
    """
    counts = {"user": 0, "assistant": 0}
    for msg in messages:
        role = msg.get("role", "")
        if role in counts:
            counts[role] += 1
    return counts


def format_response_with_tools(response_text: str) -> str:
    """
    Format agent response to highlight tool usage

    Args:
        response_text: Raw response from agent

    Returns:
        Formatted response string
    """
    # This is a simple formatter - can be enhanced to detect tool calls
    return response_text


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to max length with ellipsis

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def load_css(file_path: str) -> str:
    """
    Load CSS from file

    Args:
        file_path: Path to CSS file

    Returns:
        CSS content as string
    """
    try:
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def initialize_session_state():
    """Initialize Streamlit session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "agent_initialized" not in st.session_state:
        st.session_state.agent_initialized = False

    if "dark_mode" not in st.session_state:
        st.session_state.dark_mode = False

    if "query_count" not in st.session_state:
        st.session_state.query_count = 0


def add_message(role: str, content: str):
    """
    Add a message to session state

    Args:
        role: Message role (user or assistant)
        content: Message content
    """
    message = {
        "role": role,
        "content": content,
        "timestamp": format_timestamp()
    }
    st.session_state.messages.append(message)


def clear_chat_history():
    """Clear all messages from chat history"""
    st.session_state.messages = []
    st.session_state.query_count = 0


def get_download_filename(extension: str = "txt") -> str:
    """
    Generate download filename with timestamp

    Args:
        extension: File extension

    Returns:
        Filename string
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"chat_history_{timestamp}.{extension}"
