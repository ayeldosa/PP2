#!/usr/bin/env python3
"""
paint.py – Extended Paint Application  (TSIS-2)
Requires: pygame  (pip install pygame)

Controls:
  Mouse        – draw with active tool
  1 / 2 / 3   – brush size: small / medium / large
  Ctrl+S       – save canvas as timestamped PNG
  Escape       – cancel text input
  Enter        – confirm text input
"""

import sys
import pygame
from datetime import datetime

from tools import (
    PencilTool, LineTool, RectTool, CircleTool,
    SquareTool, RightTriangleTool, EqTriangleTool,
    RhombusTool, EraserTool, FillTool, TextTool,
)

# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────

WIN_W, WIN_H  = 1100, 720
TOOLBAR_W     = 160
CANVAS_X      = TOOLBAR_W
CANVAS_W      = WIN_W - TOOLBAR_W
CANVAS_H      = WIN_H

BRUSH_SIZES   = [2, 5, 10]

# Palette – 20 colours
PALETTE = [
    (0,   0,   0),    (255, 255, 255), (128, 128, 128), (192, 192, 192),
    (255, 0,   0),    (128, 0,   0),   (255, 128,   0), (128, 64,  0),
    (255, 255,   0),  (128, 128,  0),  (0,   255,   0), (0,   128,  0),
    (0,   255, 255),  (0,   128, 128), (0,   0,   255), (0,   0,   128),
    (255, 0,   255),  (128, 0,   128), (255, 192, 203), (165, 42,  42),
]

# Tool entries: (label, class)
TOOL_DEFS = [
    ("Pencil",    PencilTool),
    ("Line",      LineTool),
    ("Rectangle", RectTool),
    ("Circle",    CircleTool),
    ("Square",    SquareTool),
    ("R.Triangle",RightTriangleTool),
    ("Eq.Triangle",EqTriangleTool),
    ("Rhombus",   RhombusTool),
    ("Eraser",    EraserTool),
    ("Fill",      FillTool),
    ("Text",      TextTool),
]

# Colours
BG_TOOLBAR  = (30,  30,  40)
BG_CANVAS   = (255, 255, 255)
CLR_ACCENT  = (90,  140, 255)
CLR_TEXT    = (220, 220, 230)
CLR_BORDER  = (55,  55,  70)


# ─────────────────────────────────────────────────────────────
# Toolbar button layout helpers
# ─────────────────────────────────────────────────────────────

def _btn_rect(index, x=8, y_start=10, w=144, h=30, gap=4):
    return pygame.Rect(x, y_start + index * (h + gap), w, h)


def _palette_rect(i, x_off=8, y_off=420):
    col = i % 4
    row = i // 4
    return pygame.Rect(x_off + col * 36, y_off + row * 36, 32, 32)


def _size_btn_rect(i):
    """Three brush-size buttons."""
    return pygame.Rect(8 + i * 50, 360, 44, 30)


# ─────────────────────────────────────────────────────────────
# Drawing helpers
# ─────────────────────────────────────────────────────────────

def draw_toolbar(surface, tools, active_idx, active_color, brush_idx, font_sm, font_xs):
    surface.fill(BG_TOOLBAR, (0, 0, TOOLBAR_W, WIN_H))

    # ── Tool buttons ──
    for i, (label, _) in enumerate(tools):
        rect = _btn_rect(i)
        active = (i == active_idx)
        color  = CLR_ACCENT if active else (50, 52, 65)
        pygame.draw.rect(surface, color,       rect, border_radius=5)
        pygame.draw.rect(surface, CLR_BORDER,  rect, 1, border_radius=5)
        txt = font_sm.render(label, True, CLR_TEXT)
        surface.blit(txt, txt.get_rect(center=rect.center))

    # ── Brush sizes ──
    size_labels = ["S", "M", "L"]
    for i, lbl in enumerate(size_labels):
        rect   = _size_btn_rect(i)
        active = (i == brush_idx)
        color  = CLR_ACCENT if active else (50, 52, 65)
        pygame.draw.rect(surface, color,      rect, border_radius=5)
        pygame.draw.rect(surface, CLR_BORDER, rect, 1, border_radius=5)
        txt = font_sm.render(lbl, True, CLR_TEXT)
        surface.blit(txt, txt.get_rect(center=rect.center))

    # ── Colour palette ──
    for i, clr in enumerate(PALETTE):
        rect = _palette_rect(i)
        pygame.draw.rect(surface, clr, rect, border_radius=3)
        if clr == active_color:
            pygame.draw.rect(surface, (255, 255, 255), rect, 2, border_radius=3)
        else:
            pygame.draw.rect(surface, CLR_BORDER, rect, 1, border_radius=3)

    # ── Active colour swatch ──
    swatch = pygame.Rect(8, 588, 144, 36)
    pygame.draw.rect(surface, active_color, swatch, border_radius=6)
    pygame.draw.rect(surface, CLR_BORDER,   swatch, 1, border_radius=6)
    lbl = font_xs.render("Active colour", True, CLR_TEXT)
    surface.blit(lbl, (8, 630))

    # ── Ctrl+S hint ──
    hint = font_xs.render("Ctrl+S  Save", True, (120, 120, 140))
    surface.blit(hint, (8, 660))

    # ── Section labels ──
    for y, text in ((352, "Brush size"), (412, "Palette")):
        lbl = font_xs.render(text, True, (140, 140, 160))
        surface.blit(lbl, (8, y))


# ─────────────────────────────────────────────────────────────
# Save canvas
# ─────────────────────────────────────────────────────────────

def save_canvas(canvas):
    ts       = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"canvas_{ts}.png"
    pygame.image.save(canvas, filename)
    print(f"[Paint] Saved → {filename}")
    return filename


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Paint  –  TSIS 2")

    font_sm = pygame.font.SysFont("segoeui",    13, bold=True)
    font_xs = pygame.font.SysFont("segoeui",    11)
    font_hud = pygame.font.SysFont("monospace", 11)

    # Separate canvas surface (only the drawing area)
    canvas = pygame.Surface((CANVAS_W, CANVAS_H))
    canvas.fill(BG_CANVAS)

    # Instantiate all tools
    tool_instances = [cls() for _, cls in TOOL_DEFS]
    active_idx  = 0
    brush_idx   = 0
    active_color = PALETTE[0]

    def _sync_tool():
        t = tool_instances[active_idx]
        t.color      = active_color
        t.brush_size = BRUSH_SIZES[brush_idx]

    _sync_tool()

    clock    = pygame.time.Clock()
    save_msg = ""     # feedback message
    save_timer = 0

    running = True
    while running:
        dt = clock.tick(60)

        # ── Events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # ── Keyboard ──
            elif event.type == pygame.KEYDOWN:
                tool = tool_instances[active_idx]

                # Text tool intercepts keys when active
                if isinstance(tool, TextTool) and tool.is_active:
                    tool.on_key_down(canvas, event)
                else:
                    if event.key == pygame.K_1:
                        brush_idx = 0; _sync_tool()
                    elif event.key == pygame.K_2:
                        brush_idx = 1; _sync_tool()
                    elif event.key == pygame.K_3:
                        brush_idx = 2; _sync_tool()
                    elif event.key == pygame.K_s and (event.mod & pygame.KMOD_CTRL):
                        name = save_canvas(canvas)
                        save_msg   = f"Saved: {name}"
                        save_timer = 3000

            # ── Mouse ──
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                tool = tool_instances[active_idx]

                # Toolbar clicks
                if mx < TOOLBAR_W:
                    # Tool buttons
                    for i in range(len(TOOL_DEFS)):
                        if _btn_rect(i).collidepoint(mx, my):
                            active_idx = i
                            _sync_tool()
                            break
                    # Brush size buttons
                    for i in range(3):
                        if _size_btn_rect(i).collidepoint(mx, my):
                            brush_idx = i
                            _sync_tool()
                            break
                    # Palette
                    for i, clr in enumerate(PALETTE):
                        if _palette_rect(i).collidepoint(mx, my):
                            active_color = clr
                            _sync_tool()
                            break
                else:
                    # Canvas click – translate to canvas coordinates
                    cpos = (mx - CANVAS_X, my)
                    tool.color      = active_color
                    tool.brush_size = BRUSH_SIZES[brush_idx]
                    tool.on_mouse_down(canvas, cpos)

            elif event.type == pygame.MOUSEBUTTONUP:
                mx, my = event.pos
                if mx >= TOOLBAR_W:
                    cpos = (mx - CANVAS_X, my)
                    tool_instances[active_idx].on_mouse_up(canvas, cpos)

            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                if mx >= TOOLBAR_W:
                    cpos    = (mx - CANVAS_X, my)
                    buttons = pygame.mouse.get_pressed()
                    tool_instances[active_idx].on_mouse_move(canvas, cpos, buttons)

        # ── Render ──
        screen.fill(BG_TOOLBAR)

        # Draw canvas onto screen
        screen.blit(canvas, (CANVAS_X, 0))

        # Draw preview overlay (live preview layer – doesn't modify canvas)
        preview = canvas.copy()
        tool_instances[active_idx].draw_preview(preview)
        screen.blit(preview, (CANVAS_X, 0))

        # Draw toolbar
        draw_toolbar(screen, TOOL_DEFS, active_idx, active_color,
                     brush_idx, font_sm, font_xs)

        # Canvas border
        pygame.draw.rect(screen, CLR_BORDER, (CANVAS_X-1, 0, CANVAS_W+1, WIN_H), 1)

        # HUD: save message
        if save_timer > 0:
            save_timer -= dt
            surf = font_hud.render(save_msg, True, (30, 200, 100))
            screen.blit(surf, (CANVAS_X + 10, 10))

        # HUD: coords
        mx, my = pygame.mouse.get_pos()
        if mx >= CANVAS_X:
            coords = font_hud.render(f"({mx - CANVAS_X}, {my})", True, (150, 150, 170))
            screen.blit(coords, (WIN_W - 110, WIN_H - 18))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
