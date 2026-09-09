"""FFmpeg-based audio decoder that streams raw float32 PCM samples into a queue."""

import os
import queue
import subprocess
import threading
from typing import Optional

import numpy as np

from ttune.config import DEFAULT_CHANNELS, DEFAULT_SAMPLE_RATE


class AudioDecoder:
    """Streams decoded audio frames from any FFmpeg-supported format into a FIFO queue."""

    def __init__(self, file_path: str, sample_rate: int = DEFAULT_SAMPLE_RATE, start_time: float = 0.0):
        self.file_path = file_path
        self.sample_rate = sample_rate
        self.channels = DEFAULT_CHANNELS
        self.current_time = start_time
        self.is_eof = False
        self._stopped = False

        self.bytes_per_frame = 4 * self.channels
        self.chunk_frames = 2048
        self.chunk_bytes = self.chunk_frames * self.bytes_per_frame

        self._queue: queue.Queue = queue.Queue(maxsize=40)
        self._process: Optional[subprocess.Popen] = None
        self._reader_thread: Optional[threading.Thread] = None

        self._residual = np.empty((0, self.channels), dtype=np.float32)

        self._start_ffmpeg(start_time)

    def _start_ffmpeg(self, start_time: float):
        self._stopped = False
        self.is_eof = False
        self._residual = np.empty((0, self.channels), dtype=np.float32)

        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break

        cmd = ["ffmpeg"]
        if start_time > 0:
            cmd.extend(["-ss", f"{start_time:.3f}"])

        cmd.extend([
            "-i", self.file_path,
            "-vn", "-sn", "-dn",
            "-f", "f32le",
            "-ac", str(self.channels),
            "-ar", str(self.sample_rate),
            "-v", "error",
            "pipe:1"
        ])

        creationflags = 0
        if os.name == "nt":
            creationflags = 0x08000000

        self._process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=creationflags,
            bufsize=self.chunk_bytes * 4,
        )

        self._reader_thread = threading.Thread(target=self._reader_worker, daemon=True)
        self._reader_thread.start()

    def _reader_worker(self):
        """Worker thread continuously reading from ffmpeg stdout and queuing chunks."""
        proc = self._process
        if not proc or not proc.stdout:
            self.is_eof = True
            return

        try:
            while not self._stopped:
                raw_bytes = proc.stdout.read(self.chunk_bytes)
                if not raw_bytes:
                    break

                arr = np.frombuffer(raw_bytes, dtype=np.float32)
                num_complete_frames = len(arr) // self.channels
                if num_complete_frames > 0:
                    frames = arr[: num_complete_frames * self.channels].reshape(-1, self.channels)
                    while not self._stopped:
                        try:
                            self._queue.put(frames, timeout=0.1)
                            break
                        except queue.Full:
                            continue
        except Exception:
            pass
        finally:
            self.is_eof = True

    def read_frames(self, num_frames: int) -> np.ndarray:
        """Read exactly num_frames audio frames. Returns array of shape (num_frames, channels)."""
        collected = []
        collected_count = 0

        if len(self._residual) > 0:
            if len(self._residual) >= num_frames:
                out = self._residual[:num_frames]
                self._residual = self._residual[num_frames:]
                return out
            else:
                collected.append(self._residual)
                collected_count += len(self._residual)
                self._residual = np.empty((0, self.channels), dtype=np.float32)

        while collected_count < num_frames and not self._stopped:
            try:
                chunk = self._queue.get(timeout=0.04)
                needed = num_frames - collected_count
                if len(chunk) <= needed:
                    collected.append(chunk)
                    collected_count += len(chunk)
                else:
                    collected.append(chunk[:needed])
                    collected_count += needed
                    self._residual = chunk[needed:]
                    break
            except queue.Empty:
                if self.is_eof:
                    break
                break

        if collected:
            result = np.vstack(collected)
        else:
            result = np.empty((0, self.channels), dtype=np.float32)

        if len(result) < num_frames:
            padding = np.zeros((num_frames - len(result), self.channels), dtype=np.float32)
            result = np.vstack([result, padding]) if len(result) > 0 else padding

        return result

    def seek(self, target_seconds: float):
        """Seek to a specific timestamp in the track."""
        self.close()
        self.current_time = target_seconds
        self._start_ffmpeg(target_seconds)

    def close(self):
        """Cleanly terminate FFmpeg process and worker thread."""
        self._stopped = True
        proc = self._process
        self._process = None

        if proc:
            try:
                if proc.stdout:
                    proc.stdout.close()
                if proc.stderr:
                    proc.stderr.close()
                proc.terminate()
                proc.wait(timeout=0.5)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass

        if self._reader_thread and self._reader_thread.is_alive():
            self._reader_thread.join(timeout=0.5)
