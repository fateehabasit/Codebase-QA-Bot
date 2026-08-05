from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.CPP, chunk_size=800, chunk_overlap=100
)

def chunk_docs(docs):
    return splitter.split_documents(docs)