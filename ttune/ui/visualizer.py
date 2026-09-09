"""Real-time spectrum equalizer renderer using LED brick blocks and truecolor gradients."""

import math
from typing import List, Tuple

import numpy as np

from ttune.config import PEAK_COLOR, PEAK_COLOR_ALT
from ttune.ui.theme import (
    BLOCK_FULL,
    BLOCK_LOWER_HALF,
    BLOCK_OVERLINE,
    PEAK_MARK,
    SUB_BLOCKS,
    STYLE_RESET,
    color_fg,
    get_gradient_color,
)


class SpectrumVisualizer:
    """Renders the real-time FFT spectrum equalizer into terminal character rows."""

    def __init__(self):
        pass

    def calculate_layout(self, available_width: int) -> Tuple[int, int, int, int]:
        """Calculate optimal bar width, gap, total bars, and left margin for given width.

        Returns:
            (num_bars, bar_width, gap, left_padding)
        """
        width = max(10, available_width)

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
    ) -> List[str]:
        """Render spectrum visualizer into a list of strings (one string per row).

        Args:
            width: Available inner width in characters.
            height: Available inner height in rows.
            bar_heights: Normalized bar heights in range [0.0, 1.0].
            peak_heights: Normalized peak cap heights in range [0.0, 1.0].

        Returns:
            List of formatted lines from top row to bottom row.
        """
        if height <= 0 or width <= 0:
            return []

        num_bars, bar_width, gap, left_pad = self.calculate_layout(width)
        bar_block = BLOCK_FULL * bar_width
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
            prev_frac = (r - 1) / float(height)

            # Color for this height slice
            rgb = get_gradient_color(row_frac)
            color_code = color_fg(rgb)
            peak_color_code = color_fg(PEAK_COLOR)

            row_chunks = [pad_str]

            for i in range(num_bars):
                val = float(b_vals[i])
                peak = float(p_vals[i])

                # Check if peak cap is at this row
                peak_row = int(math.ceil(peak * height))
                is_peak_here = (peak_row == r and peak > 0.05 and val < (r / float(height)))

                if val >= row_frac:
                    # Solid brick
                    row_chunks.append(f"{color_code}{bar_block}")
                elif val > prev_frac:
                    # Partial brick for smoother height rendering
                    sub_val = (val - prev_frac) / (row_frac - prev_frac)
                    sub_idx = max(1, min(8, int(sub_val * 8)))
                    char = SUB_BLOCKS[sub_idx] * bar_width
                    row_chunks.append(f"{color_code}{char}")
                elif is_peak_here:
                    # Floating peak cap
                    row_chunks.append(f"{peak_color_code}{peak_block}")
                else:
                    row_chunks.append(empty_block)

                if gap > 0 and i < num_bars - 1:
                    row_chunks.append(gap_block)

            # Reset style at end of each row
            row_chunks.append(STYLE_RESET)
            row_str = "".join(row_chunks)

            # Right pad to full width if needed
            lines.append(row_str)

        return lines
