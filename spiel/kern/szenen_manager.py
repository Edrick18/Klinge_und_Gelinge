"""
spiel/kern/szenen_manager.py - Szenen-Stack-Verwaltung mit Fade-Uebergaengen

Abhängigkeiten: basis_szene, pygame
"""

import pygame
from .basis_szene import BasisSzene

# Geschwindigkeit des Fades: Punkte pro Sekunde (255 = volle Sekunde, 510 = 0.5s)
FADE_GESCHWINDIGKEIT = 510


class SzenenManager:
    def __init__(self):
        self._szenen_stack = []
        self._naechste_szene = None
        self._uebergang_alpha = 0.0
        self._uebergang_phase = None   # None | "ausblenden" | "einblenden"
        self._overlay = None

    def szene_wechseln(self, szene: BasisSzene):
        """Wechselt zur naechsten Szene mit Fade-Uebergang."""
        if self._uebergang_phase == "ausblenden":
            # Laufender Uebergang: Ziel-Szene aktualisieren
            self._naechste_szene = szene
            return
        self._naechste_szene = szene
        self._uebergang_phase = "ausblenden"
        self._uebergang_alpha = 0.0

    def szene_pushen(self, szene: BasisSzene):
        """Fuegt eine Szene sofort auf den Stack (kein Fade – fuer Ladebildschirm)."""
        self._szenen_stack.append(szene)

    def szene_entfernen(self):
        if self._szenen_stack:
            self._szenen_stack.pop()

    @property
    def aktuelle_szene(self) -> BasisSzene:
        if self._szenen_stack:
            return self._szenen_stack[-1]
        return None

    def events_verarbeiten(self, events):
        # Waehrend Ausblenden keine weiteren Klicks verarbeiten
        if self._uebergang_phase == "ausblenden":
            return
        if self.aktuelle_szene:
            self.aktuelle_szene.events_verarbeiten(events)

    def updaten(self, delta_zeit: float):
        schritt = FADE_GESCHWINDIGKEIT * delta_zeit

        if self._uebergang_phase == "ausblenden":
            self._uebergang_alpha = min(255.0, self._uebergang_alpha + schritt)
            if self._uebergang_alpha >= 255:
                # Szene tatsaechlich wechseln
                self._szenen_stack.clear()
                self._szenen_stack.append(self._naechste_szene)
                self._naechste_szene = None
                self._uebergang_phase = "einblenden"

        elif self._uebergang_phase == "einblenden":
            self._uebergang_alpha = max(0.0, self._uebergang_alpha - schritt)
            if self._uebergang_alpha <= 0:
                self._uebergang_phase = None

        if self.aktuelle_szene:
            self.aktuelle_szene.updaten(delta_zeit)

    def zeichnen(self, flaeche):
        if self.aktuelle_szene:
            self.aktuelle_szene.zeichnen(flaeche)

        # Fade-Overlay zeichnen
        if self._uebergang_phase is not None and self._uebergang_alpha > 0:
            if self._overlay is None or self._overlay.get_size() != flaeche.get_size():
                self._overlay = pygame.Surface(flaeche.get_size(), pygame.SRCALPHA)
            self._overlay.fill((0, 0, 0, int(self._uebergang_alpha)))
            flaeche.blit(self._overlay, (0, 0))
