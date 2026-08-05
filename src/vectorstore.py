from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def build_vectorstore(chunks):
    db = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory="data/vectorstore"
    )
    return db

def load_vectorstore():
    return Chroma(
        persist_directory="data/vectorstore",
        embedding_function=embeddings
    )