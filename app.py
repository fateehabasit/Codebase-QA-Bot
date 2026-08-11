import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from sentence_transformers import CrossEncoder
import gradio as gr

from src.load_docs import load_repo_files
from src.vectorstore import build_parent_retriever

load_dotenv()

print("Loading files...")
docs = load_repo_files("data/repo/OOP Project Social Network Application")
print(f"Loaded {len(docs)} files")

print("Building parent-document retriever...")
retriever = build_parent_retriever(docs)

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("GROQ_API_KEY")
)

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

prompt = ChatPromptTemplate.from_template("""
Answer the question using ONLY the following code context. Be precise about behavior
(e.g. whether arrays are resizable or fixed-size, or which functions exist) — do not
infer capabilities not shown in the code. If something isn't shown in the context,
say so explicitly rather than guessing.

{context}

Question: {question}
""")

chain = prompt | llm | StrOutputParser()

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

def answer_question(query, history=None):
    if not query.strip():
        return "Please enter a question.", ""
    candidates = retriever.invoke(query)
    top_docs = rerank(query, candidates, top_k=4)
    context = format_docs(top_docs)
    answer = chain.invoke({"context": context, "question": query})
    sources = "\n".join(f"- {d.metadata.get('source')}" for d in top_docs)
    return answer, sources

with gr.Blocks(title="Codebase Q&A Bot") as demo:
    gr.Markdown("# Codebase Q&A Bot")
    gr.Markdown(
        "Ask questions about the **OOP Social Network Application** (C++/SFML) codebase. "
        "Answers are grounded in the actual source code using RAG (retrieval-augmented generation)."
    )

    with gr.Row():
        query_box = gr.Textbox(
            label="Your question",
            placeholder="e.g. How is a new user added to the network?",
            lines=2
        )

    ask_btn = gr.Button("Ask", variant="primary")

    answer_box = gr.Textbox(label="Answer", lines=10)
    sources_box = gr.Textbox(label="Sources", lines=4)

    ask_btn.click(fn=answer_question, inputs=query_box, outputs=[answer_box, sources_box])
    query_box.submit(fn=answer_question, inputs=query_box, outputs=[answer_box, sources_box])

    gr.Examples(
        examples=[
            "How is a new user added to the network?",
            "How does the SFML GUI get set up and rendered?",
            "How are user friends handled?",
            "What data structure stores likes and comments?",
        ],
        inputs=query_box
    )

if __name__ == "__main__":
    demo.launch()