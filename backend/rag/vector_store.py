import os
import chromadb

# Absolute path to chroma database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHROMA_PATH = os.path.join(BASE_DIR, "database", "chroma_db")

# Create Chroma client
client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

# Create collection
collection = client.get_or_create_collection(
    name="health_knowledge"
)