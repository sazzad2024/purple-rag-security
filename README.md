# Compliance RAG & Red Teaming Suite

## 📖 Overview
This project demonstrates a secure **Compliance RAG (Retrieval Augmented Generation)** system and a corresponding **Red Team Toolkit** to audit it for Indirect Prompt Injection vulnerabilities.

### 🔄 Attack & Defense Pipeline
```mermaid
graph TD
    subgraph "Attacker Zone (Red Team)"
        A[Dolphin LLM<br/>(Localhost:1234)] -->|Generates| B(Malicious Payload)
        B -->|Injects Invisible Text| C[Poisoned PDF]
    end

    subgraph "Ingestion Pipeline"
        C -->|OCR & Chunking| D[Ingest Service]
        D -->|Embeddings| E[(Pinecone Vector DB)]
        E -.->|Infected Chunk Stored| E
    end

    subgraph "Defense Zone (Blue Team)"
        F(User Query) -->|Retrieval| E
        E -->|Retrieved Chunks| G{LLM Guard<br/>Firewall}
        G -->|❌ BLOCK| H[Security Alert Log]
        G -->|✅ PASS| I[Victim LLM]
    end

    style G fill:#ff9900,stroke:#333,stroke-width:2px
    style A fill:#ff4d4d,stroke:#333,stroke-width:2px
    style E fill:#00ccff,stroke:#333,stroke-width:2px
```

## 📂 Structure
*   `compliance_rag_app/`: The victim application (LangChain, Pinecone, Google Gemini).
*   `security_audit_tools/`: Offensive tools (Fuzzer, Payload Generator, Supply Chain Scanner).
*   `docs/`: Security audit reports and implementation plans.

## 🛠️ Setup

### 1. Compliance App
```bash
cd compliance_rag_app
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys
python app.py
```

### 2. Security Tools
```bash
cd security_audit_tools
# Requires LM Studio running on localhost:1234
python compliance_fuzzer.py
python scan_models.py
```

## 🛡️ Security Architecture (Key Features)

This project implements a **Defense-in-Depth** strategy using industry-standard tools:

### 1. Active Defense: `llm-guard`
We utilize `llm-guard` by ProtectAI to sanitize both Inputs (RAG Retrieval) and Outputs.
*   **Role**: Acts as a firewall for the LLM.
*   **Implementation**: `rag_core.py` -> `secure_context_retrieval()`
*   ** Capabilities**:
    *   **Prompt Injection Detection**: Scans retrieved chunks for "Jailbreak" patterns (e.g., "Ignore previous instructions").
    *   **Ban Substrings**: Blocks specific blacklisted keywords or phrases.
    *   **Anonymization**: Can mask PII (Personally Identifiable Information) before it hits the LLM.

### 2. Supply Chain Security: `modelaudit`
We use `modelaudit` to verify the integrity of the local AI models (GGUF/Pickle files).
*   **Role**: Prevents "Model Serialization Attacks" where malicious code is hidden inside model weights.
*   **Implementation**: `scan_models.py`
*   **Capabilities**:
    *   **Vulnerability Scanning**: Checks for known CVEs in model dependencies.
    *   **Integrity Verification**: Calculates SHA256 hashes to verify the model hasn't been tampered with.
    *   **Malware Detection**: Scans for dangerous pickle operators (e.g., `os.system`).
