import http.server
import socketserver
import urllib.request
import urllib.error
import sys
from typing import Any

PORT: int = 8080

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP proxy handler for serving chat UI and proxying requests to Ollama."""
    def do_OPTIONS(self) -> None:
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self) -> None:
        """Proxy POST requests for chat to Ollama's /api/generate endpoint."""
        if self.path == '/api/chat':
            content_length: int = int(self.headers.get('Content-Length', 0))
            post_data: bytes = self.rfile.read(content_length)
            req = urllib.request.Request('http://localhost:11434/api/generate', data=post_data, headers={'Content-Type': 'application/json'}, method='POST')
            try:
                with urllib.request.urlopen(req) as resp:
                    self.send_response(resp.status)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Content-Type', resp.headers.get('Content-Type', 'application/json'))
                    self.end_headers()
                    while True:
                        chunk: bytes = resp.read(4096)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
            except urllib.error.HTTPError as e:
                self.send_response(e.code)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(e.read())
        else:
            self.send_error(404)

    def do_GET(self) -> None:
        """Serve the chat UI or proxy model tags to Ollama."""
        if self.path in ['/', '/ollama_chat.html']:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            with open('ollama_chat.html', 'rb') as f:
                self.wfile.write(f.read())
        elif self.path == '/api/tags':
            req = urllib.request.Request('http://localhost:11434/api/tags', method='GET')
            try:
                with urllib.request.urlopen(req) as resp:
                    self.send_response(resp.status)
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Content-Type', resp.headers.get('Content-Type', 'application/json'))
                    self.end_headers()
                    self.wfile.write(resp.read())
            except urllib.error.HTTPError as e:
                self.send_response(e.code)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(e.read())
        else:
            super().do_GET()

    def end_headers(self) -> None:
        """Ensure CORS headers are set for GET requests."""
        if self.command == 'GET':
            self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

if __name__ == '__main__':
    with socketserver.ThreadingTCPServer(('', PORT), ProxyHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
            httpd.shutdown()
            httpd.server_close()
