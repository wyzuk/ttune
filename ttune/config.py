"""Configuration constants, format definitions, audio settings, and cyberpunk themes."""

from dataclasses import dataclass
from typing import Dict, List, Tuple

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

DEFAULT_SAMPLE_RATE = 44100
DEFAULT_CHANNELS = 2
AUDIO_BLOCK_SIZE = 1024
FFT_WINDOW_SIZE = 2048
AUDIO_BUFFER_SECONDS = 15

FREQ_MIN = 25.0
FREQ_MAX = 17500.0

TARGET_FPS = 35
SMOOTH_FACTOR = 0.58
ATTACK_FACTOR = 0.88
PEAK_DECAY_RATE = 0.028
PEAK_HOLD_FRAMES = 2

DEFAULT_VOLUME = 0.85
VOLUME_STEP = 0.05
SEEK_STEP = 5.0

THEME_PALETTES: Dict[str, List[Tuple[int, int, int]]] = {
    "cyberpunk": [
        (0, 240, 255),
        (0, 210, 255),
        (0, 170, 255),
        (30, 130, 255),
        (90, 80, 255),
        (140, 40, 255),
        (180, 20, 240),
        (220, 0, 200),
        (255, 0, 160),
        (255, 20, 120),
        (255, 50, 90),
        (255, 70, 70),
    ],
    "matrix": [
        (0, 80, 20),
        (0, 130, 40),
        (0, 180, 60),
        (0, 230, 80),
        (50, 255, 120),
        (120, 255, 170),
        (200, 255, 220),
        (240, 255, 250),
    ],
    "synthwave": [
        (255, 0, 128),
        (230, 0, 170),
        (180, 0, 220),
        (140, 20, 240),
        (255, 80, 40),
        (255, 140, 20),
        (255, 200, 0),
        (255, 240, 100),
    ],
    "fire": [
        (120, 0, 0),
        (180, 20, 0),
        (230, 60, 0),
        (255, 100, 0),
        (255, 150, 0),
        (255, 190, 20),
        (255, 230, 60),
        (255, 255, 180),
    ],
    "ice": [
        (0, 50, 120),
        (0, 100, 180),
        (0, 160, 220),
        (0, 210, 255),
        (60, 240, 255),
        (150, 250, 255),
        (220, 255, 255),
    ],
    "amber": [
        (100, 40, 0),
        (150, 70, 0),
        (200, 110, 0),
        (240, 150, 0),
        (255, 190, 20),
        (255, 220, 80),
        (255, 245, 160),
    ],
    "vaporwave": [
        (0, 245, 212),
        (78, 222, 238),
        (123, 175, 255),
        (186, 140, 255),
        (247, 137, 240),
        (255, 100, 200),
        (255, 150, 220),
    ],
    "hyperpop": [
        (60, 0, 120),
        (110, 10, 190),
        (170, 0, 240),
        (220, 0, 200),
        (255, 20, 150),
        (255, 80, 190),
        (0, 240, 255),
        (240, 255, 255),
    ],
    "toxic": [
        (15, 60, 10),
        (40, 120, 15),
        (70, 180, 20),
        (140, 240, 10),
        (210, 255, 20),
        (245, 255, 140),
    ],
    "blood_moon": [
        (50, 0, 10),
        (100, 5, 20),
        (160, 15, 35),
        (220, 20, 50),
        (255, 50, 70),
        (255, 110, 130),
        (255, 210, 220),
    ],
    "ocean_abyss": [
        (5, 20, 50),
        (10, 50, 100),
        (0, 110, 160),
        (0, 170, 190),
        (0, 230, 180),
        (120, 255, 230),
    ],
    "sunset_blaze": [
        (40, 0, 60),
        (90, 0, 80),
        (170, 20, 50),
        (230, 60, 10),
        (255, 130, 0),
        (255, 195, 20),
        (255, 240, 120),
    ],
    "aurora": [
        (10, 30, 50),
        (10, 80, 70),
        (0, 150, 100),
        (20, 220, 130),
        (60, 255, 200),
        (160, 255, 240),
    ],
    "cyber_gold": [
        (60, 35, 0),
        (110, 70, 0),
        (170, 120, 0),
        (230, 175, 0),
        (255, 220, 30),
        (255, 250, 150),
    ],
    "cotton_candy": [
        (60, 160, 255),
        (120, 200, 255),
        (190, 160, 255),
        (255, 140, 220),
        (255, 80, 180),
        (255, 180, 230),
    ],
    "rainbow": [
        (255, 0, 60),
        (255, 120, 0),
        (255, 220, 0),
        (0, 230, 80),
        (0, 210, 255),
        (60, 80, 255),
        (180, 0, 255),
        (255, 20, 180),
    ],
    "monochrome": [
        (40, 45, 55),
        (80, 90, 105),
        (130, 140, 155),
        (180, 195, 210),
        (225, 235, 245),
        (255, 255, 255),
    ],
    "sakura": [
        (60, 20, 45),
        (120, 40, 80),
        (185, 70, 125),
        (240, 120, 175),
        (255, 175, 210),
        (255, 235, 245),
    ],
}

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
        "name": "Fat Brick (4-wide)",
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
    "extra_fat": {
        "name": "Extra Fat (6-wide)",
        "description": "6-char wide chunky heavyweight fat blocks",
        "char": "█",
        "half": "▄",
        "width": 6,
        "gap": 1,
    },
    "mega_fat": {
        "name": "Mega Fat (8-wide)",
        "description": "8-char wide giant fat slab blocks",
        "char": "█",
        "half": "▄",
        "width": 8,
        "gap": 2,
    },
    "giant": {
        "name": "Giant Fat (10-wide)",
        "description": "10-char wide ultra chunky fat blocks",
        "char": "█",
        "half": "▄",
        "width": 10,
        "gap": 2,
    },
    "colossal": {
        "name": "Colossal (14-wide)",
        "description": "14-char massive monolithic fat blocks",
        "char": "█",
        "half": "▄",
        "width": 14,
        "gap": 2,
    },
    "fat_dense": {
        "name": "Dense Fat (4-wide)",
        "description": "4-char wide gapless solid wall blocks",
        "char": "█",
        "half": "▄",
        "width": 4,
        "gap": 0,
    },
    "extra_dense": {
        "name": "Extra Dense (6-wide)",
        "description": "6-char wide gapless mega wall blocks",
        "char": "█",
        "half": "▄",
        "width": 6,
        "gap": 0,
    },
    "dots": {
        "name": "Dot Matrix",
        "description": "Retro square dot matrix modules",
        "char": "■",
        "half": "▪",
        "width": 2,
        "gap": 1,
    },
    "fat_dots": {
        "name": "Fat Dot Matrix",
        "description": "4-char wide square matrix modules",
        "char": "■",
        "half": "▪",
        "width": 4,
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
    "fat_shades": {
        "name": "Fat Shaded",
        "description": "4-char wide textured shade blocks",
        "char": "▓",
        "half": "▒",
        "width": 4,
        "gap": 1,
    },
    "braille": {
        "name": "Braille Particles",
        "description": "Fine-grained braille audio points",
        "char": "⣿",
        "half": "⣤",
        "width": 2,
        "gap": 1,
    },
}

VISUALIZER_MODES = {
    "bottom": {
        "name": "Bottom-Up",
        "description": "Classic spectrum bars rising from bottom floor",
    },
    "middle": {
        "name": "Middle Mirror",
        "description": "Symmetrical bars expanding up & down from center line",
    },
    "middle_wave": {
        "name": "Middle Wave",
        "description": "Center-anchored pulsing equalizer wave",
    },
    "top_down": {
        "name": "Hanging (Top-Down)",
        "description": "Inverted icicle bars hanging from ceiling",
    },
    "stereo_split": {
        "name": "Split Mirror",
        "description": "Dual reflected center-out spectrum bands",
    },
}

DEFAULT_THEME = "cyberpunk"
DEFAULT_SHAPE = "brick"
DEFAULT_MODE = "bottom"

SPECTRUM_GRADIENT = THEME_PALETTES["cyberpunk"]
PEAK_COLOR = (255, 255, 255)
PEAK_COLOR_ALT = (255, 100, 200)

COLOR_BORDER = (0, 240, 255)
COLOR_BORDER_DIM = (0, 100, 120)
COLOR_TITLE = (240, 255, 255)
COLOR_TAG_GREEN = (0, 255, 102)
COLOR_TAG_PURPLE = (214, 0, 255)
COLOR_ARTIST = (180, 220, 255)
COLOR_ALBUM = (255, 120, 220)
COLOR_PROGRESS_BAR = (0, 255, 102)
COLOR_PROGRESS_BG = (20, 40, 45)
COLOR_LABEL = (0, 210, 230)
COLOR_TEXT_DIM = (80, 110, 120)
COLOR_KEY_BADGE = (0, 240, 255)
COLOR_KEY_TEXT = (130, 160, 175)


@dataclass
class ThemeConfig:
    """Manages active visual theme, equalizer shape, and visualizer mode."""
    palette_name: str = DEFAULT_THEME
    shape_name: str = DEFAULT_SHAPE
    viz_mode: str = DEFAULT_MODE
    show_peaks: bool = True

    @property
    def gradient(self) -> List[Tuple[int, int, int]]:
        return THEME_PALETTES.get(self.palette_name, THEME_PALETTES["cyberpunk"])

    @property
    def shape(self) -> dict:
        return VISUALIZER_SHAPES.get(self.shape_name, VISUALIZER_SHAPES["brick"])

    @property
    def mode_info(self) -> dict:
        return VISUALIZER_MODES.get(self.viz_mode, VISUALIZER_MODES["bottom"])

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

    def next_mode(self) -> str:
        keys = list(VISUALIZER_MODES.keys())
        idx = keys.index(self.viz_mode) if self.viz_mode in keys else 0
        self.viz_mode = keys[(idx + 1) % len(keys)]
        return self.viz_mode

    def prev_mode(self) -> str:
        keys = list(VISUALIZER_MODES.keys())
        idx = keys.index(self.viz_mode) if self.viz_mode in keys else 0
        self.viz_mode = keys[(idx - 1) % len(keys)]
        return self.viz_mode

