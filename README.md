# TGS to WebP Converter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A flexible Python tool to convert **TGS** (Telegram Animated Stickers) files into high-quality **animated WebP** format.

TGS files are gzip-compressed Lottie JSON animations. This module renders them frame-by-frame with [rlottie](https://github.com/nicedayzhu/rlottie-python) and encodes the result as an animated WebP using [webp](https://github.com/anibali/pywebp), giving you full control over resolution, quality, timing, resize behavior, and file size.

## Features

- **Easy Conversion** — Convert TGS to animated WebP with a single function call or CLI command.
- **Smart Timing Preservation** — Automatically adjusts output FPS to match the original animation's duration, so playback speed is preserved.
- **Manual FPS Control** — Disable automatic timing to set a custom FPS for full control over playback speed.
- **Configurable Frame Capping** — Limits output to 180 frames by default to save resources; easily adjust the cap or disable it entirely for long animations.
- **Intelligent File Size Compression** — Automatically adjusts quality and frame count to meet a target file size (e.g., ≤ 256 KB), with an optional fast mode.
- **Flexible Resize Modes** — Easily specify the output resolution and resize behavior (padding, cropping, stretching, etc.).
- **Dual Usage** — Works as a CLI tool *and* as an importable Python module. Use the simple `convert_tgs_to_webp()` function or the `TGSToWebPConverter` class for batch work.

---

## Setup & Installation

### 1. System Dependencies

This tool uses `rlottie_python`, which requires the **Cairo** graphics library.

-   **Debian / Ubuntu:**
    ```bash
    sudo apt-get install libcairo2-dev pkg-config python3-dev gcc
    ```
-   **Fedora / RHEL:**
    ```bash
    sudo dnf install cairo-devel pkg-config python3-devel gcc
    ```
-   **macOS (Homebrew):**
    ```bash
    brew install cairo pkg-config
    ```

### 2. Clone & Install

```bash
git clone https://github.com/not-right-now/tgs_to_webp.git
cd tgs_to_webp

# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate.bat     # Windows CMD
# venv\Scripts\Activate.ps1     # Windows PowerShell

# Install dependencies
pip install -r requirements.txt
```

---

## How to Use

### As a Command-Line Tool

**Basic usage:**
```bash
python tgs_to_webp.py sticker.tgs output.webp
```

**With custom settings:**
```bash
# Custom resolution and quality
python tgs_to_webp.py sticker.tgs output.webp --width 256 --height 256 --quality 90

# Compress to fit under 256 KB
python tgs_to_webp.py sticker.tgs output.webp --max-size 256

# Faster compression (allows 75%-100% of target)
python tgs_to_webp.py sticker.tgs output.webp --max-size 256 --fast

# Render all frames (no 180-frame cap)
python tgs_to_webp.py sticker.tgs output.webp --no-frame-cap

# Manual FPS (disables timing preservation)
python tgs_to_webp.py sticker.tgs output.webp --fps 15 --no-preserve-timing

# Crop instead of padding when resizing
python tgs_to_webp.py sticker.tgs output.webp --width 256 --height 128 --crop
```

**Full CLI reference:**

| Argument | Description | Default |
|---|---|---|
| `input_file` | *(required)* Path to the input TGS file. | — |
| `output_file` | *(required)* Path for the output WebP file. | — |
| `--width` | Output width in pixels (`-1` = original). | `-1` |
| `--height` | Output height in pixels (`-1` = original). | `-1` |
| `--quality` | WebP quality (0–100). Higher = better but larger. | `40` |
| `--max-frames` | Maximum frames to render (ignored if `--no-frame-cap`). | `180` |
| `--max-size` | Target file size cap in **KB**. Enables smart compression. | `None` |
| `--fps` | Frames per second (ignored unless `--no-preserve-timing`). | `30` |
| `--no-frame-cap` | Disable the frame cap — render every frame. | off |
| `--no-keep-aspect` | Stretch to fit target dimensions (ignore aspect ratio). | off |
| `--no-upscale` | Prevent enlarging sources smaller than the target. | off |
| `--crop` | When keeping aspect ratio, cover + center-crop instead of padding. | off |
| `--no-preserve-timing` | Use the manual `--fps` value instead of auto-timing. | off |
| `--fast` | Allow 75%–100% of `--max-size` for faster compression. | off |

---

### As a Python Module

#### Quick conversion

```python
from tgs_to_webp import convert_tgs_to_webp

# Simplest — all defaults
convert_tgs_to_webp('sticker.tgs', 'output.webp')

# Custom resolution & quality
convert_tgs_to_webp('sticker.tgs', 'output.webp',
                    width=256, height=256, quality=90)

# Compress to ≤ 256 KB
convert_tgs_to_webp('sticker.tgs', 'output.webp',
                    max_size=256)

# All frames, no cap
convert_tgs_to_webp('sticker.tgs', 'output.webp',
                    frame_cap=False)

# Manual FPS
convert_tgs_to_webp('sticker.tgs', 'output.webp',
                    fps=15, preserve_timing=False)
```

#### Class-based (batch / reuse)

```python
from tgs_to_webp import TGSToWebPConverter

# Configure once
converter = TGSToWebPConverter(
    width=512,
    height=512,
    quality=70,
    max_size=512,           # ≤ 512 KB
    preserve_timing=True,   # keep original speed
)

# Convert many files with the same settings
converter.convert('sticker1.tgs', 'out1.webp')
converter.convert('sticker2.tgs', 'out2.webp')
converter.convert('sticker3.tgs', 'out3.webp')
```

#### Full parameter reference — `convert_tgs_to_webp()`

| Parameter | Type | Default | Description |
|---|---|---|---|
| `tgs_path` | `str` | *(required)* | Path to input TGS file. |
| `webp_path` | `str` | *(required)* | Path for output WebP file. |
| `width` | `int` | `-1` | Output width (`-1` = original). |
| `height` | `int` | `-1` | Output height (`-1` = original). |
| `quality` | `int` | `40` | WebP quality (0–100). |
| `frame_cap` | `bool` | `True` | Whether to cap the number of rendered frames. |
| `max_frames` | `int` | `180` | Frame cap limit (ignored when `frame_cap=False`). |
| `max_size` | `int\|None` | `None` | Target file size in **KB**. Enables smart compression. |
| `keep_aspect` | `bool` | `True` | Preserve aspect ratio when resizing. |
| `allow_upscale` | `bool` | `True` | Allow enlarging smaller sources to meet target. |
| `pad` | `bool` | `True` | When `keep_aspect=True`: pad with transparency (`True`) or cover+crop (`False`). |
| `fps` | `float` | `30.0` | Manual FPS (only used when `preserve_timing=False`). |
| `preserve_timing` | `bool` | `True` | Auto-adjust FPS to keep original animation duration. |
| `compress_faster` | `bool` | `False` | Accept 75%–100% of `max_size` for faster compression. |

**Returns:** `True` on success, `False` on failure.

---

## Running the Demo

A comprehensive demo script ([`demo.py`](demo.py)) is included to showcase every feature.

1.  **Input files:** The `demo_inp/` directory already contains sample `.tgs` files. Feel free to add your own!

2.  **Run:**
    ```bash
    python demo.py
    ```
    > The demo clears `demo_out/` at the start of each run for a fresh start.

3.  **Inspect results:** All output `.webp` files are written to `demo_out/` with descriptive names like `resolution_256x256_Q70.webp`, `compress_256kb_strict.webp`, `resize_crop.webp`, etc.

The demo covers: basic conversion, custom resolution & quality, frame capping, file size compression, resize modes (pad / crop / stretch / no-upscale), manual timing, and class-based batch usage.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
