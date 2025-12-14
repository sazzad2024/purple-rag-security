import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_guard.input_scanners import PromptInjection, BanSubstrings

# Load environment variables
load_dotenv()

# FIX: Disable Symlinks for Windows
os.environ["HF_HUB_DISABLE_SYMLINKS"] = "1"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "compliance-rag")

if not GOOGLE_API_KEY or not PINECONE_API_KEY:
    raise ValueError("Please set GOOGLE_API_KEY and PINECONE_API_KEY in .env file")

# Initialize Components (Global)
print("[*] Connecting to Pinecone...")
pc = Pinecone(api_key=PINECONE_API_KEY)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vector_store = PineconeVectorStore(index_name=INDEX_NAME, embedding=embeddings)

print("[*] Initializing Gemini...")
llm = ChatGoogleGenerativeAI(model="gemini-3-pro-preview", temperature=0)

def secure_context_retrieval(chunks):
    """
    Scans retrieved chunks for prompt injection and banned substrings.
    """
    # Initialize Scanners
    scanner_injection = PromptInjection()
    scanner_substrings = BanSubstrings(substrings=["System Override", "Ignore previous instructions", "IGNORE ALL PREVIOUS INSTRUCTIONS"])
    
    safe_chunks = []
    
    print(f"🛡️ Scanning {len(chunks)} chunks with LLM Guard...")
    
    for chunk in chunks:
        text = chunk.page_content
        is_safe = True
        
        # Scan 1: Prompt Injection
        sanitized_text, valid, score = scanner_injection.scan(text)
        if not valid:
             print(f"[SECURITY ALERT] Prompt Injection detected in chunk! Score: {score}")
             is_safe = False
             
        # Scan 2: Banned Substrings
        sanitized_text, valid, score = scanner_substrings.scan(text)
        if not valid:
             print(f"[SECURITY ALERT] Banned substring detected in chunk!")
             is_safe = False
             
        if is_safe:
            safe_chunks.append(chunk)
        else:
             print(f"[!] BLOCKED MALICIOUS CHUNK: {text[:200]}...")
             
    print(f"[+] {len(safe_chunks)} chunks passed security check.")
    return safe_chunks

def query_compliance_logic(query: str, namespace: str = "production") -> dict:
    """
    Core logic to query NIST CSF and return formatted answer with evidence.
    Returns a dictionary: {"answer": str, "evidence": list}
    """
    print(f"🔍 Processing query: {query}")
    
    # A. Retrieve Context
    # Increased k to 15 to capture long lists (like CIS Controls 1-18)
    docs = vector_store.similarity_search(query, k=15, namespace=namespace)
    
    # SECURITY: Filter chunks through LLM Guard
    docs = secure_context_retrieval(docs)
    
    # B. Format Context & Collect Evidence
    context_text = ""
    evidence_list = []
    
    print(f"📚 Retrieved {len(docs)} chunks from Pinecone:")
    for i, doc in enumerate(docs):
        # Log to terminal (Under the hood view)
        source = doc.metadata.get('source', 'NIST CSF')
        page = doc.metadata.get('page', '?')
        snippet = doc.page_content[:100].replace('\n', ' ')
        print(f"   [{i+1}] Page {page} | {snippet}...")

    for i, doc in enumerate(docs):
        # Use document name in the header so LLM cites it correctly
        source_name = doc.metadata.get('source', 'NIST CSF')
        raw_page = doc.metadata.get('page', '?')
        
        # Clean up page number (remove .0 if present)
        # Logic: Convert to float -> int -> str to remove decimals, unless it's a string like "Front-1"
        try:
            page_num = str(int(float(raw_page)))
        except ValueError:
            page_num = str(raw_page)
        
        context_text += f"\n--- Document: {source_name} - Page {page_num} ---\n"
        context_text += doc.page_content
        
        evidence_list.append({
            "source": source_name,
            "page": page_num,
            "type": doc.metadata.get("type", "text"),
            "content_snippet": doc.page_content[:200] + "..."
        })

    # C. Generate Answer
    template = """
    You are a Senior Compliance Consultant specializing in NIST CSF v2.0 and CIS Controls v8.
    Your goal is to provide clear, coherent, and actionable advice based *only* on the provided context.

    Guidelines:
    1. **Synthesize, Don't Just List**: Combine information from multiple sources into a cohesive narrative.
    2. **Structure Your Answer**: Use Markdown headers (###), bullet points, and bold text for readability.
    3. **Cite Your Sources**: When making a claim, reference the specific Document and Control/Function (e.g., "According to **NIST CSF (ID.AM)**..." or "**CIS Control 5** states...").
       - ⛔ DO NOT use generic terms like "(Source 1)" or "(Source 12)".
       - ✅ ALWAYS use the document name provided in the context header.
    4. **Be Honest**: If the context doesn't contain the answer, say "I don't have enough information in the provided documents."

    Context:
    {context}
    
    Question: {question}
    
    Answer:
    """
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()
    
    answer = chain.invoke({"context": context_text, "question": query})
    
    # D. Return Structured Output
    return {
        "answer": answer,
        "evidence": evidence_list
    }
