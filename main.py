import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from sentence_transformers import CrossEncoder

from src.load_docs import load_repo_files
from src.vectorstore import build_parent_retriever

load_dotenv()

print("Loading files...")
docs = load_repo_files("data/repo/OOP Project Social Network Application")
print(f"Loaded {len(docs)} files")

print("Building parent-document retriever...")
retriever = build_parent_retriever(docs)   # note: no separate chunk_docs() call anymore

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def format_docs(docs):
    return "\n\n".join(
        f"[{doc.metadata.get('source')}]\n{doc.page_content}" for doc in docs
    )

def rerank(query, docs, top_k=4):
    if not docs:
        return docs
    pairs = [(query, d.page_content) for d in docs]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
    return [d for d, s in ranked[:top_k]]

prompt = ChatPromptTemplate.from_template("""
Answer the question using ONLY the following code context. Be precise about behavior
(e.g. whether arrays are resizable or fixed-size, or which functions exist) — do not
infer capabilities not shown in the code. If something isn't shown in the context,
say so explicitly rather than guessing.

{context}

Question: {question}
""")

def answer_question(query):
    # retrieve broadly at the parent level first
    candidates = retriever.invoke(query)
    # rerank to pick the most relevant parent chunks
    top_docs = rerank(query, candidates, top_k=4)
    context = format_docs(top_docs)
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": context, "question": query})
    return answer, top_docs

print("\nReady! Ask questions about the repo (type 'quit' to exit)\n")

while True:
    query = input("Question: ")
    if query.lower() == "quit":
        break
    answer, sources = answer_question(query)
    print("\nAnswer:", answer)
    print("\nSources:")
    for doc in sources:
        print(" -", doc.metadata.get("source"))
    print()