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

    # Check if text already fits
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
    ) -> List[str]:
        """Compose all components into a list of terminal screen lines.

        Guaranteed not to exceed `lines` rows, preventing scrolling artifacts.
        """
        cols = max(40, cols)
        lines = max(16, lines)
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
        status_tag = f"{c_green}{STYLE_BOLD}► PLAYING{STYLE_RESET}" if (is_playing and not is_paused) else (
            f"{c_badge}{STYLE_BOLD}❚❚ PAUSED{STYLE_RESET}" if is_paused else f"{c_dim}■ STOPPED{STYLE_RESET}"
        )
        vol_pct = int(round(volume * 100))
        vol_tag = f"{c_dim}MUTE{STYLE_RESET}" if is_muted else f"{c_badge}VOL: {vol_pct}%{STYLE_RESET}"
        rep_tag = f"{c_dim}REP: {playlist.repeat_mode.value}{STYLE_RESET}"
        shuf_tag = f"{c_green}SHUF{STYLE_RESET}" if playlist.shuffle_enabled else ""

        tags = [t for t in [status_tag, vol_tag, rep_tag, shuf_tag] if t]
        tags_str = "  ".join(tags)

        left_header = f" {app_tag} "
        right_header = f" {tags_str} " if tags_str else ""
        left_len = string_width(left_header)
        right_len = string_width(right_header)

        dash_count = max(0, cols - 2 - left_len - right_len)
        header_line = f"{c_border}{BOX_TOP_LEFT}{BOX_HORIZ}{left_header}{c_border_dim}{BOX_HORIZ * dash_count}{right_header}{c_border}{BOX_HORIZ}{BOX_TOP_RIGHT}{STYLE_RESET}"
        out.append(header_line)

        # -------------------------------------------------------------
        # 2. NOW PLAYING METADATA
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

        now_tag = f"{c_green}{STYLE_BOLD}NOW PLAYING{STYLE_RESET}"
        title_disp = fit_text(f'"{song_title}"', max(10, cols - 6))
        meta_disp = fit_text(artist_album, max(10, cols - string_width(fmt_badge) - 8))

        # Line A: Tag & Title
        out.append(f"{c_border}{BOX_VERT}{STYLE_RESET}  {now_tag}  {c_title}{STYLE_BOLD}{title_disp}{STYLE_RESET}")
        # Line B: Artist / Album & Audio Badge
        meta_line = f"{c_border}{BOX_VERT}{STYLE_RESET}  {c_artist}{meta_disp}{STYLE_RESET}  {c_dim}{fmt_badge}{STYLE_RESET}"
        out.append(meta_line)

        # -------------------------------------------------------------
        # 3. PLAYBACK PROGRESS BAR
        # -------------------------------------------------------------
        cur_str = format_duration(current_pos)
        dur_str = format_duration(duration) if duration > 0 else "--:--"
        pct = (current_pos / duration) if duration > 0 else 0.0
        pct = max(0.0, min(1.0, pct))
        pct_int = int(round(pct * 100))

        time_tag = f"{c_dim}[{c_badge}{cur_str}{c_dim}/{c_badge}{dur_str}{c_dim}]{STYLE_RESET}"
        pct_tag = f"{c_dim}[{c_green}{pct_int:3d}%{c_dim}]{STYLE_RESET}"

        fixed_len = string_width(time_tag) + string_width(pct_tag) + 8
        bar_avail = max(10, cols - fixed_len)
        filled_len = int(pct * bar_avail)
        empty_len = max(0, bar_avail - filled_len - 1)

        c_fill = color_fg(COLOR_PROGRESS_BAR)
        c_bg = color_fg(COLOR_PROGRESS_BG)
        prog_bar_str = (
            f"{c_fill}{PROG_FILLED * filled_len}"
            f"{color_fg(COLOR_TITLE)}{PROG_KNOB}"
            f"{c_bg}{PROG_EMPTY * empty_len}{STYLE_RESET}"
        )
        progress_line = f"{c_border}{BOX_VERT}{STYLE_RESET}  {time_tag}  {prog_bar_str}  {pct_tag}"
        out.append(progress_line)

        # -------------------------------------------------------------
        # 4. REAL-TIME AUDIO VISUALIZER
        # -------------------------------------------------------------
        # Determine heights based on available terminal lines
        # Fixed lines:
        # Header (1) + Now Playing (3) + Progress (1) + Viz Borders (2) = 7
        # Up next header (1) + Up next tracks (2..5) + Footer (3) = 6..9
        # Total fixed = 13..16
        up_next_count = 3 if lines < 26 else (5 if lines < 38 else 6)
        footer_height = 3 if cols >= 65 else 4
        fixed_lines = 7 + 1 + up_next_count + footer_height

        viz_height = max(5, lines - fixed_lines)
        viz_inner_width = max(10, cols - 4)

        # Top border of visualizer box
        viz_title = f" {c_border}{STYLE_BOLD}REAL-TIME AUDIO VISUALIZER{STYLE_RESET} "
        v_title_len = string_width(viz_title)
        v_dash = max(0, cols - 2 - v_title_len)
        v_dash_left = v_dash // 2
        v_dash_right = v_dash - v_dash_left
        viz_top = f"{c_border_dim}{BOX_TOP_LEFT}{BOX_HORIZ * v_dash_left}{viz_title}{BOX_HORIZ * v_dash_right}{BOX_TOP_RIGHT}{STYLE_RESET}"
        out.append(viz_top)

        # Render spectrum bars
        bars_lines = self.visualizer.render(
            width=viz_inner_width,
            height=viz_height,
            bar_heights=spectrum_bars,
            peak_heights=spectrum_peaks,
        )

        for bl in bars_lines:
            vis_len = string_width(bl)
            right_fill = " " * max(0, viz_inner_width - vis_len)
            out.append(f"{c_border_dim}{BOX_VERT}{STYLE_RESET} {bl}{right_fill} {c_border_dim}{BOX_VERT}{STYLE_RESET}")

        # Bottom border of visualizer box
        viz_bottom = f"{c_border_dim}{BOX_BOTTOM_LEFT}{BOX_HORIZ * (cols - 2)}{BOX_BOTTOM_RIGHT}{STYLE_RESET}"
        out.append(viz_bottom)

        # -------------------------------------------------------------
        # 5. UP NEXT PLAYLIST QUEUE
        # -------------------------------------------------------------
        out.append(f"{c_green}{STYLE_BOLD}UP NEXT{STYLE_RESET}")

        up_next_tracks = playlist.get_up_next(count=up_next_count)
        if up_next_tracks:
            for idx, track in enumerate(up_next_tracks, 1):
                t_title = track.title
                t_artist = f" - {track.artist}" if track.artist and track.artist != "Unknown Artist" else ""
                t_dur = f"[{track.duration_str}]" if track.duration > 0 else ""
                avail_title = max(10, cols - len(f" {idx}. ") - len(t_dur) - 4)
                combined = fit_text(f"{t_title}{t_artist}", avail_title)
                line_str = f" {c_badge}{idx}.{STYLE_RESET} {c_artist}{combined}{STYLE_RESET} {c_dim}{t_dur}{STYLE_RESET}"
                out.append(line_str)
        else:
            out.append(f" {c_dim}1. [Queue empty - End of playlist]{STYLE_RESET}")

        # -------------------------------------------------------------
        # 6. KEYBOARD CONTROLS FOOTER
        # -------------------------------------------------------------
        # Pad with empty lines if needed
        while len(out) < lines - footer_height:
            out.append("")

        # Divider line
        foot_border = f"{c_border_dim}{BOX_HORIZ * cols}{STYLE_RESET}"
        out.append(foot_border)

        if cols >= 80:
            # Full 2-row controls
            row1 = (
                f" {c_badge}←{STYLE_RESET} {c_key_txt}PREV{STYLE_RESET}      "
                f"{c_badge}SPACE{STYLE_RESET} {c_key_txt}PLAY/PAUSE{STYLE_RESET}      "
                f"{c_badge}→{STYLE_RESET} {c_key_txt}NEXT{STYLE_RESET}      "
                f"{c_badge}↑{STYLE_RESET} {c_key_txt}VOLUME UP{STYLE_RESET}      "
                f"{c_badge}↓{STYLE_RESET} {c_key_txt}VOLUME DOWN{STYLE_RESET}"
            )
            row2 = (
                f" {c_badge}R{STYLE_RESET} {c_key_txt}REPEAT{STYLE_RESET}    "
                f"{c_badge}S{STYLE_RESET} {c_key_txt}SHUFFLE{STYLE_RESET}       "
                f"{c_badge}M{STYLE_RESET} {c_key_txt}MUTE{STYLE_RESET}            "
                f"{c_badge}[/]{STYLE_RESET} {c_key_txt}SEEK ±5s{STYLE_RESET}      "
                f"{c_badge}Q{STYLE_RESET} {c_key_txt}QUIT{STYLE_RESET}"
            )
            out.append(row1)
            out.append(row2)
        else:
            # Compact 1-row or 2-row controls
            row1 = (
                f" {c_badge}←/→{STYLE_RESET} {c_key_txt}SKIP{STYLE_RESET}  "
                f"{c_badge}SPC{STYLE_RESET} {c_key_txt}PLAY{STYLE_RESET}  "
                f"{c_badge}↑/↓{STYLE_RESET} {c_key_txt}VOL{STYLE_RESET}  "
                f"{c_badge}R{STYLE_RESET} {c_key_txt}REP{STYLE_RESET}  "
                f"{c_badge}S{STYLE_RESET} {c_key_txt}SHUF{STYLE_RESET}  "
                f"{c_badge}Q{STYLE_RESET} {c_key_txt}QUIT{STYLE_RESET}"
            )
            out.append(row1)

        return out[:lines]
