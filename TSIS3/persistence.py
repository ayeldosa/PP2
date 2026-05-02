"""
persistence.py – Save/load leaderboard and settings (TSIS-3)
"""

import json
import os
from datetime import datetime

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE    = "settings.json"

DEFAULT_SETTINGS = {
    "sound":       True,
    "car_color":   "red",       # red | blue | green | yellow
    "difficulty":  "normal",    # easy | normal | hard
    "username":    "Player",
}

# ─────────────────────────────────────────────────────────────
# Settings
# ─────────────────────────────────────────────────────────────

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
            # fill in any missing keys from defaults
            for k, v in DEFAULT_SETTINGS.items():
                data.setdefault(k, v)
            return data
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


# ─────────────────────────────────────────────────────────────
# Leaderboard
# ─────────────────────────────────────────────────────────────

def load_leaderboard() -> list:
    """Return list of entry dicts sorted by score desc."""
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                data = json.load(f)
            return sorted(data, key=lambda e: e["score"], reverse=True)
        except Exception:
            pass
    return []


def save_score(username: str, score: int, distance: int, coins: int):
    board = load_leaderboard()
    board.append({
        "username": username,
        "score":    score,
        "distance": distance,
        "coins":    coins,
        "date":     datetime.now().strftime("%Y-%m-%d"),
    })
    board = sorted(board, key=lambda e: e["score"], reverse=True)[:10]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(board, f, indent=2)
