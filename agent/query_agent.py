import os
from dotenv import load_dotenv
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer

# Load environment
load_dotenv()

# Setup ChromaDB
chroma = PersistentClient(path="chroma_data")
collection = chroma.get_or_create_collection("standup_memory")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def query_standup(question, top_k=5):
    """
    Pure semantic CLI query against all stored standups.
    """
    query_embedding = embedder.encode(question).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    docs = results.get('documents', [[]])[0]
    return docs

if __name__ == "__main__":
    print("🔎 Standup Memory CLI")
    while True:
        q = input("Enter a question (or 'exit'): ")
        if q.lower() == 'exit':
            break
        matches = query_standup(q)
        if not matches:
            print("❌ No relevant updates found.")
        else:
            print("\nTop Matches:")
            for m in matches:
                print("—", m)
        print()