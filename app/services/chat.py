"""Servicio de chat que maneja la lógica de procesamiento de mensajes y generación de respuestas del agente."""

from sqlmodel.ext.asyncio.session import AsyncSession
from app.agents.flow import FlowAgent, prompt_system
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.prompt_repository import PromptRepository
from app.schemas.conversation_schema import ConversationCreate
from app.util.format import format_content, format_message
class ChatService:
    def __init__(self, session: AsyncSession, agent: FlowAgent):
        self.session = session
        self.agent = agent
        self.prompt = PromptRepository(session)
        self.conversation = ConversationRepository(session)

    async def chat(self, message: str, thread_id: str | None = None, conversation_id: int | None = None) -> tuple[str, int, str]:
        """Procesa un mensaje de chat, generando una respuesta del agente y actualizando la conversación."""
        db_prompt = await self.prompt.get_active_prompt()
        prompt_id = db_prompt.id if db_prompt else None
        if db_prompt is None:
            system_prompt = prompt_system()
        else:
            system_prompt = db_prompt.system_message

        system_prompt = format_content(system_prompt)

        if not conversation_id or not thread_id:
            conversation_obj = ConversationCreate(content=[], prompt_id=prompt_id)
            new_conversation = await self.conversation.create(conversation_obj)
            conversation_id = new_conversation.id
            thread_id = self.agent.generate_thread_id()

        assert conversation_id is not None
        assert thread_id is not None

        response = await self.agent.answer_message(message=message, system_prompt=system_prompt, thread_id=thread_id)
        formatted_messages = format_message(user=message, agent=response)
        await self.conversation.update_messages(conversation_id, formatted_messages)

        return response, conversation_id, thread_id
