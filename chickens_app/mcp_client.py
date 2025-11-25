import asyncio
import os
import sys
from typing import Optional, List, Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Define the path to the server script
SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "mcp_server.py")

class McpBigQueryClient:
    """
    Client adapter that forwards tool calls to the BigQuery MCP server.
    Each tool call spawns a new server instance for simplicity and robustness.
    """
    
    async def _run_tool(self, tool_name: str, arguments: dict) -> str:
        server_params = StdioServerParameters(
            command="python",
            args=[SERVER_SCRIPT],
            env=os.environ.copy()
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                
                # Extract text content
                text_content = []
                if result.content:
                    for content in result.content:
                        if content.type == "text":
                            text_content.append(content.text)
                        else:
                            # Handle other content types if necessary
                            pass
                            
                return "\n".join(text_content)

    async def query_dataset(self, query: str) -> str:
        """
        Execute a SQL query against the BigQuery dataset.
        
        Args:
            query: The SQL query to execute.
        """
        return await self._run_tool("query_dataset", {"query": query})

    async def list_tables(self) -> str:
        """
        List all tables in the configured dataset.
        """
        return await self._run_tool("list_tables", {})

    async def get_table_schema(self, table_name: str) -> str:
        """
        Get the schema of a specific table.
        
        Args:
            table_name: The name of the table.
        """
        return await self._run_tool("get_table_schema", {"table_name": table_name})

    async def get_store_temperature(self, store_id: str) -> str:
        """
        Get the current temperature of the store's freezer/fridge units.
        
        Args:
            store_id: The ID of the store (e.g., 'S001').
        """
        return await self._run_tool("get_store_temperature", {"store_id": store_id})
