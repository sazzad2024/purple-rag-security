import os
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from rag_core import query_compliance_logic

# Load environment variables
load_dotenv()

# 1. Initialize MCP Server
mcp = FastMCP("Compliance RAG")

# 2. Define RAG Tool
@mcp.tool()
def query_compliance(query: str) -> str:
    """
    Query the NIST Cybersecurity Framework (CSF) v2.0.
    Returns an answer based on the official documentation, along with evidence snapshots.
    
    Args:
        query: The user's compliance question (e.g., "What are the categories for Identity Management?").
    """
    response_data = query_compliance_logic(query)
    
    # Format for MCP (Text output)
    final_output = f"{response_data['answer']}\n\n---\n**📚 Evidence Snapshots:**\n"
    for item in response_data['evidence']:
        final_output += f"- **{item['source']} - Page {item['page']}**: \"{item['content_snippet']}\"\n"
        
    return final_output

if __name__ == "__main__":
    print("🚀 MCP Server running...")
    mcp.run()
