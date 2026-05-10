"""
start.py - Spiel-Client starten

Abhängigkeiten: spiel.kern.spiel
"""

import pygame
import sys


def update_fenster_zeigen():
    """Zeigt Pflicht-Update-Fenster (kein Ueberspringen moeglich)"""
    pygame.init()
    fenster = pygame.display.set_mode((500, 240))
    pygame.display.set_caption("Update erforderlich")
    schrift = pygame.font.Font(None, 36)
    schrift_klein = pygame.font.Font(None, 24)
    uhr = pygame.time.Clock()

    update_button = pygame.Rect(130, 150, 160, 45)
    beenden_button = pygame.Rect(320, 158, 130, 30)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if update_button.collidepoint(event.pos):
                    pygame.quit()
                    return True
                if beenden_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        fenster.fill((20, 20, 20))
        titel = schrift.render("Update erforderlich!", True, (200, 160, 60))
        fenster.blit(titel, (500 // 2 - titel.get_width() // 2, 30))
        info = schrift_klein.render("Eine neue Version ist verfuegbar.", True, (180, 180, 180))
        fenster.blit(info, (500 // 2 - info.get_width() // 2, 80))
        info2 = schrift_klein.render("Das Update wird automatisch installiert.", True, (140, 140, 140))
        fenster.blit(info2, (500 // 2 - info2.get_width() // 2, 108))

        pygame.draw.rect(fenster, (60, 160, 60), update_button)
        ja_text = schrift_klein.render("Jetzt updaten", True, (255, 255, 255))
        fenster.blit(ja_text, ja_text.get_rect(center=update_button.center))

        pygame.draw.rect(fenster, (60, 60, 60), beenden_button)
        end_text = schrift_klein.render("Beenden", True, (160, 160, 160))
        fenster.blit(end_text, end_text.get_rect(center=beenden_button.center))

        pygame.display.flip()
        uhr.tick(60)


try:
    from updater import update_verfuegbar, update_durchfuehren
    if update_verfuegbar():
        if update_fenster_zeigen():
            update_durchfuehren()
            sys.exit()
except Exception:
    pass

from spiel.kern.spiel import Spiel

if __name__ == "__main__":
    spiel = Spiel()
    spiel.starten()