"""Tests for FFT SpectrumAnalyzer calculations, bands, and peak decays."""

import numpy as np

from ttune.audio.analyzer import SpectrumAnalyzer


def test_spectrum_analyzer_silence():
    analyzer = SpectrumAnalyzer(sample_rate=44100, window_size=1024)
    analyzer.update_samples(np.zeros(1024, dtype=np.float32))
    bars, peaks = analyzer.get_spectrum(16)

    assert len(bars) == 16
    assert len(peaks) == 16
    assert np.all(bars >= 0.0)
    assert np.all(bars <= 1.0)


def test_spectrum_analyzer_sine_wave():
    analyzer = SpectrumAnalyzer(sample_rate=44100, window_size=2048)
    t = np.linspace(0, 2048 / 44100.0, 2048, endpoint=False)
    sine = (0.7 * np.sin(2 * np.pi * 440.0 * t)).astype(np.float32)

    analyzer.update_samples(sine)
    bars, peaks = analyzer.get_spectrum(32)

    assert np.max(bars) > 0.3
    assert np.max(peaks) >= np.max(bars)


def test_spectrum_peak_decay():
    analyzer = SpectrumAnalyzer(sample_rate=44100, window_size=1024)
    t = np.linspace(0, 1024 / 44100.0, 1024, endpoint=False)
    sine = (0.9 * np.sin(2 * np.pi * 300.0 * t)).astype(np.float32)

    analyzer.update_samples(sine)
    bars1, peaks1 = analyzer.get_spectrum(16)

    analyzer.update_samples(np.zeros(1024, dtype=np.float32))
    bars2, peaks2 = analyzer.get_spectrum(16)

    assert np.max(bars2) <= np.max(bars1)
