"""Screen layout renderer that composes the cyberpunk terminal UI."""

import os
import re
import unicodedata
from typing import List, Optional

import numpy as np

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
    ThemeConfig,
)
from ttune.playlist.manager import PlaylistManager, RepeatMode
from ttune.playlist.metadata import TrackMetadata, format_duration
from ttune.ui.theme import (
    BOX_BOTTOM_LEFT,
    BOX_BOTTOM_RIGHT,
    BOX_HORIZ,
    BOX_TOP_LEFT,
    BOX_TOP_RIGHT,
    BOX_VERT,
    BOX_T_UP,
    PROG_EMPTY,
    PROG_FILLED,
    PROG_KNOB,
    STYLE_BOLD,
    STYLE_DIM,
    STYLE_RESET,
    color_fg,
)
from ttune.ui.visualizer import SpectrumVisualizer

ANSI_ESCAPE_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def char_width(char: str) -> int:
    """Return terminal display width for a single unicode character."""
    if unicodedata.category(char) in ("Mn", "Me", "Cc", "Cf"):
        return 0
    w = unicodedata.east_asian_width(char)
    return 2 if w in ("F", "W") else 1


def string_width(text: str) -> int:
    """Compute visual column width of a string ignoring ANSI escape codes."""
    clean = ANSI_ESCAPE_RE.sub("", text)
    return sum(char_width(c) for c in clean)


# Alias for compatibility
strip_ansi_len = string_width


def fit_text(text: str, max_width: int) -> str:
    """Fit text within max_width display columns, truncating cleanly if needed."""
    if max_width <= 0:
        return ""

    current_w = sum(char_width(c) for c in text)
    if current_w <= max_width:
        return text

    target = max_width - 3 if max_width >= 4 else max_width
    accum = []
    w_sum = 0

    for c in text:
        cw = char_width(c)
        if w_sum + cw > target:
            break
        accum.append(c)
        w_sum += cw

    if max_width >= 4:
        return "".join(accum) + "..."
    return "".join(accum)


def center_text(text: str, total_width: int) -> str:
    """Center text within total_width display columns."""
    w = string_width(text)
    pad = max(0, total_width - w)
    pad_left = pad // 2
    return f"{' ' * pad_left}{text}"


class UIRenderer:
    """Composes the full terminal UI frames for ttune matching the retro cyberpunk aesthetic."""

    def __init__(self):
        self.visualizer = SpectrumVisualizer()

    def build_frame(
        self,
        cols: int,
        lines: int,
        playlist: PlaylistManager,
        current_pos: float,
        duration: float,
        volume: float,
        is_playing: bool,
        is_paused: bool,
        is_muted: bool,
        spectrum_bars: np.ndarray,
        spectrum_peaks: np.ndarray,
        visualizer_only: bool = False,
        theme_config: Optional[ThemeConfig] = None,
        show_playlist: bool = True,
    ) -> List[str]:
        """Compose all components into a list of terminal screen lines.

        Guaranteed not to exceed `lines` rows, preventing scrolling artifacts.
        """
        cols = max(40, cols)
        lines = max(14, lines)
        out: List[str] = []

        c_border = color_fg(COLOR_BORDER)
        c_border_dim = color_fg(COLOR_BORDER_DIM)
        c_green = color_fg(COLOR_TAG_GREEN)
        c_title = color_fg(COLOR_TITLE)
        c_artist = color_fg(COLOR_ARTIST)
        c_album = color_fg(COLOR_ALBUM)
        c_dim = color_fg(COLOR_TEXT_DIM)
        c_badge = color_fg(COLOR_KEY_BADGE)
        c_key_txt = color_fg(COLOR_KEY_TEXT)
        c_gold = color_fg((255, 215, 0))

        # -------------------------------------------------------------
        # PURE VISUALIZER MODE (Activated with 'h' key)
        # -------------------------------------------------------------
        if visualizer_only:
            bars_lines = self.visualizer.render(
                width=cols,
                height=lines,
                bar_heights=spectrum_bars,
                peak_heights=spectrum_peaks,
                theme_config=theme_config,
            )
            for bl in bars_lines:
                vis_len = string_width(bl)
                right_fill = " " * max(0, cols - vis_len)
                out.append(f"{bl}{right_fill}")
            return out[:lines]

        # -------------------------------------------------------------
        # 1. TOP SECTION: PLAYLIST (LEFT) + VISUALIZER (RIGHT)
        # No top border line, no ttune label - directly pure visuals!
        # -------------------------------------------------------------
        # Bottom metadata section needs 5 lines (divider + title + artist + progress + hints)
        bottom_needed = 5
        viz_height = max(4, lines - bottom_needed)

        if show_playlist:
            pl_width = min(36, max(22, int(cols * 0.28)))
            viz_width = max(10, cols - pl_width - 1)
        else:
            pl_width = 0
            viz_width = cols

        bars_lines = self.visualizer.render(
            width=viz_width,
            height=viz_height,
            bar_heights=spectrum_bars,
            peak_heights=spectrum_peaks,
            theme_config=theme_config,
        )

        all_tracks = playlist.tracks
        total_tracks = len(all_tracks)
        current_idx = playlist.current_index

        if show_playlist:
            # Calculate scroll offset to keep currently playing song visible
            if total_tracks <= viz_height:
                start_idx = 0
            else:
                start_idx = max(0, min(current_idx - (viz_height // 2), total_tracks - viz_height))

            for r in range(viz_height):
                t_idx = start_idx + r
                if t_idx < total_tracks:
                    meta = playlist.get_track_metadata(t_idx)
                    raw_path = all_tracks[t_idx]
                    track_title = meta.title if meta else os.path.splitext(os.path.basename(raw_path))[0]
                    is_current = (t_idx == current_idx)
                    num_str = f"{t_idx + 1}."

                    if is_current:
                        prefix = f" {c_gold}*{STYLE_RESET} {c_badge}{num_str}{STYLE_RESET} "
                        prefix_w = 4 + len(num_str) + 1
                        avail = max(4, pl_width - prefix_w)
                        t_str = fit_text(track_title, avail)
                        row_content = f"{prefix}{c_title}{STYLE_BOLD}{t_str}{STYLE_RESET}"
                    else:
                        prefix = f"   {c_dim}{num_str}{STYLE_RESET} "
                        prefix_w = 3 + len(num_str) + 1
                        avail = max(4, pl_width - prefix_w)
                        t_str = fit_text(track_title, avail)
                        row_content = f"{prefix}{c_artist}{t_str}{STYLE_RESET}"

                    pad_len = max(0, pl_width - string_width(row_content))
                    pl_part = f"{row_content}{' ' * pad_len}"
                else:
                    pl_part = " " * pl_width

                bl = bars_lines[r] if r < len(bars_lines) else ""
                bl_w = string_width(bl)
                right_fill = " " * max(0, viz_width - bl_w)
                out.append(f"{pl_part}{c_border_dim}{BOX_VERT}{STYLE_RESET}{bl}{right_fill}")
        else:
            for r in range(viz_height):
                bl = bars_lines[r] if r < len(bars_lines) else ""
                bl_w = string_width(bl)
                right_fill = " " * max(0, viz_width - bl_w)
                out.append(f"{bl}{right_fill}")

        # -------------------------------------------------------------
        # 2. HORIZONTAL DIVIDER
        # -------------------------------------------------------------
        if show_playlist:
            divider = f"{c_border_dim}{BOX_HORIZ * pl_width}{BOX_T_UP}{BOX_HORIZ * max(0, cols - pl_width - 1)}{STYLE_RESET}"
        else:
            divider = f"{c_border_dim}{BOX_HORIZ * cols}{STYLE_RESET}"
        out.append(divider)

        # -------------------------------------------------------------
        # 3. SONG DETAILS & TRACK INFO (CENTERED IN THE BOTTOM)
        # -------------------------------------------------------------
        current_meta = playlist.current_track()
        if current_meta:
            song_title = current_meta.title
            artist_album = current_meta.artist
            if current_meta.album and current_meta.album != "Unknown Album":
                artist_album += f" / {current_meta.album}"

            fmt_badge = f"[{current_meta.format_name}"
            if current_meta.bitrate:
                fmt_badge += f" • {int(current_meta.bitrate / 1000)}kbps"
            fmt_badge += "]"
        else:
            song_title = "No Track Loaded"
            artist_album = "Select a media file or folder to start playback"
            fmt_badge = ""

        # A: Centered Song Title
        max_title_w = max(10, cols - 8)
        title_fitted = fit_text(f'"{song_title}"', max_title_w)
        title_styled = f"{c_title}{STYLE_BOLD}{title_fitted}{STYLE_RESET}"
        out.append(center_text(title_styled, cols))

        # B: Centered Artist / Album & Format Badge
        meta_str = f"{c_artist}{artist_album}{STYLE_RESET}  {c_dim}{fmt_badge}{STYLE_RESET}"
        meta_fitted = fit_text(meta_str, max(10, cols - 8))
        out.append(center_text(meta_fitted, cols))

        # C: Centered Playback Progress Bar + Status
        cur_str = format_duration(current_pos)
        dur_str = format_duration(duration) if duration > 0 else "--:--"
        pct = (current_pos / duration) if duration > 0 else 0.0
        pct = max(0.0, min(1.0, pct))
        pct_int = int(round(pct * 100))

        status_tag = f"{c_green}► PLAYING{STYLE_RESET}" if (is_playing and not is_paused) else (
            f"{c_badge}❚❚ PAUSED{STYLE_RESET}" if is_paused else f"{c_dim}■ STOPPED{STYLE_RESET}"
        )
        vol_pct = int(round(volume * 100))
        vol_tag = f"{c_dim}MUTE{STYLE_RESET}" if is_muted else f"{c_badge}VOL:{vol_pct}%{STYLE_RESET}"
        time_tag = f"{c_dim}[{c_badge}{cur_str}{c_dim}/{c_badge}{dur_str}{c_dim}]{STYLE_RESET}"
        pct_tag = f"{c_dim}[{c_green}{pct_int:3d}%{c_dim}]{STYLE_RESET}"

        target_bar_len = min(36, max(8, cols - 50))
        filled_len = int(pct * target_bar_len)
        empty_len = max(0, target_bar_len - filled_len - 1)

        c_fill = color_fg(COLOR_PROGRESS_BAR)
        c_bg = color_fg(COLOR_PROGRESS_BG)
        prog_bar_str = (
            f"{c_fill}{PROG_FILLED * filled_len}"
            f"{color_fg(COLOR_TITLE)}{PROG_KNOB}"
            f"{c_bg}{PROG_EMPTY * empty_len}{STYLE_RESET}"
        )
        progress_line = f"{status_tag}  {time_tag}  {prog_bar_str}  {pct_tag}  {vol_tag}"
        out.append(center_text(progress_line, cols))

        # D: Control Shortcuts Hint
        pl_hint = "HIDE LIST" if show_playlist else "SHOW LIST"
        mode_str = theme_config.mode_info["name"].upper() if theme_config else "VIZ"
        pal_str = theme_config.palette_name.upper() if theme_config else "THEME"
        controls_line = (
            f"{c_badge}[SPACE]{c_key_txt} PLAY/PAUSE  "
            f"{c_badge}[←/→]{c_key_txt} TRACK  "
            f"{c_badge}[↑/↓]{c_key_txt} VOL  "
            f"{c_badge}[L]{c_key_txt} {pl_hint}  "
            f"{c_badge}[V]{c_key_txt} {mode_str}  "
            f"{c_badge}[T]{c_key_txt} {pal_str}  "
            f"{c_badge}[H]{c_key_txt} FULL-VIZ  "
            f"{c_badge}[B]{c_key_txt} MENU"
        )
        out.append(center_text(controls_line, cols))

        while len(out) < lines:
            out.append("")

        return out[:lines]
