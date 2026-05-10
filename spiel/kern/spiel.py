"""
spiel/kern/spiel.py - Hauptspielklasse mit Game-Loop

Abhängigkeiten: pygame, config, szenen_manager, ereignis_handler, ladebildschirm, hauptmenue_szene, netzwerk_client
"""

import sys
import pygame
import config
from .szenen_manager import SzenenManager
from .ereignis_handler import EreignisHandler
from .netzwerk_client import NetzwerkClient
from ..szenen.ladebildschirm import Ladebildschirm
from ..szenen.hauptmenue_szene import HauptmenueSzene


def _icon_erstellen() -> pygame.Surface:
    """Zeichnet das Fenster-Icon programmatisch: Schild mit Schwert."""
    icon = pygame.Surface((32, 32), pygame.SRCALPHA)
    icon.fill((0, 0, 0, 0))

    # Schild (Fuenfeck in Akzentfarbe)
    schild_punkte = [(4, 2), (28, 2), (28, 18), (16, 30), (4, 18)]
    pygame.draw.polygon(icon, (180, 120, 60), schild_punkte)
    pygame.draw.polygon(icon, (220, 160, 90), schild_punkte, 1)

    # Schwert-Klinge (vertikal, silber)
    pygame.draw.line(icon, (210, 215, 225), (16, 5), (16, 21), 2)
    # Parierstange (horizontal)
    pygame.draw.line(icon, (210, 215, 225), (9, 21), (23, 21), 2)
    # Griff
    pygame.draw.line(icon, (160, 120, 70), (16, 21), (16, 27), 2)
    # Knauf
    pygame.draw.circle(icon, (190, 150, 80), (16, 28), 2)

    return icon


class Spiel:
    def __init__(self):
        pygame.init()
        self.fenster = pygame.display.set_mode(
            (config.AUFLOESUNG_BREITE, config.AUFLOESUNG_HOEHE)
        )
        pygame.display.set_caption(config.FENSTER_TITEL)
        pygame.display.set_icon(_icon_erstellen())

        self.uhr = pygame.time.Clock()
        self.szenen_manager = SzenenManager()
        self.ereignis_handler = EreignisHandler()
        self.laufend = True
        self.netzwerk_client = NetzwerkClient()

        if self.netzwerk_client.verbinden():
            print("Verbindung zum Server hergestellt")
        else:
            print("Server nicht erreichbar — Offline-Modus")

        def naechste_szene_fabrik():
            return HauptmenueSzene(self.szenen_manager, self.netzwerk_client)

        ladebildschirm = Ladebildschirm(self.szenen_manager, naechste_szene_fabrik)
        self.szenen_manager.szene_pushen(ladebildschirm)

    def starten(self):
        while self.laufend:
            events = self.ereignis_handler.events_sammeln()
            if self.ereignis_handler.ist_beenden_event(events):
                self.beenden()
            self.szenen_manager.events_verarbeiten(events)
            self.szenen_manager.updaten(0.016)
            self.szenen_manager.zeichnen(self.fenster)
            pygame.display.flip()
            self.uhr.tick(config.FPS)

    def beenden(self):
        self.laufend = False
        if self.netzwerk_client:
            self.netzwerk_client.trennen()
        pygame.quit()
        sys.exit()
