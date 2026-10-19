#!/usr/bin/env python3
"""
Cyber-Teal & Electric Violet Sub-Pixel Terminal Loader (v2).
Completely different architecture:
- Uses 1/8th Unicode sub-blocks (▏▎▍▌▋▊▉█) for 8x horizontal resolution.
- Dual-lane layout with real-time Braille waveform equalizer and hex memory address ticker.
- 24-bit TrueColor Cyan -> Violet -> Acid Mint gradient.
- Zero external dependencies, O(1) memory footprint, guaranteed cursor restoration.
"""

import os
import sys
import time
import math

if os.name == "nt":
    os.system("")

# Sub-pixel block characters (1/8 to 8/8 width)
_SUB_BLOCKS = (" ", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█")

# Vertical Braille bars for the real-time waveform visualizer
_WAVE_BARS = ("⠀", "⡀", "⡄", "⡆", "⡇", "⣇", "⣧", "⣷", "⣿")

_TASKS = (
    (0,   "MOUNT_VFS",     "Mounting virtual filesystem nodes"),
    (14,  "ALLOC_HEAP",    "Reserving contiguous ring-buffer pages"),
    (29,  "SYNC_SHADERS",  "Compiling compute pipeline kernels"),
    (46,  "DECRYPT_BLOB",  "Verifying Ed25519 payload blocks"),
    (63,  "LINK_SYMBOLS",  "Resolving dynamic syscall table"),
    (80,  "FLUSH_CACHE",   "Warming L1/L2 instruction lines"),
    (93,  "HANDSHAKE",     "Establishing zero-copy IPC socket"),
    (100, "EXEC_READY",    "Control transferred to main thread"),
)

_HIDE_CURSOR = "\033[?25l"
_SHOW_CURSOR = "\033[?25h"
_RESET       = "\033[0m"
_FG_DIM      = "\033[38;2;75;85;105m"
_FG_LABEL    = "\033[38;2;140;160;195m"
_FG_CYAN     = "\033[38;2;0;245;212m"
_FG_VIOLET   = "\033[38;2;168;85;247m"
_FG_MINT     = "\033[38;2;110;255;160m"


def _lerp_color(t: float) -> tuple[int, int, int]:
    """Interpolates between Electric Cyan -> Neon Violet -> Acid Mint."""
    if t < 0.5:
        u = t * 2.0
        r = int(0 + 155 * u)
        g = int(240 - 155 * u)
        b = int(225 + 30 * u)
    else:
        u = (t - 0.5) * 2.0
        r = int(155 - 155 * u)
        g = int(85 + 170 * u)
        b = int(255 - 75 * u)
    return r, g, b


def _render_subpixel_bar(pct: float, width: int, elapsed: float) -> str:
    """Renders a high-precision sub-pixel bar with a shifting neon gradient."""
    total_subpixels = (pct / 100.0) * width * 8.0
    full_cells = int(total_subpixels // 8)
    remainder = int(total_subpixels % 8)

    out = []
    for i in range(width):
        # Shifting color phase along the bar
        t = ((i / max(1, width - 1)) - elapsed * 0.45) % 1.0
        r, g, b = _lerp_color(t)
        if i < full_cells:
            out.append(f"\033[38;2;{r};{g};{b}m█")
        elif i == full_cells and remainder > 0:
            out.append(f"\033[38;2;{r};{g};{b}m{_SUB_BLOCKS[remainder]}")
        else:
            out.append(f"{_FG_DIM}·")
    out.append(_RESET)
    return "".join(out)


def _render_waveform(width: int, elapsed: float, active: bool) -> str:
    """Generates an animated Braille spectrum analyzer."""
    if not active:
        return f"{_FG_MINT}{'⣿' * width}{_RESET}"
    out = []
    for i in range(width):
        val = (
            math.sin(elapsed * 8.0 + i * 0.7)
            * math.cos(elapsed * 4.5 - i * 0.4)
        )
        idx = int((val + 1.0) * 0.5 * (len(_WAVE_BARS) - 1))
        t = (i / max(1, width - 1) + elapsed * 0.3) % 1.0
        r, g, b = _lerp_color(t)
        out.append(f"\033[38;2;{r};{g};{b}m{_WAVE_BARS[idx]}")
    out.append(_RESET)
    return "".join(out)


def _get_stage(pct: float) -> tuple[str, str]:
    stage, desc = _TASKS[0][1], _TASKS[0][2]
    for threshold, s_code, s_desc in _TASKS:
        if pct >= threshold:
            stage, desc = s_code, s_desc
        else:
            break
    return stage, desc


def run_cyber_loader(duration: float = 11.0, bar_width: int = 38) -> None:
    """
    Runs a minimalist, borderless Cyber-Teal & Violet sub-pixel loading screen.
    Guaranteed minimum duration of 10+ seconds.
    """
    duration = max(10.0, float(duration))
    fps = 30.0
    frame_delay = 1.0 / fps
    start_time = time.monotonic()
    frame = 0

    # Reserve 5 lines for borderless telemetry layout
    sys.stdout.write(_HIDE_CURSOR + "\n" * 5)
    sys.stdout.flush()

    try:
        while True:
            elapsed = time.monotonic() - start_time
            u = min(1.0, elapsed / duration)

            # Non-linear multi-stage curve (simulates real I/O bursts + stalls)
            wobble = 0.018 * math.sin(u * math.pi * 6.0) * (1.0 - u)
            pct = max(0.0, min(100.0, (u + wobble) * 100.0))
            if u >= 1.0:
                pct = 100.0

            stage_code, stage_desc = _get_stage(pct)
            bar = _render_subpixel_bar(pct, bar_width, elapsed)
            wave = _render_waveform(12, elapsed, u < 1.0)

            # Deterministic pseudo-memory address & throughput metrics
            mem_addr = 0x7FF000400000 + int(pct * 0x1A4F0) + (frame * 64)
            throughput = 420.0 + 180.0 * math.sin(elapsed * 3.2) if u < 1.0 else 0.0

            # Step dots indicator (8 stages)
            completed_Dots = int((pct / 100.0) * 8)
            dots = (
                f"{_FG_CYAN}{'◆' * completed_Dots}"
                f"{_FG_DIM}{'◇' * (8 - completed_Dots)}{_RESET}"
            )

            line1 = (
                f"  {_FG_VIOLET}⚡ KERNEL//BOOT{_RESET}  {dots}  "
                f"{_FG_DIM}ADDR:{_RESET} {_FG_LABEL}0x{mem_addr:012X}{_RESET}"
            )
            line2 = f"  {_FG_DIM}├─{_RESET} {bar} {_FG_CYAN}{pct:6.2f}%{_RESET}"
            line3 = (
                f"  {_FG_DIM}├─{_RESET} {_FG_VIOLET}[{stage_code:<12}]{_RESET} "
                f"{_FG_LABEL}{stage_desc:<38}{_RESET}"
            )
            line4 = (
                f"  {_FG_DIM}└─{_RESET} {wave}  "
                f"{_FG_DIM}IO:{_RESET} {_FG_MINT}{throughput:5.1f} MB/s{_RESET}   "
                f"{_FG_DIM}T+{elapsed:05.2f}s / {duration:05.2f}s{_RESET}"
            )

            sys.stdout.write(f"\033[4A\r{line1}\n{line2}\n{line3}\n{line4}")
            sys.stdout.flush()

            if u >= 1.0:
                break

            frame += 1
            sleep_for = (start_time + frame * frame_delay) - time.monotonic()
            if sleep_for > 0:
                time.sleep(sleep_for)

        time.sleep(0.35)
    except KeyboardInterrupt:
        sys.stdout.write(f"\n  {_FG_VIOLET}[ABORT]{_RESET} Sequence interrupted.\n")
    finally:
        sys.stdout.write(_SHOW_CURSOR + "\n")
        sys.stdout.flush()


    a=input("odpowiedz")


if __name__ == "__main__":
    run_cyber_loader(duration=11.0)
