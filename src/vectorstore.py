import hashlib
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_classic.retrievers import ParentDocumentRetriever
from langchain_classic.storage import InMemoryStore
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Small chunks used only for search precision
child_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.CPP, chunk_size=300, chunk_overlap=30
)

# Large chunks returned to the LLM as actual context 
parent_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.CPP, chunk_size=3000, chunk_overlap=200
)

def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def build_parent_retriever(docs):
    vectorstore = Chroma(
        collection_name="code_chunks",
        embedding_function=embeddings,
        persist_directory="data/vectorstore"
    )
    store = InMemoryStore()  # holds the parent documents

    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
    )

    # Generate deterministic IDs for each parent doc based on its content
    ids = [content_hash(doc.page_content) for doc in docs]

    retriever.add_documents(docs)
    return retriever