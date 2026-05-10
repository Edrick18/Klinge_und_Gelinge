"""
spiel/szenen/stadt.py - Platzhalter-Stadtszene

Abhängigkeiten: pygame, config, basis_szene
"""

import pygame
import config
from ..kern.basis_szene import BasisSzene


class StadtSzene(BasisSzene):
    def __init__(self, szenen_manager, netzwerk_client, charakter: dict):
        self.szenen_manager = szenen_manager
        self.netzwerk_client = netzwerk_client
        self.charakter = charakter
        self.schrift_titel = pygame.font.Font(None, 48)
        self.schrift_info = pygame.font.Font(None, 32)

    def events_verarbeiten(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from .charakter_auswahl_szene import CharakterAuswahlSzene
                    self.szenen_manager.szene_wechseln(CharakterAuswahlSzene(self.szenen_manager, self.netzwerk_client))

    def updaten(self, delta_zeit: float):
        pass

    def zeichnen(self, flaeche: pygame.Surface):
        flaeche.fill(config.FARBE_SCHWARZ)

        name = self.charakter.get("name", "Unbekannt")
        level = self.charakter.get("level", 1)

        willkommen_text = self.schrift_titel.render(f"Willkommen, {name}! (Level {level})", True, config.FARBE_TEXT)
        willkommen_rect = willkommen_text.get_rect(center=(config.AUFLOESUNG_BREITE // 2, config.AUFLOESUNG_HOEHE // 2 - 30))
        flaeche.blit(willkommen_text, willkommen_rect)

        info_text = self.schrift_info.render("Stadt wird in Phase 4 implementiert", True, config.FARBE_TEXT_GEDIMMT)
        info_rect = info_text.get_rect(center=(config.AUFLOESUNG_BREITE // 2, config.AUFLOESUNG_HOEHE // 2 + 30))
        flaeche.blit(info_text, info_rect)