import asyncio
import sys

from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp_types import TextContent

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-5"
client = Anthropic()

def server_params() -> StdioServerParameters:
    """Describe the subprocess to run a MCP server."""
