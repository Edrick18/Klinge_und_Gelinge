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


class Spiel:
    def __init__(self):
        pygame.init()
        self.fenster = pygame.display.set_mode(
            (config.AUFLOESUNG_BREITE, config.AUFLOESUNG_HOEHE)
        )
        pygame.display.set_caption(config.FENSTER_TITEL)
        self.uhr = pygame.time.Clock()
        self.szenen_manager = SzenenManager()
        self.ereignis_handler = EreignisHandler()
        self.laufend = True
        self._erste_szene_gestartet = False
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