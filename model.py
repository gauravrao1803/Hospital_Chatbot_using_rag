import os
import torch
from dotenv import load_dotenv

from langchain_huggingface import HuggingFacePipeline, HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

llm = None
vectorstore = None
small_talk = [
    "hello", "hi", "hey",
    "how are you",
    "who are you",
    "what is your name",
    "thanks", "thank you",
    "good morning", "good evening"
]

# -------------------------
# SAFE LOADER FUNCTION
# -------------------------

def load_model():
    global llm, vectorstore

    if llm is not None:
        return  # Already loaded

    print("Loading RAG Model Safely...")

    device = 0 if torch.cuda.is_available() else -1

    llm_local = HuggingFacePipeline.from_model_id(
        model_id="google/flan-t5-base",
        task="text2text-generation",
        device=device,
        pipeline_kwargs={
            "max_new_tokens": 150,
            "temperature": 0.0
        }
    )

    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/multi-qa-mpnet-base-dot-v1"
    )

    pdf_path = "BHMRC Hospital Data.pdf"

    if not os.path.exists(pdf_path):
        raise FileNotFoundError("PDF not found!")

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(documents)

    vectorstore_local = FAISS.from_documents(chunks, embedding_model)

    llm = llm_local
    vectorstore = vectorstore_local

    print("Model Loaded Successfully ✅")


# -------------------------
# ASK FUNCTION
# -------------------------

def ask_question(query: str):

    # Load model only when needed
    load_model()

    q_lower = query.lower()

    if any(phrase in q_lower for phrase in small_talk):
        prompt = f"Answer briefly:\n\nQuestion: {query}\n\nAnswer:"
        return str(llm.invoke(prompt)).strip()

    docs = vectorstore.similarity_search(query, k=3)

    if not docs:
        return "Sorry, I couldn’t find that in the hospital information."

    context = "\n".join([d.page_content for d in docs])

    prompt = f"""
Answer ONLY using this hospital data:

{context}

Question: {query}

Answer:
"""

    return str(llm.invoke(prompt)).strip()