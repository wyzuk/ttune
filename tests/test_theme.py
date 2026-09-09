"""Tests for ThemeConfig, visualizer shapes, and palettes."""

import numpy as np
from ttune.config import THEME_PALETTES, VISUALIZER_SHAPES, ThemeConfig
from ttune.ui.theme import get_gradient_color
from ttune.ui.visualizer import SpectrumVisualizer


def test_theme_config_defaults():
    tc = ThemeConfig()
    assert tc.palette_name in THEME_PALETTES
    assert tc.shape_name in VISUALIZER_SHAPES
    assert tc.palette_name == "cyberpunk"
    assert tc.shape_name == "brick"


def test_theme_palette_switching():
    tc = ThemeConfig()
    tc.next_palette()
    assert tc.palette_name == "matrix"
    tc.prev_palette()
    assert tc.palette_name == "cyberpunk"


def test_visualizer_shapes_switching():
    tc = ThemeConfig()
    tc.next_shape()
    assert tc.shape_name == "fat"
    tc.next_shape()
    assert tc.shape_name == "thin"


def test_get_gradient_color():
    palette = THEME_PALETTES["cyberpunk"]
    c0 = get_gradient_color(0.0, palette)
    assert c0 == palette[0]
    c1 = get_gradient_color(1.0, palette)
    assert c1 == palette[-1]


def test_spectrum_visualizer_theme():
    tc = ThemeConfig(palette_name="fire", shape_name="dots")
    vis = SpectrumVisualizer()
    bars = np.linspace(0.1, 0.9, 16)
    peaks = bars + 0.05
    rendered = vis.render(width=80, height=10, bar_heights=bars, peak_heights=peaks, theme_config=tc)
    assert len(rendered) == 10
    char_dot = tc.shape["char"]
    assert any(char_dot in line for line in rendered)