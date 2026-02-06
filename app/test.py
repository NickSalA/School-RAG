from llama_index.core.indices import vector_store
from app.util.sincronizer import delete_collection_points
from app.core.services.knowledge import connect_vectorial_client, get_vector_store
from app.core.sync import upload_file
from app.core.services.llm import configure_embedding
client = connect_vectorial_client()
vector_store = get_vector_store(client, "test_flow")


path = "/home/daminin/Documents/Repositorios/School-RAG/app/files/OpcionB2_Creditos_PRONABEC_RAG_v2.pdf"
filename = "OpcionB2_Creditos_PRONABEC_RAG_v2.pdf"

configure_embedding()
upload_file(path, "test_flow")