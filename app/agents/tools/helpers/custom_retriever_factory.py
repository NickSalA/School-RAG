"""Fork de langchain_core.tools.retriever.create_retriever_tool.

NOTA: Esta es una versión modificada de la función oficial de LangChain.
La versión original dejó de funcionar correctamente tras una actualización
de LangChain que introdujo incompatibilidades. Este archivo puede eliminarse
cuando upstream arregle el issue.

Provee funciones para envolver un BaseRetriever en una Tool de LangChain,
permitiendo su uso en agentes conversacionales.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, Field

from langchain_core.tools.simple import Tool

if TYPE_CHECKING:
    from langchain_core.callbacks import Callbacks
    from langchain_core.documents import Document
    from langchain_core.retrievers import BaseRetriever


class RetrieverInput(BaseModel):
    """Input to the retriever."""

    query: str = Field(description="query to look up in retriever")


def _format_doc_with_metadata(doc: Document) -> str:
    """Formatea un documento incluyendo metadatos relevantes de forma segura."""
    filename = doc.metadata.get("filename", "Desconocido")
    return f"[Fuente: {filename}]\n{doc.page_content}"


def _get_relevant_documents(
    query: str,
    retriever: BaseRetriever,
    document_separator: str,
    callbacks: Callbacks = None,
    response_format: Literal["content", "content_and_artifact"] = "content",
) -> str | tuple[str, list[Document]]:
    docs = retriever.invoke(query, config={"callbacks": callbacks})
    content = document_separator.join(
        _format_doc_with_metadata(doc) for doc in docs
    )
    if response_format == "content_and_artifact":
        return (content, docs)

    return content


async def _aget_relevant_documents(
    query: str,
    retriever: BaseRetriever,
    document_separator: str,
    callbacks: Callbacks = None,
    response_format: Literal["content", "content_and_artifact"] = "content",
) -> str | tuple[str, list[Document]]:
    docs = await retriever.ainvoke(query, config={"callbacks": callbacks})
    content = document_separator.join(
        _format_doc_with_metadata(doc) for doc in docs
    )

    if response_format == "content_and_artifact":
        return (content, docs)

    return content


def create_retriever_tool(
    retriever: BaseRetriever,
    name: str,
    description: str,
    *,
    document_separator: str = "\n\n",
    response_format: Literal["content", "content_and_artifact"] = "content",
) -> Tool:
    """Crear una herramienta de retriever.

    Los documentos se formatean automáticamente incluyendo el metadato 'filename'
    como fuente para que el LLM pueda citar el origen de la información.
    """

    def func(query: str, run_manager=None):
        return _get_relevant_documents(
            query=query,
            retriever=retriever,
            document_separator=document_separator,
            response_format=response_format,
            callbacks=run_manager
        )

    async def afunc(query: str, run_manager=None):
        return await _aget_relevant_documents(
            query=query,
            retriever=retriever,
            document_separator=document_separator,
            response_format=response_format,
            callbacks=run_manager
        )

    return Tool(
        name=name,
        description=description,
        func=func,
        coroutine=afunc,
        args_schema=RetrieverInput,
        response_format=response_format,
    )
