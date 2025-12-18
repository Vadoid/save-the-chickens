from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from marketing_app.agent import get_marketing_agent
import uuid
import asyncio

async def consult_marketing_expert(context: str, goal: str) -> str:
    """
    Consults the Marketing Expert agent to generate creative content.
    
    Args:
        context: The situation (e.g., "50 units of Chicken Breast expiring tomorrow at Store X").
        goal: What you want the expert to do (e.g., "Write a tweet to sell this fast").
        
    Returns:
        The marketing expert's response.
    """
    print(f"📞 Calling Marketing Agent... Context: {context[:50]}...")
    
    # Initialize the marketing agent
    # We load the agent definition from the marketing_app module
    agent = get_marketing_agent()
    
    # Create a fresh session for this interaction
    # Using InMemorySessionService is sufficient for this stateless delegation
    session_service = InMemorySessionService()
    session_id = f"marketing-{uuid.uuid4().hex[:8]}"
    
    # Initialize the Runner
    # The Runner orchestrates the agent's execution loop
    runner = Runner(
        agent=agent,
        app_name="marketing_app",
        session_service=session_service
    )
    
    # Create the session in the service
    await session_service.create_session(
        app_name="marketing_app",
        user_id="system_delegation",
        session_id=session_id
    )
    
    # Construct the prompt
    # We wrap the context and goal into a structured prompt for the sub-agent
    prompt = f"Context: {context}\nGoal: {goal}"
    
    # Run the agent
    response_text = "No response from marketing expert."
    
    try:
        # Collect all events first to ensure the generator is fully consumed.
        # This is a critical pattern: if we break the loop early or don't consume
        # the generator, it can lead to "RuntimeError: generator ignored GeneratorExit"
        # or OpenTelemetry context leaks.
        events = []
        async for event in runner.run_async(
            user_id="system_delegation",
            session_id=session_id,
            new_message=types.Content(role="user", parts=[types.Part(text=prompt)])
        ):
            events.append(event)
            
        # Process the final response from the collected events
        # We look for the last event that contains a final response text
        for event in events:
            if event.is_final_response() and event.content and event.content.parts:
                response_text = event.content.parts[0].text
                break
                
        # Generate Twitter Intent URL
        import urllib.parse
        encoded_text = urllib.parse.quote(response_text)
        twitter_url = f"https://twitter.com/intent/tweet?text={encoded_text}"
        
        response_text += f"\n\n[🐦 Post to Twitter]({twitter_url})"
        
    except Exception as e:
        response_text = f"Error consulting marketing expert: {str(e)}"
        
    return response_text
