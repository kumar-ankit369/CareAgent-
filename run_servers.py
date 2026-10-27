import subprocess
import sys
import os
import time

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    frontend_dir = os.path.join(root_dir, "frontend")

    print("=" * 60)
    print("  CareAgent — Agentic AI Hospital Platform")
    print("=" * 60)
    print("[1/2] Starting FastAPI Backend on http://localhost:8000 ...")

    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--port", "8000", "--reload"],
        cwd=root_dir
    )

    time.sleep(2)

    print("[2/2] Starting Frontend Portal on http://localhost:3000 ...")
    vite_bin = os.path.join(frontend_dir, "node_modules", "vite", "bin", "vite.js")
    frontend_proc = subprocess.Popen(
        ["node", vite_bin, "--port", "3000"],
        cwd=frontend_dir
    )

    print("\n" + "=" * 60)
    print("  Platform Ready!")
    print("  • Web UI:      http://localhost:3000")
    print("  • API Docs:    http://localhost:8000/docs")
    print("=" * 60 + "\n")

    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        backend_proc.terminate()
        frontend_proc.terminate()

if __name__ == "__main__":
    main()
