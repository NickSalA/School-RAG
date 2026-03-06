"""Servicio de chat que maneja la lógica de procesamiento de mensajes y generación de respuestas del agente."""

from sqlmodel.ext.asyncio.session import AsyncSession

from app.agents.flow import FlowAgent

from app.schemas import ConversationCreate

from app.util import format_prompt, format_message

from app.services import ConversationService, PromptService

class ChatService:
    def __init__(self, session: AsyncSession, agent: FlowAgent):
        self.session = session
        self.agent = agent
        self.conversation_service = ConversationService(session)
        self.prompt_service = PromptService(session)
    async def chat(self, message: str, user_id: str | None = "anon", thread_id: str | None = None, conversation_id: int | None = None) -> tuple[str, int, str]:
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

        # Inyector Selectivo (Mini-RAG de Memoria Semántica)
        store_context = ""
        try:
            store = self.agent.agent_flow.get_store()
            if store:
                memories = []
                
                # 1. Reglas Globales (Aprobadas por quorum)
                global_results = await store.asearch(("global", "verified"), query=message, limit=2)
                for r in global_results:
                    if "rule" in r.value:
                        memories.append(f"- REGLA DEL SISTEMA: {r.value['rule']}")
                        
                # 2. Preferencias del Usuario (Personalización)
                if user_id:
                    user_results = await store.asearch(("users", str(user_id), "prefs"), query=message, limit=2)
                    for r in user_results:
                        if "preference" in r.value:
                            memories.append(f"- PREFERENCIA DE {user_id}: {r.value['preference']}")
                        
                if memories:
                    store_context = (
                        "\\n[REGLAS ACTUALIZADAS Y PREFERENCIAS (STORE)]\\n"
                        + "\\n".join(memories)
                        + "\\n(Nota Crítica: Si esta sección contradice al conocimiento base RAG o PDF, DEBES obedecer a esta sección del STORE y sus reglas prioritarias).\\n"
                    )
        except Exception as e:
            import logging
            logging.error(f"Error accediendo a la capa Store: {e}")

        final_prompt = f"{metadata}\\n{store_context}\\n{system_prompt}"

        response = await self.agent.answer_message(message=message, system_prompt=final_prompt, thread_id=thread_id, user_id=str(user_id))
        formatted_messages = format_message(user=message, agent=response)
        await self.conversation_service.update_messages(conversation_id, formatted_messages)

        return response, conversation_id, thread_id
