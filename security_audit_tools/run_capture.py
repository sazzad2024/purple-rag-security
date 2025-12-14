
import sys
import subprocess
import os

def run_captured():
    print("🚀 Running compliance_fuzzer.py with output capture...")
    
    # Define paths
    fuzzer_script = os.path.join(os.path.dirname(__file__), "compliance_fuzzer.py")
    output_file = os.path.join(os.path.dirname(__file__), "captured_log.txt")
    
    # Prepare environment
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    # Run process
    with open(output_file, "w", encoding="utf-8") as f:
        process = subprocess.Popen(
            [sys.executable, fuzzer_script],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",  # Force UTF-8 reading
            env=env # Pass environment
        )
        
        # Stream output to file and console
        for line in process.stdout:
            print(line, end="")
            f.write(line)
            f.flush()
            
        return_code = process.wait()
        print(f"\n✅ Finished with exit code: {return_code}")
        print(f"📄 Output saved to: {output_file}")

if __name__ == "__main__":
    run_captured()
