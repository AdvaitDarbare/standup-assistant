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

def query_standup(question, top_k=3):
    query_embedding = embedder.encode(question).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    return results['documents'][0] if results['documents'] else []

if __name__ == "__main__":
    while True:
        q = input("🔎 Ask a standup-related question (or 'exit'): ")
        if q.lower() == "exit":
            break
        matches = query_standup(q)
        print("\nTop Matches:")
        for match in matches:
            print("—", match)
        print()