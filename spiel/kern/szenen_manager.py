"""
spiel/kern/szenen_manager.py - Szenen-Stack-Verwaltung

Abhängigkeiten: basis_szene
"""

from .basis_szene import BasisSzene


class SzenenManager:
    def __init__(self):
        self._szenen_stack = []

    def szene_wechseln(self, szene: BasisSzene):
        self._szenen_stack.clear()
        self._szenen_stack.append(szene)

    def szene_pushen(self, szene: BasisSzene):
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
        if self.aktuelle_szene:
            self.aktuelle_szene.events_verarbeiten(events)

    def updaten(self, delta_zeit: float):
        if self.aktuelle_szene:
            self.aktuelle_szene.updaten(delta_zeit)

    def zeichnen(self, flaeche):
        if self.aktuelle_szene:
            self.aktuelle_szene.zeichnen(flaeche)