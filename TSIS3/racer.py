"""
racer.py – Core game simulation  (TSIS-3)
"""

import pygame
import random
import math
from ui import (
    C_BG, C_WHITE, C_GREY, C_ACCENT, C_RED, C_GREEN, C_BLUE,
    C_PANEL, CAR_COLORS, text, button,
)

# ─────────────────────────────────────────────────────────────
# Layout constants
# ─────────────────────────────────────────────────────────────

WIN_W, WIN_H = 900, 700
ROAD_X       = 150        # left edge of road
ROAD_W       = 600        # road width
LANE_COUNT   = 4
LANE_W       = ROAD_W // LANE_COUNT   # 150 px each
HUD_H        = 80         # top HUD bar

FINISH_DIST  = 3000       # metres to finish line

DIFF_PARAMS = {
    "easy":   {"base_speed": 4,  "spawn_rate": 0.008, "hazard_rate": 0.005},
    "normal": {"base_speed": 6,  "spawn_rate": 0.014, "hazard_rate": 0.010},
    "hard":   {"base_speed": 9,  "spawn_rate": 0.022, "hazard_rate": 0.017},
}

# ─────────────────────────────────────────────────────────────
# Helper: lane centre x
# ─────────────────────────────────────────────────────────────

def lane_x(lane: int) -> int:
    return ROAD_X + lane * LANE_W + LANE_W // 2


# ─────────────────────────────────────────────────────────────
# Road stripe scroller
# ─────────────────────────────────────────────────────────────

class Road:
    STRIPE_H  = 40
    STRIPE_GAP = 60

    def __init__(self):
        self.offset = 0.0

    def update(self, speed):
        self.offset = (self.offset + speed) % (self.STRIPE_H + self.STRIPE_GAP)

    def draw(self, surface):
        # Asphalt
        pygame.draw.rect(surface, (45, 48, 55), (ROAD_X, HUD_H, ROAD_W, WIN_H - HUD_H))
        # Kerb lines
        for x in (ROAD_X, ROAD_X + ROAD_W):
            pygame.draw.rect(surface, (200, 200, 200), (x - 2, HUD_H, 4, WIN_H - HUD_H))
        # Lane dividers (dashed)
        for lane in range(1, LANE_COUNT):
            lx = ROAD_X + lane * LANE_W
            y  = HUD_H - self.offset
            while y < WIN_H:
                pygame.draw.rect(surface, (180, 180, 100), (lx - 1, int(y), 2, self.STRIPE_H))
                y += self.STRIPE_H + self.STRIPE_GAP


# ─────────────────────────────────────────────────────────────
# Player car
# ─────────────────────────────────────────────────────────────

class Player:
    W, H = 40, 70

    def __init__(self, color, difficulty):
        self.lane   = 1
        self.x      = float(lane_x(1))
        self.y      = float(WIN_H - 140)
        self.color  = color
        self.speed  = DIFF_PARAMS[difficulty]["base_speed"]
        self.base_speed = self.speed
        # Power-up state
        self.shield  = False
        self.nitro   = False
        self.nitro_t = 0.0
        self.rect    = pygame.Rect(0, 0, self.W, self.H)

    def move(self, keys, dt):
        target_x = float(lane_x(self.lane))
        # Smooth lane transition
        self.x += (target_x - self.x) * min(1.0, 8 * dt)

        if keys[pygame.K_LEFT]  and self.lane > 0:              pass  # handled on keydown
        if keys[pygame.K_RIGHT] and self.lane < LANE_COUNT - 1: pass

        # Nitro timer
        if self.nitro:
            self.nitro_t -= dt
            if self.nitro_t <= 0:
                self.nitro   = False
                self.speed   = self.base_speed

        self.rect.centerx = int(self.x)
        self.rect.centery  = int(self.y)

    def draw(self, surface):
        r = self.rect
        # Body
        pygame.draw.rect(surface, self.color, r, border_radius=6)
        # Windows
        pygame.draw.rect(surface, (160, 220, 255),
                         (r.x+5, r.y+10, r.w-10, 20), border_radius=3)
        # Wheels
        for wx, wy in [(r.x-5, r.y+8), (r.right+1, r.y+8),
                       (r.x-5, r.bottom-22), (r.right+1, r.bottom-22)]:
            pygame.draw.rect(surface, (20, 20, 20), (wx, wy, 8, 18), border_radius=3)
        # Shield glow
        if self.shield:
            s = pygame.Surface((r.w + 20, r.h + 20), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (80, 160, 255, 90), s.get_rect())
            surface.blit(s, (r.x - 10, r.y - 10))
        # Nitro flame
        if self.nitro:
            pts = [(r.centerx - 8, r.bottom),
                   (r.centerx + 8, r.bottom),
                   (r.centerx,     r.bottom + 20)]
            pygame.draw.polygon(surface, (255, 140, 20), pts)


# ─────────────────────────────────────────────────────────────
# Traffic car
# ─────────────────────────────────────────────────────────────

TRAFFIC_COLORS = [
    (180, 60, 60), (60, 100, 200), (80, 170, 80),
    (200, 180, 50), (150, 80, 180), (60, 180, 180),
]


class TrafficCar:
    W, H = 38, 65

    def __init__(self, lane, speed):
        self.lane  = lane
        self.x     = float(lane_x(lane))
        self.y     = float(HUD_H - self.H)
        self.speed = speed
        self.color = random.choice(TRAFFIC_COLORS)
        self.rect  = pygame.Rect(0, 0, self.W, self.H)

    def update(self, dt):
        self.y    += self.speed
        self.rect.centerx = int(self.x)
        self.rect.centery  = int(self.y)

    def draw(self, surface):
        r = self.rect
        pygame.draw.rect(surface, self.color, r, border_radius=5)
        pygame.draw.rect(surface, (120, 200, 240),
                         (r.x+4, r.y+12, r.w-8, 18), border_radius=3)
        for wx, wy in [(r.x-4, r.y+6), (r.right, r.y+6),
                       (r.x-4, r.bottom-20), (r.right, r.bottom-20)]:
            pygame.draw.rect(surface, (20, 20, 20), (wx, wy, 7, 16), border_radius=2)

    @property
    def off_screen(self):
        return self.y > WIN_H + 50


# ─────────────────────────────────────────────────────────────
# Road obstacle
# ─────────────────────────────────────────────────────────────

class Obstacle:
    """Oil spill, pothole, or barrier."""
    TYPES = {
        "oil":     {"color": (20, 20, 60),   "w": 70, "h": 30, "label": "🛢", "slow": True},
        "pothole": {"color": (60, 40, 20),    "w": 50, "h": 40, "label": "⬛","slow": False},
        "barrier": {"color": (220, 80, 20),   "w": 90, "h": 20, "label": "▬", "slow": False},
    }

    def __init__(self, lane, speed, kind=None):
        self.kind  = kind or random.choice(list(self.TYPES))
        cfg        = self.TYPES[self.kind]
        self.lane  = lane
        self.x     = float(lane_x(lane))
        self.y     = float(HUD_H - cfg["h"])
        self.speed = speed
        self.w, self.h = cfg["w"], cfg["h"]
        self.color = cfg["color"]
        self.slow  = cfg["slow"]
        self.rect  = pygame.Rect(0, 0, self.w, self.h)

    def update(self, dt):
        self.y += self.speed
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        r = self.rect
        pygame.draw.ellipse(surface, self.color, r) if self.kind == "oil" else \
        pygame.draw.rect(surface,   self.color, r, border_radius=4)
        # highlight
        pygame.draw.rect(surface, (255, 255, 255), r, 1,
                         border_radius=4 if self.kind != "oil" else 0)

    @property
    def off_screen(self):
        return self.y > WIN_H + 50


# ─────────────────────────────────────────────────────────────
# Collectible (coin / power-up)
# ─────────────────────────────────────────────────────────────

class Coin:
    VALUES = {1: (C_ACCENT, 14), 3: (C_GREEN, 16), 5: ((220, 80, 200), 18)}

    def __init__(self, lane, speed, value=None):
        self.value  = value or random.choices([1, 3, 5], weights=[6, 3, 1])[0]
        self.lane   = lane
        self.x      = float(lane_x(lane))
        self.y      = float(HUD_H - 20)
        self.speed  = speed
        self.color, self.r = self.VALUES[self.value]
        self.rect   = pygame.Rect(0, 0, self.r*2, self.r*2)
        self.lifetime = 8.0

    def update(self, dt):
        self.y        += self.speed
        self.lifetime -= dt
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.r)
        f = pygame.font.SysFont("segoeui", 11, bold=True)
        s = f.render(f"+{self.value}", True, (10, 10, 10))
        surface.blit(s, s.get_rect(center=(int(self.x), int(self.y))))

    @property
    def off_screen(self):
        return self.y > WIN_H + 30 or self.lifetime <= 0


class PowerUp:
    KINDS = {
        "nitro":  {"color": (255, 140, 20),  "label": "N", "tip": "NITRO"},
        "shield": {"color": (80,  160, 255),  "label": "S", "tip": "SHIELD"},
        "repair": {"color": (80,  220, 80),   "label": "R", "tip": "REPAIR"},
    }

    def __init__(self, lane, speed):
        self.kind    = random.choice(list(self.KINDS))
        cfg          = self.KINDS[self.kind]
        self.lane    = lane
        self.x       = float(lane_x(lane))
        self.y       = float(HUD_H - 24)
        self.speed   = speed
        self.color   = cfg["color"]
        self.label   = cfg["label"]
        self.tip     = cfg["tip"]
        self.rect    = pygame.Rect(0, 0, 36, 36)
        self.lifetime = 6.0

    def update(self, dt):
        self.y        += self.speed
        self.lifetime -= dt
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=6)
        pygame.draw.rect(surface, C_WHITE,    self.rect, 2, border_radius=6)
        f = pygame.font.SysFont("segoeui", 18, bold=True)
        s = f.render(self.label, True, (10, 10, 10))
        surface.blit(s, s.get_rect(center=self.rect.center))

    @property
    def off_screen(self):
        return self.y > WIN_H + 40 or self.lifetime <= 0


# ─────────────────────────────────────────────────────────────
# Road event: nitro strip
# ─────────────────────────────────────────────────────────────

class NitroStrip:
    """Temporary speed-boost strip across full road width."""
    H = 18

    def __init__(self, speed):
        self.y     = float(HUD_H - self.H)
        self.speed = speed
        self.rect  = pygame.Rect(ROAD_X, int(self.y), ROAD_W, self.H)

    def update(self, dt):
        self.y    += self.speed
        self.rect.y = int(self.y)

    def draw(self, surface):
        colors = [(255, 80, 0), (255, 160, 0), (255, 220, 0)]
        for i, c in enumerate(colors):
            stripe_w = ROAD_W // 3
            pygame.draw.rect(surface, c,
                             (ROAD_X + i * stripe_w, int(self.y), stripe_w, self.H))
        f = pygame.font.SysFont("segoeui", 11, bold=True)
        s = f.render("NITRO STRIP", True, (10, 10, 10))
        surface.blit(s, s.get_rect(center=self.rect.center))

    @property
    def off_screen(self):
        return self.y > WIN_H + 30


# ─────────────────────────────────────────────────────────────
# HUD drawer
# ─────────────────────────────────────────────────────────────

def draw_hud(surface, score, coins, distance, speed, active_pu, pu_time, shield):
    # Background bar
    pygame.draw.rect(surface, (20, 22, 35), (0, 0, WIN_W, HUD_H))
    pygame.draw.line(surface, (55, 58, 80), (0, HUD_H), (WIN_W, HUD_H), 2)

    text(surface, f"Score: {score}",    16,  12, size=18, bold=True, color=C_ACCENT)
    text(surface, f"Coins: {coins}",    16,  40, size=16, color=C_WHITE)
    text(surface, f"Speed: {speed:.0f}", 220, 12, size=16, color=C_WHITE)

    # Distance bar
    progress = min(1.0, distance / FINISH_DIST)
    bar_x, bar_w = 400, 280
    pygame.draw.rect(surface, C_PANEL, (bar_x, 18, bar_w, 20), border_radius=6)
    pygame.draw.rect(surface, C_GREEN,  (bar_x, 18, int(bar_w * progress), 20), border_radius=6)
    pygame.draw.rect(surface, C_GREY,   (bar_x, 18, bar_w, 20), 1, border_radius=6)
    text(surface, f"{distance} / {FINISH_DIST} m", bar_x, 44, size=13, color=C_GREY)
    text(surface, "FINISH →", bar_x + bar_w + 6, 22, size=13, color=C_ACCENT)

    # Active power-up indicator
    if active_pu:
        pu_x = WIN_W - 180
        text(surface, f"[{active_pu.upper()}]", pu_x, 10, size=16, bold=True, color=C_GREEN)
        text(surface, f"{pu_time:.1f}s", pu_x, 34, size=13, color=C_GREY)

    if shield:
        text(surface, "🛡 SHIELD", WIN_W - 180, 10, size=15, bold=True, color=C_BLUE)


# ─────────────────────────────────────────────────────────────
# Main game function
# ─────────────────────────────────────────────────────────────

def run_game(screen, settings: dict) -> tuple[int, int, int]:
    """
    Run one game session.
    Returns (score, distance, coins).
    """
    clock = pygame.time.Clock()
    diff  = settings.get("difficulty", "normal")
    params = DIFF_PARAMS[diff]

    car_color = CAR_COLORS.get(settings.get("car_color", "red"), (220, 60, 60))
    player    = Player(car_color, diff)
    road      = Road()

    traffic   : list[TrafficCar] = []
    obstacles : list[Obstacle]   = []
    coins_list: list[Coin]       = []
    powerups  : list[PowerUp]    = []
    strips    : list[NitroStrip] = []

    score     = 0
    coins     = 0
    distance  = 0.0
    base_speed = float(params["base_speed"])
    road_speed = base_speed
    spawn_rate  = params["spawn_rate"]
    hazard_rate = params["hazard_rate"]

    active_pu   = None   # "nitro" | "shield" | None
    pu_timer    = 0.0
    NITRO_DURATION = 4.0

    crashed     = False
    crash_timer = 0.0

    # Lane hazard zones: some lanes are marked "slow" occasionally
    hazard_lanes: set[int] = set()
    hazard_event_timer = 0.0

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        # ── Events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return score, int(distance), coins
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT  and player.lane > 0:
                    player.lane -= 1
                if event.key == pygame.K_RIGHT and player.lane < LANE_COUNT - 1:
                    player.lane += 1
                if event.key == pygame.K_ESCAPE:
                    return score, int(distance), coins

        keys = pygame.key.get_pressed()
        player.move(keys, dt)

        # ── Road speed & difficulty scaling ──
        road_speed  = base_speed + distance / 400
        spawn_rate  = params["spawn_rate"]  + distance / 600000
        hazard_rate = params["hazard_rate"] + distance / 800000

        road.update(road_speed)
        distance += road_speed * dt * 3.5   # metres

        # ── Spawn logic ──
        def _safe_lane():
            """Pick a lane not occupied by player."""
            lanes = [l for l in range(LANE_COUNT) if l != player.lane]
            return random.choice(lanes)

        if random.random() < spawn_rate:
            traffic.append(TrafficCar(_safe_lane(), road_speed * random.uniform(0.6, 1.0)))

        if random.random() < hazard_rate:
            obstacles.append(Obstacle(_safe_lane(), road_speed))

        if random.random() < 0.006:
            lane = random.randint(0, LANE_COUNT - 1)
            if not any(c.lane == lane for c in coins_list):
                coins_list.append(Coin(lane, road_speed))

        if random.random() < 0.003 and not any(isinstance(p, PowerUp) for p in powerups):
            powerups.append(PowerUp(random.randint(0, LANE_COUNT - 1), road_speed))

        if random.random() < 0.002 and not strips:
            strips.append(NitroStrip(road_speed))

        # ── Hazard lane events ──
        hazard_event_timer -= dt
        if hazard_event_timer <= 0:
            hazard_lanes = set(random.sample(range(LANE_COUNT),
                                             k=random.randint(0, 2)))
            hazard_event_timer = random.uniform(5, 12)

        # ── Update entities ──
        for t in traffic:   t.update(dt)
        for o in obstacles: o.update(dt)
        for c in coins_list: c.update(dt)
        for p in powerups:  p.update(dt)
        for s in strips:    s.update(dt)

        traffic   = [t for t in traffic    if not t.off_screen]
        obstacles = [o for o in obstacles  if not o.off_screen]
        coins_list = [c for c in coins_list if not c.off_screen]
        powerups  = [p for p in powerups   if not p.off_screen]
        strips    = [s for s in strips     if not s.off_screen]

        # ── Collision: traffic ──
        if not crashed:
            for t in traffic:
                if player.rect.colliderect(t.rect):
                    if player.shield:
                        player.shield = False
                        active_pu = None
                        traffic.remove(t)
                        break
                    else:
                        crashed     = True
                        crash_timer = 1.5
                        break

        # ── Collision: obstacles ──
        if not crashed:
            for o in obstacles:
                if player.rect.colliderect(o.rect):
                    if o.slow:
                        player.speed = max(base_speed * 0.5, player.speed * 0.85)
                    else:
                        if player.shield:
                            player.shield = False
                            active_pu = None
                            obstacles.remove(o)
                            break
                        else:
                            crashed     = True
                            crash_timer = 1.5
                            break

        # ── Collect coins ──
        for c in list(coins_list):
            if player.rect.colliderect(c.rect):
                coins += c.value
                score += c.value * 10
                coins_list.remove(c)

        # ── Collect power-ups ──
        for p in list(powerups):
            if player.rect.colliderect(p.rect):
                powerups.remove(p)
                if p.kind == "nitro":
                    player.nitro   = True
                    player.nitro_t = NITRO_DURATION
                    player.speed   = base_speed * 2.2
                    active_pu = "nitro"
                    pu_timer  = NITRO_DURATION
                elif p.kind == "shield":
                    player.shield = True
                    active_pu = "shield"
                    pu_timer  = 0  # permanent until hit
                elif p.kind == "repair":
                    # Clears nearest obstacle
                    if obstacles:
                        obstacles.pop(0)
                    active_pu = None
                score += 50

        # ── Nitro strip collision ──
        for s in list(strips):
            if player.rect.colliderect(s.rect):
                if not player.nitro:
                    player.nitro   = True
                    player.nitro_t = 2.5
                    player.speed   = base_speed * 1.8
                    active_pu = "nitro"
                    pu_timer  = 2.5

        # ── Power-up timer ──
        if active_pu == "nitro":
            pu_timer -= dt
            if pu_timer <= 0:
                active_pu = None

        # ── Crash handling ──
        if crashed:
            crash_timer -= dt
            if crash_timer <= 0:
                return score, int(distance), coins

        # ── Finish line ──
        if distance >= FINISH_DIST:
            score += 1000
            return score, int(distance), coins

        # ── Score from distance ──
        score = int(coins * 10 + distance * 0.5)

        # ── Draw ──
        screen.fill((20, 20, 30))
        road.draw(screen)

        # Hazard zone overlay
        for lane in hazard_lanes:
            s = pygame.Surface((LANE_W - 4, WIN_H - HUD_H), pygame.SRCALPHA)
            s.fill((180, 30, 30, 25))
            screen.blit(s, (ROAD_X + lane * LANE_W + 2, HUD_H))

        for s2 in strips:    s2.draw(screen)
        for o in obstacles:  o.draw(screen)
        for c in coins_list: c.draw(screen)
        for p in powerups:   p.draw(screen)
        for t in traffic:    t.draw(screen)
        player.draw(screen)

        draw_hud(screen, score, coins, int(distance),
                 road_speed, active_pu, pu_timer, player.shield)

        # Crash flash
        if crashed:
            overlay = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
            alpha   = int(120 * (crash_timer / 1.5))
            overlay.fill((255, 30, 30, alpha))
            screen.blit(overlay, (0, 0))
            text(screen, "CRASH!", WIN_W//2, WIN_H//2 - 30,
                 size=52, bold=True, color=(255, 60, 60), center=True)

        pygame.display.flip()

    return score, int(distance), coins
