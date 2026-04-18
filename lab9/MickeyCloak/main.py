import pygame
import sys
import os
import datetime

pygame.init()

WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mickey Clock")

clock_fps = pygame.time.Clock()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
images_folder = os.path.join(BASE_DIR, "images")

clock_bg = pygame.image.load(os.path.join(images_folder, "clock.jpg")).convert_alpha()
left_hand = pygame.image.load(os.path.join(images_folder, "left_hand.png")).convert_alpha()
right_hand = pygame.image.load(os.path.join(images_folder, "right_hand.png")).convert_alpha()

clock_bg = pygame.transform.scale(clock_bg, (600, 600))
left_hand = pygame.transform.scale(left_hand, (700, 500))
right_hand = pygame.transform.scale(right_hand, (700, 500))

center = (WIDTH // 2, HEIGHT // 2)


def rotate_hand(image, angle):
    rotated = pygame.transform.rotate(image, -angle)
    rect = rotated.get_rect(center=center)
    screen.blit(rotated, rect.topleft)


running = True

while running:
    screen.blit(clock_bg, (0, 0))

    now = datetime.datetime.now()

    
    seconds = now.second + now.microsecond / 1_000_000
   
   
    minutes = now.minute + seconds / 60

  
    SECOND_OFFSET = 170
    MINUTE_OFFSET = -72


    second_angle = seconds * 6 + SECOND_OFFSET
    minute_angle = minutes * 6 + MINUTE_OFFSET

    rotate_hand(left_hand, second_angle)
    rotate_hand(right_hand, minute_angle)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            

    pygame.display.update()
    clock_fps.tick(60)
    

pygame.quit()
sys.exit()