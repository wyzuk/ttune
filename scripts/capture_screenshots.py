"""Generate preview screenshots of the ttune terminal interface."""

import os
import re
import sys
import time
from pathlib import Path
from typing import List, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from ttune.audio.player import AudioPlayer
from ttune.config import (
    COLOR_BORDER,
    COLOR_BORDER_DIM,
    COLOR_KEY_BADGE,
    COLOR_KEY_TEXT,
    COLOR_TAG_GREEN,
    COLOR_TEXT_DIM,
    COLOR_TITLE,
)
from ttune.playlist.manager import PlaylistManager
from ttune.playlist.metadata import TrackMetadata, get_metadata
from ttune.playlist.scanner import scan_media
from ttune.ui.renderer import UIRenderer, char_width
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
)

ANSI_RE = re.compile(r"\x1B\[([0-9;]*)m")


def parse_ansi_line(line: str) -> List[Tuple[str, Tuple[int, int, int], bool]]:
    """Parse a string with ANSI escape codes into list of (char, (r, g, b), is_bold)."""
    current_fg = (200, 220, 230)
    is_bold = False
    result = []
    i = 0
    n = len(line)

    while i < n:
        if line[i] == "\x1B" and i + 1 < n and line[i + 1] == "[":
            m = ANSI_RE.match(line, i)
            if m:
                code_str = m.group(1)
                i = m.end()
                codes = [int(c) for c in code_str.split(";") if c.isdigit()] if code_str else [0]
                idx = 0
                while idx < len(codes):
                    c = codes[idx]
                    if c == 0:
                        current_fg = (200, 220, 230)
                        is_bold = False
                    elif c == 1:
                        is_bold = True
                    elif c == 38 and idx + 4 < len(codes) and codes[idx + 1] == 2:
                        current_fg = (codes[idx + 2], codes[idx + 3], codes[idx + 4])
                        idx += 4
                    idx += 1
                continue
            else:
                i += 1
                continue
        else:
            ch = line[i]
            result.append((ch, current_fg, is_bold))
            i += 1

    return result


def render_terminal_to_image(
    lines: List[str],
    output_path: str,
    title: str = "ttune - terminal",
    cols: int = 90,
    font_size: int = 15,
):
    """Render terminal lines into a high-resolution terminal window screenshot."""
    font_path = "C:\\Windows\\Fonts\\consola.ttf"
    font_bold_path = "C:\\Windows\\Fonts\\consolab.ttf"

    try:
        font = ImageFont.truetype(font_path, font_size)
        font_bold = ImageFont.truetype(font_bold_path if os.path.exists(font_bold_path) else font_path, font_size)
    except Exception:
        font = ImageFont.load_default()
        font_bold = font

    dummy_img = Image.new("RGB", (100, 100))
    draw = ImageDraw.Draw(dummy_img)
    bbox = font.getbbox("M")
    char_w = bbox[2] - bbox[0] + 1
    char_h = int((bbox[3] - bbox[1]) * 1.5)

    pad_x = 24
    pad_y = 20
    title_bar_h = 36

    content_w = cols * char_w
    content_h = len(lines) * char_h

    img_w = content_w + (pad_x * 2)
    img_h = content_h + (pad_y * 2) + title_bar_h

    img = Image.new("RGB", (img_w, img_h), (8, 11, 16))
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, img_w, title_bar_h], fill=(13, 17, 23))
    draw.line([0, title_bar_h, img_w, title_bar_h], fill=(0, 240, 255), width=1)

    dot_y = title_bar_h // 2
    draw.ellipse([14, dot_y - 5, 24, dot_y + 5], fill=(255, 95, 86))
    draw.ellipse([32, dot_y - 5, 42, dot_y + 5], fill=(255, 189, 46))
    draw.ellipse([50, dot_y - 5, 60, dot_y + 5], fill=(39, 201, 63))

    try:
        t_font = ImageFont.truetype(font_path, 13)
    except Exception:
        t_font = font
    draw.text((75, dot_y - 7), title, fill=(0, 240, 255), font=t_font)

    start_y = title_bar_h + pad_y

    for row_idx, line in enumerate(lines):
        parsed = parse_ansi_line(line)
        cur_x = pad_x
        y = start_y + (row_idx * char_h)

        for ch, fg_color, is_b in parsed:
            cw = char_width(ch)
            if cw == 0:
                continue

            f = font_bold if is_b else font
            draw.text((cur_x, y), ch, fill=fg_color, font=f)
            cur_x += char_w * cw

    img.save(output_path, "PNG", optimize=True)
    print(f"Saved screenshot: {output_path} ({img_w}x{img_h})")


def generate_menu_screenshot():
    """Capture the startup menu frame."""
    cols = 88
    lines = 24
    c_border = color_fg(COLOR_BORDER)
    c_border_dim = color_fg(COLOR_BORDER_DIM)
    c_green = color_fg(COLOR_TAG_GREEN)
    c_title = color_fg(COLOR_TITLE)
    c_badge = color_fg(COLOR_KEY_BADGE)
    c_dim = color_fg(COLOR_TEXT_DIM)

    menu_options = [
        ("1", "Play a Single Audio/Video File"),
        ("2", "Play a Folder (Recursive Playlist Queue)"),
        ("3", "Search PC for Music Across All Drives"),
        ("4", "Custom Temporary Playlist Builder"),
        ("5", "Theme & Visualizer Style Customizer"),
        ("B", "Interactive Terminal File Browser"),
        ("Q", "Exit ttune"),
    ]

    out = []
    top_dash = cols - 24
    out.append(f"{c_border}{BOX_TOP_LEFT}{BOX_HORIZ * 3} [ ttune v1.0 ] {BOX_HORIZ * top_dash}{BOX_TOP_RIGHT}{STYLE_RESET}")
    out.append(f"{c_border}{BOX_VERT}{STYLE_RESET}{' ' * (cols - 2)}{c_border}{BOX_VERT}{STYLE_RESET}")
    tagline = "RETRO CYBERPUNK TERMINAL MUSIC PLAYER"
    sub = "REAL-TIME FFT AUDIO SPECTRUM EQUALIZER"
    out.append(f"{c_border}{BOX_VERT}{STYLE_RESET}   {c_green}{STYLE_BOLD}{tagline}{STYLE_RESET}")
    out.append(f"{c_border}{BOX_VERT}{STYLE_RESET}   {c_badge}{sub}{STYLE_RESET}")
    out.append(f"{c_border}{BOX_VERT}{STYLE_RESET}{' ' * (cols - 2)}{c_border}{BOX_VERT}{STYLE_RESET}")
    out.append(f"{c_border_dim}{BOX_HORIZ * cols}{STYLE_RESET}")
    out.append("")
    for key, text in menu_options:
        out.append(f"   {c_badge}[{key}]{STYLE_RESET}  {c_title}{text}{STYLE_RESET}")
        out.append("")
    while len(out) < lines - 3:
        out.append("")
    out.append(f"{c_border_dim}{BOX_HORIZ * cols}{STYLE_RESET}")
    out.append(f" {c_dim}Press key {c_badge}[1-5, B, Q]{c_dim} to navigate...{STYLE_RESET}")

    render_terminal_to_image(out[:lines], "docs/screenshot-menu.png", title="ttune - startup menu", cols=cols)


def generate_theme_screenshot():
    """Capture the theme & visualizer customizer screen."""
    from ttune.config import THEME_PALETTES, VISUALIZER_SHAPES, ThemeConfig
    from ttune.ui.theme_picker import render_palette_swatch
    from ttune.ui.theme import get_gradient_color

    cols = 88
    lines = 22
    c_border = color_fg(COLOR_BORDER)
    c_border_dim = color_fg(COLOR_BORDER_DIM)
    c_green = color_fg(COLOR_TAG_GREEN)
    c_title = color_fg(COLOR_TITLE)
    c_badge = color_fg(COLOR_KEY_BADGE)
    c_dim = color_fg(COLOR_TEXT_DIM)
    c_key_txt = color_fg(COLOR_KEY_TEXT)

    tc = ThemeConfig(palette_name="synthwave", shape_name="extra_fat", viz_mode="middle", show_peaks=True)
    out = []
    top_dash = cols - 32
    out.append(f"{c_border}{BOX_TOP_LEFT}{BOX_HORIZ * 3} [ THEME & VISUALIZER STYLES ] {BOX_HORIZ * top_dash}{BOX_TOP_RIGHT}{STYLE_RESET}")
    out.append(f"{c_border}{BOX_VERT}{STYLE_RESET}{' ' * (cols - 2)}{c_border}{BOX_VERT}{STYLE_RESET}")
    out.append(f"{c_border}{BOX_VERT}{STYLE_RESET}   {c_green}{STYLE_BOLD}CUSTOMIZE AUDIO SPECTRUM VISUALS & RGB PALETTES{STYLE_RESET}")
    out.append(f"{c_border_dim}{BOX_HORIZ * cols}{STYLE_RESET}")
    out.append("")

    swatch = render_palette_swatch("synthwave", length=16)
    out.append(f"   {c_badge}[1] Color Palette:{STYLE_RESET}  {c_title}{STYLE_BOLD}◄ SYNTHWAVE     ►{STYLE_RESET}   {swatch}")
    out.append("")
    out.append(f"   {c_badge}[2] Equalizer Shape:{STYLE_RESET} {c_title}{STYLE_BOLD}◄ Extra Fat (6-wide)   ►{STYLE_RESET}  {c_dim}(6-char wide chunky heavyweight fat blocks){STYLE_RESET}")
    out.append("")
    out.append(f" {c_green}►{STYLE_RESET} {c_badge}[3] Visualizer Mode:{STYLE_RESET} {c_title}{STYLE_BOLD}◄ Middle Mirror        ►{STYLE_RESET}  {c_dim}(Symmetrical bars expanding up & down from center line){STYLE_RESET}")
    out.append("")
    out.append(f"   {c_badge}[4] Peak Decay Caps:{STYLE_RESET} {c_green}[ENABLED]{STYLE_RESET}  {c_dim}(Press [4] or Space to toggle){STYLE_RESET}")
    out.append("")
    out.append(f"   {c_dim}─── LIVE SPECTRUM PREVIEW [MIDDLE MIRROR] ───{STYLE_RESET}")

    from ttune.ui.visualizer import SpectrumVisualizer
    vis = SpectrumVisualizer()
    p_bars = np.array([0.20, 0.40, 0.65, 0.85, 0.95, 0.75, 0.60, 0.45, 0.70, 0.90, 0.80, 0.55], dtype=np.float32)
    p_peaks = np.clip(p_bars + 0.06, 0.0, 1.0)
    preview_lines = vis.render(width=cols - 6, height=5, bar_heights=p_bars, peak_heights=p_peaks, theme_config=tc)
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

    render_terminal_to_image(out[:lines], "docs/screenshot-themes.png", title="ttune - theme & visualizer customizer", cols=cols)


def generate_all_screenshots():
    """Run real audio engine and capture screenshots for docs."""
    fav_folder = "C:\\Users\\WALTON\\Desktop\\Fav Music"
    music_file = os.path.join(fav_folder, "NebulaVex Song.mp3")

    if not os.path.exists(music_file):
        print(f"Music file not found: {music_file}")
        return

    tracks = scan_media(fav_folder)
    playlist = PlaylistManager(tracks)

    for idx, t in enumerate(tracks):
        if "NebulaVex Song.mp3" in t:
            playlist.set_tracks(tracks, start_index=idx)
            break

    player = AudioPlayer()
    renderer = UIRenderer()

    current_track = playlist.current_track()
    print(f"Loading and playing: {current_track.title} ({current_track.path})")
    player.load_and_play(current_track.path, duration=current_track.duration, start_time=12.0)

    time.sleep(2.0)

    cols = 88
    lines = 30

    viz_inner_width = max(10, cols - 4)
    num_bars = renderer.visualizer.calculate_layout(viz_inner_width)[0]
    bars, peaks = player.analyzer.get_spectrum(num_bars)

    main_frame = renderer.build_frame(
        cols=cols,
        lines=lines,
        playlist=playlist,
        current_pos=player.current_position,
        duration=player.duration,
        volume=player.raw_volume,
        is_playing=True,
        is_paused=False,
        is_muted=False,
        spectrum_bars=bars,
        spectrum_peaks=peaks,
    )
    render_terminal_to_image(main_frame, "docs/screenshot-main.png", title="ttune - now playing", cols=cols)

    time.sleep(1.2)
    bars2, peaks2 = player.analyzer.get_spectrum(num_bars)
    viz_frame = renderer.build_frame(
        cols=cols,
        lines=lines,
        playlist=playlist,
        current_pos=player.current_position,
        duration=player.duration,
        volume=player.raw_volume,
        is_playing=True,
        is_paused=False,
        is_muted=False,
        spectrum_bars=bars2,
        spectrum_peaks=peaks2,
        visualizer_only=True,
    )
    render_terminal_to_image(viz_frame, "docs/screenshot-visualizer.png", title="ttune - visualizer only mode (H)", cols=cols)

    playlist.next_track(force=True)
    next_track = playlist.current_track()
    player.load_and_play(next_track.path, duration=next_track.duration, start_time=5.0)
    time.sleep(1.2)
    num_bars_full = renderer.visualizer.calculate_layout(cols)[0]
    bars3, peaks3 = player.analyzer.get_spectrum(num_bars_full)

    playlist_frame = renderer.build_frame(
        cols=cols,
        lines=lines,
        playlist=playlist,
        current_pos=player.current_position,
        duration=player.duration,
        volume=player.raw_volume,
        is_playing=True,
        is_paused=False,
        is_muted=False,
        spectrum_bars=bars3,
        spectrum_peaks=peaks3,
        show_playlist=False,
    )
    render_terminal_to_image(playlist_frame, "docs/screenshot-playlist.png", title="ttune - full width visualizer (L key)", cols=cols)

    player.close()
    generate_menu_screenshot()
    generate_theme_screenshot()
    print("All real screenshots generated successfully!")


if __name__ == "__main__":
    generate_all_screenshots()
