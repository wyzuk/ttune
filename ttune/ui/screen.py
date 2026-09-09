"""Terminal screen initialization, size detection, and double-buffered flicker-free rendering."""

import atexit
import os
import shutil
import sys
from typing import List, Tuple

from ttune.ui.theme import STYLE_RESET


def enable_virtual_terminal() -> bool:
    """Enable ANSI virtual terminal processing and UTF-8 output on Windows."""
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    if os.name == "nt":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32

            kernel32.SetConsoleOutputCP(65001)
            kernel32.SetConsoleCP(65001)

            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                mode.value |= 0x0004
                kernel32.SetConsoleMode(handle, mode)
                return True
        except Exception:
            return False
    return True


class TerminalScreen:
    """Manages terminal state: alternate buffer, hidden cursor, and flicker-free rendering."""

    def __init__(self):
        self._is_initialized = False
        self._last_cols = 0
        self._last_lines = 0

    def init_terminal(self):
        """Enter alternate screen buffer and hide cursor."""
        if self._is_initialized:
            return
        enable_virtual_terminal()

        try:
            sys.stdout.write("\033[?1049h\033[?25l\033[2J\033[H")
            sys.stdout.flush()
        except Exception:
            pass

        self._is_initialized = True
        atexit.register(self.restore_terminal)

    def restore_terminal(self):
        """Restore main screen buffer and show cursor."""
        if not self._is_initialized:
            return
        try:
            sys.stdout.write(f"{STYLE_RESET}\033[?25h\033[?1049l")
            sys.stdout.flush()
        except Exception:
            pass
        self._is_initialized = False

    @staticmethod
    def get_size() -> Tuple[int, int]:
        """Get current terminal dimensions (columns, lines)."""
        try:
            cols, lines = shutil.get_terminal_size((80, 24))
            return max(40, cols), max(16, lines)
        except Exception:
            return 80, 24

    def has_resized(self) -> bool:
        """Check if terminal size changed since last check."""
        cols, lines = self.get_size()
        if cols != self._last_cols or lines != self._last_lines:
            self._last_cols = cols
            self._last_lines = lines
            return True
        return False

    def render_frame(self, lines: List[str]):
        """Render a full screen frame without flickering using cursor repositioning."""
        cols, num_terminal_lines = self.get_size()

        buf = ["\033[H"]

        for i in range(num_terminal_lines):
            if i < len(lines):
                line = lines[i]
                buf.append(f"{line}{STYLE_RESET}\033[K\n")
            else:
                buf.append("\033[K\n")

        output = "".join(buf).rstrip("\n")
        try:
            sys.stdout.write(output)
            sys.stdout.flush()
        except UnicodeEncodeError:
            sys.stdout.buffer.write(output.encode("utf-8", errors="replace"))
            sys.stdout.buffer.flush()
        except Exception:
            pass
