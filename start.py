"""
start.py - Spiel-Client starten

Abhängigkeiten: spiel.kern.spiel
"""

import pygame
import sys


def update_fenster_zeigen():
    """Zeigt Update-Fenster mit Pygame"""
    pygame.init()
    fenster = pygame.display.set_mode((500, 200))
    pygame.display.set_caption("Update verfügbar")
    schrift = pygame.font.Font(None, 36)
    schrift_klein = pygame.font.Font(None, 24)
    uhr = pygame.time.Clock()

    ja_button = pygame.Rect(100, 130, 120, 40)
    nein_button = pygame.Rect(280, 130, 120, 40)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ja_button.collidepoint(event.pos):
                    pygame.quit()
                    return True
                if nein_button.collidepoint(event.pos):
                    pygame.quit()
                    return False

        fenster.fill((20, 20, 20))
        titel = schrift.render("Update verfügbar!", True, (200, 160, 60))
        fenster.blit(titel, (500 // 2 - titel.get_width() // 2, 40))
        info = schrift_klein.render("Eine neue Version ist verfügbar.", True, (180, 180, 180))
        fenster.blit(info, (500 // 2 - info.get_width() // 2, 85))

        pygame.draw.rect(fenster, (60, 160, 60), ja_button)
        ja_text = schrift_klein.render("Jetzt updaten", True, (255, 255, 255))
        fenster.blit(ja_text, (ja_button.x + 10, ja_button.y + 12))

        pygame.draw.rect(fenster, (160, 60, 60), nein_button)
        nein_text = schrift_klein.render("Überspringen", True, (255, 255, 255))
        fenster.blit(nein_text, (nein_button.x + 10, nein_button.y + 12))

        pygame.display.flip()
        uhr.tick(60)


try:
    from updater import update_verfuegbar, update_durchfuehren
    if update_verfuegbar():
        if update_fenster_zeigen():
            update_durchfuehren()
except Exception:
    pass

from spiel.kern.spiel import Spiel

if __name__ == "__main__":
    spiel = Spiel()
    spiel.starten()