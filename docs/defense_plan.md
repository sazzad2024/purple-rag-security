# LLM Guard Integration Plan

## Goal Description
Build a defense mechanism against Indirect Prompt Injection by scanning retrieved RAG chunks before they reach the LLM.

## User Review Required
> [!IMPORTANT]
> This introduces a new dependency `llm-guard`. The scanning process may add latency to the retrieval pipeline.

## Proposed Changes

### [MODIFY] [rag_core.py](file:///c:/Users/aalam23/Documents/My%20Code/airedteaming/multi-framework-compliance-assistant/rag_core.py)
*   **Import**: `llm_guard.input_scanners` (PromptInjection, BanSubstrings).
*   **New Function**: `secure_context_retrieval(chunks)`.
    *   Initialize scanners.
    *   Iterate through chunks.
    *   Scan text content.
    *   Logic: `scan().valid` ? keep : discard.
*   **Update**: `query_compliance_logic`.
    *   Call `secure_context_retrieval` after `vector_store.similarity_search`.
    *   Use the filtered list for context construction.

## Verification Plan
### Automated Tests
*   Run `red_team_tools/compliance_fuzzer.py`.
*   **Expected Result**:
    *   The retrieval step finds the poisoned chunk.
    *   **BUT** the new scanner blocks it (prints `[SECURITY ALERT]`).
    *   The LLM answers "I don't have enough information" (or uses remaining chunks), effectively neutralizing the attack.
