import asyncio
import logging
from run_agent import run_conversation

# Enable debug logging for the plugin
logging.getLogger("google.adk.plugins.bigquery_agent_analytics_plugin").setLevel(logging.DEBUG)

async def main():
    print("Starting conversation...")
    result = await run_conversation("How many chickens do we have?")
    print("Conversation finished.")
    print(f"Response: {result['response']}")

if __name__ == "__main__":
    asyncio.run(main())
