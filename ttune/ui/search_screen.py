"""Interactive PC-wide song search interface."""

import os
from typing import List, Optional, Tuple

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
from ttune.playlist.searcher import global_search_engine
from ttune.ui.renderer import fit_text, string_width
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


def show_search_screen(
    screen: TerminalScreen,
    keyboard: KeyboardReader,
) -> Optional[List[str]]:
    """Interactive music search screen.

    Returns:
        List of selected track paths to play, or None if user exited back to menu.
    """
    c_border = color_fg(COLOR_BORDER)
    c_border_dim = color_fg(COLOR_BORDER_DIM)
    c_green = color_fg(COLOR_TAG_GREEN)
    c_title = color_fg(COLOR_TITLE)
    c_badge = color_fg(COLOR_KEY_BADGE)
    c_dim = color_fg(COLOR_TEXT_DIM)
    c_key_txt = color_fg(COLOR_KEY_TEXT)

    query = ""
    selected_idx = 0
    scroll_offset = 0
    notification = ""
    notification_ticks = 0

    # Initial indexing (fast search roots)
    matches = global_search_engine.search(query, limit=100)

    while True:
        cols, lines = screen.get_size()
        cols = max(55, cols)
        lines = max(18, lines)

        out = []
        top_dash = max(0, cols - 32)
        out.append(f"{c_border}{BOX_TOP_LEFT}{BOX_HORIZ * 3} [ SEARCH MUSIC ACROSS PC ] {BOX_HORIZ * top_dash}{BOX_TOP_RIGHT}{STYLE_RESET}")

        # Search Query Input Box
        q_disp = query if query else ""
        cursor_char = "█"
        q_line = f" {c_green}{STYLE_BOLD}Search:{STYLE_RESET} {c_title}{q_disp}{c_badge}{cursor_char}{STYLE_RESET}"
        out.append(f"{c_border}{BOX_VERT}{STYLE_RESET} {q_line}")

        # Notification banner if any
        if notification and notification_ticks > 0:
            notif_str = f" {c_green}{STYLE_BOLD}{notification}{STYLE_RESET}"
            out.append(f"{c_border}{BOX_VERT}{STYLE_RESET}{notif_str}")
            notification_ticks -= 1
        else:
            match_count_str = f" {c_dim}Found {len(matches)} matches across PC{STYLE_RESET}"
            out.append(f"{c_border}{BOX_VERT}{STYLE_RESET}{match_count_str}")

        out.append(f"{c_border_dim}{BOX_HORIZ * cols}{STYLE_RESET}")

        # Results area
        visible_rows = max(5, lines - 8)
        page_items = matches[scroll_offset : scroll_offset + visible_rows]

        if not matches:
            if not query:
                out.append(f"   {c_dim}[Indexing media files across your PC... Type to search]{STYLE_RESET}")
            else:
                out.append(f"   {c_dim}[No matching songs found for '{query}']{STYLE_RESET}")

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

        # Footer controls
        out.append(f"{c_border_dim}{BOX_HORIZ * cols}{STYLE_RESET}")
        footer_keys = (
            f" {c_badge}ENTER{STYLE_RESET} {c_key_txt}PLAY{STYLE_RESET}   "
            f"{c_badge}P{STYLE_RESET} {c_key_txt}PLAY ALL{STYLE_RESET}   "
            f"{c_badge}A{STYLE_RESET} {c_key_txt}ADD TO PLAYLIST{STYLE_RESET}   "
            f"{c_badge}↑/↓{STYLE_RESET} {c_key_txt}NAVIGATE{STYLE_RESET}   "
            f"{c_badge}B/ESC{STYLE_RESET} {c_key_txt}BACK{STYLE_RESET}"
        )
        out.append(footer_keys)

        screen.render_frame(out[:lines])

        key = keyboard.read_key(timeout=0.05)
        if not key:
            continue

        if key == "UP":
            if matches:
                selected_idx = max(0, selected_idx - 1)
                if selected_idx < scroll_offset:
                    scroll_offset = selected_idx
        elif key == "DOWN":
            if matches:
                selected_idx = min(len(matches) - 1, selected_idx + 1)
                if selected_idx >= scroll_offset + visible_rows:
                    scroll_offset = selected_idx - visible_rows + 1
        elif key == "ENTER":
            if matches and 0 <= selected_idx < len(matches):
                # Return single track to play
                return [matches[selected_idx]]
        elif key in ("P", "p") and not (len(key) == 1 and key.isprintable() and len(query) == 0 and False):
            if matches:
                # Play all search matches
                return matches
        elif key in ("A", "a") and selected_idx < len(matches):
            added = global_custom_playlist.add(matches[selected_idx])
            song_name = os.path.basename(matches[selected_idx])
            notification = f"+ Added '{fit_text(song_name, 35)}' to Custom Playlist ({global_custom_playlist.count} total)"
            notification_ticks = 20
        elif key == "BACKSPACE":
            if query:
                query = query[:-1]
                matches = global_search_engine.search(query, limit=100)
                selected_idx = 0
                scroll_offset = 0
        elif key in ("ESCAPE",):
            return None
        elif key in ("b", "B") and len(query) == 0:
            return None
        elif len(key) == 1 and key.isprintable():
            query += key
            matches = global_search_engine.search(query, limit=100)
            selected_idx = 0
            scroll_offset = 0
