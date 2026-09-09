"""Tests for UI frame composition and terminal resize adaptation."""

import numpy as np

from ttune.playlist.manager import PlaylistManager
from ttune.ui.renderer import UIRenderer, fit_text, strip_ansi_len


def test_fit_text():
    assert fit_text("short", 10) == "short"
    assert fit_text("a very long string that needs truncation", 15) == "a very long ..."
    assert fit_text("abc", 2) == "ab"


def test_strip_ansi_len():
    colored = "\033[38;2;0;240;255mHello\033[0m"
    assert strip_ansi_len(colored) == 5


def test_renderer_frame_dimensions():
    renderer = UIRenderer()
    pm = PlaylistManager(["song1.mp3", "song2.mp3"])

    # Test standard terminal 80x24
    lines_80x24 = renderer.build_frame(
        cols=80,
        lines=24,
        playlist=pm,
        current_pos=15.0,
        duration=120.0,
        volume=0.85,
        is_playing=True,
        is_paused=False,
        is_muted=False,
        spectrum_bars=np.zeros(20, dtype=np.float32),
        spectrum_peaks=np.zeros(20, dtype=np.float32),
    )
    assert len(lines_80x24) <= 24

    # Test small terminal 50x16
    lines_50x16 = renderer.build_frame(
        cols=50,
        lines=16,
        playlist=pm,
        current_pos=0.0,
        duration=0.0,
        volume=0.5,
        is_playing=False,
        is_paused=False,
        is_muted=False,
        spectrum_bars=np.zeros(10, dtype=np.float32),
        spectrum_peaks=np.zeros(10, dtype=np.float32),
    )
    assert len(lines_50x16) <= 16

    # Test wide terminal 140x45
    lines_140x45 = renderer.build_frame(
        cols=140,
        lines=45,
        playlist=pm,
        current_pos=45.0,
        duration=180.0,
        volume=1.0,
        is_playing=True,
        is_paused=False,
        is_muted=False,
        spectrum_bars=np.zeros(40, dtype=np.float32),
        spectrum_peaks=np.zeros(40, dtype=np.float32),
    )
    assert len(lines_140x45) <= 45


def test_visualizer_only_mode():
    renderer = UIRenderer()
    pm = PlaylistManager(["song1.mp3"])

    lines_viz = renderer.build_frame(
        cols=80,
        lines=30,
        playlist=pm,
        current_pos=10.0,
        duration=100.0,
        volume=1.0,
        is_playing=True,
        is_paused=False,
        is_muted=False,
        spectrum_bars=np.zeros(20, dtype=np.float32),
        spectrum_peaks=np.zeros(20, dtype=np.float32),
        visualizer_only=True,
    )
    assert len(lines_viz) <= 30
    full_text = "\n".join(lines_viz)
    # Visualizer only mode fills the frame with pure visualizer lines
    assert "UP NEXT" not in full_text
    assert "song1.mp3" not in full_text


def test_playlist_sidebar_toggle():
    renderer = UIRenderer()
    pm = PlaylistManager(["track_alpha.mp3", "track_beta.mp3"])

    # Test with playlist visible (default)
    lines_with_pl = renderer.build_frame(
        cols=80,
        lines=24,
        playlist=pm,
        current_pos=10.0,
        duration=120.0,
        volume=0.8,
        is_playing=True,
        is_paused=False,
        is_muted=False,
        spectrum_bars=np.zeros(20, dtype=np.float32),
        spectrum_peaks=np.zeros(20, dtype=np.float32),
        show_playlist=True,
    )
    text_with_pl = "\n".join(lines_with_pl)
    # Song name should appear on left playlist with star for active track
    assert "*" in text_with_pl
    assert "track alpha" in text_with_pl
    assert "UP NEXT" not in text_with_pl

    # Test with playlist hidden ('l' key toggled off)
    lines_without_pl = renderer.build_frame(
        cols=80,
        lines=24,
        playlist=pm,
        current_pos=10.0,
        duration=120.0,
        volume=0.8,
        is_playing=True,
        is_paused=False,
        is_muted=False,
        spectrum_bars=np.zeros(20, dtype=np.float32),
        spectrum_peaks=np.zeros(20, dtype=np.float32),
        show_playlist=False,
    )
    text_without_pl = "\n".join(lines_without_pl)
    # The left playlist sidebar is gone
    assert "track beta" not in text_without_pl
    assert "UP NEXT" not in text_without_pl


