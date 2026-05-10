"""
spiel/szenen/ladebildschirm.py - Ladebildschirm-Szene

Abhängigkeiten: pygame, config, basis_szene
"""

import pygame
import config
from ..kern.basis_szene import BasisSzene


class Ladebildschirm(BasisSzene):
    def __init__(self, szenen_manager, naechste_szene_fabrik):
        self.szenen_manager = szenen_manager
        self.naechste_szene_fabrik = naechste_szene_fabrik
        self.vergangene_zeit = 0.0
        self.schrift_titel = pygame.font.Font(None, 72)
        self.schrift_untertitel = pygame.font.Font(None, 36)

    def events_verarbeiten(self, events):
        pass

    def updaten(self, delta_zeit: float):
        self.vergangene_zeit += delta_zeit
        if self.vergangene_zeit >= config.LADEBILDSCHIRM_DAUER:
            naechste_szene = self.naechste_szene_fabrik()
            self.szenen_manager.szene_wechseln(naechste_szene)

    def zeichnen(self, flaeche: pygame.Surface):
        flaeche.fill(config.FARBE_HINTERGRUND)

        titel_text = self.schrift_titel.render("PROJEKT RPG", True, config.FARBE_AKZENT)
        titel_rect = titel_text.get_rect(center=(config.AUFLOESUNG_BREITE // 2, config.AUFLOESUNG_HOEHE // 3))
        flaeche.blit(titel_text, titel_rect)

        untertitel_text = self.schrift_untertitel.render("Wird geladen...", True, config.FARBE_TEXT_GEDIMMT)
        untertitel_rect = untertitel_text.get_rect(center=(config.AUFLOESUNG_BREITE // 2, config.AUFLOESUNG_HOEHE // 2))
        flaeche.blit(untertitel_text, untertitel_rect)

        balken_breite = 400
        balken_hoehe = 20
        balken_x = (config.AUFLOESUNG_BREITE - balken_breite) // 2
        balken_y = config.AUFLOESUNG_HOEHE * 2 // 3

        pygame.draw.rect(flaeche, config.FARBE_PANEL, (balken_x, balken_y, balken_breite, balken_hoehe))

        fortschritt = min(self.vergangene_zeit / config.LADEBILDSCHIRM_DAUER, 1.0)
        balken_fuell_breite = int(balken_breite * fortschritt)
        pygame.draw.rect(flaeche, config.FARBE_AKZENT, (balken_x, balken_y, balken_fuell_breite, balken_hoehe))