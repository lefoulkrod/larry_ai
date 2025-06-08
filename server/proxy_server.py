import http.server
import socketserver
import urllib.request
import urllib.error
import sys
import asyncio
from typing import Any
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from agents.agent import root_agent
from google.genai import types
import os

PORT: int = 8080

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Instantiate and store an Agent Runner
        session_service = InMemorySessionService()
        self.session = asyncio.run(session_service.create_session(
            app_name="larry_ai_chat_app", 
            user_id="default_user"
        ))
        self.runner = Runner(
            agent=root_agent,  # The agent we want to run
            app_name="larry_ai_chat_app",  # Associates runs with our app
            session_service=session_service  # Uses our session manager
        )
        super().__init__(*args, **kwargs)

    """HTTP proxy handler for serving chat UI and proxying requests to Ollama."""
    def do_OPTIONS(self) -> None:
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self) -> None:
        """Handle POST requests for chat and pass to agent runner."""
        if self.path == '/api/chat':
            content_length: int = int(self.headers.get('Content-Length', 0))
            post_data: bytes = self.rfile.read(content_length)
            import json
            try:
                data = json.loads(post_data.decode('utf-8'))
                user_query = data.get('message') or data.get('query') or ''
            except Exception:
                self.send_response(400)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"error": "Invalid JSON or missing message field."}')
                return
            # Call the agent and get the response
            agent_response = self.handle_agent_chat(user_query, self.session.user_id, self.session.id)
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = json.dumps({"response": agent_response}).encode('utf-8')
            self.wfile.write(response)
        else:
            self.send_error(404)

    def do_GET(self) -> None:
        """Serve the chat UI or proxy model tags to Ollama."""
        if self.path in ['/', '/ollama_chat.html']:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            # Serve ollama_chat.html from the public directory
            html_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'server', 'public', 'ollama_chat.html')
            try:
                with open(html_path, 'rb') as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.wfile.write(b'<h1>ollama_chat.html not found</h1>')
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
        elif self.path.startswith('/public/'):
            # Serve static files from the public directory
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'server', self.path.lstrip('/'))
            if os.path.isfile(file_path):
                self.send_response(200)
                # Basic content type detection
                if file_path.endswith('.css'):
                    self.send_header('Content-Type', 'text/css')
                elif file_path.endswith('.js'):
                    self.send_header('Content-Type', 'application/javascript')
                elif file_path.endswith('.html'):
                    self.send_header('Content-Type', 'text/html')
                else:
                    self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404)
        else:
            super().do_GET()

    def end_headers(self) -> None:
        """Ensure CORS headers are set for GET requests."""
        if self.command == 'GET':
            self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def handle_agent_chat(self, user_query: str, user_id: str = "default_user", session_id: str = "default_session") -> str:
        """Handles a chat message by passing it to the agent runner and returning the response."""
        async def call_agent_async(query: str, runner, user_id, session_id):
            content = types.Content(role='user', parts=[types.Part(text=query)])
            final_response_text = "Agent did not produce a final response."
            async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
                if event.is_final_response():
                    if event.content and event.content.parts:
                        final_response_text = event.content.parts[0].text
                    elif event.actions and getattr(event.actions, 'escalate', False):
                        final_response_text = f"Agent escalated: {getattr(event, 'error_message', 'No specific message.')}"
                    break
            return final_response_text

        # Run the async function in the current (sync) context
        return asyncio.run(call_agent_async(user_query, self.runner, user_id, session_id))

if __name__ == '__main__':
    from server import start_server
    start_server()
