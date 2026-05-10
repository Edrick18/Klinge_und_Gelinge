"""
server/logik/authentifizierung.py - Authentifizierung von Spielern

Abhängigkeiten: server.datenbank.datenbank
"""

import re

from server.datenbank.datenbank import Datenbank, passwort_hashen, passwort_pruefen


class Authentifizierung:
    def __init__(self, datenbank: Datenbank):
        self.datenbank = datenbank

    def registrieren(self, benutzername: str, passwort: str) -> dict:
        if not self._benutzername_valid(benutzername):
            return {"erfolg": False, "nachricht": "Benutzername muss 3-20 Zeichen haben und nur Buchstaben, Zahlen oder Unterstriche enthalten"}

        if len(passwort) < 6:
            return {"erfolg": False, "nachricht": "Passwort muss mindestens 6 Zeichen haben"}

        hashwert = passwort_hashen(passwort)
        if self.datenbank.spieler_erstellen(benutzername, hashwert):
            return {"erfolg": True, "nachricht": "Konto erstellt"}
        else:
            return {"erfolg": False, "nachricht": "Benutzername bereits vergeben"}

    def einloggen(self, benutzername: str, passwort: str) -> dict:
        spieler = self.datenbank.spieler_laden(benutzername)
        if not spieler:
            return {"erfolg": False, "nachricht": "Benutzername oder Passwort falsch"}

        if not passwort_pruefen(passwort, spieler["passwort_hash"]):
            return {"erfolg": False, "nachricht": "Benutzername oder Passwort falsch"}

        self.datenbank.letzten_login_aktualisieren(spieler["id"])
        return {"erfolg": True, "spieler_id": spieler["id"], "nachricht": "Willkommen"}

    def _benutzername_valid(self, name: str) -> bool:
        if len(name) < 3 or len(name) > 20:
            return False
        return bool(re.match(r"^[a-zA-Z0-9_]+$", name))