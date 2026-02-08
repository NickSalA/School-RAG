"""Adaptador de LlamaIndex Retriever para LangChain.

Implementa un retriever compatible con LangChain que usa internamente
LlamaIndex con post-procesamiento de ventana de contexto (SentenceWindowRetrieval).
"""

from typing import List, Any, Optional
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document as LCDocument
from llama_index.core import QueryBundle
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from llama_index.core.schema import NodeWithScore

class LlamaIndexWindowRetriever(BaseRetriever):
    index: Any
    top_k: int = 3

    def _get_relevant_documents(
        self, query: str, *, run_manager: Optional[CallbackManagerForRetrieverRun] = None
    ) -> List[LCDocument]:

        retriever = self.index.as_retriever(similarity_top_k=self.top_k)
        nodes: List[NodeWithScore] = retriever.retrieve(query)

        processor = MetadataReplacementPostProcessor(target_metadata_key="window")
        new_nodes = processor.postprocess_nodes(nodes, query_bundle=QueryBundle(query))

        langchain_docs = []
        for node in new_nodes:
            langchain_docs.append(
                LCDocument(
                    page_content=node.text,
                    metadata=node.metadata
                )
            )

        return langchain_docs
