"""
Streamlit UI for AI Customer Support Agent Chat
"""
import os
import streamlit as st
import vertexai
from vertexai.agent_engines import AgentEngine

# Import local modules
import config
import utils


# Page Configuration
st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
css = utils.load_css("styles.css")
if css:
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Initialize session state
utils.initialize_session_state()


def initialize_agent():
    """Initialize the Vertex AI agent"""
    try:
        # Set credentials
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config.GOOGLE_APPLICATION_CREDENTIALS

        # Initialize Vertex AI
        vertexai.init(
            project=config.PROJECT_ID,
            location=config.LOCATION,
            staging_bucket=config.STAGING_BUCKET
        )

        # Load the agent
        agent = AgentEngine(resource_name=config.AGENT_RESOURCE_NAME)

        st.session_state.agent = agent
        st.session_state.agent_initialized = True

        return True

    except Exception as e:
        st.error(f"Failed to initialize agent: {str(e)}")
        return False


def query_agent(user_input: str) -> str:
    """
    Query the AI agent with user input

    Args:
        user_input: User's question or message

    Returns:
        Agent's response as string
    """
    try:
        with st.spinner("Agent is thinking..."):
            response = st.session_state.agent.query(input=user_input)
            return response.get("output", "No response received.")

    except Exception as e:
        return f"Error querying agent: {str(e)}"


def render_sidebar():
    """Render the sidebar with controls and quick actions"""
    with st.sidebar:
        st.title(f"{config.APP_ICON} {config.APP_TITLE}")

        # Dark/Light Mode Toggle
        st.subheader("Theme")
        dark_mode = st.toggle("Dark Mode", value=st.session_state.dark_mode)
        if dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = dark_mode
            st.rerun()

        st.divider()

        # Quick Calculator Buttons
        st.subheader("Quick Calculations")
        st.caption("Click to send a calculation query")

        for calc in config.QUICK_CALCULATIONS:
            if st.button(calc["label"], key=f"calc_{calc['label']}", use_container_width=True):
                # Add user message
                utils.add_message("user", calc["query"])

                # Get agent response
                response = query_agent(calc["query"])
                utils.add_message("assistant", response)

                st.session_state.query_count += 1
                st.rerun()

        st.divider()

        # Sample Queries
        with st.expander("Sample Customer Support Queries"):
            for i, query in enumerate(config.SAMPLE_QUERIES, 1):
                st.caption(f"{i}. {query}")
                if st.button("Send", key=f"sample_{i}", use_container_width=True):
                    utils.add_message("user", query)
                    response = query_agent(query)
                    utils.add_message("assistant", response)
                    st.session_state.query_count += 1
                    st.rerun()

        st.divider()

        # Chat History Management
        st.subheader("Chat History")

        # Display statistics
        message_counts = utils.get_message_count(st.session_state.messages)
        col1, col2 = st.columns(2)
        col1.metric("User", message_counts["user"])
        col2.metric("Agent", message_counts["assistant"])

        st.caption(f"Total queries: {st.session_state.query_count}")

        # Export options
        if st.session_state.messages:
            st.subheader("Export Chat")

            # Export as text
            text_data = utils.export_chat_to_text(st.session_state.messages)
            st.download_button(
                label="Download as TXT",
                data=text_data,
                file_name=utils.get_download_filename("txt"),
                mime="text/plain",
                use_container_width=True
            )

            # Export as JSON
            json_data = utils.export_chat_to_json(st.session_state.messages)
            st.download_button(
                label="Download as JSON",
                data=json_data,
                file_name=utils.get_download_filename("json"),
                mime="application/json",
                use_container_width=True
            )

            st.divider()

            # Clear history button
            if st.button("Clear Chat History", type="secondary", use_container_width=True):
                utils.clear_chat_history()
                st.rerun()

        st.divider()

        # Agent Information
        with st.expander("Agent Information"):
            st.caption(f"**Project:** {config.PROJECT_ID}")
            st.caption(f"**Location:** {config.LOCATION}")
            st.caption(f"**Model:** Gemini 2.0 Flash")
            st.caption(f"**MCP Server:** [Link]({config.MCP_SERVER_URL})")


def render_chat_interface():
    """Render the main chat interface"""

    # Display greeting if no messages
    if not st.session_state.messages:
        st.info(config.DEFAULT_GREETING)

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            st.caption(f"_{message.get('timestamp', '')}_")

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        utils.add_message("user", prompt)

        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
            st.caption(f"_{utils.format_timestamp()}_")

        # Get agent response
        response = query_agent(prompt)

        # Add and display assistant message
        utils.add_message("assistant", response)
        with st.chat_message("assistant"):
            st.markdown(response)
            st.caption(f"_{utils.format_timestamp()}_")

        st.session_state.query_count += 1
        st.rerun()


def main():
    """Main application function"""

    # Initialize agent if not already done
    if not st.session_state.agent_initialized:
        with st.spinner("Initializing AI Agent..."):
            if not initialize_agent():
                st.error("Failed to initialize the agent. Please check your configuration.")
                st.stop()

    # Render sidebar
    render_sidebar()

    # Main content area
    st.title(f"{config.APP_ICON} AI Agent Chat")
    st.caption("Powered by Vertex AI Agent Engine with Gemini 2.0 Flash")

    # Render chat interface
    render_chat_interface()

    # Footer
    st.divider()
    st.caption("Built with Google Agent Development Kit | MCP Server on Cloud Run | Vertex AI Agent Engine")


if __name__ == "__main__":
    main()
