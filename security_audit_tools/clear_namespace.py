
import os
import sys
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment logic from compliance_fuzzer
victim_env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'multi-framework-compliance-assistant', '.env'))
load_dotenv(victim_env_path, override=True)

if not os.getenv("PINECONE_API_KEY"):
    print("❌ API Key missing")
    sys.exit(1)

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index_name = os.getenv("PINECONE_INDEX_NAME", "compliance-rag")
index = pc.Index(index_name)

try:
    print(f"🧹 Clearing namespace 'red_team_attack' in index '{index_name}'...")
    index.delete(delete_all=True, namespace="red_team_attack")
    print("✅ Namespace cleared.")
except Exception as e:
    print(f"❌ Error: {e}")
