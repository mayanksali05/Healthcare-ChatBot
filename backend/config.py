import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# MongoDB. Never hardcode a URI that carries credentials - keep it in the
# environment (and in a secret store for anything beyond local development).
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")

MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "healthcare_chatbot")