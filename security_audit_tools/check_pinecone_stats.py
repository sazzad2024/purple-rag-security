import os
import sys
from pinecone import Pinecone

# Helper to load .env from victim dir
victim_env_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'multi-framework-compliance-assistant', '.env'))
from dotenv import load_dotenv
if os.path.exists(victim_env_path):
    load_dotenv(victim_env_path, override=True)

api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME", "compliance-rag")

if not api_key:
    print("❌ Any API KEY found.")
    sys.exit(1)

pc = Pinecone(api_key=api_key)
index = pc.Index(index_name)

try:
    stats = index.describe_index_stats()
    print(f"Index Name: {index_name}")
    print(f"Total Vectors: {stats.total_vector_count}")
    print("Namespaces:")
    for ns in stats.namespaces:
        print(f" - {ns}: {stats.namespaces[ns].vector_count} vectors")
except Exception as e:
    print(f"Error fetching stats: {e}")
