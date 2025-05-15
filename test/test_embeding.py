from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

with open("duolingo_grammar.txt", "r", encoding="utf-8") as file:
    english_text = file.read()

splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
docs = splitter.create_documents([english_text])

if not docs:
    print("⚠️ Không có tài liệu nào để xử lý.")
    exit()

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

sample_embedding = embedding_model.embed_documents([doc.page_content for doc in docs])
print(f"✅ Số lượng embedding: {len(sample_embedding)}")

vector_db = Chroma.from_documents(
    documents=docs,
    embedding=embedding_model,
    persist_directory="./chroma_english_learning"
)

vector_db.persist()
print("✅ Embedding đã lưu thành công!")
