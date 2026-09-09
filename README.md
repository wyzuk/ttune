# ttune 🎧

```text
  _   _                      
 | |_| |_ _   _ _ __   ___   
 | __| __| | | | '_ \ / _ \  
 | |_| |_| |_| | | | |  __/  
  \__|\__|\__,_|_| |_|\___|  
```

> **Retro Cyberpunk Terminal Music Player with Real-Time FFT Spectrum Visualizer**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-00f0ff.svg?style=flat-square)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-00ff66.svg?style=flat-square)](LICENSE)
[![Platform: Windows | Linux | macOS](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-ff007f.svg?style=flat-square)](https://github.com/wyzuk/ttune)
[![Audio Backend: FFmpeg](https://img.shields.io/badge/backend-FFmpeg%20%2B%20PortAudio-bd00ff.svg?style=flat-square)](https://ffmpeg.org/)

---

## ⚡ Overview

**ttune** is a lightweight, responsive terminal music player built for power users and terminal enthusiasts who want a genuine retro cyberpunk experience without sacrificing audio fidelity or visual aesthetics.

Unlike mockups or pseudo-visualizers that generate random dancing bars, **ttune** performs real-time **Fast Fourier Transform (FFT)** spectrum analysis on the exact audio samples currently playing through your soundcard.

---

## 🌌 Visual Aesthetic

- **Retro Cyberpunk CRT Look**: Thin neon-cyan borders (`┌`, `─`, `┐`, `│`), bright neon green tags (`NOW PLAYING`), soft magenta metadata accents, and deep dark terminal background.
- **Hardware-Style RGB LED Equalizer**: Spectrum bars rendered with terminal blocks (`█`) transitioning through a smooth truecolor gradient:
  $$\text{Cyan} \longrightarrow \text{Blue} \longrightarrow \text{Purple} \longrightarrow \text{Magenta} \longrightarrow \text{Pink / Red}$$
- **Peak Decay Caps**: Dynamic floating peak indicators with configurable hold and smooth gravity decay.
- **Ultra-Clean Density**: No web-dashboard clutter, no heavy cards, no sluggish frameworks. Everything feels like a lightning-fast native terminal utility.

---

## ✨ Features

- 🎵 **Universal Format Decoding via FFmpeg**:
  Plays **MP3, WAV, FLAC, AAC, M4A, OGG, OPUS, MP4, MKV, WebM, AVI, AIFF, WMA**, and every audio/video format decodable by FFmpeg (video files decode the audio track automatically).
- 📊 **Real-Time FFT Spectrum Analyzer**:
  Logarithmic frequency distribution covering sub-bass (25 Hz) through treble (17.5 kHz) with asymmetric attack/decay smoothing to avoid jitter while staying punchy on drum hits.
- 📂 **Recursive Directory Discovery & Natural Sorting**:
  Point ttune to any folder to recursively scan all subdirectories. Naturally sorts tracks (e.g., `track 2` before `track 10`).
- 🏷️ **Smart Metadata & Filename Cleanups**:
  Extracts title, artist, album, duration, and bitrate via `mutagen` and `ffprobe`. Automatically strips web suffixes (`(Official Video)`, `(getmp3.pro)`, `(MP3_160K)`) if tags are missing.
- 📋 **Compact UP NEXT Queue**:
  Displays upcoming tracks in the playlist with duration and artist tags.
- 🎛️ **Zero-Flicker Double-Buffered Screen Rendering**:
  Uses ANSI cursor repositioning to update frames at ~35 FPS with zero terminal flicker and minimal CPU overhead (<3%).
- 📐 **Adaptive Resizing**:
  Dynamically scales visualizer height, bar widths, and playlist items when terminal dimensions change.
- 🗂️ **Interactive Terminal File Browser**:
  Built-in terminal browser to navigate folders, preview directories, and queue albums.

---

## ⌨️ Keyboard Controls

| Key | Action |
|:---:|:---|
| <kbd>SPACE</kbd> | **Play / Pause** toggle |
| <kbd>→</kbd> | **Next track** |
| <kbd>←</kbd> | **Previous track** |
| <kbd>↑</kbd> | **Volume Up** (+5%) |
| <kbd>↓</kbd> | **Volume Down** (-5%) |
| <kbd>[</kbd> | **Seek backward** 5 seconds |
| <kbd>]</kbd> | **Seek forward** 5 seconds |
| <kbd>R</kbd> | **Toggle Repeat Mode** (`ALL` → `ONE` → `OFF`) |
| <kbd>S</kbd> | **Toggle Shuffle Mode** |
| <kbd>M</kbd> | **Toggle Mute** |
| <kbd>Q</kbd> / <kbd>ESC</kbd> | **Quit** and restore terminal |

---

## 🚀 Installation

### 1. Prerequisites

- **Python 3.9+**
- **FFmpeg** installed and accessible in your system `PATH`:
  - **Windows**: `winget install Gyan.FFmpeg`
  - **macOS**: `brew install ffmpeg`
  - **Linux (Debian/Ubuntu)**: `sudo apt install ffmpeg`
  - **Linux (Fedora/RHEL)**: `sudo dnf install ffmpeg`

### 2. Install ttune

#### From GitHub Repository:
```bash
git clone https://github.com/wyzuk/ttune.git
cd ttune
pip install -e .
```

#### Directly with pip:
```bash
pip install git+https://github.com/wyzuk/ttune.git
```

---

## 🎧 Usage

### Launch Interactive Mode
Launch `ttune` without arguments to open the startup menu and terminal file browser:
```bash
ttune
```

### Play a Specific Track
```bash
ttune "C:\Music\synthwave_track.flac"
```

### Play an Entire Music Folder
```bash
ttune "C:\Users\WALTON\Desktop\Fav Music"
```

### Play Video Audio Directly
```bash
ttune "music_video.mp4"
```

### Set Initial Volume
```bash
ttune "C:\Music" --volume 70
```

---

## 🏗️ Architecture & Project Structure

```text
ttune/
├── pyproject.toml              # Build & dependency specifications
├── README.md                   # Documentation & guide
├── LICENSE                     # MIT License
├── .gitignore                  # Git ignore rules
├── ttune/
│   ├── __init__.py             # Version and package identity
│   ├── __main__.py             # Entry point for `python -m ttune`
│   ├── cli.py                  # CLI parsing & main application loop
│   ├── config.py               # Theme colors, frequency bands & audio settings
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── decoder.py          # FFmpeg raw float32 PCM streaming pipeline
│   │   ├── analyzer.py         # Real-time FFT spectrum analyzer with log bands
│   │   └── player.py           # sounddevice output stream & volume engine
│   ├── playlist/
│   │   ├── __init__.py
│   │   ├── scanner.py          # Recursive scanner with natural sort
│   │   ├── metadata.py         # Mutagen & ffprobe tag extraction
│   │   └── manager.py          # Playlist queue, shuffle & repeat engine
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── theme.py            # ANSI truecolor formatting & box characters
│   │   ├── screen.py           # Terminal setup, UTF-8 & flicker-free renderer
│   │   ├── visualizer.py       # LED brick spectrum equalizer renderer
│   │   ├── renderer.py         # Screen layout composer
│   │   └── browser.py          # Interactive startup menu & file navigator
│   └── input/
│       ├── __init__.py
│       └── keyboard.py         # Non-blocking cross-platform keyboard reader
└── tests/
    ├── test_scanner.py         # Media discovery tests
    ├── test_metadata.py        # Tag extraction & duration tests
    ├── test_playlist.py        # Queue navigation & repeat mode tests
    ├── test_analyzer.py        # FFT spectrum & peak decay tests
    ├── test_renderer.py        # Layout sizing & truncation tests
    └── test_integration.py     # Full player state integration tests
```

---

## 🧪 Running Tests

Run the test suite with pytest:
```bash
pytest -v
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
