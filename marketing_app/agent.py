from google.adk.agents import Agent
import os

# Load instructions
INSTRUCTION_FILE = os.path.join(os.path.dirname(__file__), "instructions.txt")
with open(INSTRUCTION_FILE, "r") as f:
    instructions = f.read()

# Define the Marketing Agent
marketing_agent = Agent(
    model="gemini-2.5-flash",
    name="marketing_agent",
    description="A creative marketing expert who writes social media copy for retail products.",
    instruction=instructions,
    tools=[] # No tools needed, just pure creativity!
)

def get_marketing_agent():
    return marketing_agent
