#!/usr/bin/env python3
"""Servidor HTTP para o dashboard BUENOSERV — serve index.html + API /api/state"""
import http.server
import json
import os
import sys

DASHBOARD_DIR = os.path.expanduser("~/.config/opencode/dashboard")
STATE_FILE = os.path.expanduser("~/.config/opencode/state/agent_state.json")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/state":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            try:
                with open(STATE_FILE) as f:
                    self.wfile.write(f.read().encode())
            except FileNotFoundError:
                self.wfile.write(json.dumps({"error": "state not found"}).encode())
            return
        elif self.path == "/" or self.path == "/index.html":
            self.path = "/index.html"
        return super().do_GET()

    def translate_path(self, path):
        path = super().translate_path(path)
        rel = os.path.relpath(path, os.getcwd())
        return os.path.join(DASHBOARD_DIR, os.path.basename(path))

if __name__ == "__main__":
    os.chdir(DASHBOARD_DIR)
    server = http.server.HTTPServer(("0.0.0.0", PORT), DashboardHandler)
    print(f"📊 Dashboard BUENOSERV -> http://localhost:{PORT}")
    print(f"   Pressione Ctrl+C para parar")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado")
        server.server_close()
