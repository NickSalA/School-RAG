"""Servicio de chat que maneja la lógica de procesamiento de mensajes y generación de respuestas del agente."""

from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import User
from app.schemas import ConversationCreate, ChatIn

from app.util import format_prompt, format_message

from app.services.conversation_service import ConversationService
from app.services.prompt_service import PromptService

class ChatService:
    def __init__(self, session: AsyncSession, agent):
        self.session = session
        self.agent = agent
        self.conversation_service = ConversationService(session)
        self.prompt_service = PromptService(session)
    async def chat(self, chat: ChatIn, user: User) -> tuple[str, int]:
        """Procesa un mensaje de chat, generando una respuesta del agente y actualizando la conversación."""
        prompt = await self.prompt_service.get_active_prompt()
        system_prompt = format_prompt(prompt.system_message)

        if not chat.conversation_id:
            conversation_obj = ConversationCreate(content=[], prompt_id=prompt.id, user_id=user.id)
            new_conversation = await self.conversation_service.create(conversation_obj)
            chat.conversation_id = new_conversation.id

        assert chat.conversation_id is not None

        metadata = f"""
        # Información de contexto
        - ID de conversación: {chat.conversation_id}
        - Nombre del usuario: {user.name or "Desconocido"}
        """

        # Inyector Selectivo (Mini-RAG de Memoria Semántica)
        store_context = ""
        try:
            store = self.agent.agent_flow.get_store()
            if store:
                memories = []

                # 1. Reglas Globales (Aprobadas por quorum)
                global_results = await store.asearch(("global", "verified"), query=chat.message, limit=2)
                for r in global_results:
                    if "rule" in r.value:
                        memories.append(f"- REGLA DEL SISTEMA: {r.value['rule']}")

                # 2. Preferencias del Usuario (Personalización)
                if user.id:
                    user_results = await store.asearch(("users", str(user.id), "prefs"), query=chat.message, limit=2)
                    for r in user_results:
                        if "preference" in r.value:
                            memories.append(f"- PREFERENCIA DE {user.id}: {r.value['preference']}")

                if memories:
                    store_context = (
                        "\\n[REGLAS ACTUALIZADAS Y PREFERENCIAS (STORE)]\\n"
                        + "\\n".join(memories)
                        + "\\n(Nota Crítica: Si esta sección contradice al conocimiento base RAG o PDF, DEBES obedecer a esta sección del STORE y sus reglas prioritarias).\\n"
                    )
        except Exception as e:
            raise RuntimeError(f"Error accediendo al store para contexto adicional: {e}") from e

        final_prompt = f"{metadata}\\n{store_context}\\n{system_prompt}"

        response = await self.agent.answer_message(message=chat.message, system_prompt=final_prompt, conversation_id=chat.conversation_id, checkpoint_ns=user.id)
        formatted_messages = format_message(user=chat.message, agent=response)
        await self.conversation_service.update_messages(chat.conversation_id, formatted_messages)

        return response, chat.conversation_id
