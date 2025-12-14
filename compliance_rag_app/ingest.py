import os
import time
from dotenv import load_dotenv
from docling.document_converter import DocumentConverter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec
from langchain_core.documents import Document

# Load environment variables
load_dotenv()

# FIX: Disable Symlinks for Windows (avoids WinError 1314)
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "compliance-rag")

if not GOOGLE_API_KEY or not PINECONE_API_KEY:
    raise ValueError("Please set GOOGLE_API_KEY and PINECONE_API_KEY in .env file")

def ingest_data(namespace="production", docs_to_ingest=None):
    print("🚀 Starting Ingestion Process...")
    
    # Define documents to ingest with their specific configs
    # Offset: Number of pages to subtract to match printed page numbers
    if docs_to_ingest is None:
        docs_to_ingest = [
            {"file": "nist_csf_2.0.pdf", "source": "NIST CSF 2.0", "offset": 5},
            {"file": "CIS_Controls_v8_Guide.pdf", "source": "CIS Controls v8", "offset": 12},
            {"file": "hipaa.pdf", "source": "HIPAA Security Rule", "offset": 0}, # Adjust offset if needed
            {"file": "PCI-DSS-v4_0_1.pdf", "source": "PCI DSS v4.0.1", "offset": 0} # Adjust offset if needed
        ]

    documents = []

    for doc_config in docs_to_ingest:
        file_path = doc_config["file"]
        source_name = doc_config["source"]
        offset = doc_config["offset"]

        if not os.path.exists(file_path):
            print(f"⚠️ Warning: File {file_path} not found. Skipping.")
            continue

        print(f"📄 Parsing {source_name} ({file_path}) with Docling...")
        converter = DocumentConverter()
        try:
            result = converter.convert(file_path)
            doc = result.document
        except Exception as e:
            print(f"[-] Error parsing {file_path}: {e}")
            continue
        
        print(f"[+] Creating chunks for {source_name}...")
        
        # Iterate over texts
        for item in doc.texts:
            text = item.text.strip()
            if len(text) < 50: # Skip very short snippets
                continue
                
            # Create metadata
            # FIX: Adjust page number based on document offset
            raw_page = int(item.prov[0].page_no) if item.prov else 0
            adjusted_page = raw_page - offset if raw_page > offset else f"Front-{raw_page}"

            metadata = {
                "source": source_name,
                "page": adjusted_page,
                "type": "text",
                # We can add bounding box info here if needed for "snapshots"
                # "bbox": str(item.prov[0].bbox) if item.prov else "" 
            }
            
            documents.append(Document(page_content=text, metadata=metadata))

        # Iterate over tables
        for table in doc.tables:
            # Convert table to markdown or CSV format for embedding
            table_text = table.export_to_markdown()
            
            # FIX: Adjust page number for tables too
            raw_page = int(table.prov[0].page_no) if table.prov else 0
            adjusted_page = raw_page - offset if raw_page > offset else f"Front-{raw_page}"

            metadata = {
                "source": source_name,
                "page": adjusted_page,
                "type": "table"
            }
            documents.append(Document(page_content=table_text, metadata=metadata))

    print(f"[+] Created {len(documents)} total chunks from all documents.")

    # 3. Initialize Embeddings
    print("🧠 Initializing Gemini Embeddings...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # 4. Initialize Pinecone
    print("[*] Initializing Pinecone...")
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    # Check if index exists, if not create it
    existing_indexes = [i.name for i in pc.list_indexes()]
    if INDEX_NAME in existing_indexes:
        print(f"[+] Index '{INDEX_NAME}' already exists.")
        # print(f"🗑️ Deleting existing index '{INDEX_NAME}' to ensure clean slate...")
        # pc.delete_index(INDEX_NAME)
        # time.sleep(5) # Wait for deletion
    else:
        print(f"[*] Creating index '{INDEX_NAME}'...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=768, # Dimension for embedding-001
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        time.sleep(10) # Wait for index to be ready
    
    # 5. Upload to Pinecone
    print("[*] Uploading vectors to Pinecone...")
    vector_store = PineconeVectorStore.from_documents(
        documents=documents,
        embedding=embeddings,
        index_name=INDEX_NAME,
        namespace=namespace
    )
    
    print("[:] Ingestion Complete!")

if __name__ == "__main__":
    ingest_data()
