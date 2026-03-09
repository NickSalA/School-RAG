from app.services import ChatService
from app.agents.flow import FlowAgent
from app.core.database import get_session_context, get_session

async def test_chat():
    async with get_session_context() as session:
        chat_service = ChatService(session, FlowAgent())
    
        response, conversation_id, thread_id = await chat_service.chat("Hola, ¿cómo estás?", user_id="test_user")
        
        print("Chat response:", response)
        print("Conversation ID:", conversation_id)
        print("Thread ID:", thread_id)

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_chat())