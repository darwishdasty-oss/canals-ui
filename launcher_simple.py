"""
Simple launcher — fallback that doesn't need pywebview.
Opens the user's default browser to the Streamlit app.
Use this if pywebview is causing issues.
"""
import os
import sys
import socket
import subprocess
import time
import threading
import webbrowser
from pathlib import Path


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).parent.resolve()


HERE = app_dir()
APP_FILE = HERE / "app.py"


def find_free_port(preferred=8501):
    for port in (preferred, 8502, 8503, 8504, 0):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return s.getsockname()[1]
            except OSError:
                continue
    return 0


def main():
    print("=" * 60)
    print("  Hydraulic Design Studio")
    print("=" * 60)

    if not APP_FILE.exists():
        print(f"!! app.py not found at {APP_FILE}")
        if getattr(sys, "frozen", False):
            input("Press Enter to exit…")
        sys.exit(1)

    port = find_free_port()
    if port == 0:
        print("!! No free port found")
        sys.exit(1)

    print(f"  Starting server on port {port}…")

    # Spawn streamlit as a subprocess (cleaner than in-process threading)
    cmd = [
        sys.executable, "-m", "streamlit", "run", str(APP_FILE),
        "--server.headless", "true",
        "--server.port", str(port),
        "--server.address", "127.0.0.1",
        "--browser.gatherUsageStats", "false",
        "--theme.base", "dark",
    ]
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.STDOUT,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))

    # Wait for server
    deadline = time.time() + 25
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                break
        except OSError:
            if proc.poll() is not None:
                print("!! Streamlit exited")
                sys.exit(1)
            time.sleep(0.3)

    url = f"http://127.0.0.1:{port}"
    print(f"  Server: {url}")
    print("  Opening browser…")
    webbrowser.open(url)
    print("  Close the console window or press Ctrl+C to quit.")

    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Fatal: {e}")
        if getattr(sys, "frozen", False):
            input("Press Enter to exit…")
        raise
