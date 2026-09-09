"""Cross-platform non-blocking keyboard input reader supporting Windows and Unix."""

import os
import queue
import sys
import threading
import time
from typing import Optional

if os.name == "nt":
    import msvcrt

    class KeyboardReader:
        """Reads keyboard inputs non-blockingly on Windows with pipe fallback."""

        def __init__(self):
            self.is_tty = sys.stdin.isatty()
            self._pipe_queue = None
            self._stop_event = None

            if not self.is_tty:
                self._pipe_queue = queue.Queue()
                self._stop_event = threading.Event()
                self._thread = threading.Thread(target=self._pipe_reader, daemon=True)
                self._thread.start()

        def _pipe_reader(self):
            while self._stop_event and not self._stop_event.is_set():
                try:
                    line = sys.stdin.readline()
                    if not line:
                        break
                    for ch in line.strip():
                        if self._pipe_queue:
                            self._pipe_queue.put(ch)
                except Exception:
                    break

        def read_key(self, timeout: float = 0.05) -> Optional[str]:
            """Read a single key press with timeout in seconds."""
            if not self.is_tty and self._pipe_queue:
                try:
                    return self._pipe_queue.get(timeout=timeout)
                except queue.Empty:
                    return None

            start_time = time.time()
            while time.time() - start_time < timeout:
                if msvcrt.kbhit():
                    ch = msvcrt.getwch()
                    if ch in ("\x00", "\xe0"):
                        ch2 = msvcrt.getwch()
                        if ch2 == "H":
                            return "UP"
                        elif ch2 == "P":
                            return "DOWN"
                        elif ch2 == "K":
                            return "LEFT"
                        elif ch2 == "M":
                            return "RIGHT"
                        return None

                    if ch == " ":
                        return "SPACE"
                    elif ch in ("\r", "\n"):
                        return "ENTER"
                    elif ch == "\x08":
                        return "BACKSPACE"
                    elif ch == "\x1b":
                        return "ESCAPE"
                    return ch
                time.sleep(0.005)
            return None

        def cleanup(self):
            if self._stop_event:
                self._stop_event.set()

else:
    import select
    import termios
    import tty

    class KeyboardReader:
        """Reads keyboard inputs non-blockingly on Unix/macOS/Linux."""

        def __init__(self):
            self.is_tty = sys.stdin.isatty()
            self._old_settings = None
            if self.is_tty:
                try:
                    self._old_settings = termios.tcgetattr(sys.stdin)
                    tty.setcbreak(sys.stdin.fileno())
                except Exception:
                    pass

        def read_key(self, timeout: float = 0.05) -> Optional[str]:
            if not self.is_tty:
                return None
            try:
                rlist, _, _ = select.select([sys.stdin], [], [], timeout)
                if not rlist:
                    return None

                ch = sys.stdin.read(1)
                if ch == "\x1b":
                    rlist2, _, _ = select.select([sys.stdin], [], [], 0.02)
                    if rlist2:
                        ch2 = sys.stdin.read(1)
                        if ch2 == "[":
                            ch3 = sys.stdin.read(1)
                            if ch3 == "A":
                                return "UP"
                            elif ch3 == "B":
                                return "DOWN"
                            elif ch3 == "C":
                                return "RIGHT"
                            elif ch3 == "D":
                                return "LEFT"
                    return "ESCAPE"

                if ch == " ":
                    return "SPACE"
                elif ch in ("\r", "\n"):
                    return "ENTER"
                elif ch in ("\x7f", "\x08"):
                    return "BACKSPACE"
                return ch
            except Exception:
                return None

        def cleanup(self):
            if self._old_settings is not None:
                try:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._old_settings)
                except Exception:
                    pass
