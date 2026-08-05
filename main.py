import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from src.load_docs import load_repo_files
from src.chunking import chunk_docs
from src.vectorstore import build_vectorstore

load_dotenv()

print("Loading files...")
docs = load_repo_files("data/repo/OOP Project Social Network Application")
print(f"Loaded {len(docs)} files")

print("Chunking...")
chunks = chunk_docs(docs)
print(f"Created {len(chunks)} chunks")

print("Building vector store...")
db = build_vectorstore(chunks)
retriever = db.as_retriever(search_kwargs={"k": 4})

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

prompt = ChatPromptTemplate.from_template("""
Answer the question based only on the following context from the codebase:

{context}

Question: {question}
""")

def format_docs(docs):
    return "\n\n".join(
        f"[{doc.metadata.get('source')}]\n{doc.page_content}" for doc in docs
    )

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

print("\nReady! Ask questions about the repo (type 'quit' to exit)\n")

while True:
    query = input("Question: ")
    if query.lower() == "quit":
        break
    # get sources separately for display
    source_docs = retriever.invoke(query)
    answer = rag_chain.invoke(query)
    print("\nAnswer:", answer)
    print("\nSources:")
    for doc in source_docs:
        print(" -", doc.metadata.get("source"))
    print()