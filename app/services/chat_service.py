"""Servicio de chat que maneja la lógica de procesamiento de mensajes y generación de respuestas del agente."""

from sqlmodel.ext.asyncio.session import AsyncSession

from app.agents.flow import FlowAgent

from app.schemas.conversation_schema import ConversationCreate

from app.util.format import format_prompt, format_message

from app.services.conversation_service import ConversationService
from app.services.prompt_service import PromptService

class ChatService:
    def __init__(self, session: AsyncSession, agent: FlowAgent):
        self.session = session
        self.agent = agent
        self.conversation_service = ConversationService(session)
        self.prompt_service = PromptService(session)
    async def chat(self, message: str, thread_id: str | None = None, conversation_id: int | None = None) -> tuple[str, int, str]:
        """Procesa un mensaje de chat, generando una respuesta del agente y actualizando la conversación."""
        prompt = await self.prompt_service.get_active_prompt()
        system_prompt = format_prompt(prompt.system_message)

        if not conversation_id or not thread_id:
            conversation_obj = ConversationCreate(content=[], prompt_id=prompt.id)
            new_conversation = await self.conversation_service.create(conversation_obj)
            conversation_id = new_conversation.id
            thread_id = self.agent.generate_thread_id()

        assert conversation_id is not None
        assert thread_id is not None

        metadata = f"""
        # Información de contexto
        - ID de conversación: {conversation_id}
        """

        final_prompt = f"{metadata}\n\n{system_prompt}"

        response = await self.agent.answer_message(message=message, system_prompt=final_prompt, thread_id=thread_id)
        formatted_messages = format_message(user=message, agent=response)
        await self.conversation_service.update_messages(conversation_id, formatted_messages)

        return response, conversation_id, thread_id
