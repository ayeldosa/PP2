"""
ui.py – Screen renderers and UI widget helpers  (TSIS-3)
"""

import pygame
from persistence import load_leaderboard, save_settings

# ─────────────────────────────────────────────────────────────
# Colours & fonts helpers
# ─────────────────────────────────────────────────────────────

C_BG        = (15,  15,  25)
C_ROAD      = (40,  44,  52)
C_WHITE     = (240, 240, 255)
C_GREY      = (130, 130, 150)
C_ACCENT    = (255, 200,  50)
C_RED       = (220,  60,  60)
C_GREEN     = ( 60, 200,  80)
C_BLUE      = ( 60, 130, 255)
C_DARK      = ( 30,  30,  45)
C_PANEL     = ( 22,  22,  38)

CAR_COLORS = {
    "red":    (220,  60,  60),
    "blue":   ( 60, 130, 255),
    "green":  ( 60, 200,  80),
    "yellow": (255, 210,  50),
}


def _font(size, bold=False):
    return pygame.font.SysFont("segoeui", size, bold=bold)


def text(surface, msg, x, y, size=20, color=C_WHITE, bold=False, center=False):
    f   = _font(size, bold)
    sur = f.render(str(msg), True, color)
    rect = sur.get_rect()
    if center:
        rect.centerx = x
        rect.y = y
    else:
        rect.x, rect.y = x, y
    surface.blit(sur, rect)
    return rect


def button(surface, label, rect, hover=False, accent=False):
    base = C_ACCENT if accent else (55, 58, 80)
    if hover:
        base = tuple(min(255, c + 30) for c in base)
    pygame.draw.rect(surface, base,    rect, border_radius=8)
    pygame.draw.rect(surface, C_GREY,  rect, 1, border_radius=8)
    f   = _font(18, bold=True)
    sur = f.render(label, True, C_DARK if accent else C_WHITE)
    surface.blit(sur, sur.get_rect(center=rect.center))
    return rect


# ─────────────────────────────────────────────────────────────
# Main Menu
# ─────────────────────────────────────────────────────────────

def main_menu(screen, settings: dict) -> str:
    """
    Returns: 'play' | 'leaderboard' | 'settings' | 'quit'
    """
    W, H = screen.get_size()
    clock = pygame.time.Clock()

    btn_w, btn_h = 240, 48
    btns = {
        "play":        pygame.Rect(W//2 - btn_w//2, 260, btn_w, btn_h),
        "leaderboard": pygame.Rect(W//2 - btn_w//2, 320, btn_w, btn_h),
        "settings":    pygame.Rect(W//2 - btn_w//2, 380, btn_w, btn_h),
        "quit":        pygame.Rect(W//2 - btn_w//2, 440, btn_w, btn_h),
    }
    labels = {"play": "▶  Play", "leaderboard": "🏆  Leaderboard",
              "settings": "⚙  Settings", "quit": "✕  Quit"}

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                for key, rect in btns.items():
                    if rect.collidepoint(mx, my):
                        return key

        # draw
        screen.fill(C_BG)
        # road stripes background
        for i in range(0, H, 60):
            pygame.draw.rect(screen, (22, 22, 35), (W//2 - 180, i, 360, 30))

        text(screen, "RACER", W//2, 120, size=72, color=C_ACCENT, bold=True, center=True)
        text(screen, "TSIS-3", W//2, 200, size=22, color=C_GREY, center=True)
        text(screen, f"Player: {settings['username']}", W//2, 230, size=14, color=C_GREY, center=True)

        for key, rect in btns.items():
            button(screen, labels[key], rect,
                   hover=rect.collidepoint(mx, my),
                   accent=(key == "play"))

        pygame.display.flip()
        clock.tick(60)


# ─────────────────────────────────────────────────────────────
# Name Entry
# ─────────────────────────────────────────────────────────────

def name_entry(screen, settings: dict) -> str:
    """Returns entered username (or existing one)."""
    W, H = screen.get_size()
    clock = pygame.time.Clock()
    name  = settings.get("username", "")
    font  = _font(28)
    ok_btn = pygame.Rect(W//2 - 100, 380, 200, 48)

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return name
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return name or "Player"
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isprintable() and len(name) < 16:
                    name += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ok_btn.collidepoint(mx, my):
                    return name or "Player"

        screen.fill(C_BG)
        text(screen, "Enter your name", W//2, 180, size=32, bold=True, center=True)

        # Input box
        box = pygame.Rect(W//2 - 160, 280, 320, 52)
        pygame.draw.rect(screen, C_PANEL, box, border_radius=8)
        pygame.draw.rect(screen, C_ACCENT, box, 2, border_radius=8)
        sur = font.render(name + "|", True, C_WHITE)
        screen.blit(sur, sur.get_rect(center=box.center))

        button(screen, "OK  →", ok_btn, hover=ok_btn.collidepoint(mx, my), accent=True)
        pygame.display.flip()
        clock.tick(60)


# ─────────────────────────────────────────────────────────────
# Settings Screen
# ─────────────────────────────────────────────────────────────

def settings_screen(screen, settings: dict) -> dict:
    """Mutates and returns settings dict."""
    W, H   = screen.get_size()
    clock  = pygame.time.Clock()
    back   = pygame.Rect(W//2 - 100, H - 90, 200, 44)

    car_colors  = ["red", "blue", "green", "yellow"]
    difficulties = ["easy", "normal", "hard"]

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_settings(settings); return settings
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back.collidepoint(mx, my):
                    save_settings(settings); return settings
                # Sound toggle
                snd_btn = pygame.Rect(W//2 + 60, 210, 110, 36)
                if snd_btn.collidepoint(mx, my):
                    settings["sound"] = not settings["sound"]
                # Car colour cycle
                cc_btn = pygame.Rect(W//2 + 60, 270, 110, 36)
                if cc_btn.collidepoint(mx, my):
                    idx = car_colors.index(settings["car_color"])
                    settings["car_color"] = car_colors[(idx + 1) % len(car_colors)]
                # Difficulty cycle
                df_btn = pygame.Rect(W//2 + 60, 330, 110, 36)
                if df_btn.collidepoint(mx, my):
                    idx = difficulties.index(settings["difficulty"])
                    settings["difficulty"] = difficulties[(idx + 1) % len(difficulties)]

        screen.fill(C_BG)
        text(screen, "Settings", W//2, 120, size=40, bold=True, center=True)

        rows = [
            (210, "Sound",      "ON" if settings["sound"] else "OFF"),
            (270, "Car Color",  settings["car_color"].capitalize()),
            (330, "Difficulty", settings["difficulty"].capitalize()),
        ]
        for y, label, value in rows:
            text(screen, label, W//2 - 180, y + 8, size=20)
            btn_r = pygame.Rect(W//2 + 60, y, 110, 36)
            clr = CAR_COLORS.get(value.lower(), C_ACCENT) if label == "Car Color" else C_ACCENT
            button(screen, value, btn_r, hover=btn_r.collidepoint(mx, my))

        # Car preview swatch
        swatch_x = W//2 + 185
        pygame.draw.rect(screen, CAR_COLORS[settings["car_color"]],
                         (swatch_x, 268, 28, 40), border_radius=4)

        button(screen, "← Back", back, hover=back.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(60)


# ─────────────────────────────────────────────────────────────
# Leaderboard Screen
# ─────────────────────────────────────────────────────────────

def leaderboard_screen(screen) -> None:
    W, H   = screen.get_size()
    clock  = pygame.time.Clock()
    back   = pygame.Rect(W//2 - 100, H - 80, 200, 44)
    board  = load_leaderboard()

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back.collidepoint(mx, my):
                    return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    return

        screen.fill(C_BG)
        text(screen, "🏆  Top 10", W//2, 60, size=36, bold=True, color=C_ACCENT, center=True)

        headers = ["#", "Name", "Score", "Dist", "Coins", "Date"]
        cols    = [80, 170, 320, 440, 540, 640]
        for i, h in enumerate(headers):
            text(screen, h, cols[i], 120, size=14, color=C_GREY, bold=True)

        pygame.draw.line(screen, C_GREY, (60, 142), (W - 60, 142))

        for rank, entry in enumerate(board[:10], 1):
            y   = 150 + rank * 36
            clr = C_ACCENT if rank == 1 else C_WHITE
            row = [
                str(rank),
                entry.get("username", "?")[:12],
                str(entry.get("score", 0)),
                f'{entry.get("distance", 0)} m',
                str(entry.get("coins", 0)),
                entry.get("date", ""),
            ]
            for i, val in enumerate(row):
                text(screen, val, cols[i], y, size=16, color=clr)

        if not board:
            text(screen, "No scores yet. Play a game!", W//2, 300,
                 size=20, color=C_GREY, center=True)

        button(screen, "← Back", back, hover=back.collidepoint(mx, my))
        pygame.display.flip()
        clock.tick(60)


# ─────────────────────────────────────────────────────────────
# Game Over Screen
# ─────────────────────────────────────────────────────────────

def game_over_screen(screen, score, distance, coins) -> str:
    """Returns 'retry' | 'menu'"""
    W, H   = screen.get_size()
    clock  = pygame.time.Clock()
    retry  = pygame.Rect(W//2 - 220, 440, 200, 48)
    menu   = pygame.Rect(W//2 + 20,  440, 200, 48)

    while True:
        mx, my = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry.collidepoint(mx, my): return "retry"
                if menu.collidepoint(mx, my):  return "menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: return "retry"
                if event.key == pygame.K_ESCAPE: return "menu"

        screen.fill(C_BG)
        # Red flash overlay
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((180, 30, 30, 60))
        screen.blit(overlay, (0, 0))

        text(screen, "GAME OVER", W//2, 130, size=64, bold=True, color=C_RED, center=True)

        stats = [
            ("Score",    str(score)),
            ("Distance", f"{distance} m"),
            ("Coins",    str(coins)),
        ]
        for i, (label, value) in enumerate(stats):
            y = 260 + i * 50
            text(screen, label, W//2 - 160, y, size=22, color=C_GREY)
            text(screen, value, W//2 + 40,  y, size=22, color=C_WHITE, bold=True)

        button(screen, "↺  Retry",    retry, hover=retry.collidepoint(mx, my), accent=True)
        button(screen, "⌂  Main Menu", menu,  hover=menu.collidepoint(mx, my))

        text(screen, "R = retry   ESC = menu", W//2, H - 30,
             size=12, color=C_GREY, center=True)
        pygame.display.flip()
        clock.tick(60)
