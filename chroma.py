from chromadb import PersistentClient

# Connect to Chroma
chroma = PersistentClient(path="chroma_data")
collection = chroma.get_or_create_collection("standup_memory")

# Fetch and print all documents
results = collection.get()

print("📦 ChromaDB Contents:")
for doc, doc_id in zip(results['documents'], results['ids']):
    print(f"🧾 ID: {doc_id}\n📄 Content: {doc}\n---")