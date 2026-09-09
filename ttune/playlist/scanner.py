"""Media file discovery with recursive scanning and natural sorting."""

import os
import re
from pathlib import Path
from typing import List

from ttune.config import SUPPORTED_EXTENSIONS


def natural_sort_key(text: str):
    """Generate a key for natural/human sorting (e.g., 'track 2' before 'track 10')."""
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r"(\d+)", text)]


def is_supported_file(file_path: str) -> bool:
    """Check if a file has a supported media extension."""
    _, ext = os.path.splitext(file_path)
    return ext.lower() in SUPPORTED_EXTENSIONS


def scan_media(path_str: str) -> List[str]:
    """Scan a file or directory for supported media files.

    Args:
        path_str: Path to a file or directory.

    Returns:
        A list of absolute paths to supported media files, naturally sorted.
    """
    path = Path(path_str).resolve()

    if not path.exists():
        raise FileNotFoundError(f"Path not found: {path_str}")

    if path.is_file():
        if is_supported_file(str(path)):
            return [str(path)]
        else:
            raise ValueError(
                f"Unsupported media format '{path.suffix}'. "
                f"Supported formats include: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            )

    discovered: List[str] = []
    skip_dirs = {".git", ".svn", ".hg", "__pycache__", "node_modules", "$recycle.bin"}

    for root, dirs, files in os.walk(str(path)):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d.lower() not in skip_dirs]

        for file in files:
            if file.startswith("."):
                continue
            full_path = os.path.join(root, file)
            if is_supported_file(full_path):
                discovered.append(full_path)

    discovered.sort(key=lambda p: natural_sort_key(os.path.basename(p)))
    return discovered
