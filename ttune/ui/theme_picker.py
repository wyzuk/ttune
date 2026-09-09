"""Interactive theme and visualizer style customizer screen."""

import os
from typing import Optional

import numpy as np

from ttune.config import (
    COLOR_BORDER,
    COLOR_BORDER_DIM,
    COLOR_KEY_BADGE,
    COLOR_KEY_TEXT,
    COLOR_TAG_GREEN,
    COLOR_TEXT_DIM,
    COLOR_TITLE,
    THEME_PALETTES,
    VISUALIZER_MODES,
    VISUALIZER_SHAPES,
    ThemeConfig,
)
from ttune.input.keyboard import KeyboardReader
from ttune.ui.screen import TerminalScreen
from ttune.ui.theme import (
    BOX_BOTTOM_LEFT,
    BOX_BOTTOM_RIGHT,
    BOX_HORIZ,
    BOX_TOP_LEFT,
    BOX_TOP_RIGHT,
    BOX_VERT,
    STYLE_BOLD,
    STYLE_DIM,
    STYLE_RESET,
    color_fg,
    get_gradient_color,
)
from ttune.ui.visualizer import SpectrumVisualizer


def render_palette_swatch(palette_name: str, length: int = 14) -> str:
    """Render a colored mini swatch of the palette using truecolor blocks."""
    grad = THEME_PALETTES.get(palette_name, THEME_PALETTES["cyberpunk"])
    chunks = []
    for i in range(length):
        frac = i / float(length - 1) if length > 1 else 0.0
        rgb = get_gradient_color(frac, gradient=grad)
        chunks.append(f"{color_fg(rgb)}█")
    chunks.append(STYLE_RESET)
    return "".join(chunks)


def show_theme_picker(
    screen: TerminalScreen,
    keyboard: KeyboardReader,
    theme_config: ThemeConfig,
) -> ThemeConfig:
    """Run interactive theme and visualizer style picker until user exits."""
    c_border = color_fg(COLOR_BORDER)
    c_border_dim = color_fg(COLOR_BORDER_DIM)
    c_green = color_fg(COLOR_TAG_GREEN)
    c_title = color_fg(COLOR_TITLE)
    c_badge = color_fg(COLOR_KEY_BADGE)
    c_dim = color_fg(COLOR_TEXT_DIM)
    c_key_txt = color_fg(COLOR_KEY_TEXT)

    selected_row = 0  # 0: Palette, 1: Shape, 2: Visualizer Mode, 3: Peak Caps
    vis_preview = SpectrumVisualizer()

    while True:
        cols, lines = screen.get_size()
        cols = max(55, cols)
        lines = max(18, lines)

        out = []
        top_dash = max(0, cols - 32)
        out.append(f"{c_border}{BOX_TOP_LEFT}{BOX_HORIZ * 3} [ THEME & VISUALIZER STYLES ] {BOX_HORIZ * top_dash}{BOX_TOP_RIGHT}{STYLE_RESET}")
        out.append(f"{c_border}{BOX_VERT}{STYLE_RESET}{' ' * (cols - 2)}{c_border}{BOX_VERT}{STYLE_RESET}")

        # Subtitle
        out.append(f"{c_border}{BOX_VERT}{STYLE_RESET}   {c_green}{STYLE_BOLD}CUSTOMIZE AUDIO SPECTRUM VISUALS & RGB PALETTES{STYLE_RESET}")
        out.append(f"{c_border_dim}{BOX_HORIZ * cols}{STYLE_RESET}")
        out.append("")

        # 1. Color Palette Row
        is_sel_0 = selected_row == 0
        ptr0 = f"{c_green}►{STYLE_RESET} " if is_sel_0 else "  "
        cur_pal = theme_config.palette_name
        swatch = render_palette_swatch(cur_pal, length=16)
        pal_line = (
            f" {ptr0}{c_badge}[1] Color Palette:{STYLE_RESET}  "
            f"{c_title}{STYLE_BOLD}◄ {cur_pal.upper():13s} ►{STYLE_RESET}   {swatch}"
        )
        out.append(pal_line)
        out.append("")

        # 2. Shape Row
        is_sel_1 = selected_row == 1
        ptr1 = f"{c_green}►{STYLE_RESET} " if is_sel_1 else "  "
        cur_shape = theme_config.shape_name
        shape_info = VISUALIZER_SHAPES.get(cur_shape, VISUALIZER_SHAPES["brick"])
        shape_line = (
            f" {ptr1}{c_badge}[2] Equalizer Shape:{STYLE_RESET} "
            f"{c_title}{STYLE_BOLD}◄ {shape_info['name']:22s} ►{STYLE_RESET}  "
            f"{c_dim}({shape_info['description']}){STYLE_RESET}"
        )
        out.append(shape_line)
        out.append("")

        # 3. Visualizer Mode Row (Middle visualizer, bottom-up, etc.)
        is_sel_2 = selected_row == 2
        ptr2 = f"{c_green}►{STYLE_RESET} " if is_sel_2 else "  "
        mode_info = theme_config.mode_info
        mode_line = (
            f" {ptr2}{c_badge}[3] Visualizer Mode:{STYLE_RESET} "
            f"{c_title}{STYLE_BOLD}◄ {mode_info['name']:22s} ►{STYLE_RESET}  "
            f"{c_dim}({mode_info['description']}){STYLE_RESET}"
        )
        out.append(mode_line)
        out.append("")

        # 4. Peak Caps Row
        is_sel_3 = selected_row == 3
        ptr3 = f"{c_green}►{STYLE_RESET} " if is_sel_3 else "  "
        peak_status = f"{c_green}[ENABLED]{STYLE_RESET}" if theme_config.show_peaks else f"{c_dim}[DISABLED]{STYLE_RESET}"
        peak_line = (
            f" {ptr3}{c_badge}[4] Peak Decay Caps:{STYLE_RESET} "
            f"{peak_status}  {c_dim}(Press [4] or Space to toggle){STYLE_RESET}"
        )
        out.append(peak_line)
        out.append("")

        # 5. Live Visualizer Preview Box
        mode_label = mode_info['name'].upper()
        out.append(f"   {c_dim}─── LIVE SPECTRUM PREVIEW [{mode_label}] ───{STYLE_RESET}")
        
        # 16 preview bars with nice audio curve
        p_bars = np.array([0.20, 0.40, 0.65, 0.85, 0.95, 0.75, 0.60, 0.45, 0.70, 0.90, 0.80, 0.55, 0.40, 0.30, 0.20, 0.15], dtype=np.float32)
        p_peaks = np.clip(p_bars + 0.06, 0.0, 1.0)
        
        preview_h = 5
        preview_lines = vis_preview.render(
            width=max(20, cols - 6),
            height=preview_h,
            bar_heights=p_bars,
            peak_heights=p_peaks,
            theme_config=theme_config,
        )
        for pl in preview_lines:
            out.append(f"   {pl}")

        while len(out) < lines - 3:
            out.append("")

        out.append(f"{c_border_dim}{BOX_HORIZ * cols}{STYLE_RESET}")
        footer_help = (
            f" {c_badge}↑/↓{STYLE_RESET} {c_key_txt}SELECT{STYLE_RESET}   "
            f"{c_badge}←/→{STYLE_RESET} {c_key_txt}CHANGE{STYLE_RESET}   "
            f"{c_badge}[1-4]{STYLE_RESET} {c_key_txt}QUICK SWITCH{STYLE_RESET}   "
            f"{c_badge}ENTER/B/ESC{STYLE_RESET} {c_key_txt}DONE / BACK{STYLE_RESET}"
        )
        out.append(footer_help)

        screen.render_frame(out[:lines])

        key = keyboard.read_key(timeout=0.05)
        if not key:
            continue

        k = key.upper()
        if key == "UP":
            selected_row = (selected_row - 1) % 4
        elif key == "DOWN":
            selected_row = (selected_row + 1) % 4
        elif key in ("LEFT", "h", "H"):
            if selected_row == 0:
                theme_config.prev_palette()
            elif selected_row == 1:
                theme_config.prev_shape()
            elif selected_row == 2:
                theme_config.prev_mode()
            elif selected_row == 3:
                theme_config.show_peaks = not theme_config.show_peaks
        elif key in ("RIGHT", "l", "L"):
            if selected_row == 0:
                theme_config.next_palette()
            elif selected_row == 1:
                theme_config.next_shape()
            elif selected_row == 2:
                theme_config.next_mode()
            elif selected_row == 3:
                theme_config.show_peaks = not theme_config.show_peaks
        elif k == "1":
            theme_config.next_palette()
        elif k == "2":
            theme_config.next_shape()
        elif k == "3":
            theme_config.next_mode()
        elif k in ("4", "SPACE"):
            theme_config.show_peaks = not theme_config.show_peaks
        elif k in ("ENTER", "B", "Q", "ESCAPE"):
            break

    return theme_config

