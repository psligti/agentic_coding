"""OpenCode Python - LSP Integration"""
from __future__ import annotations
from typing import Optional, Dict, Any
import asyncio
import json
import logging
from dataclasses import dataclass

from opencode_python.core.event_bus import bus, Events


logger = logging.getLogger(__name__)


@dataclass
class SymbolInfo:
    """Symbol information"""
    name: str
    kind: str
    location: Dict[str, int]
    container_name: Optional[str] = None
    documentation: Optional[str] = None


@dataclass
class HoverInfo:
    """Hover information"""
    text: str
    documentation: Optional[str] = None


@dataclass
class CodeAction:
    """Code action for navigation"""
    kind: str
    uri: Optional[str] = None
    range: Optional[Dict[str, int]] = None


class LSPClient:
    """
    Language Server Protocol client for Python 3.10+
    
    Provides basic LSP functionality:
    - Connect/disconnect to LSP server
    - Get symbol at point (textDocument/symbol)
    - Get hover information (textDocument/hover)
    - Execute code actions (workspace/executeCommand)
    """
    def __init__(self, session_id: str):
        self.session_id = session_id
        self._process: Optional[asyncio.subprocess.Process] = None
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._pending_requests: Dict[str, Dict[str, Any]] = {}

    async def connect(self, server_command: str, root_path: str) -> None:
        """Connect to LSP server"""
        logger.info(f"Connecting to LSP server: {server_command}")

        # Start LSP server process
        process = await asyncio.create_subprocess_exec(
            server_command.split(),
            cwd=root_path,
        )

        self._reader = process.stdout
        self._writer = process.stdin

        # Start reader task
        asyncio.create_task(self._read_loop())

        # Start writer task
        asyncio.create_task(self._write_loop())

        logger.info("LSP client connected")

    async def disconnect(self) -> None:
        """Disconnect from LSP server"""
        logger.info("Disconnecting from LSP server")

        # Terminate process
        if self._process:
            self._process.terminate()
            await self._process.wait()

        logger.info("LSP client disconnected")

    async def _read_loop(self) -> None:
        """Read responses from LSP server"""
        buffer = ""
        
        while True:
            try:
                data = await self._reader.read(1024)
                
                if not data:
                    # End of file
                    break
                
                buffer += data.decode('utf-8', errors='ignore')
                
                # Process each line
                for line in buffer.split('\n'):
                    if line:
                        await self._handle_response(line)
            except Exception as e:
                logger.error(f"LSP read error: {e}")
                break

    async def _write_loop(self) -> None:
        """Write requests to LSP server"""
        if not self._writer:
            return
        
        while True:
            # Wait for pending requests
            while self._pending_requests:
                await asyncio.sleep(0.01)
            
            # Check if terminated
            if not self._writer or self._writer.is_closing():
                break

    async def _handle_response(self, line: str) -> None:
        """Handle response from LSP server"""
        if not line.strip():
            return
        
        try:
            response = json.loads(line)
            
            if "result" in response:
                result_data = response["result"]
                
                if "id" in result_data:
                    request_id = result_data["id"]
                    self._pending_requests.pop(request_id)
                
                # Extract result info
                if "result" in result_data:
                    result_info = result_data["result"]
                    
                    if "id" in result_data:
                        request_id = result_data["id"]
                        self._pending_requests.pop(request_id)
                    
                    # Extract symbol info
                        if "result" in result_data:
                            result_info = result_data["result"]
                            return SymbolInfo(
                                name=result_info.get("name", ""),
                                kind=result_info.get("kind", ""),
                                location=result_info.get("location", {}),
                            )
                
                elif "method" in response and response["method"] == "window/logMessage":
                    # Handle log messages
                    for msg in response.get("messages", []):
                        logger.debug(f"LSP log: {msg.get('type')}: {msg.get('message', '')}")
                elif "method" in response and response["method"] == "window/logTrace":
                    # Handle trace messages
                    logger.debug(f"LSP trace: {response.get('trace', '')}")
            
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LSP response: {e}")

    async def _send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send request to LSP server"""
        request_id = str(id(self))
        
        # Build request
        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params,
        }
        
        # Send request
        if self._writer:
            json_str = json.dumps(request) + "\n"

        return {"jsonrpc": "2.0", "id": request_id}

    async def _request_counter(self) -> str:
        """Generate unique request ID"""
        import uuid
        return str(uuid.uuid4())