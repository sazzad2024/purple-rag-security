
import ollama
import sys

model_name = "dolphin-llama3"

print(f"🚀 Attempting to pull '{model_name}' via Ollama API...")
try:
    # Check if we can connect first
    print("📡 Checking connection to Ollama service...")
    ollama.list()
    print("✅ Connection established!")

    print(f"⬇️ Pulling model: {model_name} (This may take a while)...")
    # stream=True allows us to see progress if we iterated, but for simplicity here we just wait
    progress = ollama.pull(model_name, stream=True)
    
    for p in progress:
        status = p.get('status', '')
        if 'downloading' in status and 'total' in p:
             percent = (p.get('completed', 0) / p.get('total', 1)) * 100
             print(f"\r{status}: {percent:.1f}%", end="")
        else:
             print(f"\n{status}")

    print(f"\n✅ Successfully pulled {model_name}!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    print("Ensure Ollama is running (tray icon) even if the CLI command doesn't work.")
    sys.exit(1)
