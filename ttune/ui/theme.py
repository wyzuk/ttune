"""Cyberpunk color palette, ANSI truecolor escape utilities, and box drawing symbols."""

from typing import List, Tuple

from ttune.config import (
    COLOR_ALBUM,
    COLOR_ARTIST,
    COLOR_BORDER,
    COLOR_BORDER_DIM,
    COLOR_KEY_BADGE,
    COLOR_KEY_TEXT,
    COLOR_LABEL,
    COLOR_PROGRESS_BAR,
    COLOR_PROGRESS_BG,
    COLOR_TAG_GREEN,
    COLOR_TAG_PURPLE,
    COLOR_TEXT_DIM,
    COLOR_TITLE,
    PEAK_COLOR,
    SPECTRUM_GRADIENT,
)

# Box drawing characters
BOX_HORIZ = "─"
BOX_VERT = "│"
BOX_TOP_LEFT = "┌"
BOX_TOP_RIGHT = "┐"
BOX_BOTTOM_LEFT = "└"
BOX_BOTTOM_RIGHT = "┘"
BOX_T_DOWN = "┬"
BOX_T_UP = "┴"
BOX_T_RIGHT = "├"
BOX_T_LEFT = "┤"
BOX_CROSS = "┼"

# Visualizer brick blocks
BLOCK_FULL = "█"
BLOCK_UPPER_HALF = "▀"
BLOCK_LOWER_HALF = "▄"
BLOCK_OVERLINE = "▔"
PEAK_MARK = "━"
SUB_BLOCKS = [" ", " ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

# Progress bar characters
PROG_FILLED = "━"
PROG_KNOB = "●"
PROG_EMPTY = "─"


def rgb_fg(r: int, g: int, b: int) -> str:
    """ANSI 24-bit Truecolor foreground sequence."""
    return f"\033[38;2;{r};{g};{b}m"


def rgb_bg(r: int, g: int, b: int) -> str:
    """ANSI 24-bit Truecolor background sequence."""
    return f"\033[48;2;{r};{g};{b}m"


def color_fg(rgb: Tuple[int, int, int]) -> str:
    return rgb_fg(rgb[0], rgb[1], rgb[2])


def color_bg(rgb: Tuple[int, int, int]) -> str:
    return rgb_bg(rgb[0], rgb[1], rgb[2])


STYLE_RESET = "\033[0m"
STYLE_BOLD = "\033[1m"
STYLE_DIM = "\033[2m"
STYLE_ITALIC = "\033[3m"


def interpolate_color(c1: Tuple[int, int, int], c2: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    """Linearly interpolate between two RGB colors."""
    factor = max(0.0, min(1.0, factor))
    r = int(c1[0] + (c2[0] - c1[0]) * factor)
    g = int(c1[1] + (c2[1] - c1[1]) * factor)
    b = int(c1[2] + (c2[2] - c1[2]) * factor)
    return (r, g, b)


def get_gradient_color(height_fraction: float) -> Tuple[int, int, int]:
    """Map a vertical fraction (0.0 at bottom to 1.0 at top) to the spectrum gradient."""
    fraction = max(0.0, min(1.0, height_fraction))
    gradient = SPECTRUM_GRADIENT
    n_stops = len(gradient)
    if n_stops == 1:
        return gradient[0]

    pos = fraction * (n_stops - 1)
    idx = int(pos)
    if idx >= n_stops - 1:
        return gradient[-1]

    sub_factor = pos - idx
    return interpolate_color(gradient[idx], gradient[idx + 1], sub_factor)
