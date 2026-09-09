# ttune

> A retro terminal music player with a real-time RGB spectrum visualizer.

![ttune Main Screen](docs/screenshot-main.png)

---

## Overview

**ttune** is a lightweight terminal music player designed with a retro cyberpunk CRT aesthetic. It provides hardware-style audio spectrum analysis directly in your terminal, driven by live Fast Fourier Transform (FFT) analysis of currently playing audio samples.

---

## Features

- **Real-Time FFT Spectrum Visualizer**: Hardware-like equalizer bars rendered with truecolor RGB LED blocks. Includes dynamic peak hold and smooth gravity decay.
- **Theme & Visualizer Style Customizer (`T` Key)**: Choose from 7 color palettes (*Cyberpunk*, *Matrix*, *Synthwave*, *Fire*, *Ice*, *Amber*, *Vaporwave*) and 5 visualizer shapes (*Brick*, *Fat/Wide*, *Thin/Needle*, *Dots*, *Shades*) with live spectrum preview.
- **PC-Wide Music Search (`S` in Menu)**: Instantly search audio across drives (`C:\`, `D:\`, `E:\`) and folders (`Music`, `Desktop`, `Downloads`) with live query filtering and one-key playback.
- **Temporary Custom Playlist (`P` in Menu / `A` to Add)**: Queue songs on the fly from the file browser or search screen, reorder tracks, and play custom queues.
- **Return to Menu (`B` Key)**: Return from active playback back to the interactive home menu at any time.
- **Visualizer-Only Mode (`H` Key)**: Press <kbd>H</kbd> to hide all song information and queue, expanding the spectrum visualizer to fill the entire terminal screen.
- **Rock-Solid Layout with Centered Metadata**: The visualizer is anchored directly at the top with centered song title, artist, and progress bar below, preventing layout jitter or bouncing during full-screen resizing.
- **Universal Media Playback**: Supports all common audio formats and decodes the audio track from video files without displaying video.
- **Recursive Directory Discovery**: Automatically scans music folders and builds naturally sorted playlists (`track 2` before `track 10`).
- **Smart Metadata Extraction**: Reads embedded title, artist, album, and bitrate tags with automatic clean filename fallback.
- **Zero-Flicker Screen Buffer**: Uses ANSI cursor home positioning at ~35 FPS with low CPU consumption (<3%).

---

## Visualizer & Interface

![Real-Time RGB Visualizer](docs/screenshot-visualizer.png)

![Playlist & Queue](docs/screenshot-playlist.png)

![Theme & Visualizer Style Customizer](docs/screenshot-themes.png)

![Interactive Startup Menu](docs/screenshot-menu.png)

---

## Supported Media Formats

Playback and decoding are handled through FFmpeg / libav:

| Category | Formats |
|:---|:---|
| **Audio** | MP3, WAV, FLAC, AAC, M4A, OGG, OPUS, WMA, AIFF, ALAC, APE, AC3 |
| **Video (Audio Track)** | MP4, MKV, WebM, AVI, MOV, WMV, FLV, M4V, TS |

*Video formats such as MP4, MKV, and WebM are supported through the media backend and are treated primarily as audio sources.*

---

## Keyboard Controls

### Playback Screen
| Key | Action |
|:---|:---|
| <kbd>Space</kbd> | Play / Pause |
| <kbd>←</kbd> | Previous track |
| <kbd>→</kbd> | Next track |
| <kbd>↑</kbd> | Volume up (+5%) |
| <kbd>↓</kbd> | Volume down (-5%) |
| <kbd>B</kbd> | Return to Home Menu |
| <kbd>T</kbd> | Open Theme & Style Customizer |
| <kbd>H</kbd> | Toggle pure visualizer mode (hide song info & queue) |
| <kbd>[</kbd> | Seek backward (-5s) |
| <kbd>]</kbd> | Seek forward (+5s) |
| <kbd>R</kbd> | Cycle repeat mode (`ALL` → `ONE` → `OFF`) |
| <kbd>S</kbd> | Toggle shuffle |
| <kbd>M</kbd> | Toggle mute |
| <kbd>Q</kbd> / <kbd>Esc</kbd> | Quit ttune |

### Navigation & Menus
| Screen | Key | Action |
|:---|:---|:---|
| **Home Menu** | <kbd>1</kbd> / <kbd>F</kbd> | Pick Single File |
| | <kbd>2</kbd> / <kbd>D</kbd> | Pick Folder / Playlist |
| | <kbd>3</kbd> / <kbd>S</kbd> | Search PC for Music |
| | <kbd>4</kbd> / <kbd>P</kbd> | Custom Playlist Builder |
| | <kbd>5</kbd> / <kbd>T</kbd> | Customize Themes & Shapes |
| **File Browser** | <kbd>↑</kbd> / <kbd>↓</kbd> | Navigate files / folders |
| | <kbd>Enter</kbd> | Open folder / Play file |
| | <kbd>A</kbd> | Add highlighted track to Custom Playlist |
| | <kbd>B</kbd> / <kbd>Esc</kbd> | Back |
| **Search Screen**| *Type text* | Live query filtering across PC |
| | <kbd>Enter</kbd> | Play selected track |
| | <kbd>P</kbd> | Play all matching tracks |
| | <kbd>A</kbd> | Add highlighted track to Custom Playlist |
| | <kbd>Esc</kbd> | Return to Menu |
| **Playlist Screen**| <kbd>Enter</kbd> / <kbd>P</kbd>| Start playback of playlist |
| | <kbd>D</kbd> | Remove selected track |
| | <kbd>C</kbd> | Clear playlist |
| | <kbd>U</kbd> / <kbd>J</kbd> | Move track Up / Down |
| | <kbd>B</kbd> / <kbd>Esc</kbd> | Return to Menu |
| **Theme Customizer**| <kbd>←</kbd> / <kbd>→</kbd> | Cycle Color Palettes |
| | <kbd>S</kbd> | Cycle Visualizer Shapes (Brick, Fat, Thin, Dots, Shades) |
| | <kbd>P</kbd> | Toggle Peak Decay Caps |
| | <kbd>Enter</kbd> / <kbd>Esc</kbd> | Apply & Return |

---

## Installation

### Prerequisites

- **Python 3.9+**
- **FFmpeg** on system PATH:
  - **Windows**: `winget install Gyan.FFmpeg`
  - **macOS**: `brew install ffmpeg`
  - **Linux**: `sudo apt install ffmpeg`

### Install with pip

```bash
git clone https://github.com/wyzuk/ttune.git
cd ttune
pip install -e .
```

Once installed, the `ttune` command is available directly in PowerShell, CMD, or bash.

---

## Usage

### Interactive Mode
Launch directly to open the startup menu and file browser:
```bash
ttune
```

### Play a Single File
```bash
ttune "C:\Music\synthwave_track.flac"
```

### Play an Entire Folder
```bash
ttune "C:\Users\Username\Music"
```

### Adjust Starting Volume
```bash
ttune "C:\Users\Username\Music" --volume 70
```

---

## Built With

- **Python 3** — Core application architecture and CLI
- **FFmpeg / libav** — Multi-format streaming and raw PCM decoding
- **NumPy** — Fast Fourier Transform (FFT) and frequency band math
- **sounddevice / PortAudio** — Low-latency real-time audio output
- **Mutagen** — Audio tag metadata extraction
- **Windows Console / ANSI Truecolor** — Terminal styling and 24-bit color rendering

---

## License

This project is licensed under the [MIT License](LICENSE).
