"""Stardew-style pixel SVG icons for lifeVoice UI."""

from urllib.parse import quote

# Palette
EARTH = "#8B5E3C"
WHEAT = "#F4D06F"
LEAF = "#6A994E"
SKY = "#A7C7E7"
PEACH = "#F9A875"
CREAM = "#FDF8E8"
INK = "#5C3D28"

# Char → color key for grid templates
_PALETTE = {
    "E": EARTH,
    "W": WHEAT,
    "L": LEAF,
    "S": SKY,
    "P": PEACH,
    "C": CREAM,
    "K": INK,
    ".": None,
}

# 16×16 grids (. = transparent)
_ICONS: dict[str, list[str]] = {
    "professional": [
        "................",
        "....EEEEEE....",
        "...EEEEEEEE...",
        "...EE....EE...",
        "...EEEEEEEE...",
        "...EEEEEEEE...",
        "...EE....EE...",
        "...EEEEEEEE...",
        "....EEEEEE....",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    "family": [
        "................",
        "......LL........",
        ".....LLLL.......",
        "....LLLLLL......",
        "...LLLLLLLL.....",
        "...LL....LL.....",
        "...LL....LL.....",
        "...LLLLLLLL.....",
        "...LLLLLLLL.....",
        "....LL..LL......",
        "....LL..LL......",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    "friend": [
        "................",
        ".....PPPP.......",
        ".PP..PPPP..PP...",
        "PPPPPPPPPPPPPP..",
        "PPPPPPPPPPPPPP..",
        ".PPPPPPPPPPPP...",
        "..PPPPPPPPPP....",
        "...PPPPPPPP.....",
        "....PPPPPP......",
        ".....PPPP.......",
        "......PP........",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    "you": [
        "................",
        "....SSSSSS......",
        ".SSSSSSSSSSSS...",
        ".SSSSSSSSSSSS...",
        ".SSSSSSSSSSSS...",
        ".SS........SS...",
        ".SS........SS...",
        ".SSSSSSSSSSSS...",
        ".SSSSSSSSSSSS...",
        "..SSSSSSSSSS....",
        "...SSSSSSSS.....",
        "....SSSSSS......",
        "................",
        "................",
        "................",
        "................",
    ],
    "random": [
        "................",
        ".....WWWW.......",
        "....WWWWWW......",
        "...WWWWWWWW.....",
        "...WW....WW.....",
        "...WW....WW.....",
        "...WWWWWWWW.....",
        "...WWWWWWWW.....",
        "...WW....WW.....",
        "...WW....WW.....",
        "...WWWWWWWW.....",
        "....WWWWWW......",
        ".....WWWW.......",
        "................",
        "................",
        "................",
    ],
    "friend_optimist": [
        "................",
        "......WW........",
        ".....WWWW.......",
        "....WWWWWW......",
        "....WWWWWW......",
        "...WWWWWWWW.....",
        "...WWWWWWWW.....",
        "....WWWWWW......",
        ".....WWWW.......",
        "......WW........",
        "................",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    "friend_pessimist": [
        "................",
        "....SSSSSS......",
        ".SSSSSSSSSS.....",
        "SSSSSSSSSSSS....",
        "SSSSSSSSSSSS....",
        "SSSSSSSSSSSS....",
        "..SSSSSSSS......",
        "...SSSSSS.......",
        "....SSSS........",
        ".....SS.........",
        "......S.........",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
    "friend_brainrot": [
        "................",
        "......PP........",
        ".....PPPP.......",
        "....PP..PP......",
        "...PP....PP.....",
        "...PP....PP.....",
        "....PP..PP......",
        ".....PPPP.......",
        "......PP........",
        ".....PPPP.......",
        "....PP..PP......",
        "...PP....PP.....",
        "................",
        "................",
        "................",
        "................",
    ],
    "friend_jejemon": [
        "................",
        "......WW........",
        ".....W..W.......",
        "....W....W......",
        "....WWWWWW......",
        ".....W..W.......",
        "......WW........",
        ".....W..W.......",
        "....W....W......",
        "....WWWWWW......",
        ".....W..W.......",
        "......WW........",
        "................",
        "................",
        "................",
        "................",
    ],
    "friend_youngstunna": [
        "................",
        "......PP........",
        ".....PPPP.......",
        "....PPPPPP......",
        "...PPPPPPPP.....",
        "....PPPPPP......",
        ".....PPPP.......",
        "......PP........",
        ".....PPPP.......",
        "....PPPPPP......",
        "...PPPPPPPP.....",
        "................",
        "................",
        "................",
        "................",
        "................",
    ],
}

_PERSONA_KEYS = {
    "Professional": "professional",
    "Family": "family",
    "Friend": "friend",
    "You": "you",
    "Random": "random",
}

_FRIEND_KEYS = {
    "Optimist": "friend_optimist",
    "Pessimist": "friend_pessimist",
    "Brainrot": "friend_brainrot",
    "Jejemon": "friend_jejemon",
    "Youngstunna": "friend_youngstunna",
}


def _grid_to_svg(grid: list[str], pixel: int = 4) -> str:
    w, h = len(grid[0]), len(grid)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w * pixel} {h * pixel}" '
        f'shape-rendering="crispEdges">'
    ]
    for y, row in enumerate(grid):
        for x, ch in enumerate(row):
            fill = _PALETTE.get(ch)
            if fill:
                parts.append(
                    f'<rect x="{x * pixel}" y="{y * pixel}" width="{pixel}" height="{pixel}" fill="{fill}"/>'
                )
    parts.append("</svg>")
    return "".join(parts)


def pixel_icon_data_uri(icon_key: str) -> str:
    grid = _ICONS.get(icon_key)
    if not grid:
        grid = _ICONS["friend"]
    svg = _grid_to_svg(grid)
    return "data:image/svg+xml," + quote(svg)


def pixel_icon_html(icon_key: str, size: int = 72, alt: str = "") -> str:
    src = pixel_icon_data_uri(icon_key)
    label = alt or icon_key.replace("_", " ").title()
    return (
        f'<img class="lv-pixel-icon" src="{src}" width="{size}" height="{size}" '
        f'alt="{label}" title="{label}" />'
    )


def persona_icon_key(persona_label: str) -> str:
    return _PERSONA_KEYS.get(persona_label, "friend")


def friend_icon_key(style: str) -> str:
    return _FRIEND_KEYS.get(style, "friend_optimist")
