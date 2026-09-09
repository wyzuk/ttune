"""PC-wide media file search engine with smart indexing and directory filtering."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set

from ttune.config import SUPPORTED_EXTENSIONS
from ttune.playlist.scanner import is_supported_file, natural_sort_key


class MusicSearchEngine:
    """Fast search engine scanning common music and user locations across the PC."""

    def __init__(self):
        self._cached_files: List[str] = []
        self._is_indexed: bool = False
        self._custom_roots: List[str] = []
        self._setup_search_roots()

    def _setup_search_roots(self):
        """Determine primary user search locations on this PC."""
        roots: List[Path] = []
        home = Path(os.path.expanduser("~")).resolve()

        common_subdirs = ["Music", "Desktop", "Downloads", "Documents", "Videos"]
        for sub in common_subdirs:
            p = home / sub
            if p.exists() and p.is_dir():
                roots.append(p)

        roots.append(home)

        if os.name == "nt":
            import string
            for letter in string.ascii_uppercase:
                if letter in ("C", "A", "B"):
                    continue
                drive_p = Path(f"{letter}:\\")
                if drive_p.exists() and drive_p.is_dir():
                    roots.append(drive_p)

        self._roots = roots

    def index_all(self, max_files: int = 2000) -> List[str]:
        """Index media files across roots, skipping system and build folders."""
        if self._is_indexed and self._cached_files:
            return self._cached_files

        skip_dir_names = {
            "appdata", "windows", "program files", "program files (x86)",
            "programdata", "node_modules", ".git", ".svn", "__pycache__",
            "$recycle.bin", "system volume information", "recovery",
            "venv", ".venv", "site-packages", ".gemini", ".vscode"
        }

        discovered: List[str] = []
        seen_paths: Set[str] = set()

        for root_path in self._roots:
            if not root_path.exists():
                continue

            try:
                for current_dir, dirs, files in os.walk(str(root_path)):
                    dirs[:] = [
                        d for d in dirs
                        if not d.startswith(".")
                        and d.lower() not in skip_dir_names
                    ]

                    for f in files:
                        if f.startswith("."):
                            continue
                        _, ext = os.path.splitext(f)
                        if ext.lower() in SUPPORTED_EXTENSIONS:
                            full = os.path.join(current_dir, f)
                            if full not in seen_paths:
                                seen_paths.add(full)
                                discovered.append(full)
                                if len(discovered) >= max_files:
                                    break

                    if len(discovered) >= max_files:
                        break
            except (PermissionError, OSError):
                continue

        discovered.sort(key=lambda p: natural_sort_key(os.path.basename(p)))
        self._cached_files = discovered
        self._is_indexed = True
        return discovered

    def search(self, query: str, limit: int = 100) -> List[str]:
        """Search indexed media files matching query string."""
        if not self._is_indexed:
            self.index_all()

        q = query.strip().lower()
        if not q:
            return self._cached_files[:limit]

        query_tokens = q.split()
        results: List[str] = []

        for path in self._cached_files:
            filename = os.path.basename(path).lower()
            if all(token in filename for token in query_tokens):
                results.append(path)
            elif all(token in path.lower() for token in query_tokens):
                results.append(path)

            if len(results) >= limit:
                break

        return results


global_search_engine = MusicSearchEngine()
