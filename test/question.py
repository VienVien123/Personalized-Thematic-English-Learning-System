from langchain_community.vectorstores import Chroma
from langchain.embeddings import HuggingFaceEmbeddings
import google.generativeai as genai
import os

# Cấu hình Gemini
genai.configure(api_key="AIzaSyBg2npP92SnJRQwMSQAII_bPYeFyGh4ZCw")
model = genai.GenerativeModel("gemini-1.5-flash")

# Load embedding model giống lúc tạo
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load lại Chroma vector DB đã persist
persist_path = "./chroma_english_learning"
vector_db = Chroma(persist_directory=persist_path, embedding_function=embedding_model)

# Truy vấn mẫu
query = "How do I describe my hobbies?"
retrieved_docs = vector_db.similarity_search(query, k=4)
context = "\n".join([doc.page_content for doc in retrieved_docs])

# RAG prompt
prompt = f"""
You are an English learning assistant.
Use the following context to answer the user's question clearly and simply.

Context:
{context}

Question: {query}

Answer:
"""

# Gửi vào Gemini
response = model.generate_content(prompt)
print("💬 Gemini Answer:\n", response.text)
