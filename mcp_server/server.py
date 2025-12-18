import os
import random
import uuid
import json
import httpx
import logging
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
# "chickens-local-tools" is the server name
mcp = FastMCP("chickens-local-tools")

# Configure logging
# Stdio server logging must NOT write to stdout, as it corrupts the protocol.
# FastMCP handles this by redirecting default logging to stderr.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

@mcp.tool()
def get_store_temperature(store_id: str) -> str:
    """
    Get the current temperature of the store's freezer/fridge units.
    
    This function simulates retrieving real-time IoT sensor data from store units.
    It returns temperature readings and status (OK, WARNING, CRITICAL) for
    various units like Freezers, Fridges, and Display Cases.
    
    Args:
        store_id: The ID of the store (e.g., 'S001').
        
    Returns:
        str: A JSON string containing temperature data for units.
    """
    units = ["Freezer-1", "Freezer-2", "Fridge-Main", "Display-Case"]
    data = {"store_id": store_id, "units": []}
    
    for unit in units:
        # 90% chance of good temp, 10% chance of issue
        if random.random() > 0.1:
            temp = round(random.uniform(-22.0, -18.0), 1)
            status = "OK"
        else:
            temp = round(random.uniform(-15.0, -5.0), 1)
            status = "WARNING" if temp < -10 else "CRITICAL"
            
        data["units"].append({
            "unit_id": unit,
            "temperature_celsius": temp,
            "status": status
        })
        
    return json.dumps(data, indent=2)

@mcp.tool()
async def consult_marketing_expert(context: str, goal: str) -> str:
    """
    Consults the Marketing Expert agent to generate creative content via A2A Protocol.
    
    Args:
        context: The situation (e.g., "50 units of Chicken Breast expiring tomorrow at Store X").
        goal: What you want the expert to do (e.g., "Write a tweet to sell this fast").
        
    Returns:
        The marketing expert's response.
    """
    logger.info(f"📞 Calling Marketing Agent (A2A)... Context: {context[:50]}...")
    
    marketing_server_url = "http://localhost:8001/"
    
    # Construct the prompt
    prompt = f"Context: {context}\nGoal: {goal}"
    
    # Create JSON-RPC payload
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "message/send",
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "parts": [{"text": prompt}]
            }
        }
    }
    
    try:
        async with httpx.AsyncClient() as client:
            # We use a comprehensive timeout as LLM generation might take time
            response = await client.post(marketing_server_url, json=payload, timeout=60.0)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse A2A response
            if "error" in data:
                return f"Error from Marketing Agent: {data['error']}"
            
            if "result" in data and "message" in data["result"]:
                message = data["result"]["message"]
                if "parts" in message and message["parts"]:
                    response_text = message["parts"][0].get("text", "No text response")
                else:
                    response_text = "Empty response from agent"
            else:
                 response_text = f"Unexpected response format: {json.dumps(data)}"

            # Generate Twitter Intent URL (Client-side enhancement)
            import urllib.parse
            encoded_text = urllib.parse.quote(response_text)
            twitter_url = f"https://twitter.com/intent/tweet?text={encoded_text}"
            
            response_text += f"\n\n[🐦 Post to Twitter]({twitter_url})"
            
            return response_text

    except httpx.RequestError as e:
        return f"Error connecting to Marketing Agent Server: {str(e)}. (Is it running on port 8001?)"
    except Exception as e:
        return f"Error consulting marketing expert: {str(e)}"

if __name__ == "__main__":
    # Stdio is the default transport for FastMCP
    mcp.run()
