# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Main agent definition for the Calculator Support Agent."""

from google.adk.agents import Agent

from .prompt import agent_instruction
from .tools import get_mcp_tools

# Create the root agent with lazy tool initialization
# This is the main agent that will be deployed to Vertex AI
# Tools are initialized via the factory function to avoid pickling issues
root_agent = Agent(
    model="gemini-2.5-flash",
    name="calculator_support_agent",
    instruction=agent_instruction,
    tools=[get_mcp_tools],  # Pass the factory function, not the instantiated toolset
)

print(f"✅ Agent '{root_agent.name}' created successfully")
print(f"   Model: {root_agent.model}")
print(f"   Tools: Lazy-loaded MCP toolset")
