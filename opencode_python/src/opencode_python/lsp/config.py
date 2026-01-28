"""OpenCode Python - LSP utilities and configuration"""

from __future__ import annotations
from typing import Optional, List
from pathlib import Path
import subprocess
import logging

from opencode_python.lsp.client import LSPClient, DocumentSymbols, HoverProvider


logger = logging.getLogger(__name__)


class LSPConfig:
    """LSP configuration"""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize LSP configuration

        Args:
            config_path: Custom LSP config file path
        """
        self.config_path = config_path

    def load_workspace(self) -> str:
        """Load workspace root from config or detect git

        Returns:
            Workspace root directory path
        """
        if self.config_path and self.config_path.exists():
            with open(self.config_path, "r") as f:
                content = f.read()
                # Extract workspace path from config
                for line in content.strip().split("\n"):
                    if line.strip().startswith("workspace_root"):
                        path = line.split("=", 1)
                        path = path.strip().strip()
                        if path and Path(path).exists():
                            return path
                logger.info(f"Loaded workspace root from config: {path}")
            
            logger.debug(f"Workspace root: {self.config_path or self.config_path.exists()}")
        
        # Fallback to git root detection
        from git import Repo
        try:
            repo = Repo(search_working_directory())
            root = repo.git.working_dir
            logger.info(f"Detected git workspace root: {root}")
            return root
        except Exception:
            logger.warning("Could not detect git workspace root")
            return str(Path.cwd())


class LSPServerConfig:
    """Language server configuration"""

    def __init__(self, server_path: Optional[Path] = None, language_id: str = "python"):
        """Initialize language server

        Args:
            server_path: Path to language server binary
            language_id: Language server ID
        """
        self.server_path = server_path
        self.language_id = language_id

    def is_available(self) -> bool:
        """Check if language server is available

        Returns:
            True if server binary exists, False otherwise
        """
        if self.server_path and self.server_path.exists():
            return True
        return False
