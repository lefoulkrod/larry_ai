import os
import socketserver
from .proxy_server import ProxyHandler, PORT

def start_server():
    with socketserver.ThreadingTCPServer(('', PORT), ProxyHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
            httpd.shutdown()
            httpd.server_close()
