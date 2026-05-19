"""User avatar options. Images: assets/avatar_1.png … avatar_6.png (or assets/avatars/)."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "assets"
AVATARS_DIR = ASSETS_DIR / "avatars"

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp", ".svg")

AVATAR_OPTIONS: list[dict[str, str]] = [
    {"id": "avatar_1", "label": "Abigail"},
    {"id": "avatar_2", "label": "Elliot"},
    {"id": "avatar_3", "label": "Haley"},
    {"id": "avatar_4", "label": "Sebastian"},
    {"id": "avatar_5", "label": "Emily"},
    {"id": "avatar_6", "label": "Alex"},
]

DEFAULT_AVATAR_ID = "avatar_1"


def resolve_avatar_path(avatar_id: str | None) -> str:
    """Return path to the avatar image file."""
    aid = (avatar_id or DEFAULT_AVATAR_ID).strip() or DEFAULT_AVATAR_ID
    for folder in (ASSETS_DIR, AVATARS_DIR):
        for ext in IMAGE_EXTENSIONS:
            path = folder / f"{aid}{ext}"
            if path.is_file():
                return str(path)
    return str(AVATARS_DIR / f"{aid}.svg")
