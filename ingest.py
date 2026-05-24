import os
import chromadb
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()

client = chromadb.PersistentClient(path="./db")
collection = client.get_or_create_collection(name="nepal_laws")


def load_pdfs(docs_folder="./docs"):
    texts = []
    for filename in os.listdir(docs_folder):
        if filename.endswith(".pdf"):
            print(f"Reading {filename}...")
            reader = PdfReader(os.path.join(docs_folder, filename))
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text and len(text.strip()) > 50:
                    texts.append({
                        "text": text,
                        "source": filename,
                        "page": i + 1
                    })
    return texts


def ingest():
    texts = load_pdfs()
    print(f"Total pages loaded: {len(texts)}")

    for i, item in enumerate(texts):
        collection.add(
            documents=[item["text"]],
            metadatas=[{"source": item["source"], "page": item["page"]}],
            ids=[f"doc_{i}"]
        )
    print("✅ All documents stored in ChromaDB!")


if __name__ == "__main__":
    ingest()