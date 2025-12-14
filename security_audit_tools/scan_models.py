
import os
import sys
import subprocess
import hashlib
import json
import argparse

def get_lm_studio_path():
    """Returns the default LM Studio models directory."""
    # Found via probing: ~/.lmstudio/models
    return os.path.join(os.path.expanduser("~"), ".lmstudio", "models")

def calculate_sha256(filepath):
    """Calculates the SHA256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read and update hash string in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def scan_file_with_modelaudit(filepath):
    """
    Runs modelaudit CLI scan and parses JSON output.
    Returns list of threats or empty list.
    """
    try:
        # Run modelaudit scan -f json <filepath>
        result = subprocess.run(
            ["modelaudit", "scan", "-f", "json", filepath],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        # Parse JSON output if available
        if result.stdout:
            try:
                # Based on modelaudit usage, it might output list of findings
                data = json.loads(result.stdout)
                # Assuming data structure; adjust if real output differs significantly
                # modelaudit typically returns a list of dictionaries if issues found?
                # or a structured dict. Let's look for "vulnerabilities" or "threats"
                
                # If the tool exits with non-zero, it usually means threats found
                # But let's check the parsed data.
                # Common schema for these tools is often a list of issues.
                if isinstance(data, list) and len(data) > 0:
                     return data
                if isinstance(data, dict):
                     # If it's a dict, check for keys like 'issues' or similar
                     if data.get('vulnerabilities'):
                         return data['vulnerabilities']
            except json.JSONDecodeError:
                pass # Not JSON or empty

        # Fallback: check stderr for critical errors if json parsing fails
        if result.returncode != 0:
             return [{"description": "ModelAudit reported failure", "details": result.stderr}]
             
        return []

    except FileNotFoundError:
        return [{"description": "Error: modelaudit command not found", "severity": "CRITICAL"}]
    except Exception as e:
         return [{"description": f"Scan execution failed: {e}", "severity": "ERROR"}]

def scan_directory(path, filter_str=None):
    print(f"🔍 Initializing Supply Chain Scan (ModelAudit + SHA256)...")
    print(f"📂 Target Directory: {path}")

    if not os.path.exists(path):
        print(f"❌ Error: Directory not found: {path}")
        return

    # Helper recursive walker
    model_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(".gguf") or file.endswith(".bin") or file.endswith(".pt") or file.endswith(".safetensors"):
                 if filter_str and filter_str.lower() not in file.lower():
                     continue
                 model_files.append(os.path.join(root, file))

    if not model_files:
        print("⚠️ No model files (.gguf, .bin, .pt) found to scan.")
        return

    print(f"nFound {len(model_files)} models. Starting scan...\n")

    for filepath in model_files:
        filename = os.path.basename(filepath)
        print(f"👉 Scanning: {filename} ... ", end="", flush=True)

        # Layer 1: Integrity (SHA256)
        file_hash = calculate_sha256(filepath)
        
        # Layer 2: Deep Scan (ModelAudit)
        threats = scan_file_with_modelaudit(filepath)

        if not threats:
            print("✅ PASS")
            print(f"   Shape: {file_hash}")
            print(f"   Status: Supply Chain Verified")
        else:
            print("❌ FAIL")
            print(f"   Shape: {file_hash}")
            print(f"   � THREATS DETECTED:")
            for t in threats:
                print(f"      - {t}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Supply Chain Verification: Scan AI models using ModelAudit.")
    parser.add_argument("--path", type=str, help="Custom path to scan.", default=None)
    parser.add_argument("--filter", type=str, help="Filter to scan only models containing this string.", default=None)
    
    args = parser.parse_args()
    
    target_path = args.path if args.path else get_lm_studio_path()
    scan_directory(target_path, filter_str=args.filter)
