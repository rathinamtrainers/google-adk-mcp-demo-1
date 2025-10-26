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

"""Tools configuration for the Calculator Support Agent."""

import os
from google.adk.tools.mcp_tool import McpToolset, StreamableHTTPConnectionParams

# MCP Calculator Server URL (deployed on Cloud Run)
MCP_SERVER_URL = os.getenv(
    "MCP_SERVER_URL",
    "https://mcp-calculator-server-oyhyp5p3ua-uc.a.run.app/mcp"
)


def get_mcp_tools():
    """
    Factory function to create MCP toolset.

    This is a function rather than a module-level variable to avoid
    pickling issues during deployment (MCPToolset contains file handles
    that can't be pickled).

    Returns:
        MCPToolset or callable: The MCP toolset for calculator operations
    """
    return MCPToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=MCP_SERVER_URL,
            # No headers needed as the Cloud Run service allows unauthenticated access
            # If you secure the MCP server later, add authentication headers here:
            # headers={
            #     "Authorization": "Bearer " + os.getenv("MCP_AUTH_TOKEN"),
            # },
        ),
        # Filter to only include the calculator tools we want
        tool_filter=[
            "add",
            "subtract",
            "multiply",
            "divide",
            "power",
            "sqrt",
            "percentage"
        ],
        # Add a prefix to tool names to avoid conflicts (optional)
        # tool_name_prefix="calc_",
    )
