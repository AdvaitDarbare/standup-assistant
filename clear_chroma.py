# clear_chroma.py
from chromadb import PersistentClient

# Connect to Chroma
chroma = PersistentClient(path="chroma_data")
collection = chroma.get_or_create_collection("standup_memory")

# Get all IDs
all_ids = collection.get()["ids"]

# Delete all by ID
if all_ids:
    collection.delete(ids=all_ids)
    print(f"✅ Cleared {len(all_ids)} entries from ChromaDB.")
else:
    print("ℹ️ ChromaDB is already empty.")