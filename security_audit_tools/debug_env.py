import os
from dotenv import load_dotenv

env_path = os.path.abspath(os.path.join(os.getcwd(), '..', 'multi-framework-compliance-assistant', '.env'))
print(f"Expected env path: {env_path}")
print(f"Exists: {os.path.exists(env_path)}")

success = load_dotenv(env_path)
print(f"Load dotenv success: {success}")

print(f"GOOGLE_API_KEY set: {bool(os.getenv('GOOGLE_API_KEY'))}")
print(f"PINECONE_API_KEY set: {bool(os.getenv('PINECONE_API_KEY'))}")
