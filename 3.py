#!/usr/bin/env python3
"""
Phosphor Green CRT Radar & Bio-Signal Oscilloscope Screen (v3).
Not a loading bar — a full 2D real-time animated HUD screen rendered in the terminal.
Features:
- Rotating 360-degree Radar Sweep with phosphor persistence decay and target locking.
- Real-time sinusoidal Lissajous / ECG oscilloscope waveform panel.
- Zero external dependencies, O(1) pre-allocated frame buffers (no memory leaks),
  single-write double buffering for zero flicker.
"""

import os
import sys
import time
import math

if os.name == "nt":
    os.system("")

# ANSI Control Sequences
_HIDE_CURSOR = "\033[?25l"
_SHOW_CURSOR = "\033[?25h"
_RESET       = "\033[0m"
_BG_CRT      = "\033[48;2;4;12;6m"
_FG_BORDER   = "\033[38;2;20;95;40m"
_FG_DIM      = "\033[38;2;18;65;30m"
_FG_MID      = "\033[38;2;40;180;75m"
_FG_BRIGHT   = "\033[38;2;110;255;135m"
_FG_WHITE_G  = "\033[38;2;210;255;220m"

# Pre-defined radar targets: (normalized_x, normalized_y, label)
_TARGETS = (
    ( 0.45, -0.35, "NODE_ALPHA"),
    (-0.55,  0.25, "RF_BEACON "),
    ( 0.20,  0.60, "SAT_UPLINK"),
    (-0.30, -0.50, "PROXY_09  "),
)

_SHADE_CHARS = ("·", "░", "▒", "▓", "█")


def _phosphor_color(intensity: float) -> str:
    """Maps 0.0-1.0 phosphor intensity to 24-bit CRT green shades."""
    if intensity > 0.88:
        return _FG_WHITE_G
    if intensity > 0.65:
        return _FG_BRIGHT
    if intensity > 0.35:
        return _FG_MID
    return _FG_DIM


def _render_radar_row(
    row_idx: int, height: int, width: int, sweep_angle: float
) -> tuple[str, str]:
    """
    Renders one horizontal scanline of the circular radar and detects active lock.
    Aspect ratio corrected (2 chars wide per 1 char tall).
    """
    ny = (row_idx - (height - 1) / 2.0) / ((height - 1) / 2.0)
    row_chars = []
    locked_label = "SCANNING_SECTOR..."

    for col_idx in range(width):
        nx = (col_idx - (width - 1) / 2.0) / ((width - 1) / 2.0)
        dist = math.hypot(nx, ny)

        if dist > 1.03:
            row_chars.append(" ")
            continue

        # Outer ring and inner range rings
        if 0.96 <= dist <= 1.03 or abs(dist - 0.5) < 0.035:
            row_chars.append(f"{_FG_BORDER}·")
            continue

        # Crosshair axes
        if abs(nx) < 0.025 or abs(ny) < 0.045:
            row_chars.append(f"{_FG_DIM}+")
            continue

        # Calculate polar angle and phosphor trail behind sweep line
        angle = math.atan2(ny, nx)
        diff = (sweep_angle - angle) % (2.0 * math.pi)
        trail = max(0.0, 1.0 - (diff / (math.pi * 0.65)))

        # Check proximity to any target
        target_hit = False
        for tx, ty, tlabel in _TARGETS:
            if math.hypot(nx - tx, ny - ty) < 0.11:
                target_hit = True
                if trail > 0.55:
                    locked_label = f"LOCK: {tlabel}"
                if trail > 0.25:
                    row_chars.append(f"{_FG_WHITE_G}◈")
                else:
                    row_chars.append(f"{_FG_MID}◈")
                break

        if target_hit:
            continue

        if trail > 0.93:
            # Leading laser edge of the radar sweep
            row_chars.append(f"{_FG_WHITE_G}█")
        elif trail > 0.08:
            shade_idx = min(4, int(trail * 4.5))
            color = _phosphor_color(trail)
            row_chars.append(f"{color}{_SHADE_CHARS[shade_idx]}")
        else:
            row_chars.append(" ")

    return "".join(row_chars), locked_label


def _render_oscilloscope_row(
    row_idx: int, height: int, width: int, elapsed: float
) -> str:
    """Renders a dual-harmonic green oscilloscope wave on the right panel."""
    ny = (row_idx - (height - 1) / 2.0) / ((height - 1) / 2.0)
    chars = []
    for x in range(width):
        t = (x / max(1, width - 1)) * math.pi * 3.0
        # Composite carrier + modulation wave
        wave_y = 0.55 * math.sin(t - elapsed * 6.5) * math.cos(t * 0.4 + elapsed * 2.2)
        dist = abs(ny - wave_y)
        if dist < 0.13:
            chars.append(f"{_FG_WHITE_G}━")
        elif dist < 0.26:
            chars.append(f"{_FG_MID}·")
        elif abs(ny) < 0.05:
            chars.append(f"{_FG_DIM}┄")
        else:
            chars.append(" ")
    return "".join(chars)


def run_phosphor_screen(duration: float = 11.0) -> None:
    """
    Displays a 14-line animated Phosphor Green Radar & Oscilloscope HUD screen
    for at least `duration` seconds (minimum 10.0s enforced).
    """
    duration = max(10.0, float(duration))
    fps = 30.0
    frame_delay = 1.0 / fps
    start_time = time.monotonic()
    frame = 0

    radar_h = 11
    radar_w = 25
    scope_w = 24
    total_inner_w = radar_w + scope_w + 5  # 54 chars total inside borders

    # Reserve 15 vertical lines once to render in-place without scrolling
    sys.stdout.write(_HIDE_CURSOR + "\n" * (radar_h + 4))
    sys.stdout.flush()

    try:
        while True:
            elapsed = time.monotonic() - start_time
            if elapsed >= duration:
                break

            sweep_angle = (elapsed * 2.6) % (2.0 * math.pi) - math.pi
            deg = int(((sweep_angle + math.pi) / (2.0 * math.pi)) * 360.0) % 360
            freq = 433.92 + 0.08 * math.sin(elapsed * 5.0)

            top_bar = f"{_FG_BORDER}┏{'━' * radar_w}┳{'━' * (scope_w + 4)}┓{_RESET}"
            header = (
                f"{_FG_BORDER}┃{_BG_CRT}{_FG_BRIGHT} ☢ CRT//RADAR_SWEEP      "
                f"{_FG_BORDER}┃{_BG_CRT}{_FG_BRIGHT} SIGNAL_OSCILLOSCOPE        {_FG_BORDER}┃{_RESET}"
            )
            sep_bar = f"{_FG_BORDER}┣{'━' * radar_w}╋{'━' * (scope_w + 4)}┫{_RESET}"

            lines = [top_bar, header, sep_bar]
            active_lock = "SCANNING_SECTOR..."

            for r in range(radar_h):
                r_str, lock_candidate = _render_radar_row(r, radar_h, radar_w, sweep_angle)
                if lock_candidate != "SCANNING_SECTOR...":
                    active_lock = lock_candidate

                if r < 6:
                    s_str = _render_oscilloscope_row(r, 6, scope_w, elapsed)
                    right_col = f"  {s_str}  "
                elif r == 6:
                    right_col = f"{_FG_DIM}  {'─' * scope_w}  "
                elif r == 7:
                    right_col = f"  {_FG_MID}AZIMUTH : {_FG_WHITE_G}{deg:03d}° DEG      "
                elif r == 8:
                    right_col = f"  {_FG_MID}CARRIER : {_FG_WHITE_G}{freq:06.2f} MHz  "
                elif r == 9:
                    right_col = f"  {_FG_MID}STATUS  : {_FG_BRIGHT}{active_lock:<16}"
                else:
                    rem = max(0.0, duration - elapsed)
                    right_col = f"  {_FG_DIM}UPTIME  : {elapsed:05.2f}s (-{rem:04.1f}s) "

                lines.append(
                    f"{_FG_BORDER}┃{_BG_CRT}{r_str}{_FG_BORDER}┃{_BG_CRT}{right_col}{_RESET}{_FG_BORDER}┃{_RESET}"
                )

            bot_bar = f"{_FG_BORDER}┗{'━' * radar_w}┻{'━' * (scope_w + 4)}┛{_RESET}"
            lines.append(bot_bar)

            # Single atomic stdout write to prevent tearing/flicker
            sys.stdout.write(f"\033[{len(lines) - 1}A\r" + "\n".join(lines))
            sys.stdout.flush()

            frame += 1
            sleep_time = (start_time + frame * frame_delay) - time.monotonic()
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        sys.stdout.write(f"\n{_FG_BRIGHT}[!] CRT HUD terminated.{_RESET}\n")
    finally:
        sys.stdout.write(_SHOW_CURSOR + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    run_phosphor_screen(duration=11.0)
