"""Interactive startup menu and terminal file/folder browser with playlist and theme integration."""

import os
import sys
from pathlib import Path
from typing import List, Optional, Union

from ttune.config import (
    COLOR_ARTIST,
    COLOR_BORDER,
    COLOR_BORDER_DIM,
    COLOR_KEY_BADGE,
    COLOR_KEY_TEXT,
    COLOR_TAG_GREEN,
    COLOR_TEXT_DIM,
    COLOR_TITLE,
    ThemeConfig,
)
from ttune.input.keyboard import KeyboardReader
from ttune.playlist.custom_playlist import global_custom_playlist
from ttune.playlist.scanner import is_supported_file, natural_sort_key
from ttune.ui.playlist_screen import show_playlist_screen
from ttune.ui.search_screen import show_search_screen
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
from ttune.ui.theme_picker import show_theme_picker


class FileBrowser:
    """Interactive in-terminal file and directory browser."""

    def __init__(self, initial_path: Optional[str] = None):
        self.current_dir = Path(initial_path or os.getcwd()).resolve()
        self.selected_index = 0
        self.scroll_offset = 0
        self.items: List[Path] = []
        self._notification = ""
        self._notification_ticks = 0
        self._refresh_items()

    def _refresh_items(self):
        """Read directory contents, sorting folders first then supported files."""
        try:
            entries = list(self.current_dir.iterdir())
        except PermissionError:
            entries = []

        dirs = [e for e in entries if e.is_dir() and not e.name.startswith(".")]
        files = [e for e in entries if e.is_file() and is_supported_file(str(e))]

        dirs.sort(key=lambda d: natural_sort_key(d.name))
        files.sort(key=lambda f: natural_sort_key(f.name))

        self.items = dirs + files
        self.selected_index = max(0, min(self.selected_index, len(self.items) - 1)) if self.items else 0
        self.scroll_offset = 0

    def navigate_up(self):
        """Go up to parent directory."""
        if self.current_dir.parent != self.current_dir:
            self.current_dir = self.current_dir.parent
            self._refresh_items()

    def enter_selected(self) -> Optional[str]:
        """Enter selected folder or return file path if media file selected."""
        if not self.items or self.selected_index >= len(self.items):
            return None

        selected = self.items[self.selected_index]
        if selected.is_dir():
            self.current_dir = selected
            self.selected_index = 0
            self._refresh_items()
            return None
        else:
            return str(selected)

    def add_selected_to_playlist(self) -> str:
        """Add selected item (file or directory contents) to custom playlist."""
        if not self.items or self.selected_index >= len(self.items):
            return ""

        selected = self.items[self.selected_index]
        if selected.is_file():
            global_custom_playlist.add(str(selected))
            return f"+ Added '{selected.name}' to custom playlist ({global_custom_playlist.count} total)"
        else:
            # Add all supported files in dir
            files = [str(f) for f in selected.glob("*.*") if is_supported_file(str(f))]
            added = global_custom_playlist.add_many(files)
            return f"+ Added {added} songs from '{selected.name}' to custom playlist"

    def move_selection(self, delta: int, visible_count: int):
        if not self.items:
            return
        self.selected_index = max(0, min(len(self.items) - 1, self.selected_index + delta))

        # Adjust scroll offset
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + visible_count:
            self.scroll_offset = self.selected_index - visible_count + 1

    def run(self, screen, keyboard: KeyboardReader) -> Optional[str]:
        """Run interactive file browser until a path is chosen or user exits."""
        c_border = color_fg(COLOR_BORDER)
        c_border_dim = color_fg(COLOR_BORDER_DIM)
        c_green = color_fg(COLOR_TAG_GREEN)
        c_title = color_fg(COLOR_TITLE)
        c_badge = color_fg(COLOR_KEY_BADGE)
        c_dim = color_fg(COLOR_TEXT_DIM)
        c_key_txt = color_fg(COLOR_KEY_TEXT)

        while True:
            cols, lines = screen.get_size()
            cols = max(55, cols)
            lines = max(18, lines)

            out = []
            header = f"{c_border}{BOX_TOP_LEFT}{BOX_HORIZ} [ ttune BROWSER ] {c_border_dim}{BOX_HORIZ * max(0, cols - 22)}{c_border}{BOX_TOP_RIGHT}{STYLE_RESET}"
            out.append(header)

            curr_dir_str = str(self.current_dir)
            if len(curr_dir_str) > cols - 8:
                curr_dir_str = "..." + curr_dir_str[-(cols - 11):]
            out.append(f"{c_border}{BOX_VERT}{STYLE_RESET}  {c_badge}Location:{STYLE_RESET} {c_title}{curr_dir_str}{STYLE_RESET}")

            if self._notification and self._notification_ticks > 0:
                out.append(f"{c_border}{BOX_VERT}{STYLE_RESET}  {c_green}{STYLE_BOLD}{self._notification}{STYLE_RESET}")
                self._notification_ticks -= 1
            else:
                out.append(f"{c_border_dim}{BOX_HORIZ * cols}{STYLE_RESET}")

            visible_rows = max(5, lines - 8)
            page_items = self.items[self.scroll_offset : self.scroll_offset + visible_rows]

            if not self.items:
                out.append(f"  {c_dim}[Empty or no supported media files in this folder]{STYLE_RESET}")

            for i, item in enumerate(page_items):
                actual_idx = self.scroll_offset + i
                is_selected = actual_idx == self.selected_index
                pointer = f"{c_green}►{STYLE_RESET} " if is_selected else "  "

                if item.is_dir():
                    icon = f"{c_badge}📁 "
                    name = f"{item.name}/"
                else:
                    icon = f"{c_green}🎵 "
                    name = item.name

                max_name_len = max(10, cols - 12)
                if len(name) > max_name_len:
                    name = name[: max_name_len - 3] + "..."

                if is_selected:
                    name_colored = f"{c_title}{STYLE_BOLD}{name}{STYLE_RESET}"
                else:
                    name_colored = f"{c_key_txt}{name}{STYLE_RESET}"

                out.append(f" {pointer}{icon}{name_colored}")

            while len(out) < lines - 3:
                out.append("")

            # Footer
            out.append(f"{c_border_dim}{BOX_HORIZ * cols}{STYLE_RESET}")
            footer_keys = (
                f" {c_badge}ENTER{STYLE_RESET} {c_key_txt}SELECT{STYLE_RESET}   "
                f"{c_badge}A{STYLE_RESET} {c_key_txt}ADD TO PLAYLIST{STYLE_RESET}   "
                f"{c_badge}P{STYLE_RESET} {c_key_txt}PLAY DIR{STYLE_RESET}   "
                f"{c_badge}BKSP{STYLE_RESET} {c_key_txt}UP{STYLE_RESET}   "
                f"{c_badge}B/ESC{STYLE_RESET} {c_key_txt}BACK{STYLE_RESET}"
            )
            out.append(footer_keys)

            screen.render_frame(out[:lines])

            key = keyboard.read_key(timeout=0.05)
            if not key:
                continue

            k = key.upper()
            if key == "UP":
                self.move_selection(-1, visible_rows)
            elif key == "DOWN":
                self.move_selection(1, visible_rows)
            elif key in ("ENTER", "RIGHT"):
                res = self.enter_selected()
                if res:
                    return res
            elif key in ("BACKSPACE", "LEFT"):
                self.navigate_up()
            elif k == "A":
                msg = self.add_selected_to_playlist()
                if msg:
                    self._notification = msg
                    self._notification_ticks = 20
            elif k == "P":
                return str(self.current_dir)
            elif k in ("B", "Q", "ESCAPE"):
                return None


def show_startup_menu(
    screen,
    keyboard: KeyboardReader,
    theme_config: Optional[ThemeConfig] = None,
) -> Optional[Union[str, List[str]]]:
    """Display the cyberpunk startup screen and return chosen path(s) or None to exit."""
    desktop_fav = Path(os.path.expanduser("~")) / "Desktop" / "Fav Music"
    has_fav = desktop_fav.exists() and desktop_fav.is_dir()

    t_cfg = theme_config if theme_config is not None else ThemeConfig()

    c_border = color_fg(COLOR_BORDER)
    c_border_dim = color_fg(COLOR_BORDER_DIM)
    c_green = color_fg(COLOR_TAG_GREEN)
    c_title = color_fg(COLOR_TITLE)
    c_badge = color_fg(COLOR_KEY_BADGE)
    c_dim = color_fg(COLOR_TEXT_DIM)

    while True:
        cols, lines = screen.get_size()
        cols = max(60, cols)
        lines = max(22, lines)

        playlist_count = global_custom_playlist.count
        playlist_badge = f"({playlist_count} tracks)" if playlist_count > 0 else "(empty)"

        menu_options = [
            ("1", "Play a Single Audio/Video File"),
            ("2", "Play a Folder (Recursive Queue)"),
        ]
        if has_fav:
            menu_options.append(("3", f"Play Fav Music ({desktop_fav.name})"))

        menu_options.extend([
            ("4" if has_fav else "3", "Interactive Terminal File Browser"),
            ("S", "Search Music Across PC"),
            ("P", f"Custom Temporary Playlist {playlist_badge}"),
            ("T", f"Customize Themes & Visualizer ({t_cfg.palette_name.upper()}, {t_cfg.shape_name})"),
            ("Q", "Exit ttune"),
        ])

        out = []
        top_dash = max(0, cols - 24)
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

        while len(out) < lines - 3:
            out.append("")

        out.append(f"{c_border_dim}{BOX_HORIZ * cols}{STYLE_RESET}")
        out.append(f" {c_dim}Press key {c_badge}[1-4, S, P, T]{c_dim} or {c_badge}[Q]{c_dim} to exit...{STYLE_RESET}")

        screen.render_frame(out[:lines])

        key = keyboard.read_key(timeout=0.1)
        if not key:
            continue

        k = key.upper()
        if k == "1":
            screen.restore_terminal()
            print(f"\n{color_fg(COLOR_TAG_GREEN)}Enter file path (audio or video):{STYLE_RESET}")
            try:
                p = input("> ").strip().strip('"').strip("'")
                screen.init_terminal()
                if p and Path(p).exists():
                    return p
            except (EOFError, KeyboardInterrupt):
                screen.init_terminal()
                return None
        elif k == "2":
            screen.restore_terminal()
            print(f"\n{color_fg(COLOR_TAG_GREEN)}Enter folder path:{STYLE_RESET}")
            try:
                p = input("> ").strip().strip('"').strip("'")
                screen.init_terminal()
                if p and Path(p).exists():
                    return p
            except (EOFError, KeyboardInterrupt):
                screen.init_terminal()
                return None
        elif k == "3" and has_fav:
            return str(desktop_fav)
        elif (k == "4" and has_fav) or (k == "3" and not has_fav):
            browser = FileBrowser(str(desktop_fav if has_fav else os.getcwd()))
            chosen = browser.run(screen, keyboard)
            if chosen:
                return chosen
        elif k == "S":
            # Search music across PC
            chosen_search = show_search_screen(screen, keyboard)
            if chosen_search:
                return chosen_search
        elif k == "P":
            # View/play custom playlist
            chosen_playlist = show_playlist_screen(screen, keyboard)
            if chosen_playlist:
                return chosen_playlist
        elif k == "T":
            # Customize themes
            show_theme_picker(screen, keyboard, t_cfg)
        elif k in ("Q", "ESCAPE"):
            return None
