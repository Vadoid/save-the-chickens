from google.adk.agents import Agent
from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryAgentAnalyticsPlugin

import logging
import os
from mcp.client.session import ClientSession

# --- Monkey Patch Start ---
# PROBLEM: The BigQuery MCP server currently returns a "400 Bad Request" error when the client 
# attempts to call `resources/list` and `prompts/list` during initialization.
# This causes the ADK agent to crash before it can even list the available tools.
#
# SOLUTION: We monkey-patch the `ClientSession` methods to intercept these specific calls.
# Instead of sending a request to the server, we immediately return an empty result.
# This allows the initialization to proceed to `tools/list`, which IS supported.
print("🔧 Applying MCP ClientSession monkey patch...")
async def mock_list_resources(self, *args, **kwargs):
    print("⚠️ Monkey-patched list_resources called - bypassing unsupported server endpoint")
    class ResourceResult:
        resources = []
        nextCursor = None
    return ResourceResult()

async def mock_list_prompts(self, *args, **kwargs):
    print("⚠️ Monkey-patched list_prompts called - bypassing unsupported server endpoint")
    class PromptResult:
        prompts = []
        nextCursor = None
    return PromptResult()

# Apply the patches to the class definition
ClientSession.list_resources = mock_list_resources
ClientSession.list_prompts = mock_list_prompts
print("✅ MCP ClientSession monkey patch applied.")
# --- Monkey Patch End ---

import dotenv
import os # Import os for better path handling (optional, but good practice)
import sys # Import sys for exiting the application (critical for Uvicorn stability)
from pathlib import Path
import logging

# Configure logging to reduce verbosity in dev UI
# Allow environment variable to control logging level (default: WARNING to hide tool call details)
LOG_LEVEL = os.getenv("ADK_LOG_LEVEL", "WARNING").upper()
logging.getLogger("google.adk").setLevel(getattr(logging, LOG_LEVEL, logging.WARNING))
logging.getLogger("google.genai").setLevel(getattr(logging, LOG_LEVEL, logging.WARNING))
# Keep general logging at INFO level for important messages
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Get the project root directory (parent of chickens_app)
PROJECT_ROOT = Path(__file__).parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

# Load .env file from project root
dotenv.load_dotenv(ENV_FILE)

# Read configuration from environment variables
GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET", "save_the_chickens")  # Default to save_the_chickens if not set

# Validate required environment variables
if not GOOGLE_CLOUD_PROJECT:
    raise ValueError(
        "GOOGLE_CLOUD_PROJECT environment variable is required. "
        "Please set it in your .env file or environment."
    )

print(f"✅ Using project: {GOOGLE_CLOUD_PROJECT}, dataset: {BIGQUERY_DATASET}")

# Helper function to replace placeholders in instruction strings
def replace_instruction_placeholders(instruction_text: str) -> str:
    """Replace {PROJECT_ID} and {DATASET_NAME} placeholders with actual values from env."""
    return instruction_text.replace("{PROJECT_ID}", GOOGLE_CLOUD_PROJECT).replace(
        "{DATASET_NAME}", BIGQUERY_DATASET
    )

# --- Fallback Instruction (Used only if file loading fails) ---
# YOU MUST ensure this fallback is sufficient to describe the agent's core function.
FALLBACK_INSTRUCTION_TEMPLATE = """
You are a BigQuery data analysis agent for chicken product retail operations.
You are able to answer questions on data stored in project-id: '{PROJECT_ID}' on the `{DATASET_NAME}` dataset.
Note: Your detailed analysis protocol file was not found. Please operate based on general SQL query generation.
"""
# -------------------------------------------------------------


# 1. Define the path to your instructions file
INSTRUCTION_FILE_PATH = Path(__file__).parent / "instructions.txt"

# 2. Load the instructions from the file with improved error handling
try:
    with open(INSTRUCTION_FILE_PATH, 'r') as f:
        # Load the entire content as a single string
        comprehensive_instructions = f.read()
        print(f"✅ Successfully loaded instructions from {INSTRUCTION_FILE_PATH}")
        # Combine the base and comprehensive instructions
        agent_instruction_content_template = (
            """
            You are a BigQuery data analysis agent for chicken product retail operations.
            You are able to answer questions on data stored in project-id: '{PROJECT_ID}' on the `{DATASET_NAME}` dataset.
            
            ---
            
            # Comprehensive Data Analysis Protocol:
            
            """
            + comprehensive_instructions
            + """
            
            # Maps Integration
            You also have access to Maps tools. Use these for real-world location analysis, finding competition/places and calculating necessary travel routes.
            Include a hyperlink to an interactive map in your response where appropriate.
            """
        )
        # Replace placeholders with actual values from environment
        agent_instruction_content = replace_instruction_placeholders(agent_instruction_content_template)

except FileNotFoundError:
    # CRITICAL FIX: If the file is not found, log the error and use the defined fallback.
    print(f"❌ CRITICAL ERROR: Instruction file not found at {INSTRUCTION_FILE_PATH}.")
    print("⚠️ Defining agent with FALLBACK INSTRUCTION. Execution may be limited.")
    agent_instruction_content = replace_instruction_placeholders(FALLBACK_INSTRUCTION_TEMPLATE)


# 3. Initialize Tools
from mcp_server.tools import (
    get_maps_mcp_toolset,
    get_bigquery_mcp_toolset,
    get_local_mcp_toolset
)

maps_toolset = get_maps_mcp_toolset()
bigquery_toolset = get_bigquery_mcp_toolset()
local_toolset = get_local_mcp_toolset()

# ADK Agent accepts a list of callables as tools
# MCPToolset is likely an object that needs to be passed directly or its tools extracted.
# Based on user example: tools=[maps_toolset, bigquery_toolset]
# We also want to keep consult_marketing_expert and get_store_temperature.
agent_tools = [
     maps_toolset, 
     bigquery_toolset, 
     local_toolset
]


# --- Initialize the Plugin ---
# The BigQueryAgentAnalyticsPlugin logs all agent interactions (prompts, tool calls, responses)
# to a BigQuery table. This is crucial for auditing, debugging, and analyzing agent performance.
bq_logging_plugin = BigQueryAgentAnalyticsPlugin(
    project_id=GOOGLE_CLOUD_PROJECT, # project_id is required input from user
    dataset_id=BIGQUERY_DATASET, # dataset_id is required input from user
    table_id="agent_events" # Optional: defaults to "agent_events". The plugin automatically creates this table if it doesn't exist.
)

# 4. Define the Agent object
# This is the main "Brain" of the application.
root_agent = Agent(
    model=os.getenv("MODEL_NAME", "gemini-2.5-flash"),
    name="chickens_agent",
    description="Agent that answers questions about chicken product retail data, waste optimization, and stock management by executing SQL queries.",
    # Use the content determined in the try/except block (either from file or fallback)
    instruction=agent_instruction_content, 
    tools=agent_tools
)



# 5. Define the Agent Getter Function
# 5. Define the App object
from google.adk.apps import App

app = App(
    name="chickens_app",
    root_agent=root_agent,
    plugins=[bq_logging_plugin]
)

# 6. Define the Agent Getter Function
def get_chickens_agent():
    return app