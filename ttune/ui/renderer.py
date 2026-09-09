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

        # -------------------------------------------------------------
        # 1. TOP HEADER: ttune & STATUS
        # -------------------------------------------------------------
        app_tag = f"{c_border}{STYLE_BOLD}ttune{STYLE_RESET}"

        if visualizer_only:
            status_tag = f"{c_green}{STYLE_BOLD}► VISUALIZER ONLY{STYLE_RESET}"
            vol_pct = int(round(volume * 100))
            vol_tag = f"{c_dim}MUTE{STYLE_RESET}" if is_muted else f"{c_badge}VOL: {vol_pct}%{STYLE_RESET}"
            hint_tag = f"{c_dim}[H] RESTORE UI{STYLE_RESET}"
            tags = [status_tag, vol_tag, hint_tag]
        else:
            status_tag = f"{c_green}{STYLE_BOLD}► PLAYING{STYLE_RESET}" if (is_playing and not is_paused) else (
                f"{c_badge}{STYLE_BOLD}❚❚ PAUSED{STYLE_RESET}" if is_paused else f"{c_dim}■ STOPPED{STYLE_RESET}"
            )
            vol_pct = int(round(volume * 100))
            vol_tag = f"{c_dim}MUTE{STYLE_RESET}" if is_muted else f"{c_badge}VOL: {vol_pct}%{STYLE_RESET}"
            rep_tag = f"{c_dim}REP: {playlist.repeat_mode.value}{STYLE_RESET}"
            shuf_tag = f"{c_green}SHUF{STYLE_RESET}" if playlist.shuffle_enabled else ""
            theme_tag = f"{c_dim}{theme_config.palette_name.upper()}{STYLE_RESET}" if theme_config else ""
            tags = [t for t in [status_tag, vol_tag, rep_tag, shuf_tag, theme_tag] if t]

        tags_str = "  ".join(tags)

        left_header = f" {app_tag} "
        right_header = f" {tags_str} " if tags_str else ""
        left_len = string_width(left_header)
        right_len = string_width(right_header)

        dash_count = max(0, cols - 2 - left_len - right_len)
        header_line = f"{c_border}{BOX_TOP_LEFT}{BOX_HORIZ}{left_header}{c_border_dim}{BOX_HORIZ * dash_count}{right_header}{c_border}{BOX_HORIZ}{BOX_TOP_RIGHT}{STYLE_RESET}"
        out.append(header_line)

        # -------------------------------------------------------------
        # 2. PURE VISUALIZER MODE (Activated with 'h' key)
        # -------------------------------------------------------------
        if visualizer_only:
            # Visualizer fills the entire remaining screen height!
            viz_height = max(4, lines - 2)
            viz_inner_width = max(10, cols - 4)

            bars_lines = self.visualizer.render(
                width=viz_inner_width,
                height=viz_height,
                bar_heights=spectrum_bars,
                peak_heights=spectrum_peaks,
                theme_config=theme_config,
            )

            for bl in bars_lines:
                vis_len = string_width(bl)
                right_fill = " " * max(0, viz_inner_width - vis_len)
                out.append(f"{c_border_dim}{BOX_VERT}{STYLE_RESET} {bl}{right_fill} {c_border_dim}{BOX_VERT}{STYLE_RESET}")

            # Bottom border
            viz_bottom = f"{c_border}{BOX_BOTTOM_LEFT}{BOX_HORIZ * (cols - 2)}{BOX_BOTTOM_RIGHT}{STYLE_RESET}"
            out.append(viz_bottom)
            return out[:lines]

        # -------------------------------------------------------------
        # 3. EXTENDED VISUALIZER AT THE TOP (Prevents layout bouncing!)
        # -------------------------------------------------------------
        # Calculate rows needed for bottom metadata section
        up_next_count = 2 if lines < 25 else (3 if lines < 32 else (4 if lines < 40 else 5))
        bottom_needed = 5 + up_next_count
        viz_height = max(4, lines - 2 - bottom_needed)
        viz_inner_width = max(10, cols - 4)

        # Render spectrum bars directly at top
        bars_lines = self.visualizer.render(
            width=viz_inner_width,
            height=viz_height,
            bar_heights=spectrum_bars,
            peak_heights=spectrum_peaks,
            theme_config=theme_config,
        )

        for bl in bars_lines:
            vis_len = string_width(bl)
            right_fill = " " * max(0, viz_inner_width - vis_len)
            out.append(f"{c_border_dim}{BOX_VERT}{STYLE_RESET} {bl}{right_fill} {c_border_dim}{BOX_VERT}{STYLE_RESET}")

        # Visualizer bottom frame border
        viz_bottom = f"{c_border_dim}{BOX_BOTTOM_LEFT}{BOX_HORIZ * (cols - 2)}{BOX_BOTTOM_RIGHT}{STYLE_RESET}"
        out.append(viz_bottom)

        # -------------------------------------------------------------
        # 4. SONG DETAILS & TRACK INFO (CENTERED IN THE MIDDLE)
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

        # C: Centered Playback Progress Bar
        cur_str = format_duration(current_pos)
        dur_str = format_duration(duration) if duration > 0 else "--:--"
        pct = (current_pos / duration) if duration > 0 else 0.0
        pct = max(0.0, min(1.0, pct))
        pct_int = int(round(pct * 100))

        time_tag = f"{c_dim}[{c_badge}{cur_str}{c_dim}/{c_badge}{dur_str}{c_dim}]{STYLE_RESET}"
        pct_tag = f"{c_dim}[{c_green}{pct_int:3d}%{c_dim}]{STYLE_RESET}"

        # Calculate progress bar width (centered, max 50 chars wide)
        fixed_len = string_width(time_tag) + string_width(pct_tag) + 6
        target_bar_len = min(40, max(8, cols - fixed_len - 10))
        filled_len = int(pct * target_bar_len)
        empty_len = max(0, target_bar_len - filled_len - 1)

        c_fill = color_fg(COLOR_PROGRESS_BAR)
        c_bg = color_fg(COLOR_PROGRESS_BG)
        prog_bar_str = (
            f"{c_fill}{PROG_FILLED * filled_len}"
            f"{color_fg(COLOR_TITLE)}{PROG_KNOB}"
            f"{c_bg}{PROG_EMPTY * empty_len}{STYLE_RESET}"
        )
        progress_line = f"{time_tag}  {prog_bar_str}  {pct_tag}"
        out.append(center_text(progress_line, cols))

        # -------------------------------------------------------------
        # 5. UP NEXT PLAYLIST QUEUE
        # -------------------------------------------------------------
        # Subtle horizontal divider
        divider = f"{c_border_dim}{BOX_HORIZ * max(10, cols - 4)}{STYLE_RESET}"
        out.append(center_text(divider, cols))

        up_next_header = f"{c_green}{STYLE_BOLD}UP NEXT{STYLE_RESET}"
        out.append(f"  {up_next_header}")

        up_next_tracks = playlist.get_up_next(count=up_next_count)
        if up_next_tracks:
            for idx, track in enumerate(up_next_tracks, 1):
                t_title = track.title
                t_artist = f" - {track.artist}" if track.artist and track.artist != "Unknown Artist" else ""
                t_dur = f"[{track.duration_str}]" if track.duration > 0 else ""
                avail_title = max(10, cols - len(f"    {idx}. ") - len(t_dur) - 4)
                combined = fit_text(f"{t_title}{t_artist}", avail_title)
                line_str = f"    {c_badge}{idx}.{STYLE_RESET} {c_artist}{combined}{STYLE_RESET} {c_dim}{t_dur}{STYLE_RESET}"
                out.append(line_str)
        else:
            out.append(f"    {c_dim}1. [Queue empty - End of playlist]{STYLE_RESET}")

        # Ensure exact lines count without scrolling
        while len(out) < lines:
            out.append("")

        return out[:lines]
