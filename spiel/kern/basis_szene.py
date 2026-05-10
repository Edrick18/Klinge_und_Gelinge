"""
spiel/kern/basis_szene.py - Abstrakte Basisklasse für alle Szenen

Abhängigkeiten: keine externen Dependencies
"""

from abc import ABC, abstractmethod


class BasisSzene(ABC):
    @abstractmethod
    def events_verarbeiten(self, events):
        pass

    @abstractmethod
    def updaten(self, delta_zeit: float):
        pass

    @abstractmethod
    def zeichnen(self, flaeche):
        pass