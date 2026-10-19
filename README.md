# Terminal FX Loaders (24-Bit ANSI)

A lightweight, zero-dependency collection of 24-bit TrueColor terminal loading screens and procedural ASCII/pixel-art animations for Python CLI applications. Built purely with Python's standard library (`sys`, `os`, `time`, `math`) for an `O(1)` memory footprint and zero external package overhead.

## Key Features

* **Zero Dependencies**: No `rich`, `curses`, or `colorama` required. Runs out of the box on Python 3.8+.
* **24-Bit TrueColor Engine**: Real-time RGB wave interpolation and sine-based shaders using raw ANSI escape sequences (`\033[38;2;R;G;Bm`).
* **Flicker-Free Rendering**: Single buffered `sys.stdout.write` calls per frame locked at 30 FPS without CPU busy-waiting.
* **Memory Safe**: Pre-allocated static tuples and deterministic math calculations prevent garbage collection spikes or memory leaks.
* **Crash-Safe Cursor Handling**: Guaranteed terminal cursor restoration (`\033[?25h`) via `try...finally` blocks, even on `Ctrl+C` (`KeyboardInterrupt`).
* **Cross-Platform**: Native support for Linux, macOS, and Windows 10/11 (Windows Terminal / PowerShell / CMD).
* **10 second animation**: Every animation lasts for minimum 10 seconds which makes your project look more `professional`.

---

## Included Modules

| Module | Visual Style | Palette | Resolution / Technique |
| :--- | :--- | :--- | :--- |
| `red_black_loader.py` | Framed UI + Shimmer Progress Bar (`0-100%`) | Crimson, Scarlet & Obsidian Black | Full-block (`█`) traveling sine wave |
| `cyber_subpixel_loader_v2.py` | Borderless Kernel Telemetry + Braille Equalizer | Electric Cyan, Neon Violet & Acid Mint | 1/8th Sub-pixel Unicode blocks (`▏▎▍▌▋▊▉█`) |
| `emerald_matrix_screen_v3.py` | 2D Bio-Radar & Plasma Interference Field | Phosphor Forest, Emerald & Neon Lime | Multi-density ASCII/Unicode shading (`·∶∷░▒▓█`) |
| `pixel_art_arcade_loader_v4.py` | Animated 16x16 Cyber-Skull Sprite + Embers | Synthwave Gold, Hot Magenta & Deep Indigo | Half-block vertical pixel packing (`▀` = 2px/cell) |

---

## Installation

Clone the repository and copy the desired loader script into your project directory:

```bash
git clone https://github.com/YOUR_USERNAME/terminal-fx-loaders.git
cd terminal-fx-loaders
```

*(Note: Ensure filenames use underscores `_` instead of hyphens `-` when importing them as Python modules).*

---

## Usage

### 1. Standalone Demo
Run any module directly from the terminal:

```bash
python red_black_loader.py
python cyber_subpixel_loader_v2.py
python emerald_matrix_screen_v3.py
python pixel_art_arcade_loader_v4.py
```

### 2. Basic Integration
Import and call the loader function at the start of your CLI script. All loaders enforce a minimum duration of `10.0` seconds.

```python
from red_black_loader import run_loading_screen
from cyber_subpixel_loader_v2 import run_cyber_loader
from emerald_matrix_screen_v3 import run_green_screen
from pixel_art_arcade_loader_v4 import run_pixel_art_screen

# Choose one for your startup sequence:
run_loading_screen(duration=11.0)
# run_cyber_loader(duration=11.0)
# run_green_screen(duration=11.0)
# run_pixel_art_screen(duration=11.0)
```

### 3. Running Tasks in the Background (Threaded)
To execute actual initialization logic (API calls, file I/O, database connections) while the animation plays:

```python
import threading
import time
from pixel_art_arcade_loader_v4 import run_pixel_art_screen

def init_app(state: dict) -> None:
    # Put your actual startup logic here (e.g., API requests, DB setup)
    time.sleep(4.0)
    state["ready"] = True

def main() -> None:
    app_state = {"ready": False}

    # Start background task in a daemon thread
    worker = threading.Thread(target=init_app, args=(app_state,), daemon=True)
    worker.start()

    # Play the terminal animation while the background thread works
    run_pixel_art_screen(duration=10.5)

    # Wait for the background thread to finish (if it took longer than 10.5s)
    worker.join()
    print(f"Application initialized successfully: {app_state['ready']}")

if __name__ == "__main__":
    main()
```

---

## Project Structure

```text
terminal-fx-loaders/
├── red_black_loader.py           # v1: Crimson & Obsidian 0-100% progress bar
├── cyber_subpixel_loader_v2.py   # v2: Sub-pixel Cyber-Teal & Violet loader
├── emerald_matrix_screen_v3.py   # v3: 2D Emerald flickering plasma/radar screen
├── pixel_art_arcade_loader_v4.py # v4: Half-block 16x16 Pixel-Art Mecha core
└── README.md                     # Project documentation
```

---

## Requirements

* **Python**: 3.8 or higher
* **Terminal**: Any modern terminal emulator supporting 24-bit TrueColor and UTF-8 (Windows Terminal, Alacritty, Kitty, WezTerm, iTerm2, GNOME Terminal, VS Code Integrated Terminal).

## License

MIT License
