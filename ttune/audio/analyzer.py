"""Real-time FFT spectrum analyzer with logarithmic frequency bands and peak decay."""

import threading
from typing import List, Tuple

import numpy as np

from ttune.config import (
    ATTACK_FACTOR,
    DEFAULT_SAMPLE_RATE,
    FFT_WINDOW_SIZE,
    FREQ_MAX,
    FREQ_MIN,
    PEAK_DECAY_RATE,
    PEAK_HOLD_FRAMES,
    SMOOTH_FACTOR,
)


class SpectrumAnalyzer:
    """Performs real-time Fast Fourier Transform (FFT) analysis on audio samples."""

    def __init__(self, sample_rate: int = DEFAULT_SAMPLE_RATE, window_size: int = FFT_WINDOW_SIZE):
        self.sample_rate = sample_rate
        self.window_size = window_size
        self._lock = threading.Lock()

        # Ring buffer for latest audio samples (mono float32)
        self._buffer = np.zeros(self.window_size, dtype=np.float32)
        self._hanning = np.hanning(self.window_size).astype(np.float32)

        # State tracking for smoothing & peak decay
        self._num_bars = 32
        self._prev_heights = np.zeros(self._num_bars, dtype=np.float32)
        self._peak_heights = np.zeros(self._num_bars, dtype=np.float32)
        self._peak_holds = np.zeros(self._num_bars, dtype=np.int32)

        # Pre-calculated frequency band indices
        self._bin_indices: List[Tuple[int, int]] = []
        self._freq_weights = np.ones(self._num_bars, dtype=np.float32)
        self._setup_bands(self._num_bars)

    def _setup_bands(self, num_bars: int):
        """Precompute FFT bin index ranges for logarithmic frequency distribution."""
        self._num_bars = max(8, num_bars)
        self._prev_heights = np.zeros(self._num_bars, dtype=np.float32)
        self._peak_heights = np.zeros(self._num_bars, dtype=np.float32)
        self._peak_holds = np.zeros(self._num_bars, dtype=np.int32)

        nyquist = self.sample_rate / 2.0
        freq_max = min(FREQ_MAX, nyquist)
        # Logarithmically spaced frequency edges
        edges = np.geomspace(FREQ_MIN, freq_max, self._num_bars + 1)

        fft_freqs = np.fft.rfftfreq(self.window_size, d=1.0 / self.sample_rate)
        indices = []

        for i in range(self._num_bars):
            low = edges[i]
            high = edges[i + 1]
            idx_start = int(np.searchsorted(fft_freqs, low))
            idx_end = int(np.searchsorted(fft_freqs, high))
            if idx_end <= idx_start:
                idx_end = idx_start + 1
            idx_end = min(idx_end, len(fft_freqs))
            idx_start = min(idx_start, idx_end - 1)
            indices.append((idx_start, idx_end))

        self._bin_indices = indices

        # Frequency tilt weighting (compensates for 1/f spectral roll-off so highs and mids look lively)
        center_freqs = np.sqrt(edges[:-1] * edges[1:])
        weights = np.power(center_freqs / 300.0, 0.42)
        # Gentle roll-off for extreme sub-bass rumble
        weights[:2] *= 0.75
        self._freq_weights = weights.astype(np.float32)

    def update_samples(self, samples: np.ndarray):
        """Feed newly played audio samples into the ring buffer.

        Thread-safe; called directly from audio playback callback.
        """
        if len(samples) == 0:
            return

        # Downmix stereo to mono if needed
        if samples.ndim == 2:
            mono = np.mean(samples, axis=1)
        else:
            mono = samples

        n = len(mono)
        with self._lock:
            if n >= self.window_size:
                self._buffer[:] = mono[-self.window_size :]
            else:
                self._buffer[:-n] = self._buffer[n:]
                self._buffer[-n:] = mono

    def get_spectrum(self, num_bars: int) -> Tuple[np.ndarray, np.ndarray]:
        """Compute FFT spectrum magnitudes and peak caps for the given number of bars.

        Returns:
            (bar_heights, peak_heights) where values are normalized in range [0.0, 1.0].
        """
        if num_bars != self._num_bars:
            with self._lock:
                self._setup_bands(num_bars)

        with self._lock:
            samples_copy = self._buffer.copy()

        # Check for silence or near-silence
        rms = np.sqrt(np.mean(samples_copy**2))
        if rms < 1e-5:
            # Decay smoothly to zero
            self._prev_heights *= 0.75
            self._peak_heights = np.maximum(0.0, self._peak_heights - PEAK_DECAY_RATE)
            return self._prev_heights.copy(), self._peak_heights.copy()

        # Apply Hanning window
        windowed = samples_copy * self._hanning

        # Compute Real FFT magnitude
        fft_mag = np.abs(np.fft.rfft(windowed))

        # Compute raw energy per frequency band
        raw_heights = np.zeros(self._num_bars, dtype=np.float32)
        for i, (start, end) in enumerate(self._bin_indices):
            band_energy = np.mean(fft_mag[start:end]) * self._freq_weights[i]
            # Convert to decibels with dynamic range -54 dB to 0 dB
            db = 20.0 * np.log10(band_energy + 1e-5)
            # Map -54dB..0dB to 0.0..1.0
            norm = (db + 54.0) / 54.0
            raw_heights[i] = max(0.0, min(1.0, norm))

        # Apply asymmetric attack / smooth decay (EMA)
        current_heights = np.zeros(self._num_bars, dtype=np.float32)
        for i in range(self._num_bars):
            curr = raw_heights[i]
            prev = self._prev_heights[i]
            if curr > prev:
                # Fast attack for snappy beat responsiveness
                current_heights[i] = prev * (1.0 - ATTACK_FACTOR) + curr * ATTACK_FACTOR
            else:
                # Smooth decay to prevent jitter
                current_heights[i] = prev * SMOOTH_FACTOR + curr * (1.0 - SMOOTH_FACTOR)

        self._prev_heights[:] = current_heights

        # Update peak caps with hold & decay
        for i in range(self._num_bars):
            h = current_heights[i]
            p = self._peak_heights[i]
            if h >= p:
                self._peak_heights[i] = h
                self._peak_holds[i] = PEAK_HOLD_FRAMES
            else:
                if self._peak_holds[i] > 0:
                    self._peak_holds[i] -= 1
                else:
                    self._peak_heights[i] = max(h, p - PEAK_DECAY_RATE)

        return current_heights.copy(), self._peak_heights.copy()

    def reset(self):
        """Reset internal buffers and spectrum state."""
        with self._lock:
            self._buffer.fill(0.0)
            self._prev_heights.fill(0.0)
            self._peak_heights.fill(0.0)
            self._peak_holds.fill(0)
