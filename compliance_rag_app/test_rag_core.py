from rag_core import query_compliance_logic

print("🧪 Testing rag_core directly...")
try:
    result = query_compliance_logic("What are the 5 functions?")
    print("\n✅ Success! Result snippet:")
    print(result['answer'][:200])
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
