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
    )
    store = InMemoryStore()  # holds the parent documents

    # Split parent docs ourselves FIRST, so ids can be generated to match the actual post-split document count.
    parent_docs = parent_splitter.split_documents(docs)
    ids = [content_hash(d.page_content) for d in parent_docs]

    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=store,
        child_splitter=child_splitter,
    )

    retriever.add_documents(parent_docs, ids=ids) 
    return retriever