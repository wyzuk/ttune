"""Interactive screen to view and manage user's temporary custom playlist."""

import os
from typing import List, Optional

from ttune.config import (
    COLOR_BORDER,
    COLOR_BORDER_DIM,
    COLOR_KEY_BADGE,
    COLOR_KEY_TEXT,
    COLOR_TAG_GREEN,
    COLOR_TEXT_DIM,
    COLOR_TITLE,
)
from ttune.input.keyboard import KeyboardReader
from ttune.playlist.custom_playlist import global_custom_playlist
from ttune.playlist.metadata import clean_filename
from ttune.ui.renderer import fit_text
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
)


def show_playlist_screen(
    screen: TerminalScreen,
    keyboard: KeyboardReader,
) -> Optional[List[str]]:
    """Screen for reviewing and managing the custom temporary playlist.

    Returns:
        List of track paths if user chooses to start playback, or None if backed out.
    """
    c_border = color_fg(COLOR_BORDER)
    c_border_dim = color_fg(COLOR_BORDER_DIM)
    c_green = color_fg(COLOR_TAG_GREEN)
    c_title = color_fg(COLOR_TITLE)
    c_badge = color_fg(COLOR_KEY_BADGE)
    c_dim = color_fg(COLOR_TEXT_DIM)
    c_key_txt = color_fg(COLOR_KEY_TEXT)

    selected_idx = 0
    scroll_offset = 0

    while True:
        cols, lines = screen.get_size()
        cols = max(55, cols)
        lines = max(18, lines)

        tracks = global_custom_playlist.tracks
        selected_idx = max(0, min(selected_idx, len(tracks) - 1)) if tracks else 0

        out = []
        top_dash = max(0, cols - 32)
        out.append(f"{c_border}{BOX_TOP_LEFT}{BOX_HORIZ * 3} [ CUSTOM TEMPORARY PLAYLIST ] {BOX_HORIZ * top_dash}{BOX_TOP_RIGHT}{STYLE_RESET}")
        out.append(f"{c_border}{BOX_VERT}{STYLE_RESET}  {c_green}{STYLE_BOLD}Queued Tracks:{STYLE_RESET} {c_title}{len(tracks)} songs{STYLE_RESET}")
        out.append(f"{c_border_dim}{BOX_HORIZ * cols}{STYLE_RESET}")

        visible_rows = max(5, lines - 7)
        page_items = tracks[scroll_offset : scroll_offset + visible_rows]

        if not tracks:
            out.append(f"   {c_dim}[Custom playlist is empty]{STYLE_RESET}")
            out.append(f"   {c_dim}Add songs from Search ([S]) or File Browser ([4]){STYLE_RESET}")

        for i, path in enumerate(page_items):
            actual_idx = scroll_offset + i
            is_selected = actual_idx == selected_idx
            ptr = f"{c_green}▶{STYLE_RESET} " if is_selected else "  "

            filename = os.path.basename(path)
            cleaned = clean_filename(filename)
            _, ext = os.path.splitext(filename)
            fmt_badge = f"{c_dim}[{ext.lstrip('.').upper()}]{STYLE_RESET}"

            avail = max(10, cols - 16)
            name_disp = fit_text(cleaned, avail)

            if is_selected:
                item_str = f"{ptr}{c_badge}{actual_idx + 1:2d}.{STYLE_RESET} {c_title}{STYLE_BOLD}{name_disp}{STYLE_RESET} {fmt_badge}"
            else:
                item_str = f"{ptr}{c_dim}{actual_idx + 1:2d}.{STYLE_RESET} {c_key_txt}{name_disp}{STYLE_RESET} {fmt_badge}"

            out.append(f" {item_str}")

        while len(out) < lines - 3:
            out.append("")

        out.append(f"{c_border_dim}{BOX_HORIZ * cols}{STYLE_RESET}")
        footer_keys = (
            f" {c_badge}ENTER/P{STYLE_RESET} {c_key_txt}PLAY{STYLE_RESET}   "
            f"{c_badge}D{STYLE_RESET} {c_key_txt}REMOVE{STYLE_RESET}   "
            f"{c_badge}C{STYLE_RESET} {c_key_txt}CLEAR{STYLE_RESET}   "
            f"{c_badge}↑/↓{STYLE_RESET} {c_key_txt}NAVIGATE{STYLE_RESET}   "
            f"{c_badge}B/ESC{STYLE_RESET} {c_key_txt}BACK{STYLE_RESET}"
        )
        out.append(footer_keys)

        screen.render_frame(out[:lines])

        key = keyboard.read_key(timeout=0.05)
        if not key:
            continue

        k = key.upper()
        if key == "UP":
            if tracks:
                selected_idx = max(0, selected_idx - 1)
                if selected_idx < scroll_offset:
                    scroll_offset = selected_idx
        elif key == "DOWN":
            if tracks:
                selected_idx = min(len(tracks) - 1, selected_idx + 1)
                if selected_idx >= scroll_offset + visible_rows:
                    scroll_offset = selected_idx - visible_rows + 1
        elif k in ("ENTER", "P"):
            if tracks:
                return tracks
        elif k == "D":
            if tracks and selected_idx < len(tracks):
                global_custom_playlist.remove(selected_idx)
        elif k == "C":
            global_custom_playlist.clear()
            selected_idx = 0
            scroll_offset = 0
        elif k in ("B", "ESCAPE", "Q"):
            return None
