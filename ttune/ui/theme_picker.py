"""Interactive theme and visualizer style customizer screen."""

import os
from typing import Optional

from ttune.config import (
    COLOR_BORDER,
    COLOR_BORDER_DIM,
    COLOR_KEY_BADGE,
    COLOR_KEY_TEXT,
    COLOR_TAG_GREEN,
    COLOR_TEXT_DIM,
    COLOR_TITLE,
    THEME_PALETTES,
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


def render_shape_preview(shape_key: str, palette_name: str) -> str:
    """Render a mini 3-bar equalizer preview of the chosen shape and theme."""
    shape = VISUALIZER_SHAPES.get(shape_key, VISUALIZER_SHAPES["brick"])
    grad = THEME_PALETTES.get(palette_name, THEME_PALETTES["cyberpunk"])
    char = shape.get("char", "█")
    half = shape.get("half", "▄")
    width = shape.get("width", 2)
    gap = " " * shape.get("gap", 1)

    c1 = color_fg(get_gradient_color(0.3, gradient=grad))
    c2 = color_fg(get_gradient_color(0.7, gradient=grad))
    c3 = color_fg(get_gradient_color(1.0, gradient=grad))

    # Top row
    row_top = f"  {char * width}{gap}{char * width}{gap}{c3}{half * width}{STYLE_RESET}"
    # Bottom row
    row_bot = f"{c1}{char * width}{gap}{c2}{char * width}{gap}{c1}{char * width}{STYLE_RESET}"
    return f"{row_top}\n{row_bot}"


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

    selected_row = 0  # 0: Color Theme, 1: Visualizer Shape, 2: Peak Caps

    palette_keys = list(THEME_PALETTES.keys())
    shape_keys = list(VISUALIZER_SHAPES.keys())

    while True:
        cols, lines = screen.get_size()
        cols = max(55, cols)
        lines = max(18, lines)

        out = []
        top_dash = cols - 32
        out.append(f"{c_border}{BOX_TOP_LEFT}{BOX_HORIZ * 3} [ THEME & VISUALIZER STYLES ] {BOX_HORIZ * top_dash}{BOX_TOP_RIGHT}{STYLE_RESET}")
        out.append(f"{c_border}{BOX_VERT}{STYLE_RESET}{' ' * (cols - 2)}{c_border}{BOX_VERT}{STYLE_RESET}")

        # Subtitle
        out.append(f"{c_border}{BOX_VERT}{STYLE_RESET}   {c_green}{STYLE_BOLD}CUSTOMIZE AUDIO SPECTRUM VISUALS & RGB PALETTES{STYLE_RESET}")
        out.append(f"{c_border_dim}{BOX_HORIZ * cols}{STYLE_RESET}")
        out.append("")

        # 1. Color Palette Row
        is_sel_0 = selected_row == 0
        ptr0 = f"{c_green}▶{STYLE_RESET} " if is_sel_0 else "  "
        cur_pal = theme_config.palette_name
        swatch = render_palette_swatch(cur_pal, length=16)
        pal_line = (
            f" {ptr0}{c_badge}[1] Color Palette:{STYLE_RESET}  "
            f"{c_title}{STYLE_BOLD}◀ {cur_pal.upper():12s} ▶{STYLE_RESET}   {swatch}"
        )
        out.append(pal_line)
        out.append("")

        # 2. Shape Row
        is_sel_1 = selected_row == 1
        ptr1 = f"{c_green}▶{STYLE_RESET} " if is_sel_1 else "  "
        cur_shape = theme_config.shape_name
        shape_info = VISUALIZER_SHAPES[cur_shape]
        shape_line = (
            f" {ptr1}{c_badge}[2] Equalizer Shape:{STYLE_RESET} "
            f"{c_title}{STYLE_BOLD}◀ {shape_info['name']:16s} ▶{STYLE_RESET}  "
            f"{c_dim}({shape_info['description']}){STYLE_RESET}"
        )
        out.append(shape_line)
        out.append("")

        # 3. Peak Caps Row
        is_sel_2 = selected_row == 2
        ptr2 = f"{c_green}▶{STYLE_RESET} " if is_sel_2 else "  "
        peak_status = f"{c_green}[ENABLED]{STYLE_RESET}" if theme_config.show_peaks else f"{c_dim}[DISABLED]{STYLE_RESET}"
        peak_line = (
            f" {ptr2}{c_badge}[3] Peak Decay Caps:{STYLE_RESET} "
            f"{peak_status}  {c_dim}(Press [3] or Space to toggle){STYLE_RESET}"
        )
        out.append(peak_line)
        out.append("")

        # 4. Live Visualizer Preview Box
        out.append(f"   {c_dim}─── LIVE SPECTRUM PREVIEW ───{STYLE_RESET}")
        preview_shape = VISUALIZER_SHAPES[cur_shape]
        w = preview_shape["width"]
        g = " " * preview_shape["gap"]
        ch = preview_shape["char"]
        hf = preview_shape["half"]

        grad = theme_config.gradient
        # 8 preview bars
        p_bars = [0.35, 0.55, 0.90, 1.0, 0.75, 0.85, 0.50, 0.30]
        # 3 rows preview
        for r in (3, 2, 1):
            row_c = []
            for b in p_bars:
                frac = r / 3.0
                prev = (r - 1) / 3.0
                color_str = color_fg(get_gradient_color(frac, gradient=grad))
                if b >= frac:
                    row_c.append(f"{color_str}{ch * w}")
                elif b > prev:
                    row_c.append(f"{color_str}{hf * w}")
                else:
                    row_c.append(" " * w)
                row_c.append(g)
            out.append(f"   {''.join(row_c)}{STYLE_RESET}")

        while len(out) < lines - 3:
            out.append("")

        out.append(f"{c_border_dim}{BOX_HORIZ * cols}{STYLE_RESET}")
        footer_help = (
            f" {c_badge}↑/↓{STYLE_RESET} {c_key_txt}SELECT{STYLE_RESET}   "
            f"{c_badge}←/→{STYLE_RESET} {c_key_txt}CHANGE{STYLE_RESET}   "
            f"{c_badge}ENTER/B/ESC{STYLE_RESET} {c_key_txt}DONE / BACK{STYLE_RESET}"
        )
        out.append(footer_help)

        screen.render_frame(out[:lines])

        key = keyboard.read_key(timeout=0.05)
        if not key:
            continue

        k = key.upper()
        if key == "UP":
            selected_row = (selected_row - 1) % 3
        elif key == "DOWN":
            selected_row = (selected_row + 1) % 3
        elif key in ("LEFT", "h", "H"):
            if selected_row == 0:
                theme_config.prev_palette()
            elif selected_row == 1:
                theme_config.prev_shape()
            elif selected_row == 2:
                theme_config.show_peaks = not theme_config.show_peaks
        elif key in ("RIGHT", "l", "L"):
            if selected_row == 0:
                theme_config.next_palette()
            elif selected_row == 1:
                theme_config.next_shape()
            elif selected_row == 2:
                theme_config.show_peaks = not theme_config.show_peaks
        elif k == "1":
            theme_config.next_palette()
        elif k == "2":
            theme_config.next_shape()
        elif k in ("3", "SPACE") and selected_row == 2:
            theme_config.show_peaks = not theme_config.show_peaks
        elif k in ("ENTER", "B", "Q", "ESCAPE"):
            break

    return theme_config
