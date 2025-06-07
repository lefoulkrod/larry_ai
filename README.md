# COMPUTRON 9000
I am COMPUTRON 9000.

## Features
- Modern, responsive chat UI (ChatGPT style)
- Model selector (auto-populated from Ollama)
- System prompt for consistent assistant behavior
- Python proxy server for CORS and API routing
- Easy setup with [uv](https://github.com/astral-sh/uv) and `pyproject.toml`

## Requirements
- Python 3.11.12 (see `.python-version`)
- [uv](https://github.com/astral-sh/uv) (for dependency and venv management)
- Ollama running locally (default: `http://localhost:11434`)

## Setup

1. **Clone the repo:**
   ```sh
   git clone <this-repo-url>
   cd chat_app
   ```

2. **Create a virtual environment:**
   ```sh
   uv venv .venv
   ```

3. **Activate the virtual environment:**
   - On Unix/macOS:
     ```sh
     source .venv/bin/activate
     ```
   - On Windows:
     ```sh
     .venv\Scripts\activate
     ```

4. **Install dependencies:**
   ```sh
   uv pip install -r pyproject.toml
   ```

5. **Start the proxy server:**
   ```sh
   python proxy_server.py
   ```

6. **Open the chat UI:**
   - Visit [http://localhost:8080](http://localhost:8080) in your browser.

## Usage
- Select a model from the dropdown (auto-populated from Ollama).
- Type your message and press Enter or click Send.
- The assistant will always respond as "Larry AI".

## Project Structure
```
chat_app/
    ollama_chat.html      # Chat UI (frontend)
    proxy_server.py       # Python proxy server
    pyproject.toml        # Project metadata and dependencies
    .python-version       # Python version pin
```

## Notes
- The `.venv` folder is local and should not be committed to git.
- The system prompt is hardcoded in the frontend for consistent assistant behavior.
- The proxy server handles CORS and API routing for the frontend.

## License
MIT
