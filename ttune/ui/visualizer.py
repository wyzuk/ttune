"""Real-time spectrum equalizer renderer supporting multiple shape styles and color themes."""

import math
from typing import List, Optional, Tuple

import numpy as np

from ttune.config import PEAK_COLOR, ThemeConfig
from ttune.ui.theme import (
    BLOCK_FULL,
    BLOCK_LOWER_HALF,
    PEAK_MARK,
    STYLE_RESET,
    color_fg,
    get_gradient_color,
)


class SpectrumVisualizer:
    """Renders the real-time FFT spectrum equalizer into terminal character rows."""

    def __init__(self):
        pass

    def calculate_layout(
        self,
        available_width: int,
        theme_config: Optional[ThemeConfig] = None,
    ) -> Tuple[int, int, int, int]:
        """Calculate optimal bar width, gap, total bars, and left margin for given width."""
        width = max(10, available_width)

        if theme_config and theme_config.shape:
            shape = theme_config.shape
            bar_width = shape.get("width", 2)
            gap = shape.get("gap", 1)
        else:
            if width >= 70:
                bar_width = 2
                gap = 1
            elif width >= 40:
                bar_width = 2
                gap = 1
            elif width >= 25:
                bar_width = 1
                gap = 1
            else:
                bar_width = 1
                gap = 0

        slot = bar_width + gap
        num_bars = max(4, (width - 2) // slot)
        used_width = num_bars * slot - gap
        left_pad = max(0, (width - used_width) // 2)

        return num_bars, bar_width, gap, left_pad

    def render(
        self,
        width: int,
        height: int,
        bar_heights: np.ndarray,
        peak_heights: np.ndarray,
        theme_config: Optional[ThemeConfig] = None,
    ) -> List[str]:
        """Render spectrum visualizer into a list of strings (one string per row).

        Args:
            width: Available inner width in characters.
            height: Available inner height in rows.
            bar_heights: Normalized bar heights in range [0.0, 1.0].
            peak_heights: Normalized peak cap heights in range [0.0, 1.0].
            theme_config: Active theme and visualizer configuration.

        Returns:
            List of formatted lines from top row to bottom row.
        """
        if height <= 0 or width <= 0:
            return []

        shape_info = theme_config.shape if theme_config else {}
        gradient = theme_config.gradient if theme_config else None
        show_peaks = theme_config.show_peaks if theme_config else True

        char_full = shape_info.get("char", BLOCK_FULL)
        char_half = shape_info.get("half", BLOCK_LOWER_HALF)

        num_bars, bar_width, gap, left_pad = self.calculate_layout(width, theme_config)
        bar_block = char_full * bar_width
        half_block = char_half * bar_width
        peak_block = PEAK_MARK * bar_width
        empty_block = " " * bar_width
        gap_block = " " * gap
        pad_str = " " * left_pad

        # Clamp and scale arrays to match num_bars
        n = len(bar_heights)
        if n != num_bars:
            if n > 0:
                indices = np.linspace(0, n - 1, num_bars).astype(int)
                b_vals = bar_heights[indices]
                p_vals = peak_heights[indices]
            else:
                b_vals = np.zeros(num_bars, dtype=np.float32)
                p_vals = np.zeros(num_bars, dtype=np.float32)
        else:
            b_vals = bar_heights
            p_vals = peak_heights

        lines: List[str] = []

        # Render from top row (height) down to bottom row (1)
        for r in range(height, 0, -1):
            row_frac = r / float(height)

            # Color for this height slice from active palette
            rgb = get_gradient_color(row_frac, gradient=gradient)
            color_code = color_fg(rgb)
            peak_color_code = color_fg(PEAK_COLOR)

            row_chunks = [pad_str]

            for i in range(num_bars):
                val = float(b_vals[i])
                peak = float(p_vals[i])

                peak_row = int(math.ceil(peak * height))
                is_peak_here = (
                    show_peaks
                    and peak_row == r
                    and peak > 0.05
                    and val < (r / float(height))
                )

                if val >= row_frac:
                    row_chunks.append(f"{color_code}{bar_block}")
                elif val >= (row_frac - 0.5 / float(height)):
                    row_chunks.append(f"{color_code}{half_block}")
                elif is_peak_here:
                    row_chunks.append(f"{peak_color_code}{peak_block}")
                else:
                    row_chunks.append(empty_block)

                if gap > 0 and i < num_bars - 1:
                    row_chunks.append(gap_block)

            row_chunks.append(STYLE_RESET)
            row_str = "".join(row_chunks)
            lines.append(row_str)

        return lines
