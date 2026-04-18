import pygame
import sys

pygame.init()


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Ball")


WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0 , 0 , 255)

ball_x = WIDTH // 2
ball_y = HEIGHT // 2
radius = 25
step = 20

clock = pygame.time.Clock()

running = True
while running:
    screen.fill(WHITE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT and ball_x - step - radius >= 0:
                ball_x -= step
            if event.key == pygame.K_RIGHT and ball_x + step + radius <= WIDTH:
                ball_x += step
            if event.key == pygame.K_UP and ball_y - step - radius >= 0:
                ball_y -= step
            if event.key == pygame.K_DOWN and ball_y + step + radius <= HEIGHT:
                ball_y += step

    pygame.draw.circle(screen, RED, (ball_x, ball_y), radius)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()