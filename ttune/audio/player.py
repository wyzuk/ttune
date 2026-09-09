"""Audio player engine using sounddevice output stream and real-time audio callback."""

import threading
import time
from typing import Callable, Optional

import numpy as np
import sounddevice as sd

from ttune.audio.analyzer import SpectrumAnalyzer
from ttune.audio.decoder import AudioDecoder
from ttune.config import (
    AUDIO_BLOCK_SIZE,
    DEFAULT_CHANNELS,
    DEFAULT_SAMPLE_RATE,
    DEFAULT_VOLUME,
    SEEK_STEP,
    VOLUME_STEP,
)


class AudioPlayer:
    """High-performance audio player engine with real-time FFT spectrum coupling."""

    def __init__(self, sample_rate: int = DEFAULT_SAMPLE_RATE):
        self.sample_rate = sample_rate
        self.channels = DEFAULT_CHANNELS
        self.block_size = AUDIO_BLOCK_SIZE

        self.analyzer = SpectrumAnalyzer(sample_rate=self.sample_rate)

        self._is_playing = False
        self._is_paused = False
        self._volume = DEFAULT_VOLUME
        self._is_muted = False
        self._current_file: Optional[str] = None
        self._total_duration: float = 0.0
        self._played_frames: int = 0
        self._start_offset_seconds: float = 0.0

        self._lock = threading.RLock()
        self._decoder: Optional[AudioDecoder] = None
        self._stream: Optional[sd.OutputStream] = None
        self._on_track_end: Optional[Callable[[], None]] = None

        self._eos_detected = False
        self._eos_signaled = False

    @property
    def is_playing(self) -> bool:
        return self._is_playing and not self._is_paused

    @property
    def is_paused(self) -> bool:
        return self._is_paused

    @property
    def volume(self) -> float:
        return 0.0 if self._is_muted else self._volume

    @property
    def raw_volume(self) -> float:
        return self._volume

    @property
    def is_muted(self) -> bool:
        return self._is_muted

    @property
    def current_position(self) -> float:
        """Current playback position in seconds."""
        with self._lock:
            if not self._decoder:
                return 0.0
            pos = self._start_offset_seconds + (self._played_frames / float(self.sample_rate))
            if self._total_duration > 0:
                return min(pos, self._total_duration)
            return pos

    @property
    def duration(self) -> float:
        return self._total_duration

    def set_on_track_end(self, callback: Callable[[], None]):
        """Set callback invoked when current track finishes playback."""
        self._on_track_end = callback

    def _audio_callback(self, outdata: np.ndarray, frames: int, time_info, status):
        """Real-time PortAudio stream callback."""
        with self._lock:
            if not self._is_playing or self._is_paused or not self._decoder:
                outdata.fill(0)
                self.analyzer.update_samples(np.zeros(frames, dtype=np.float32))
                return

            chunk = self._decoder.read_frames(frames)

            if self._decoder.is_eof and np.all(chunk == 0):
                outdata.fill(0)
                self.analyzer.update_samples(np.zeros(frames, dtype=np.float32))
                if not self._eos_detected:
                    self._eos_detected = True
                    threading.Thread(target=self._handle_track_finished, daemon=True).start()
                return

            effective_volume = 0.0 if self._is_muted else self._volume
            if effective_volume != 1.0:
                processed = chunk * effective_volume
            else:
                processed = chunk

            outdata[:] = processed

            self._played_frames += frames

            self.analyzer.update_samples(processed)

    def _handle_track_finished(self):
        """Worker triggered when a track reaches end of stream."""
        with self._lock:
            if self._eos_signaled:
                return
            self._eos_signaled = True

        if self._on_track_end:
            try:
                self._on_track_end()
            except Exception:
                pass

    def load_and_play(self, file_path: str, duration: float = 0.0, start_time: float = 0.0):
        """Load and start playback of a new media file."""
        with self._lock:
            self.stop()

            self._current_file = file_path
            self._total_duration = max(0.0, duration)
            self._start_offset_seconds = max(0.0, start_time)
            self._played_frames = 0
            self._eos_detected = False
            self._eos_signaled = False
            self.analyzer.reset()

            self._decoder = AudioDecoder(
                file_path=file_path,
                sample_rate=self.sample_rate,
                start_time=start_time,
            )

            if self._stream is None or not self._stream.active:
                self._stream = sd.OutputStream(
                    samplerate=self.sample_rate,
                    channels=self.channels,
                    blocksize=self.block_size,
                    dtype=np.float32,
                    callback=self._audio_callback,
                )
                self._stream.start()

            self._is_playing = True
            self._is_paused = False

    def pause(self):
        with self._lock:
            self._is_paused = True

    def resume(self):
        with self._lock:
            self._is_paused = False

    def toggle_play_pause(self):
        with self._lock:
            if self._is_paused:
                self.resume()
            else:
                self.pause()

    def stop(self):
        """Stop playback and release resources."""
        with self._lock:
            self._is_playing = False
            self._is_paused = False
            self._played_frames = 0
            self._eos_detected = False
            self._eos_signaled = False

            if self._decoder:
                self._decoder.close()
                self._decoder = None

            self.analyzer.reset()

    def seek(self, target_seconds: float):
        """Seek to specific position in seconds."""
        with self._lock:
            if not self._decoder or not self._current_file:
                return

            target = max(0.0, target_seconds)
            if self._total_duration > 0:
                target = min(target, self._total_duration)

            self._start_offset_seconds = target
            self._played_frames = 0
            self._eos_detected = False
            self._eos_signaled = False
            self._decoder.seek(target)

    def seek_relative(self, delta_seconds: float):
        """Seek relative to current playback position."""
        pos = self.current_position
        self.seek(pos + delta_seconds)

    def set_volume(self, level: float):
        """Set volume level (0.0 to 1.5)."""
        with self._lock:
            self._volume = max(0.0, min(1.5, level))

    def volume_up(self, step: float = VOLUME_STEP):
        self.set_volume(self._volume + step)

    def volume_down(self, step: float = VOLUME_STEP):
        self.set_volume(self._volume - step)

    def toggle_mute(self):
        with self._lock:
            self._is_muted = not self._is_muted

    def close(self):
        """Completely shut down player, decoder, and audio hardware stream."""
        self.stop()
        with self._lock:
            if self._stream:
                try:
                    self._stream.stop()
                    self._stream.close()
                except Exception:
                    pass
                self._stream = None
