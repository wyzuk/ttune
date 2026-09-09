"""Real-time spectrum equalizer renderer supporting multiple shape styles and color themes."""

import math
from typing import List, Optional, Tuple

import numpy as np

from ttune.config import COLOR_BORDER_DIM, PEAK_COLOR, ThemeConfig
from ttune.ui.theme import (
    BLOCK_FULL,
    BLOCK_LOWER_HALF,
    BLOCK_UPPER_HALF,
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
        num_bars = max(4, (width - 2) // slot) if slot > 0 else 4
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
        mode = theme_config.viz_mode if theme_config else "bottom"

        char_full = shape_info.get("char", BLOCK_FULL)
        char_half = shape_info.get("half", BLOCK_LOWER_HALF)

        num_bars, bar_width, gap, left_pad = self.calculate_layout(width, theme_config)
        bar_block = char_full * bar_width
        half_block = char_half * bar_width
        upper_half_block = BLOCK_UPPER_HALF * bar_width
        peak_block = PEAK_MARK * bar_width
        empty_block = " " * bar_width
        gap_block = " " * gap
        pad_str = " " * left_pad

        n = len(bar_heights)
        if n != num_bars:
            if n > 0:
                indices = np.linspace(0, n - 1, num_bars).astype(int)
                b_vals = bar_heights[indices].copy()
                p_vals = peak_heights[indices].copy()
            else:
                b_vals = np.zeros(num_bars, dtype=np.float32)
                p_vals = np.zeros(num_bars, dtype=np.float32)
        else:
            b_vals = bar_heights.copy()
            p_vals = peak_heights.copy()

        HEADROOM = 0.84
        b_vals = np.clip(b_vals * HEADROOM, 0.0, 1.0)
        p_vals = np.clip(p_vals * HEADROOM, 0.0, 1.0)

        lines: List[str] = []

        if mode == "middle":
            mid = (height + 1) / 2.0
            max_dist = max(1.0, (height - 1) / 2.0 if height > 1 else 1.0)
            peak_color_code = color_fg(PEAK_COLOR)

            for r in range(height, 0, -1):
                dist = abs(r - mid)
                frac = min(1.0, dist / max_dist)
                rgb = get_gradient_color(frac, gradient=gradient)
                color_code = color_fg(rgb)

                row_chunks = [pad_str]
                for i in range(num_bars):
                    val = float(b_vals[i])
                    peak = float(p_vals[i])
                    val_dist = val * max_dist
                    peak_dist = peak * max_dist

                    is_peak_here = (
                        show_peaks
                        and abs(dist - peak_dist) < 0.6
                        and peak > 0.08
                        and dist > val_dist + 0.3
                    )

                    if dist <= val_dist:
                        row_chunks.append(f"{color_code}{bar_block}")
                    elif dist <= val_dist + 0.5:
                        if r > mid:
                            row_chunks.append(f"{color_code}{half_block}")
                        elif r < mid:
                            row_chunks.append(f"{color_code}{upper_half_block}")
                        else:
                            row_chunks.append(f"{color_code}{bar_block}")
                    elif abs(r - mid) < 0.6:
                        if val > 0.03:
                            row_chunks.append(f"{color_code}{half_block}")
                        else:
                            dim_c = color_fg(COLOR_BORDER_DIM)
                            row_chunks.append(f"{dim_c}{'─' * bar_width}")
                    elif is_peak_here:
                        p_mark = peak_block if r > mid else ("_" * bar_width)
                        row_chunks.append(f"{peak_color_code}{p_mark}")
                    else:
                        row_chunks.append(empty_block)

                    if gap > 0 and i < num_bars - 1:
                        row_chunks.append(gap_block)

                row_chunks.append(STYLE_RESET)
                lines.append("".join(row_chunks))

            return lines

        elif mode == "middle_wave":
            mid = (height + 1) / 2.0
            max_dist = max(1.0, (height - 1) / 2.0 if height > 1 else 1.0)
            peak_color_code = color_fg(PEAK_COLOR)

            for r in range(height, 0, -1):
                dist = abs(r - mid)
                frac = min(1.0, dist / max_dist)
                rgb = get_gradient_color(frac, gradient=gradient)
                color_code = color_fg(rgb)

                row_chunks = [pad_str]
                for i in range(num_bars):
                    val = float(b_vals[i])
                    peak = float(p_vals[i])
                    val_dist = val * max_dist
                    peak_dist = peak * max_dist

                    if abs(dist - val_dist) < 0.6 and val > 0.05:
                        if r > mid:
                            row_chunks.append(f"{color_code}{half_block}")
                        else:
                            row_chunks.append(f"{color_code}{upper_half_block}")
                    elif dist < val_dist:
                        row_chunks.append(f"{color_code}{bar_block}")
                    elif abs(r - mid) < 0.6:
                        dim_c = color_fg(COLOR_BORDER_DIM)
                        row_chunks.append(f"{dim_c}{'━' * bar_width if val > 0.05 else '─' * bar_width}")
                    elif show_peaks and abs(dist - peak_dist) < 0.6 and peak > 0.08:
                        row_chunks.append(f"{peak_color_code}{peak_block if r > mid else '_' * bar_width}")
                    else:
                        row_chunks.append(empty_block)

                    if gap > 0 and i < num_bars - 1:
                        row_chunks.append(gap_block)

                row_chunks.append(STYLE_RESET)
                lines.append("".join(row_chunks))

            return lines

        elif mode == "top_down":
            peak_color_code = color_fg(PEAK_COLOR)

            for r in range(height, 0, -1):
                row_frac = (height - r + 1) / float(height)
                rgb = get_gradient_color(row_frac, gradient=gradient)
                color_code = color_fg(rgb)

                row_chunks = [pad_str]
                for i in range(num_bars):
                    val = float(b_vals[i])
                    peak = float(p_vals[i])
                    peak_row = height - int(math.ceil(peak * height)) + 1

                    is_peak_here = (
                        show_peaks
                        and peak_row == r
                        and peak > 0.05
                        and val < row_frac
                    )

                    if val >= row_frac:
                        row_chunks.append(f"{color_code}{bar_block}")
                    elif val >= (row_frac - 0.5 / float(height)):
                        row_chunks.append(f"{color_code}{upper_half_block}")
                    elif is_peak_here:
                        row_chunks.append(f"{peak_color_code}{'_' * bar_width}")
                    else:
                        row_chunks.append(empty_block)

                    if gap > 0 and i < num_bars - 1:
                        row_chunks.append(gap_block)

                row_chunks.append(STYLE_RESET)
                lines.append("".join(row_chunks))

            return lines

        elif mode == "stereo_split":
            mid = (height + 1) / 2.0
            max_dist = max(1.0, (height - 1) / 2.0 if height > 1 else 1.0)
            peak_color_code = color_fg(PEAK_COLOR)

            for r in range(height, 0, -1):
                dist = abs(r - mid)
                frac = min(1.0, dist / max_dist)
                rgb = get_gradient_color(frac, gradient=gradient)
                color_code = color_fg(rgb)

                row_chunks = [pad_str]
                for i in range(num_bars):
                    val = float(b_vals[i])
                    peak = float(p_vals[i])
                    val_dist = val * max_dist
                    peak_dist = peak * max_dist

                    if r >= mid:
                        if dist <= val_dist:
                            row_chunks.append(f"{color_code}{bar_block}")
                        elif dist <= val_dist + 0.5:
                            row_chunks.append(f"{color_code}{half_block}")
                        elif show_peaks and abs(dist - peak_dist) < 0.6 and peak > 0.08:
                            row_chunks.append(f"{peak_color_code}{peak_block}")
                        else:
                            row_chunks.append(empty_block)
                    else:
                        if dist <= val_dist:
                            row_chunks.append(f"{color_code}{bar_block}")
                        elif dist <= val_dist + 0.5:
                            row_chunks.append(f"{color_code}{upper_half_block}")
                        elif show_peaks and abs(dist - peak_dist) < 0.6 and peak > 0.08:
                            row_chunks.append(f"{peak_color_code}{'_' * bar_width}")
                        else:
                            row_chunks.append(empty_block)

                    if gap > 0 and i < num_bars - 1:
                        row_chunks.append(gap_block)

                row_chunks.append(STYLE_RESET)
                lines.append("".join(row_chunks))

            return lines

        else:
            for r in range(height, 0, -1):
                row_frac = r / float(height)

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

