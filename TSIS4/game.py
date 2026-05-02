import pygame
import random
from config import *
import time

class SnakeGame:
    def __init__(self, settings, username=""):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 24)
        self.big_font = pygame.font.SysFont("arial", 48)
        
        self.settings = settings
        self.username = username
        
        # Инициализируем все переменные сразу
        self.snake = None
        self.direction = None
        self.next_direction = None
        self.score = 0
        self.level = 1
        self.speed = 10
        self.food = None
        self.poison = None
        self.power_up = None
        self.power_up_type = None
        self.power_up_end_time = 0
        self.shield_active = False
        self.obstacles = []
        self.last_move = 0
        self.personal_best = 0
        
        self.reset_game()   # теперь безопасно вызываем


    def reset_game(self):
        self.snake = [(GRID_WIDTH//2, GRID_HEIGHT//2)]
        self.direction = (1, 0)
        self.next_direction = (1, 0)
        
        self.score = 0
        self.level = 1
        self.speed = 10
        
        self.food = self.spawn_food()
        self.poison = None
        self.power_up = None
        self.power_up_type = None
        self.power_up_end_time = 0
        self.shield_active = False
        self.obstacles = []                    # ← Важно!
        self.last_move = pygame.time.get_ticks()

    def spawn_food(self):
        while True:
            pos = (random.randint(1, GRID_WIDTH-2), random.randint(1, GRID_HEIGHT-2))
            if pos not in self.snake and pos not in self.obstacles:
                return pos

    def spawn_poison(self):
        if random.random() < 0.3 and not self.poison:  # 30% chance
            while True:
                pos = (random.randint(1, GRID_WIDTH-2), random.randint(1, GRID_HEIGHT-2))
                if pos not in self.snake and pos != self.food and pos not in self.obstacles:
                    self.poison = pos
                    return

    def spawn_power_up(self):
        if not self.power_up and random.random() < 0.2:
            while True:
                pos = (random.randint(1, GRID_WIDTH-2), random.randint(1, GRID_HEIGHT-2))
                if pos not in self.snake and pos != self.food and pos != self.poison and pos not in self.obstacles:
                    self.power_up = pos
                    self.power_up_type = random.choice(["speed", "slow", "shield"])
                    return

    def generate_obstacles(self):
        self.obstacles = []
        count = self.level + 2
        for _ in range(count):
            while True:
                pos = (random.randint(3, GRID_WIDTH-4), random.randint(3, GRID_HEIGHT-4))
                if (pos not in self.snake and 
                    abs(pos[0] - self.snake[0][0]) > 3 and 
                    abs(pos[1] - self.snake[0][1]) > 3):
                    self.obstacles.append(pos)
                    break

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_move < 1000 / self.speed:
            return False

        self.direction = self.next_direction
        head = (self.snake[0][0] + self.direction[0], self.snake[0][1] + self.direction[1])
        self.snake.insert(0, head)
        self.last_move = now

        # Collisions
        if (head[0] <= 0 or head[0] >= GRID_WIDTH-1 or 
            head[1] <= 0 or head[1] >= GRID_HEIGHT-1 or 
            head in self.snake[1:] or head in self.obstacles):
            if self.shield_active:
                self.shield_active = False
                self.snake.pop(0)  # undo move
                return False
            return True  # game over

        ate_food = False
        if head == self.food:
            self.score += random.choice([10, 20, 30])
            self.food = self.spawn_food()
            ate_food = True
        else:
            self.snake.pop()

        if self.poison and head == self.poison:
            self.snake = self.snake[:-2] if len(self.snake) > 2 else self.snake[:1]
            self.poison = None
            if len(self.snake) <= 1:
                return True

        if self.power_up and head == self.power_up:
            self.activate_power_up()
            self.power_up = None

        # Level up
        if self.score // 100 + 1 > self.level:
            self.level += 1
            self.speed += 2
            if self.level >= 3:
                self.generate_obstacles()

        self.spawn_poison()
        self.spawn_power_up()
        return False

    def activate_power_up(self):
        now = pygame.time.get_ticks()
        if self.power_up_type == "speed":
            self.speed += 8
            self.power_up_end_time = now + 5000
        elif self.power_up_type == "slow":
            self.speed = max(5, self.speed - 5)
            self.power_up_end_time = now + 5000
        elif self.power_up_type == "shield":
            self.shield_active = True

    def draw(self):
        self.screen.fill((0, 0, 0))
        
        # Grid
        if self.settings["grid_overlay"]:
            for x in range(0, SCREEN_WIDTH, GRID_SIZE):
                pygame.draw.line(self.screen, (40, 40, 40), (x, 0), (x, SCREEN_HEIGHT))
            for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
                pygame.draw.line(self.screen, (40, 40, 40), (0, y), (SCREEN_WIDTH, y))

        # Snake
        color = self.settings["snake_color"]
        for i, segment in enumerate(self.snake):
            rect = pygame.Rect(segment[0]*GRID_SIZE, segment[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(self.screen, color if i == 0 else [c-40 for c in color], rect)

        # Food
        fx, fy = self.food
        pygame.draw.rect(self.screen, (255, 100, 0), 
                        (fx*GRID_SIZE, fy*GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # Poison
        if self.poison:
            px, py = self.poison
            pygame.draw.rect(self.screen, (139, 0, 0), 
                           (px*GRID_SIZE, py*GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # Power-up
        if self.power_up:
            color = {"speed": (255, 215, 0), "slow": (0, 191, 255), "shield": (138, 43, 226)}
            px, py = self.power_up
            pygame.draw.rect(self.screen, color[self.power_up_type], 
                           (px*GRID_SIZE, py*GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # Obstacles
        for obs in self.obstacles:
            pygame.draw.rect(self.screen, (100, 100, 100), 
                           (obs[0]*GRID_SIZE, obs[1]*GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # HUD
        score_text = self.font.render(f"Score: {self.score}  Level: {self.level}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))
        
        if self.power_up_end_time > pygame.time.get_ticks():
            remaining = (self.power_up_end_time - pygame.time.get_ticks()) // 1000
            status = self.font.render(f"Power-up: {remaining}s", True, (255, 215, 0))
            self.screen.blit(status, (SCREEN_WIDTH - 200, 10))

        pygame.display.flip()