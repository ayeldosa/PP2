"""
tools.py – Drawing tool implementations for Paint TSIS-2
"""

import pygame
from collections import deque


# ─────────────────────────────────────────────────────────────
# Base Tool
# ─────────────────────────────────────────────────────────────

class Tool:
    """Abstract base class for all drawing tools."""

    def __init__(self):
        self.color      = (0, 0, 0)
        self.brush_size = 2

    def on_mouse_down(self, canvas, pos): pass
    def on_mouse_move(self, canvas, pos, buttons): pass
    def on_mouse_up(self,   canvas, pos): pass
    def on_key_down(self,   canvas, event): pass
    def draw_preview(self,  surface): pass   # called every frame for live preview


# ─────────────────────────────────────────────────────────────
# Pencil (freehand)
# ─────────────────────────────────────────────────────────────

class PencilTool(Tool):
    def __init__(self):
        super().__init__()
        self._last_pos = None

    def on_mouse_down(self, canvas, pos):
        self._last_pos = pos
        pygame.draw.circle(canvas, self.color, pos, max(1, self.brush_size // 2))

    def on_mouse_move(self, canvas, pos, buttons):
        if buttons[0] and self._last_pos:
            pygame.draw.line(canvas, self.color, self._last_pos, pos, self.brush_size)
            self._last_pos = pos

    def on_mouse_up(self, canvas, pos):
        self._last_pos = None


# ─────────────────────────────────────────────────────────────
# Straight Line (with live preview)
# ─────────────────────────────────────────────────────────────

class LineTool(Tool):
    def __init__(self):
        super().__init__()
        self._start    = None
        self._cur_pos  = None
        self._snapshot = None   # canvas state before drag

    def on_mouse_down(self, canvas, pos):
        self._start    = pos
        self._cur_pos  = pos
        self._snapshot = canvas.copy()

    def on_mouse_move(self, canvas, pos, buttons):
        if buttons[0] and self._start:
            self._cur_pos = pos

    def draw_preview(self, surface):
        if self._start and self._cur_pos:
            pygame.draw.line(surface, self.color, self._start, self._cur_pos, self.brush_size)

    def on_mouse_up(self, canvas, pos):
        if self._start:
            canvas.blit(self._snapshot, (0, 0))
            pygame.draw.line(canvas, self.color, self._start, pos, self.brush_size)
        self._start = self._cur_pos = self._snapshot = None


# ─────────────────────────────────────────────────────────────
# Rectangle
# ─────────────────────────────────────────────────────────────

class RectTool(Tool):
    def __init__(self):
        super().__init__()
        self._start    = None
        self._cur_pos  = None
        self._snapshot = None

    def on_mouse_down(self, canvas, pos):
        self._start    = pos
        self._cur_pos  = pos
        self._snapshot = canvas.copy()

    def on_mouse_move(self, canvas, pos, buttons):
        if buttons[0] and self._start:
            self._cur_pos = pos

    def draw_preview(self, surface):
        if self._start and self._cur_pos:
            rect = _make_rect(self._start, self._cur_pos)
            pygame.draw.rect(surface, self.color, rect, self.brush_size)

    def on_mouse_up(self, canvas, pos):
        if self._start:
            canvas.blit(self._snapshot, (0, 0))
            rect = _make_rect(self._start, pos)
            pygame.draw.rect(canvas, self.color, rect, self.brush_size)
        self._start = self._cur_pos = self._snapshot = None


# ─────────────────────────────────────────────────────────────
# Circle
# ─────────────────────────────────────────────────────────────

class CircleTool(Tool):
    def __init__(self):
        super().__init__()
        self._start    = None
        self._cur_pos  = None
        self._snapshot = None

    def on_mouse_down(self, canvas, pos):
        self._start    = pos
        self._cur_pos  = pos
        self._snapshot = canvas.copy()

    def on_mouse_move(self, canvas, pos, buttons):
        if buttons[0] and self._start:
            self._cur_pos = pos

    def draw_preview(self, surface):
        if self._start and self._cur_pos:
            cx, cy, r = _circle_params(self._start, self._cur_pos)
            if r > 0:
                pygame.draw.circle(surface, self.color, (cx, cy), r, self.brush_size)

    def on_mouse_up(self, canvas, pos):
        if self._start:
            canvas.blit(self._snapshot, (0, 0))
            cx, cy, r = _circle_params(self._start, pos)
            if r > 0:
                pygame.draw.circle(canvas, self.color, (cx, cy), r, self.brush_size)
        self._start = self._cur_pos = self._snapshot = None


# ─────────────────────────────────────────────────────────────
# Square (constrained rectangle)
# ─────────────────────────────────────────────────────────────

class SquareTool(Tool):
    def __init__(self):
        super().__init__()
        self._start    = None
        self._cur_pos  = None
        self._snapshot = None

    def on_mouse_down(self, canvas, pos):
        self._start    = pos
        self._cur_pos  = pos
        self._snapshot = canvas.copy()

    def on_mouse_move(self, canvas, pos, buttons):
        if buttons[0] and self._start:
            self._cur_pos = pos

    def draw_preview(self, surface):
        if self._start and self._cur_pos:
            rect = _square_rect(self._start, self._cur_pos)
            pygame.draw.rect(surface, self.color, rect, self.brush_size)

    def on_mouse_up(self, canvas, pos):
        if self._start:
            canvas.blit(self._snapshot, (0, 0))
            rect = _square_rect(self._start, pos)
            pygame.draw.rect(canvas, self.color, rect, self.brush_size)
        self._start = self._cur_pos = self._snapshot = None


# ─────────────────────────────────────────────────────────────
# Right Triangle
# ─────────────────────────────────────────────────────────────

class RightTriangleTool(Tool):
    def __init__(self):
        super().__init__()
        self._start    = None
        self._cur_pos  = None
        self._snapshot = None

    def on_mouse_down(self, canvas, pos):
        self._start    = pos
        self._cur_pos  = pos
        self._snapshot = canvas.copy()

    def on_mouse_move(self, canvas, pos, buttons):
        if buttons[0] and self._start:
            self._cur_pos = pos

    def draw_preview(self, surface):
        if self._start and self._cur_pos:
            pts = _right_triangle_pts(self._start, self._cur_pos)
            pygame.draw.polygon(surface, self.color, pts, self.brush_size)

    def on_mouse_up(self, canvas, pos):
        if self._start:
            canvas.blit(self._snapshot, (0, 0))
            pts = _right_triangle_pts(self._start, pos)
            pygame.draw.polygon(canvas, self.color, pts, self.brush_size)
        self._start = self._cur_pos = self._snapshot = None


# ─────────────────────────────────────────────────────────────
# Equilateral Triangle
# ─────────────────────────────────────────────────────────────

class EqTriangleTool(Tool):
    def __init__(self):
        super().__init__()
        self._start    = None
        self._cur_pos  = None
        self._snapshot = None

    def on_mouse_down(self, canvas, pos):
        self._start    = pos
        self._cur_pos  = pos
        self._snapshot = canvas.copy()

    def on_mouse_move(self, canvas, pos, buttons):
        if buttons[0] and self._start:
            self._cur_pos = pos

    def draw_preview(self, surface):
        if self._start and self._cur_pos:
            pts = _eq_triangle_pts(self._start, self._cur_pos)
            pygame.draw.polygon(surface, self.color, pts, self.brush_size)

    def on_mouse_up(self, canvas, pos):
        if self._start:
            canvas.blit(self._snapshot, (0, 0))
            pts = _eq_triangle_pts(self._start, pos)
            pygame.draw.polygon(canvas, self.color, pts, self.brush_size)
        self._start = self._cur_pos = self._snapshot = None


# ─────────────────────────────────────────────────────────────
# Rhombus
# ─────────────────────────────────────────────────────────────

class RhombusTool(Tool):
    def __init__(self):
        super().__init__()
        self._start    = None
        self._cur_pos  = None
        self._snapshot = None

    def on_mouse_down(self, canvas, pos):
        self._start    = pos
        self._cur_pos  = pos
        self._snapshot = canvas.copy()

    def on_mouse_move(self, canvas, pos, buttons):
        if buttons[0] and self._start:
            self._cur_pos = pos

    def draw_preview(self, surface):
        if self._start and self._cur_pos:
            pts = _rhombus_pts(self._start, self._cur_pos)
            pygame.draw.polygon(surface, self.color, pts, self.brush_size)

    def on_mouse_up(self, canvas, pos):
        if self._start:
            canvas.blit(self._snapshot, (0, 0))
            pts = _rhombus_pts(self._start, pos)
            pygame.draw.polygon(canvas, self.color, pts, self.brush_size)
        self._start = self._cur_pos = self._snapshot = None


# ─────────────────────────────────────────────────────────────
# Eraser
# ─────────────────────────────────────────────────────────────

class EraserTool(Tool):
    BG_COLOR = (255, 255, 255)

    def __init__(self):
        super().__init__()
        self._last_pos = None

    def on_mouse_down(self, canvas, pos):
        self._last_pos = pos
        r = self.brush_size * 3
        pygame.draw.circle(canvas, self.BG_COLOR, pos, r)

    def on_mouse_move(self, canvas, pos, buttons):
        if buttons[0] and self._last_pos:
            r = self.brush_size * 3
            pygame.draw.line(canvas, self.BG_COLOR, self._last_pos, pos, r * 2)
            self._last_pos = pos

    def on_mouse_up(self, canvas, pos):
        self._last_pos = None


# ─────────────────────────────────────────────────────────────
# Flood Fill (BFS)
# ─────────────────────────────────────────────────────────────

class FillTool(Tool):
    def on_mouse_down(self, canvas, pos):
        target = canvas.get_at(pos)[:3]   # ignore alpha
        fill   = self.color[:3]
        if target == fill:
            return
        _flood_fill(canvas, pos, target, fill)

    def on_mouse_move(self, canvas, pos, buttons): pass
    def on_mouse_up(self,   canvas, pos):          pass


def _flood_fill(surface, start, target_color, fill_color):
    """BFS flood fill on a pygame Surface."""
    w, h   = surface.get_size()
    queue  = deque([start])
    visited = set()
    visited.add(start)

    while queue:
        x, y = queue.popleft()
        if surface.get_at((x, y))[:3] != target_color:
            continue
        surface.set_at((x, y), fill_color)

        for nx, ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            if 0 <= nx < w and 0 <= ny < h and (nx,ny) not in visited:
                visited.add((nx, ny))
                queue.append((nx, ny))


# ─────────────────────────────────────────────────────────────
# Text Tool
# ─────────────────────────────────────────────────────────────

class TextTool(Tool):
    FONT_SIZE = 20

    def __init__(self):
        super().__init__()
        self._pos      = None
        self._text     = ""
        self._active   = False
        self._font     = None

    def _get_font(self):
        if self._font is None:
            self._font = pygame.font.SysFont("monospace", self.FONT_SIZE)
        return self._font

    def on_mouse_down(self, canvas, pos):
        # If there was pending text, commit it first
        if self._active and self._text:
            self._render(canvas)
        self._pos    = pos
        self._text   = ""
        self._active = True

    def on_key_down(self, canvas, event):
        if not self._active:
            return
        if event.key == pygame.K_RETURN:
            self._render(canvas)
            self._active = False
            self._text   = ""
        elif event.key == pygame.K_ESCAPE:
            self._active = False
            self._text   = ""
        elif event.key == pygame.K_BACKSPACE:
            self._text = self._text[:-1]
        else:
            if event.unicode and event.unicode.isprintable():
                self._text += event.unicode

    def draw_preview(self, surface):
        if self._active and self._pos:
            font = self._get_font()
            display = self._text + "|"   # cursor blink indicator
            rendered = font.render(display, True, self.color)
            surface.blit(rendered, self._pos)

    def _render(self, canvas):
        if self._text and self._pos:
            font     = self._get_font()
            rendered = font.render(self._text, True, self.color)
            canvas.blit(rendered, self._pos)

    @property
    def is_active(self):
        return self._active


# ─────────────────────────────────────────────────────────────
# Geometry helpers
# ─────────────────────────────────────────────────────────────

def _make_rect(p1, p2):
    x = min(p1[0], p2[0])
    y = min(p1[1], p2[1])
    w = abs(p1[0] - p2[0])
    h = abs(p1[1] - p2[1])
    return pygame.Rect(x, y, max(w, 1), max(h, 1))


def _square_rect(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    side = max(abs(dx), abs(dy))
    sx   = p1[0] + (side if dx >= 0 else -side)
    sy   = p1[1] + (side if dy >= 0 else -side)
    return _make_rect(p1, (sx, sy))


def _circle_params(p1, p2):
    cx = (p1[0] + p2[0]) // 2
    cy = (p1[1] + p2[1]) // 2
    r  = int(((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2) ** 0.5 / 2)
    return cx, cy, r


def _right_triangle_pts(p1, p2):
    return [p1, (p1[0], p2[1]), p2]


def _eq_triangle_pts(p1, p2):
    import math
    base_x1, base_x2 = p1[0], p2[0]
    base_y  = p2[1]
    mid_x   = (base_x1 + base_x2) / 2
    height  = abs(base_x2 - base_x1) * math.sqrt(3) / 2
    top_y   = base_y - height
    return [(base_x1, base_y), (base_x2, base_y), (int(mid_x), int(top_y))]


def _rhombus_pts(p1, p2):
    cx = (p1[0] + p2[0]) // 2
    cy = (p1[1] + p2[1]) // 2
    return [
        (cx,     p1[1]),
        (p2[0],  cy),
        (cx,     p2[1]),
        (p1[0],  cy),
    ]
