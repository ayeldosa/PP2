import pygame
import datetime

pygame.init()

WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mickey Clock")

clock_fps = pygame.time.Clock()

clock_bg = pygame.image.load("/Users/pelmen/Desktop/programs/PP2-1/lab9/MickeyCloak/images/clock.jpg")
left_hand = pygame.image.load("/Users/pelmen/Desktop/programs/PP2-1/lab9/MickeyCloak/images/right_hand.png")
right_hand = pygame.image.load("/Users/pelmen/Desktop/programs/PP2-1/lab9/MickeyCloak/images/left_hand.png")

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