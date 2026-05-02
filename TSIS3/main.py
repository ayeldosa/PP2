#!/usr/bin/env python3
"""
main.py – Entry point for Racer TSIS-3
Requires: pygame  (pip install pygame)

Controls:
  ← / →     change lane
  ESC        pause / return to menu
"""

import sys
import pygame

from persistence import load_settings, save_settings, save_score
from ui import main_menu, name_entry, settings_screen, leaderboard_screen, game_over_screen
from racer import run_game, WIN_W, WIN_H


def main():
    pygame.init()
    screen   = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Racer  –  TSIS 3")

    settings = load_settings()

    # ── App state machine ──
    state = "menu"

    while True:
        if state == "menu":
            choice = main_menu(screen, settings)
            if choice == "quit":
                break
            elif choice == "play":
                # Name entry before first game (or if username is default)
                settings["username"] = name_entry(screen, settings)
                save_settings(settings)
                state = "game"
            elif choice == "leaderboard":
                leaderboard_screen(screen)
                state = "menu"
            elif choice == "settings":
                settings = settings_screen(screen, settings)
                state = "menu"

        elif state == "game":
            score, distance, coins = run_game(screen, settings)
            save_score(settings["username"], score, distance, coins)
            state = "game_over"
            last_result = (score, distance, coins)

        elif state == "game_over":
            score, distance, coins = last_result
            action = game_over_screen(screen, score, distance, coins)
            if action == "retry":
                state = "game"
            else:
                state = "menu"

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
