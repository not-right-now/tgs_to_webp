# TGS to WebP Converter 🎞️✨

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A handy and flexible Python tool to convert TGS (Telegram Animated Stickers) files into high-quality animated WebP format.

The primary goal of this project is to provide a simple way to convert these animations while intelligently preserving the original timing and duration, so your animations don't look sped up or slowed down. It's perfect for developers, content creators, or anyone who wants to use TGS animations in web projects.

## 🚀 Features

- **😋 Easy Conversion**: Convert TGS to animated WebP with a single command or function call.
- **🧠 Smart Timing Preservation**: Automatically adjusts FPS to match the original animation's duration.
- **⚙️ Manual Control**: Option to disable automatic timing and set a manual FPS for full control.
- **📦 Intelligent File Size Compression**: A special version of the script automatically adjusts quality and frame count to meet a file size target (e.g., under 500KB).
- **🎨 Customizable Output**: Easily specify output resolution (`width`, `height`) and `quality`.
- **💻 Dual Usage Mode**: Can be used as a command-line tool or imported as a module into your own Python projects.
- **✌️ Three Flavors**:
    1.  `tgs_to_webp.py`: **Performance-focused** version that limits animations to 180 frames to prevent high resource usage. Ideal for most stickers.
    2.  `tgs_to_webp_no_frame_limits.py`: **Power-user** version that removes the 180-frame limit for extra-long animations. Use with caution!
    3.  `tgs_to_webp_with_file_size_restriction.py`: **Size-focused** version that intelligently compresses the output to stay under a specific file size cap. Perfect for platforms with strict file size limits.

---

## 🔧 Setup & Installation

Before you can use the converter, you'll need to set up your environment.

### 1. System Dependencies (Cairo)

This tool uses `lottie`, which relies on the Cairo graphics library to render animation frames. You'll need to install it on your system first.

-   **On Fedora (and other RHEL-based systems):**
    ```bash
    sudo dnf install cairo-devel pkg-config python3-devel gcc
    ```
-   **On Debian/Ubuntu:**
    ```bash
    sudo apt-get install libcairo2-dev pkg-config python3-dev
    ```
-   **On macOS (using Homebrew):**
    ```bash
    brew install cairo pkg-config
    ```

### 2. Clone the Repository

Get the project files by cloning the repository:
```bash
git clone https://github.com/not-right-now/tgs_to_webp.git
cd tgs_to_webp
```

### 3. Install Python Packages

Install the required Python libraries using the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

---

## 💡 How to Use

You can use this tool directly from your terminal or import it into your Python scripts.

### As a Command-Line Tool

This is the quickest way to convert a single file. The arguments are the same for all script versions.

**Basic Usage:**
```bash
python tgs_to_webp.py path/to/your/sticker.tgs path/to/your/output.webp
```

**Command-Line Arguments:**

| Argument              | Description                                                                                             | Default    |
| --------------------- | ------------------------------------------------------------------------------------------------------- | ---------- |
| `input_file`          | (Required) Path to the input TGS file.                                                                  | -          |
| `output_file`         | (Required) Path for the output WebP file.                                                               | -          |
| `--width`             | Output width in pixels.                                                                                 | `Original` |
| `--height`            | Output height in pixels.                                                                                | `Original` |
| `--quality`           | WebP quality (0-100). Higher is better.                                                                 | `80`       |
| `--fps`               | Frames per second. **Ignored by default** in timing-preserving scripts.                                 | `30`       |
| `--no-preserve-timing`| (Only in `tgs_to_webp.py`) A flag to disable automatic timing preservation and use the manual `--fps` value instead. | `False`    |

**Example with custom settings:**
```bash
python tgs_to_webp.py "demo_inp/AnimatedSticker.tgs" "demo_out/custom.webp" --width 256 --height 256 --quality 95
```

### As a Python Module

Import the converter into your project for more programmatic control.

**Simple Usage (Recommended):**
```python
from tgs_to_webp import convert_tgs_to_webp

success = convert_tgs_to_webp('input.tgs', 'output.webp', quality=90)

if success:
    print("🎉 Conversion successful!")
else:
    print("😢 Conversion failed.")
```

**Advanced Usage (Class-based):**
For more complex scenarios, you can use the `TGSToWebPConverter` class. This is useful if you want to convert multiple files with the same settings.
```python
from tgs_to_webp import TGSToWebPConverter

# Configure the converter once
converter = TGSToWebPConverter(
    width=512,
    height=512,
    quality=85,
    preserve_timing=True # This is the default
)

# Reuse it for multiple files
converter.convert('sticker1.tgs', 'output1.webp')
converter.convert('sticker2.tgs', 'output2.webp')
```

---

## 📦 The "File Size Restricted" Version

Do you need your final WebP file to be under a certain size (e.g., 500KB)? The `tgs_to_webp_with_file_size_restriction.py` script is your solution! It uses a smart optimization algorithm to find the best combination of frame count and quality to meet a target file size.

**🚨 Warning:** This process can be slower than the other scripts because it has to pre-render all frames and then run multiple compression tests to find the optimal result.

To use it, simply point to the correct script file:

**Command-Line:**
```bash
python tgs_to_webp_with_file_size_restriction.py your_sticker.tgs your_output.webp
```

**Python Module:**
```python
# Import from the size-restricted script
from tgs_to_webp_with_file_size_restriction import convert_tgs_to_webp

# The rest of your code remains the same!
success = convert_tgs_to_webp('animation.tgs', 'output_under_500kb.webp')
```

---

## ⚠️ The "No Frame Limits" Version

For animations that are longer than 180 frames, the standard `tgs_to_webp.py` will cap the output to save memory and CPU time. If you absolutely need to render every single frame of a long animation, you can use `tgs_to_webp_no_frame_limits.py`.

**🚨 Warning:** Converting animations with a very high frame count can be resource-intensive and may consume a lot of RAM and CPU. Use this version wisely!

To use it, simply change your script file or import statement:

```python
# Instead of from tgs_to_webp import ...
from tgs_to_webp_no_frame_limits import convert_tgs_to_webp

# The rest of your code remains the same!
success = convert_tgs_to_webp('long_animation.tgs', 'long_output.webp')
```

---

## 🎬 Running the Demo

A comprehensive demo script (`demo.py`) is included to showcase all the features.

1.  **Check TGS files**: The `demo_inp/` directory already contains a couple of sample `.tgs` files to get you started. Feel free to add your own!

2.  **Run the script**:
    ```bash
    python demo.py
    ```
    > **Note:** The demo script will first clear the `demo_out/` directory to ensure a fresh start for each run.

3.  **Check the results**: The script will run through various conversion scenarios and place all the output `.webp` files in the `demo_out/` directory for you to inspect.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
