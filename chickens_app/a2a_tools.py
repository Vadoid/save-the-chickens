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
    agent = get_marketing_agent()
    session_service = InMemorySessionService()
    session_id = f"marketing-{uuid.uuid4().hex[:8]}"
    
    runner = Runner(
        agent=agent,
        app_name="marketing_app",
        session_service=session_service
    )
    
    # Create session
    await session_service.create_session(
        app_name="marketing_app",
        user_id="system_delegation",
        session_id=session_id
    )
    
    # Construct the prompt
    prompt = f"Context: {context}\nGoal: {goal}"
    
    # Run the agent
    response_text = "No response from marketing expert."
    
    try:
        async for event in runner.run_async(
            user_id="system_delegation",
            session_id=session_id,
            new_message=types.Content(role="user", parts=[types.Part(text=prompt)])
        ):
            if event.is_final_response() and event.content and event.content.parts:
                response_text = event.content.parts[0].text
                break
    except Exception as e:
        response_text = f"Error consulting marketing expert: {str(e)}"
        
    return response_text
