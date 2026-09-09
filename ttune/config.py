"""Configuration constants, format definitions, audio settings, and color themes."""

from dataclasses import dataclass
from typing import List, Tuple

# Supported media extensions
AUDIO_EXTENSIONS = {
    ".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg", ".opus",
    ".wma", ".aiff", ".aif", ".alac", ".ape", ".ac3", ".dts",
    ".amr", ".mid", ".midi", ".weba"
}

VIDEO_EXTENSIONS = {
    ".mp4", ".mkv", ".webm", ".avi", ".mov", ".wmv", ".flv",
    ".m4v", ".ts", ".3gp"
}

SUPPORTED_EXTENSIONS = AUDIO_EXTENSIONS | VIDEO_EXTENSIONS

# Audio processing constants
DEFAULT_SAMPLE_RATE = 44100
DEFAULT_CHANNELS = 2
AUDIO_BLOCK_SIZE = 1024  # sounddevice callback buffer size
FFT_WINDOW_SIZE = 2048   # FFT analysis window
AUDIO_BUFFER_SECONDS = 15 # Decode buffer duration in seconds

# Audio frequency range for spectrum analyzer
FREQ_MIN = 25.0
FREQ_MAX = 17500.0

# Visualizer animation constants
TARGET_FPS = 35
SMOOTH_FACTOR = 0.58       # Decay factor for exponential moving average
ATTACK_FACTOR = 0.88       # Fast attack for snappy response
PEAK_DECAY_RATE = 0.028    # Rate at which peak caps fall
PEAK_HOLD_FRAMES = 2       # Hold peak at highest level for N frames

# Playback defaults
DEFAULT_VOLUME = 0.85
VOLUME_STEP = 0.05
SEEK_STEP = 5.0

# Cyberpunk retro color palette
# Gradient stops from bottom of spectrum to top (Cyan -> Blue -> Purple -> Magenta -> Pink/Red)
SPECTRUM_GRADIENT: List[Tuple[int, int, int]] = [
    (0, 240, 255),    # Cyan
    (0, 210, 255),    # Bright Blue-Cyan
    (0, 170, 255),    # Sky Blue
    (30, 130, 255),   # Royal Blue
    (90, 80, 255),    # Deep Indigo
    (140, 40, 255),   # Purple
    (180, 20, 240),   # Electric Violet
    (220, 0, 200),    # Magenta
    (255, 0, 160),    # Deep Pink
    (255, 20, 120),   # Hot Pink
    (255, 50, 90),    # Neon Coral
    (255, 70, 70),    # Neon Red-Pink
]

PEAK_COLOR = (255, 255, 255)  # Bright white for peak cap
PEAK_COLOR_ALT = (255, 100, 200) # Alternate peak cap color

# Cyberpunk UI Colors (R, G, B)
COLOR_BORDER = (0, 240, 255)         # Neon Cyan
COLOR_BORDER_DIM = (0, 100, 120)     # Dim Cyan
COLOR_TITLE = (240, 255, 255)        # Crisp Cyan-White
COLOR_TAG_GREEN = (0, 255, 102)      # Bright Neon Green
COLOR_TAG_PURPLE = (214, 0, 255)     # Bright Purple
COLOR_ARTIST = (180, 220, 255)       # Soft Cyan
COLOR_ALBUM = (255, 120, 220)        # Soft Magenta
COLOR_PROGRESS_BAR = (0, 255, 102)   # Neon Green
COLOR_PROGRESS_BG = (20, 40, 45)     # Dark Slate
COLOR_LABEL = (0, 210, 230)          # Teal Label
COLOR_TEXT_DIM = (80, 110, 120)      # Muted Teal-Gray
COLOR_KEY_BADGE = (0, 240, 255)      # Cyan for keyboard shortcut keys
COLOR_KEY_TEXT = (130, 160, 175)     # Dim Cyan for shortcut descriptions
