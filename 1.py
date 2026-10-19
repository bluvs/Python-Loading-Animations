#!/usr/bin/env python3
"""
Lightweight, zero-dependency, low-RAM terminal loading screen.
Features a crimson/black 24-bit ANSI shimmer effect, rotating status logs,
and guaranteed cursor restoration to prevent terminal state leaks.
"""

import os
import sys
import time
import math

# Enable ANSI escape sequences on Windows 10/11
if os.name == "nt":
    os.system("")

# Pre-allocated static tuples to minimize memory overhead and GC pressure
_SPINNER_FRAMES = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
_STATUS_STEPS = (
    (0,   "Initializing core environment..."),
    (15,  "Allocating virtual memory buffers..."),
    (32,  "Verifying cryptographic signatures..."),
    (50,  "Loading execution modules..."),
    (68,  "Optimizing runtime pipeline..."),
    (85,  "Synchronizing state threads..."),
    (96,  "Finalizing startup sequence..."),
    (100, "System ready.                   "),
)

# ANSI control constants
_HIDE_CURSOR = "\033[?25l"
_SHOW_CURSOR = "\033[?25h"
_RESET       = "\033[0m"
_BG_BLACK    = "\033[48;2;12;12;12m"
_FG_DARK_GRAY= "\033[38;2;55;55;55m"
_FG_MUTED    = "\033[38;2;160;160;160m"
_FG_BRIGHT   = "\033[38;2;255;60;60m"
_FG_CRIMSON  = "\033[38;2;190;15;25m"
_FG_BORDER   = "\033[38;2;90;15;20m"


def _get_status(pct: float) -> str:
    current = _STATUS_STEPS[0][1]
    for threshold, text in _STATUS_STEPS:
        if pct >= threshold:
            current = text
        else:
            break
    return current


def _build_shimmer_bar(pct: float, width: int, phase: float) -> str:
    """Builds a progress bar with a moving crimson/scarlet highlight wave."""
    filled = int(round((pct / 100.0) * width))
    chars = []
    
    for i in range(width):
        if i < filled:
            # Traveling wave calculation for the red/black shine effect
            wave = math.sin((i * 0.35) - phase)
            if wave > 0.82:
                # Specular highlight (bright scarlet/white-hot edge)
                r, g, b = 255, 85, 85
            elif wave > 0.0:
                # Mid-crimson shine
                r = int(140 + 110 * wave)
                g = int(15 * wave)
                b = int(20 * wave)
            else:
                # Deep shadow crimson/black
                r = int(45 + 75 * (1.0 + wave))
                g, b = 0, 5
            chars.append(f"\033[38;2;{r};{g};{b}m█")
        else:
            # Unfilled track in dark obsidian gray
            chars.append(f"{_FG_DARK_GRAY}░")
            
    chars.append(_RESET)
    return "".join(chars)


def run_loading_screen(duration: float = 11.0, bar_width: int = 42) -> None:
    """
    Runs the crimson & black shining loading animation.
    Guaranteed to take at least `duration` seconds (default 11.0s).
    """
    duration = max(10.0, float(duration))
    fps = 30.0
    frame_delay = 1.0 / fps
    start_time = time.monotonic()
    frame_idx = 0

    # Reserve 4 vertical lines for the UI box and hide cursor
    sys.stdout.write(_HIDE_CURSOR + "\n" * 4)
    sys.stdout.flush()

    try:
        while True:
            elapsed = time.monotonic() - start_time
            raw_progress = min(1.0, elapsed / duration)
            
            # Smooth easing curve (ease-in-out cubic blend) for realistic loading feel
            smoothed = 0.7 * raw_progress + 0.3 * (
                3 * (raw_progress ** 2) - 2 * (raw_progress ** 3)
            )
            pct = min(100.0, smoothed * 100.0)
            phase = elapsed * 7.5  # Speed of the red/black shine wave

            spinner = _SPINNER_FRAMES[frame_idx % len(_SPINNER_FRAMES)] if pct < 100.0 else "✔"
            status_msg = _get_status(pct)
            bar_str = _build_shimmer_bar(pct, bar_width, phase)

            # Pulsing title glow
            pulse = int(160 + 95 * (0.5 + 0.5 * math.sin(elapsed * 4.0)))
            title_color = f"\033[38;2;{pulse};20;30m"

            inner_width = bar_width + 12
            top_border = f"{_FG_BORDER}╔{'═' * inner_width}╗{_RESET}"
            bot_border = f"{_FG_BORDER}╚{'═' * inner_width}╝{_RESET}"

            header_text = f" {spinner} SYSTEM INITIALIZATION"
            eta_val = max(0.0, duration - elapsed)
            eta_text = f"ETA: {eta_val:04.1f}s "
            pad_len = max(1, inner_width - len(header_text) - len(eta_text))

            line1 = (
                f"{_FG_BORDER}║{_BG_BLACK}{title_color}{header_text}"
                f"{' ' * pad_len}{_FG_MUTED}{eta_text}{_RESET}{_FG_BORDER}║{_RESET}"
            )
            line2 = (
                f"{_FG_BORDER}║{_BG_BLACK}  [{bar_str}{_BG_BLACK}] "
                f"{_FG_BRIGHT}{pct:6.2f}% {_RESET}{_FG_BORDER}║{_RESET}"
            )
            status_padded = f"  > {status_msg}".ljust(inner_width)
            line3 = (
                f"{_FG_BORDER}║{_BG_BLACK}{_FG_CRIMSON}{status_padded}"
                f"{_RESET}{_FG_BORDER}║{_RESET}"
            )

            # Move cursor up 4 lines and overwrite in a single buffered write
            output = f"\033[4A\r{top_border}\n{line1}\n{line2}\n{line3}\n{bot_border}"
            sys.stdout.write(output)
            sys.stdout.flush()

            if raw_progress >= 1.0:
                break

            frame_idx += 1
            # Precise frame pacing without busy-waiting CPU spikes
            next_frame_time = start_time + (frame_idx * frame_delay)
            sleep_time = next_frame_time - time.monotonic()
            if sleep_time > 0:
                time.sleep(sleep_time)

        time.sleep(0.4)
    except KeyboardInterrupt:
        sys.stdout.write(f"\n{_FG_BRIGHT}[!] Loading aborted by user.{_RESET}\n")
    finally:
        # Always restore cursor visibility to avoid corrupting user's terminal
        sys.stdout.write(_SHOW_CURSOR + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    run_loading_screen(duration=11.0)
