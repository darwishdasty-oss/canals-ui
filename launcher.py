"""
Hydraulic Design Studio — Windows launcher.

Starts the Streamlit server in a background thread, waits for it to come up,
and then opens a NATIVE WINDOW via pywebview pointed at the local server.

When bundled with PyInstaller, this becomes a single .exe that opens its
own desktop window — no browser, no console.

Usage (after build):
    HydraulicStudio.exe

Usage (from source, dev):
    python launcher.py
"""
import os
import sys
import socket
import threading
import time
import webbrowser
import logging
from pathlib import Path

# Quiet down Streamlit's verbose logging in the window
logging.getLogger("streamlit").setLevel(logging.ERROR)
logging.getLogger("tornado").setLevel(logging.ERROR)
logging.getLogger("asyncio").setLevel(logging.ERROR)

# ----- Locate bundled data when frozen with PyInstaller -------------------
def app_dir() -> Path:
    """Return the directory containing our bundled files."""
    if getattr(sys, "frozen", False):
        # PyInstaller: files live in sys._MEIPASS (onefile) or next to .exe
        base = Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
        return base
    return Path(__file__).parent.resolve()


HERE = app_dir()
APP_FILE = HERE / "app.py"


# ----- Pick a free port for the Streamlit server -------------------------
def find_free_port(preferred: int = 8501) -> int:
    for port in (preferred, 8502, 8503, 8504, 0):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return s.getsockname()[1]
            except OSError:
                continue
    return 0


# ----- Run the Streamlit server in a background thread -------------------
def start_streamlit(port: int) -> threading.Thread:
    """Spawn streamlit in this process (so it shares the .exe memory)."""
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    os.environ["STREAMLIT_GLOBAL_SUPPRESS_DEPRECATION_WARNINGS"] = "true"
    os.environ["STREAMLIT_LOG_LEVEL"] = "error"
    os.environ["STREAMLIT_THEME_BASE"] = "dark"

    from streamlit.web import cli as stcli  # noqa: E402
    from streamlit.runtime.scriptrunner import add_script_run_ctx  # noqa: E402

    sys.argv = [
        "streamlit", "run", str(APP_FILE),
        "--server.headless", "true",
        "--server.port", str(port),
        "--server.address", "127.0.0.1",
        "--browser.gatherUsageStats", "false",
        "--global.suppressDeprecationWarnings", "true",
        "--theme.base", "dark",
    ]

    def _run():
        try:
            stcli.main()
        except SystemExit:
            pass
        except Exception as e:  # pragma: no cover
            print(f"Streamlit exited: {e}", file=sys.stderr)

    t = threading.Thread(target=_run, daemon=True, name="streamlit-server")
    t.start()
    return t


def wait_for_server(port: int, timeout: float = 25.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.25)
    return False


# ----- Open the native window via pywebview -------------------------------
def open_window(url: str, title: str = "Hydraulic Design Studio"):
    """Open a real native window.  Uses Edge WebView2 on Windows."""
    try:
        import webview
    except ImportError:
        # pywebview missing → fall back to the user's browser
        webbrowser.open(url)
        return

    window_kwargs = dict(
        title=title,
        url=url,
        width=1440,
        height=900,
        min_size=(1024, 700),
        resizable=True,
        background_color="#0e1014",
        text_select=True,
    )

    # On Windows, use Edge Chromium backend
    if sys.platform.startswith("win"):
        try:
            window_kwargs["gui"] = "edgechromium"
        except Exception:
            pass

    webview.start()
    webview.create_window(**window_kwargs)


# ----- Entry point --------------------------------------------------------
def main():
    # Friendly ASCII banner to the console (visible if run from cmd)
    print("=" * 60)
    print("  Hydraulic Design Studio")
    print("  Starting local server…")
    print("=" * 60)

    if not APP_FILE.exists():
        print(f"!! app.py not found at {APP_FILE}", file=sys.stderr)
        if getattr(sys, "frozen", False):
            input("Press Enter to exit…")
        sys.exit(1)

    port = find_free_port()
    if port == 0:
        print("!! No free port found", file=sys.stderr)
        sys.exit(1)

    t = start_streamlit(port)

    if not wait_for_server(port, timeout=25):
        print("!! Streamlit failed to start in time", file=sys.stderr)
        sys.exit(1)

    url = f"http://127.0.0.1:{port}"
    print(f"  Server: {url}")
    print("  Opening window…")
    open_window(url)

    # When the window closes, exit the process
    print("  Window closed — shutting down.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Fatal: {e}", file=sys.stderr)
        if getattr(sys, "frozen", False):
            input("Press Enter to exit…")
        raise
