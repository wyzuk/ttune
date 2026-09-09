"""Configuration constants, format definitions, audio settings, and cyberpunk themes."""

from dataclasses import dataclass
from typing import Dict, List, Tuple

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
AUDIO_BLOCK_SIZE = 1024
FFT_WINDOW_SIZE = 2048
AUDIO_BUFFER_SECONDS = 15

# Frequency range for spectrum analyzer
FREQ_MIN = 25.0
FREQ_MAX = 17500.0

# Visualizer animation constants
TARGET_FPS = 35
SMOOTH_FACTOR = 0.58
ATTACK_FACTOR = 0.88
PEAK_DECAY_RATE = 0.028
PEAK_HOLD_FRAMES = 2

# Playback defaults
DEFAULT_VOLUME = 0.85
VOLUME_STEP = 0.05
SEEK_STEP = 5.0

# Visualizer Color Palettes (RGB gradients from bottom to top)
THEME_PALETTES: Dict[str, List[Tuple[int, int, int]]] = {
    "cyberpunk": [
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
    ],
    "matrix": [
        (0, 80, 20),      # Deep Dark Green
        (0, 130, 40),     # Forest Green
        (0, 180, 60),     # Cyber Green
        (0, 230, 80),     # Neon Lime
        (50, 255, 120),   # Bright Green
        (120, 255, 170),  # Mint Green
        (200, 255, 220),  # Pale Mint
        (240, 255, 250),  # Bright White-Green
    ],
    "synthwave": [
        (255, 0, 128),    # Hot Pink
        (230, 0, 170),    # Deep Magenta
        (180, 0, 220),    # Purple Violet
        (140, 20, 240),   # Electric Violet
        (255, 80, 40),    # Neon Coral
        (255, 140, 20),   # Sunset Orange
        (255, 200, 0),    # Golden Yellow
        (255, 240, 100),  # Bright Neon Yellow
    ],
    "fire": [
        (120, 0, 0),      # Deep Maroon
        (180, 20, 0),     # Blood Red
        (230, 60, 0),     # Crimson Red
        (255, 100, 0),    # Flame Orange
        (255, 150, 0),    # Bright Amber
        (255, 190, 20),   # Golden Flame
        (255, 230, 60),   # Solar Flare
        (255, 255, 180),  # White Heat
    ],
    "ice": [
        (0, 50, 120),     # Deep Navy
        (0, 100, 180),    # Ocean Blue
        (0, 160, 220),    # Arctic Blue
        (0, 210, 255),    # Glacial Cyan
        (60, 240, 255),   # Ice Teal
        (150, 250, 255),  # Frost Azure
        (220, 255, 255),  # Pure Frost White
    ],
    "amber": [
        (100, 40, 0),     # Dark Amber
        (150, 70, 0),     # Warm Amber
        (200, 110, 0),    # Classic Phosphor
        (240, 150, 0),    # Bright Amber
        (255, 190, 20),   # Golden Glow
        (255, 220, 80),   # Warm Sunlight
        (255, 245, 160),  # Phosphor Peak
    ],
    "vaporwave": [
        (0, 245, 212),    # Turquoise Mint
        (78, 222, 238),   # Soft Cyan
        (123, 175, 255),  # Sky Lavender
        (186, 140, 255),  # Lilac
        (247, 137, 240),  # Bubblegum Pink
        (255, 100, 200),  # Soft Orchid
        (255, 150, 220),  # Pastel Rose
    ],
}

# Visualizer Shapes & Block Styles
VISUALIZER_SHAPES = {
    "brick": {
        "name": "Standard Brick",
        "description": "2-char wide solid LED blocks",
        "char": "█",
        "half": "▄",
        "width": 2,
        "gap": 1,
    },
    "fat": {
        "name": "Fat / Extra Wide",
        "description": "4-char wide chunky retro equalizer",
        "char": "█",
        "half": "▄",
        "width": 4,
        "gap": 1,
    },
    "thin": {
        "name": "Thin / Needle",
        "description": "1-char wide slim high-density bars",
        "char": "█",
        "half": "▄",
        "width": 1,
        "gap": 1,
    },
    "dots": {
        "name": "Dot Matrix",
        "description": "Retro square dot matrix modules",
        "char": "■",
        "half": "▪",
        "width": 2,
        "gap": 1,
    },
    "shades": {
        "name": "Shaded Blocks",
        "description": "Textured gradient shade textures",
        "char": "▓",
        "half": "▒",
        "width": 2,
        "gap": 1,
    },
}

DEFAULT_THEME = "cyberpunk"
DEFAULT_SHAPE = "brick"

# Backward compatibility alias
SPECTRUM_GRADIENT = THEME_PALETTES["cyberpunk"]
PEAK_COLOR = (255, 255, 255)
PEAK_COLOR_ALT = (255, 100, 200)

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


@dataclass
class ThemeConfig:
    """Manages active visual theme and equalizer shape."""
    palette_name: str = DEFAULT_THEME
    shape_name: str = DEFAULT_SHAPE
    show_peaks: bool = True

    @property
    def gradient(self) -> List[Tuple[int, int, int]]:
        return THEME_PALETTES.get(self.palette_name, THEME_PALETTES["cyberpunk"])

    @property
    def shape(self) -> dict:
        return VISUALIZER_SHAPES.get(self.shape_name, VISUALIZER_SHAPES["brick"])

    def next_palette(self) -> str:
        keys = list(THEME_PALETTES.keys())
        idx = keys.index(self.palette_name) if self.palette_name in keys else 0
        self.palette_name = keys[(idx + 1) % len(keys)]
        return self.palette_name

    def prev_palette(self) -> str:
        keys = list(THEME_PALETTES.keys())
        idx = keys.index(self.palette_name) if self.palette_name in keys else 0
        self.palette_name = keys[(idx - 1) % len(keys)]
        return self.palette_name

    def next_shape(self) -> str:
        keys = list(VISUALIZER_SHAPES.keys())
        idx = keys.index(self.shape_name) if self.shape_name in keys else 0
        self.shape_name = keys[(idx + 1) % len(keys)]
        return self.shape_name

    def prev_shape(self) -> str:
        keys = list(VISUALIZER_SHAPES.keys())
        idx = keys.index(self.shape_name) if self.shape_name in keys else 0
        self.shape_name = keys[(idx - 1) % len(keys)]
        return self.shape_name
