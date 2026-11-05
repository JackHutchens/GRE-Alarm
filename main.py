"""
Launcher for GRE Torture Alarm Application.

Starts the local REST backend server and opens the modern dark mode GUI
in the default browser.
"""

import sys
import time
import webbrowser
import threading
from app.server import run_server

HOST = "127.0.0.1"
PORT = 8765
URL = f"http://{HOST}:{PORT}/"

def open_browser():
    time.sleep(0.6)
    print(f"\n[LAUNCH] Opening GRE Torture Alarm GUI at {URL}...")
    webbrowser.open(URL)

def main():
    print("=" * 70)
    print("  GRE TORTURE ALARM - PROTOTYPE APPLICATION")
    print("  Real-Time Procedural Psychoacoustic Synthesis & GRE Training")
    print("=" * 70)
    print(f"[*] Starting local server on http://{HOST}:{PORT}...")
    
    # Launch browser in a background thread
    threading.Thread(target=open_browser, daemon=True).start()

    # Run HTTP server
    server = run_server(host=HOST, port=PORT)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down GRE Torture Alarm. Sleep well (if you dare).")
        server.server_close()

if __name__ == "__main__":
    main()
