"""
server/logik/charakter_verwaltung.py - Server-seitige Charakterverwaltung

Abhängigkeiten: server.datenbank.datenbank
"""

import re

from server.datenbank.datenbank import Datenbank


VERFÜGBARE_MASTERIEN = [
    "krieger", "waechter", "zauberer",
    "schicksalsritter", "schatten", "herold"
]

GRUNDWERT_ZU_KLASSE = {
    "staerke":       "krieger",
    "vitalitaet":    "waechter",
    "weisheit":      "zauberer",
    "glueck":        "schicksalsritter",
    "beweglichkeit": "schatten",
    "charisma":      "herold"
}

MASTERIE_ANZEIGENAME = {
    "krieger": "Krieger",
    "waechter": "Wächter",
    "zauberer": "Zauberer",
    "schicksalsritter": "Schicksalsritter",
    "schatten": "Schatten",
    "herold": "Herold"
}


class CharakterVerwaltung:
    def __init__(self, datenbank: Datenbank):
        self.datenbank = datenbank

    def charakter_erstellen(self, spieler_id: int, name: str, masterie_1: str, stats: dict) -> dict:
        if not self._name_valid(name):
            return {"erfolg": False, "nachricht": "Name muss 3-20 Zeichen haben und nur Buchstaben, Zahlen oder Leerzeichen enthalten"}

        if masterie_1 not in VERFÜGBARE_MASTERIEN:
            return {"erfolg": False, "nachricht": "Ungültige Masterie"}

        if not self._stats_valid(stats):
            return {"erfolg": False, "nachricht": "Genau 20 Punkte müssen verteilt werden (Min: 10, Max: 25 pro Wert)"}

        if self.datenbank.masterie_belegt(spieler_id, masterie_1):
            return {"erfolg": False, "nachricht": "Masterie bereits vergeben"}

        if self.datenbank.spieler_hat_charaktere(spieler_id) >= 6:
            return {"erfolg": False, "nachricht": "Maximal 6 Charaktere pro Spieler"}

        charakter_id = self.datenbank.charakter_erstellen(spieler_id, name, masterie_1, stats)
        if charakter_id:
            return {"erfolg": True, "charakter_id": charakter_id, "nachricht": "Charakter erstellt"}
        else:
            return {"erfolg": False, "nachricht": "Name bereits vergeben"}

    def charaktere_laden(self, spieler_id: int) -> list:
        return self.datenbank.charaktere_laden(spieler_id)

    def charakter_laden(self, charakter_id: int):
        return self.datenbank.charakter_laden(charakter_id)

    def _name_valid(self, name: str) -> bool:
        if len(name) < 3 or len(name) > 20:
            return False
        return bool(re.match(r"^[a-zA-Z0-9 ÄÖÜäöüß]+$", name))

    def _stats_valid(self, stats: dict) -> bool:
        required_stats = ["staerke", "vitalitaet", "weisheit", "glueck", "beweglichkeit", "charisma"]
        if not all(s in stats for s in required_stats):
            return False

        summe = sum(stats.values())
        if summe != 80:
            return False

        for wert in stats.values():
            if wert < 10 or wert > 25:
                return False

        return True