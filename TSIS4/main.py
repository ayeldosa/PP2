import pygame
import sys
from game import SnakeGame
from db import init_db, save_game_result, get_top_10, get_personal_best
from config import load_settings, save_settings

pygame.init()
screen = pygame.display.set_mode((800, 600))
font = pygame.font.SysFont("arial", 32)
small_font = pygame.font.SysFont("arial", 24)

def draw_text(text, y, size=32, color=(255,255,255)):
    f = pygame.font.SysFont("arial", size)
    txt = f.render(text, True, color)
    screen.blit(txt, (400 - txt.get_width()//2, y))

def main_menu(settings):
    username = ""
    input_active = True
    
    while True:
        screen.fill((0, 0, 0))
        
        # Заголовок
        draw_text("SNAKE GAME", 80, 48, (0, 255, 100))
        
        # Поле ввода имени
        draw_text("Введите имя игрока:", 180, 32, (200, 200, 200))
        
        # Отображение текущего имени
        name_color = (0, 255, 0) if input_active else (100, 100, 100)
        name_surf = font.render(username + ("|" if input_active else ""), True, name_color)
        screen.blit(name_surf, (400 - name_surf.get_width()//2, 230))
        
        # Кнопки
        buttons = [
            ("PLAY", 320, (0, 255, 0)),
            ("Leaderboard", 380, (255, 255, 255)),
            ("Settings", 440, (255, 255, 255)),
            ("Quit", 500, (255, 100, 100))
        ]
        
        mouse_pos = pygame.mouse.get_pos()
        
        for text, y_pos, base_color in buttons:
            # Подсветка при наведении
            color = (255, 255, 0) if y_pos - 10 <= mouse_pos[1] <= y_pos + 40 else base_color
            draw_text(text, y_pos, 36, color)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Ввод имени
            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN and username.strip():
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif len(username) < 15 and event.unicode.isalnum() or event.unicode == "_":
                    username += event.unicode

            # Клик мышью
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                
                if 310 <= my <= 355:          # === PLAY ===
                    if username.strip():
                        print(f"▶ Запуск игры с именем: {username.strip()}")
                        try:
                            game = SnakeGame(settings, username.strip())
                            game.personal_best = get_personal_best(username.strip())
                            print("Игра создана успешно. Запуск игрового цикла...")
                            run_game(game, settings)
                            return
                        except Exception as e:
                            print("❌ ОШИБКА при запуске игры:")
                            import traceback
                            traceback.print_exc()
                            
                            # Показываем ошибку на экране
                            screen.fill((20, 0, 0))
                            draw_text("ERROR!", 180, 48, (255, 50, 50))
                            draw_text(str(e)[:50], 260, 24, (255, 200, 0))
                            draw_text("Нажми любую клавишу для возврата...", 340, 22)
                            pygame.display.flip()
                            wait_for_key()
                    else:
                        print("⚠ Введите имя перед началом игры!")

                elif 370 <= my <= 415:       # Leaderboard
                    show_leaderboard()
                    
                elif 430 <= my <= 475:       # Settings
                    settings = show_settings(settings)
                    
                elif 490 <= my <= 535:       # Quit
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        pygame.time.wait(10)


# Вспомогательная функция (добавь в конец файла, если её нет)
def wait_for_key():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

def run_game(game, settings):
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and game.direction != (0, 1):
                    game.next_direction = (0, -1)
                elif event.key == pygame.K_DOWN and game.direction != (0, -1):
                    game.next_direction = (0, 1)
                elif event.key == pygame.K_LEFT and game.direction != (1, 0):
                    game.next_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and game.direction != (-1, 0):
                    game.next_direction = (1, 0)

        if game.update():
            # Game Over
            save_game_result(game.username, game.score, game.level)
            game_over_screen(game)
            return

        game.draw()
        game.clock.tick(60)

def game_over_screen(game):
    while True:
        screen.fill((0, 0, 0))
        draw_text("GAME OVER", 150, 48, (255, 0, 0))
        draw_text(f"Score: {game.score}", 250)
        draw_text(f"Level: {game.level}", 300)
        draw_text(f"Personal Best: {game.personal_best}", 350)
        
        draw_text("Retry", 450)
        draw_text("Main Menu", 500)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if 450 <= my <= 480:
                    new_game = SnakeGame(game.settings, game.username)
                    new_game.personal_best = game.personal_best
                    run_game(new_game, game.settings)
                    return
                elif 500 <= my <= 530:
                    return

        pygame.display.flip()

def show_leaderboard():
    top = get_top_10()
    while True:
        screen.fill((0, 0, 0))
        draw_text("LEADERBOARD", 50, 40)
        
        for i, entry in enumerate(top):
            text = f"{i+1}. {entry['username']} - {entry['score']} pts (Lvl {entry['level_reached']})"
            txt = small_font.render(text, True, (255, 255, 255))
            screen.blit(txt, (100, 120 + i*40))

        draw_text("Back", 520)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and 520 <= event.pos[1] <= 550:
                return

        pygame.display.flip()

def show_settings(settings):
    new_settings = settings.copy()
    while True:
        screen.fill((0, 0, 0))
        draw_text("SETTINGS", 100)
        
        draw_text(f"Grid Overlay: {'ON' if new_settings['grid_overlay'] else 'OFF'}", 200)
        draw_text(f"Sound: {'ON' if new_settings['sound'] else 'OFF'}", 250)
        draw_text("Snake Color: Click to change", 300)

        draw_text("Save & Back", 450)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return settings
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if 200 <= my <= 230:
                    new_settings["grid_overlay"] = not new_settings["grid_overlay"]
                elif 250 <= my <= 280:
                    new_settings["sound"] = not new_settings["sound"]
                elif 300 <= my <= 330:
                    # Simple color cycle
                    colors = [[0,255,0], [255,0,0], [0,0,255], [255,165,0]]
                    idx = colors.index(new_settings["snake_color"]) if new_settings["snake_color"] in colors else 0
                    new_settings["snake_color"] = colors[(idx+1)%len(colors)]
                elif 450 <= my <= 480:
                    save_settings(new_settings)
                    return new_settings

        pygame.display.flip()

if __name__ == "__main__":
    init_db()
    settings = load_settings()
    main_menu(settings)