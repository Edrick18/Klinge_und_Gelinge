"""
server/logic/snapshot.py - Charakter-Snapshot für Kämpfe

Abhängigkeiten: server.datenbank.datenbank, spiel.systeme.stat_berechnung,
                 spiel.systeme.skill_definitionen
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from spiel.systeme.stat_berechnung import StatBerechnung
from spiel.systeme.skill_definitionen import skill_laden


class Snapshot:
    def __init__(self, datenbank):
        self.datenbank = datenbank

    def erstellen(self, charakter_id: int) -> dict | None:
        charakter = self.datenbank.charakter_laden(charakter_id)
        if not charakter:
            return None

        kampfwerte = StatBerechnung.alle_berechnen(charakter)

        cursor = self.datenbank.verbindung.cursor()
        cursor.execute("""
            SELECT cs.skill_id, cs.klassen_id, cs.skill_level,
                   cs.slot_typ, cs.slot_nummer
            FROM charakter_klassen_skills cs
            WHERE cs.charakter_id = ? AND cs.ausgeruestet = 1
            ORDER BY cs.slot_typ, cs.slot_nummer
        """, (charakter_id,))
        rows = cursor.fetchall()

        ausgeruestete_skills = {"aktiv": [None, None, None], "passiv": [None, None]}
        klassen_id = None

        for row in rows:
            skill_id, klasse_id, skill_level, slot_typ, slot_nummer = row
            if klassen_id is None:
                klassen_id = klasse_id
            skill_def = skill_laden(klasse_id, skill_id)
            eintrag = {
                "skill_id": skill_id,
                "slot": slot_nummer,
                "definition": skill_def,
                "skill_level": skill_level or 1
            }
            if slot_typ == "aktiv" and 1 <= slot_nummer <= 3:
                ausgeruestete_skills["aktiv"][slot_nummer - 1] = eintrag
            elif slot_typ == "passiv" and 1 <= slot_nummer <= 2:
                ausgeruestete_skills["passiv"][slot_nummer - 1] = eintrag

        return {
            **charakter,
            **kampfwerte,
            "klassen_id": klassen_id or charakter.get("masterie_1", "krieger"),
            "ausgeruestete_skills": ausgeruestete_skills,
            "ausgeruestete_items": {}
        }

    def erstellen_und_speichern(self, charakter_id: int) -> dict | None:
        snapshot = self.erstellen(charakter_id)
        if snapshot:
            self.datenbank.snapshot_speichern(charakter_id, snapshot)
        print(f"Snapshot erstellt für Charakter {charakter_id}: {snapshot is not None}")
        return snapshot

    def laden(self, charakter_id: int) -> dict | None:
        return self.datenbank.snapshot_laden(charakter_id)

    def aktualisieren(self, charakter_id: int) -> dict | None:
        return self.erstellen_und_speichern(charakter_id)