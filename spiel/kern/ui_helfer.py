"""
spiel/kern/ui_helfer.py - Wiederverwendbare UI-Hilfsfunktionen

Stellt button_zeichnen() und balken_zeichnen() mit Hover-Effekten bereit.
"""

import pygame
import config


def button_zeichnen(flaeche, rect, text, schrift,
                    farbe_bg=None, farbe_hover=None,
                    farbe_text=None, farbe_rand=None,
                    rand_breite=1):
    """
    Zeichnet einen Button. Leuchtet automatisch auf wenn die Maus drueber ist.
    Gibt True zurueck wenn gerade gehovert wird.
    """
    maus_pos = pygame.mouse.get_pos()
    ist_hover = rect.collidepoint(maus_pos)

    if farbe_bg is None:
        farbe_bg = config.FARBE_PANEL
    if farbe_hover is None:
        farbe_hover = tuple(min(255, c + 35) for c in farbe_bg)
    if farbe_text is None:
        farbe_text = config.FARBE_TEXT if ist_hover else config.FARBE_TEXT_GEDIMMT
    if farbe_rand is None:
        farbe_rand = config.FARBE_AKZENT if ist_hover else config.FARBE_RAND

    hintergrund = farbe_hover if ist_hover else farbe_bg
    pygame.draw.rect(flaeche, hintergrund, rect)
    pygame.draw.rect(flaeche, farbe_rand, rect, rand_breite)

    text_surf = schrift.render(text, True, farbe_text)
    flaeche.blit(text_surf, text_surf.get_rect(center=rect.center))

    return ist_hover


def balken_zeichnen(flaeche, x, y, breite, hoehe, wert, max_wert, farbe_fuell,
                    farbe_bg=None, farbe_rand=None):
    """Zeichnet einen Fortschrittsbalken."""
    if farbe_bg is None:
        farbe_bg = config.FARBE_PANEL
    if farbe_rand is None:
        farbe_rand = config.FARBE_RAND

    pygame.draw.rect(flaeche, farbe_bg, (x, y, breite, hoehe))
    if max_wert > 0:
        fuell = int(breite * max(0.0, min(1.0, wert / max_wert)))
        if fuell > 0:
            pygame.draw.rect(flaeche, farbe_fuell, (x, y, fuell, hoehe))
    pygame.draw.rect(flaeche, farbe_rand, (x, y, breite, hoehe), 1)
