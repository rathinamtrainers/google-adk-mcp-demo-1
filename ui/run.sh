#!/bin/bash
#
# Launch script for AI Agent Streamlit UI
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}  AI Agent Chat - Streamlit UI${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}Virtual environment created.${NC}"
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source .venv/bin/activate

# Check if requirements are installed
if [ ! -f ".venv/.requirements_installed" ]; then
    echo -e "${YELLOW}Installing requirements...${NC}"
    pip install --upgrade pip
    pip install -r requirements.txt
    touch .venv/.requirements_installed
    echo -e "${GREEN}Requirements installed successfully.${NC}"
else
    echo -e "${GREEN}Requirements already installed.${NC}"
fi

# Set Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS=/home/agenticai/agentic-ai-batch-2025-bb06223e6daf.json

# Check if credentials file exists
if [ ! -f "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo -e "${RED}Error: Credentials file not found at $GOOGLE_APPLICATION_CREDENTIALS${NC}"
    echo -e "${YELLOW}Please set GOOGLE_APPLICATION_CREDENTIALS to the correct path.${NC}"
    exit 1
fi

echo -e "${GREEN}Credentials configured.${NC}"
echo ""

# Launch Streamlit
echo -e "${BLUE}Starting Streamlit UI...${NC}"
echo -e "${YELLOW}The app will open in your browser automatically.${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server.${NC}"
echo ""

streamlit run app.py \
    --server.port=8501 \
    --server.address=localhost \
    --browser.gatherUsageStats=false

echo ""
echo -e "${BLUE}======================================================================${NC}"
echo -e "${GREEN}Thank you for using AI Agent Chat!${NC}"
echo -e "${BLUE}======================================================================${NC}"
