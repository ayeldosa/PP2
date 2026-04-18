import pygame
import sys
import os
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT  = 700, 500 
sc = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Music Player")
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

font = pygame.font.SysFont(None, 40)
music_folder = "music"
playlist = [
    os.path.join(music_folder, file)
    for file in os.listdir(music_folder)
    if file.endswith((".mp3", ".wav"))
]

if not playlist:
    print("Нет музыки в папке music")
    pygame.quit()
    sys.exit()

current_track = 0
is_playing = False


def load_track(index):
    pygame.mixer.music.load(playlist[index])


load_track(current_track)

running = True
clock = pygame.time.Clock()

while running:
    sc.fill(WHITE)

    track_name = os.path.basename(playlist[current_track])
    text = font.render(f"Track: {track_name}", True, BLACK)

    controls = font.render(
        "P - Play | S - Stop | N - Next | B - Back | Q - Quit",
        True,
        BLACK
    )

    sc.blit(text, (50, 120))
    sc.blit(controls, (50, 200))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                pygame.mixer.music.play()
                is_playing = True

            elif event.key == pygame.K_s:
                pygame.mixer.music.stop()
                is_playing = False

            elif event.key == pygame.K_n:
                current_track = (current_track + 1) % len(playlist)
                load_track(current_track)
                pygame.mixer.music.play()
                is_playing = True

            elif event.key == pygame.K_b:
                current_track = (current_track - 1) % len(playlist)
                load_track(current_track)
                pygame.mixer.music.play()
                is_playing = True

            elif event.key == pygame.K_q:
                running = False

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()