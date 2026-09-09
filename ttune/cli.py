"""CLI entry point and main application controller for ttune."""

import argparse
import os
import shutil
import signal
import sys
import time
from pathlib import Path
from typing import List, Optional, Union

from ttune import __version__
from ttune.audio.player import AudioPlayer
from ttune.config import DEFAULT_VOLUME, TARGET_FPS, ThemeConfig
from ttune.input.keyboard import KeyboardReader
from ttune.playlist.custom_playlist import global_custom_playlist
from ttune.playlist.manager import PlaylistManager, RepeatMode
from ttune.playlist.scanner import scan_media
from ttune.ui.browser import show_startup_menu
from ttune.ui.renderer import UIRenderer
from ttune.ui.screen import TerminalScreen
from ttune.ui.theme import STYLE_BOLD, STYLE_RESET, color_fg
from ttune.ui.theme_picker import show_theme_picker


def check_ffmpeg() -> bool:
    """Verify that ffmpeg executable is available on system PATH."""
    return shutil.which("ffmpeg") is not None


def print_ffmpeg_error():
    """Display clear instructions if FFmpeg is missing."""
    red = color_fg((255, 60, 90))
    cyan = color_fg((0, 240, 255))
    yellow = color_fg((255, 200, 0))

    print(f"\n{red}{STYLE_BOLD}ERROR: FFmpeg is required by ttune but was not found on your system PATH.{STYLE_RESET}\n")
    print(f"{cyan}To install FFmpeg:{STYLE_RESET}")
    if os.name == "nt":
        print(f"  {yellow}winget install Gyan.FFmpeg{STYLE_RESET}")
        print("  or download from: https://www.gyan.dev/ffmpeg/builds/")
    elif sys.platform == "darwin":
        print(f"  {yellow}brew install ffmpeg{STYLE_RESET}")
    else:
        print(f"  {yellow}sudo apt install ffmpeg{STYLE_RESET} (Debian/Ubuntu)")
        print(f"  {yellow}sudo dnf install ffmpeg{STYLE_RESET} (Fedora)")
    print("\nAfter installing, re-run ttune.\n")


class TTuneApp:
    """Main application runtime coordinator."""

    def __init__(self, target_path: Optional[str] = None, volume: float = DEFAULT_VOLUME):
        self.target_path = target_path
        self.screen = TerminalScreen()
        self.keyboard = KeyboardReader()
        self.player = AudioPlayer()
        self.playlist = PlaylistManager()
        self.renderer = UIRenderer()
        self.theme_config = ThemeConfig()
        self.running = False
        self.volume = volume
        self.visualizer_only = False

    def on_track_finished(self):
        """Callback from audio engine when track finishes."""
        next_track = self.playlist.next_track(force=False)
        if next_track:
            self.player.load_and_play(next_track.path, duration=next_track.duration)
        else:
            self.player.stop()

    def start_track(self):
        """Start playing current track in playlist."""
        curr = self.playlist.current_track()
        if curr:
            self.player.load_and_play(curr.path, duration=curr.duration)

    def run(self):
        """Main application lifecycle."""
        if not check_ffmpeg():
            print_ffmpeg_error()
            return 1

        self.screen.init_terminal()

        # Handle signals cleanly
        def sig_handler(signum, frame):
            self.cleanup()
            sys.exit(0)

        signal.signal(signal.SIGINT, sig_handler)
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, sig_handler)

        try:
            chosen = self.target_path

            while True:
                # If no initial path or returning from player via 'B':
                if not chosen:
                    chosen = show_startup_menu(self.screen, self.keyboard, self.theme_config)
                    if not chosen:
                        # User chose to quit from startup menu
                        break

                # Resolve track paths
                if isinstance(chosen, list):
                    tracks = chosen
                else:
                    try:
                        tracks = scan_media(chosen)
                    except Exception as e:
                        self.screen.restore_terminal()
                        print(f"{color_fg((255, 60, 90))}Error loading media: {e}{STYLE_RESET}")
                        time.sleep(1.5)
                        self.screen.init_terminal()
                        chosen = None
                        continue

                if not tracks:
                    self.screen.restore_terminal()
                    print(f"{color_fg((255, 60, 90))}No supported media files found in: {chosen}{STYLE_RESET}")
                    time.sleep(1.5)
                    self.screen.init_terminal()
                    chosen = None
                    continue

                # Populate playlist and start playback
                self.playlist.set_tracks(tracks)
                self.player.set_volume(self.volume)
                self.player.set_on_track_end(self.on_track_finished)
                self.start_track()

                # Main render & control loop
                self.running = True
                frame_interval = 1.0 / TARGET_FPS
                return_to_menu = False

                while self.running:
                    loop_start = time.time()

                    # 1. Process keyboard inputs
                    key = self.keyboard.read_key(timeout=0.01)
                    if key:
                        if key == "SPACE":
                            self.player.toggle_play_pause()
                        elif key == "RIGHT":
                            next_meta = self.playlist.next_track(force=True)
                            if next_meta:
                                self.player.load_and_play(next_meta.path, duration=next_meta.duration)
                        elif key == "LEFT":
                            prev_meta = self.playlist.prev_track()
                            if prev_meta:
                                self.player.load_and_play(prev_meta.path, duration=prev_meta.duration)
                        elif key == "UP":
                            self.player.volume_up()
                        elif key == "DOWN":
                            self.player.volume_down()
                        elif key in ("b", "B"):
                            # Back to Home Menu!
                            self.player.stop()
                            return_to_menu = True
                            self.running = False
                            break
                        elif key in ("t", "T"):
                            # Open theme & visualizer customizer
                            show_theme_picker(self.screen, self.keyboard, self.theme_config)
                        elif key in ("h", "H"):
                            self.visualizer_only = not self.visualizer_only
                        elif key in ("q", "Q", "ESCAPE"):
                            self.running = False
                            return 0
                        elif key in ("r", "R"):
                            self.playlist.toggle_repeat()
                        elif key in ("s", "S"):
                            self.playlist.toggle_shuffle()
                        elif key in ("m", "M"):
                            self.player.toggle_mute()
                        elif key == "[":
                            self.player.seek_relative(-5.0)
                        elif key == "]":
                            self.player.seek_relative(5.0)

                    # 2. Get current terminal dimensions
                    cols, lines = self.screen.get_size()

                    # 3. Calculate FFT spectrum equalizer bars
                    viz_inner_width = max(10, cols - 4)
                    num_bars = self.renderer.visualizer.calculate_layout(
                        viz_inner_width, self.theme_config
                    )[0]
                    bars, peaks = self.player.analyzer.get_spectrum(num_bars)

                    # 4. Compose UI frame
                    screen_lines = self.renderer.build_frame(
                        cols=cols,
                        lines=lines,
                        playlist=self.playlist,
                        current_pos=self.player.current_position,
                        duration=self.player.duration,
                        volume=self.player.raw_volume,
                        is_playing=self.player.is_playing,
                        is_paused=self.player.is_paused,
                        is_muted=self.player.is_muted,
                        spectrum_bars=bars,
                        spectrum_peaks=peaks,
                        visualizer_only=self.visualizer_only,
                        theme_config=self.theme_config,
                    )

                    # 5. Render without flickering
                    self.screen.render_frame(screen_lines)

                    # 6. Throttle to target FPS
                    elapsed = time.time() - loop_start
                    sleep_time = max(0.001, frame_interval - elapsed)
                    time.sleep(sleep_time)

                if return_to_menu:
                    chosen = None
                    continue
                else:
                    break

        finally:
            self.cleanup()

        return 0

    def cleanup(self):
        """Ensure all hardware devices, threads, and terminal states are restored."""
        self.running = False
        try:
            self.player.close()
        except Exception:
            pass
        try:
            self.keyboard.cleanup()
        except Exception:
            pass
        try:
            self.screen.restore_terminal()
        except Exception:
            pass


def main():
    """CLI parser and launcher."""
    parser = argparse.ArgumentParser(
        prog="ttune",
        description="Retro Cyberpunk Terminal Music Player with Real-Time FFT Spectrum Visualizer",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=None,
        help="Path to an audio/video file or folder containing media files.",
    )
    parser.add_argument(
        "-v", "--volume",
        type=int,
        default=85,
        help="Initial volume percentage (0-150, default: 85)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"ttune v{__version__}",
    )

    args = parser.parse_args()
    vol_float = max(0.0, min(1.5, args.volume / 100.0))

    app = TTuneApp(target_path=args.path, volume=vol_float)
    sys.exit(app.run())


if __name__ == "__main__":
    main()
