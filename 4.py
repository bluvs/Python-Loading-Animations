#!/usr/bin/env python3
"""
Retro Arcade Pixel-Art Terminal Scene (v4).
Pure character-based pixel art engine using half-block vertical packing (▀).
Each terminal cell renders TWO vertical pixels (foreground = top, background = bottom).
Features an animated cyberpunk Mecha/Skull core with floating embers,
blinkingvisor, vertical bobbing, and a retro synthwave color palette.
Zero external dependencies, O(1) memory footprint, guaranteed cursor cleanup.
"""

import os
import sys
import time
import math

if os.name == "nt":
    os.system("")

_HIDE_CURSOR = "\033[?25l"
_SHOW_CURSOR = "\033[?25h"
_RESET       = "\033[0m"

# 16x16 Pixel Art Sprite: Cyber-Skull / Mecha Core
# Legend:
# '.' = empty background
# 'O' = dark outline
# 'S' = mid armor / bone shadow
# 'H' = bright armor highlight
# 'E' = glowing visor / eyes (animated color)
# 'C' = core energy vents (pulsing)
_SPRITE_16X16 = (
    "....OOOOOOOO....",
    "..OOSSSSSSSSOO..",
    ".OSSHSSSSSSHSSO.",
    ".OSHHHHHHHHHHSO.",
    "OSSHSSSSSSSSHSIO",
    "OSSOEEEEEEEEOSSO",
    "OSSEEEEEEEEEESSO",
    "OSSOEEEEEEEEOSSO",
    "OSSSSSSSSSSSSSSO",
    ".OSSSSOOOOSSSSO.",
    ".OSSSOCCCCOSSSO.",
    "..OSSOCCCCOSSO..",
    "..OSO.O..O.OSO..",
    "...OO.O..O.OO...",
    "......O..O......",
    "................",
)


def _bg_grid_color(x: int, y: int, t: float) -> tuple[int, int, int]:
    """Computes a dark synthwave retro background with rising plasma embers."""
    # Rising ember particles using deterministic hash math (no random allocations)
    ember_phase = (x * 37 + int(y + t * 12.0) * 17) % 97
    if ember_phase == 0 and ((x + int(t * 5)) % 3 == 0):
        # Bright golden/orange rising spark
        return (255, 180, 50)
    if ember_phase == 1:
        # Dimmer crimson spark
        return (190, 45, 90)

    # Synthwave horizon wave in the lower background
    wave = math.sin(x * 0.25 + t * 3.0) + math.cos(y * 0.35 - t * 2.0)
    base_r = int(14 + 8 * wave)
    base_g = int(8 + 4 * wave)
    base_b = int(28 + 14 * wave)
    return (max(6, base_r), max(4, base_g), max(14, base_b))


def _resolve_pixel(
    x: int, y: int, width: int, height: int, elapsed: float
) -> tuple[int, int, int]:
    """Returns the 24-bit (R, G, B) color of pixel (x, y) at time `elapsed`."""
    # Sprite dimensions (scaled 2x horizontally for nice proportions, or 1x1)
    sprite_h = 16
    sprite_w = 16

    # Bobbing motion (hovering up and down + slight horizontal sway)
    bob_y = int(round(math.sin(elapsed * 4.2) * 1.5))
    bob_x = int(round(math.cos(elapsed * 2.1) * 2.0))

    sx = x - ((width - sprite_w) // 2 + bob_x)
    sy = y - ((height - sprite_h) // 2 + bob_y)

    if 0 <= sx < sprite_w and 0 <= sy < sprite_h:
        px = _SPRITE_16X16[sy][sx]
        if px != ".":
            # Shimmer wave across the sprite armor
            shimmer = 0.5 + 0.5 * math.sin((sx + sy) * 0.45 - elapsed * 6.0)
            if px == "O":
                return (25, 15, 40)
            if px == "S":
                r = int(110 + 45 * shimmer)
                g = int(120 + 50 * shimmer)
                b = int(160 + 55 * shimmer)
                return (r, g, b)
            if px == "H" or px == "I":
                r = int(200 + 55 * shimmer)
                g = int(215 + 40 * shimmer)
                b = (255)
                return (r, g, b)
            if px == "E":
                # Blinking / scanning cyber-visor (Gold <-> Hot Magenta <-> Laser Cyan)
                scan_x = int((elapsed * 18.0) % sprite_w)
                if abs(sx - scan_x) <= 1:
                    return (255, 255, 220)  # White-hot scanner beam
                pulse = 0.5 + 0.5 * math.sin(elapsed * 8.0)
                return (255, int(40 + 160 * pulse), int(120 - 80 * pulse))
            if px == "C":
                # Breathing reactor vents in toxic cyan/gold
                vent = 0.5 + 0.5 * math.sin(elapsed * 14.0 + sy)
                return (int(40 + 215 * vent), int(220 + 35 * vent), 255)

    # Energy aura ring around the pixel-art sprite
    cx = width * 0.5 + bob_x
    cy = height * 0.5 + bob_y
    dist = math.hypot(x - cx, y - cy)
    ring = math.sin(dist * 0.85 - elapsed * 7.5)
    if 7.5 < dist < 11.5 and ring > 0.72:
        intensity = (ring - 0.72) / 0.28
        return (
            int(255 * intensity),
            int(70 * intensity),
            int(160 * intensity),
        )

    return _bg_grid_color(x, y, elapsed)


def _render_pixel_canvas(width: int, height: int, elapsed: float) -> list[str]:
    """
    Packs a `width x height` pixel buffer into `height // 2` terminal rows
    using the upper-half block character `▀` (FG = top pixel, BG = bottom pixel).
    """
    rows_out = []
    border_fg = "\033[38;2;120;60;170m"
    for y in range(0, height, 2):
        line_parts = [f"  {border_fg}▐{_RESET}"]
        for x in range(width):
            r1, g1, b1 = _resolve_pixel(x, y, width, height, elapsed)
            r2, g2, b2 = _resolve_pixel(x, y + 1, width, height, elapsed)
            line_parts.append(
                f"\033[38;2;{r1};{g1};{b1}m\033[48;2;{r2};{g2};{b2}m▀"
            )
        line_parts.append(f"{_RESET}{border_fg}▌{_RESET}")
        rows_out.append("".join(line_parts))
    return rows_out


def run_pixel_art_screen(duration: float = 11.0) -> None:
    """
    Runs the animated Pixel-Art terminal screen for at least `duration` seconds.
    """
    duration = max(10.0, float(duration))
    fps = 30.0
    frame_delay = 1.0 / fps
    start_time = time.monotonic()
    frame = 0

    px_width = 36
    px_height = 20  # 20 vertical pixels = 10 terminal rows
    term_rows = (px_height // 2) + 3

    sys.stdout.write(_HIDE_CURSOR + "\n" * term_rows)
    sys.stdout.flush()

    border_col = "\033[38;2;120;60;170m"
    gold_col   = "\033[38;2;255;200;70m"
    pink_col   = "\033[38;2;255;75;165m"
    dim_col    = "\033[38;2;130;115;160m"

    top_bar = f"  {border_col}▛{'▀' * px_width}▜{_RESET}"
    bot_bar = f"  {border_col}▙{'▄' * px_width}▟{_RESET}"

    try:
        while True:
            elapsed = time.monotonic() - start_time
            if elapsed >= duration:
                break

            canvas_rows = _render_pixel_canvas(px_width, px_height, elapsed)

            # Retro arcade ticker below the pixel canvas
            dots = "▪" * ((frame // 5) % 4) + "▫" * (3 - ((frame // 5) % 4))
            status_line = (
                f"  {pink_col}★ ARCADE//CORE{_RESET} {dots} "
                f"{dim_col}FRAME:{_RESET} {gold_col}{frame:04d}{_RESET}  "
                f"{dim_col}TIME:{_RESET} {gold_col}{elapsed:05.2f}s{_RESET}"
            )

            full_output = "\n".join([top_bar, *canvas_rows, bot_bar, status_line])
            sys.stdout.write(f"\033[{term_rows}A\r{full_output}")
            sys.stdout.flush()

            frame += 1
            sleep_for = (start_time + frame * frame_delay) - time.monotonic()
            if sleep_for > 0:
                time.sleep(sleep_for)

    except KeyboardInterrupt:
        sys.stdout.write(f"\n  {pink_col}[!] Pixel engine stopped.{_RESET}\n")
    finally:
        sys.stdout.write(_SHOW_CURSOR + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    run_pixel_art_screen(duration=11.0)
