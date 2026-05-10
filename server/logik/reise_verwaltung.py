"""
server/logik/reise_verwaltung.py - Offline-Reisen Verwaltung

Abhängigkeiten: datetime, random, json
"""

import random
import json
from datetime import datetime, timedelta


RARITAET_NORMAL = "normal"
RARITAET_SELTEN = "selten"
RARITAET_EPISCH = "episch"
RARITAET_LEGENDAER = "legendaer"

QUEST_NAMEN = {
    "normal": ["Goblin-Lager säubern", "Wölfe vertreiben", "Banditenpatrouille"],
    "selten": ["Trollbrücke befreien", "Verfluchter Friedhof", "Schmugglerhöhle"],
    "episch": ["Drachennest erkunden", "Nekromanten-Turm", "Vergessene Ruinen"],
    "legendaer": ["Uralter Drache", "Lich-König", "Portal der Verdammnis"]
}

QUEST_BESCHREIBUNGEN = {
    "normal": ["Eine Gruppe Goblins terrorisiert die Umgebung.", "Wölfe haben sich niedergelassen."],
    "selten": ["Ein Troll blockiert die Brücke.", "Tote stehen nachts auf."],
    "episch": ["Ein Drache bewacht sein Nest.", "Nekromanten experimentieren."],
    "legendaer": ["Ein uraltes Böses erwacht.", "Das Portal zur Verdammnis öffnet sich."]
}


class ReiseVerwaltung:
    def __init__(self, datenbank, quest_generator, kampf_engine_klasse):
        self.datenbank = datenbank
        self.quest_generator = quest_generator
        self.kampf_engine_klasse = kampf_engine_klasse

    def _raritaet_wuerfeln(self):
        wuerf = random.random()
        if wuerf < 0.03:
            return RARITAET_LEGENDAER
        elif wuerf < 0.15:
            return RARITAET_EPISCH
        elif wuerf < 0.40:
            return RARITAET_SELTEN
        return RARITAET_NORMAL

    def _quest_generieren(self, charakter_level: int) -> dict:
        raritaet = self._raritaet_wuerfeln()
        basis = charakter_level * 10
        if raritaet == RARITAET_LEGENDAER:
            gold = int(basis * 5.0 * random.uniform(0.9, 1.1))
            xp = int(gold * 2.5)
            schwierigkeit = 4.0
        elif raritaet == RARITAET_EPISCH:
            gold = int(basis * 2.5 * random.uniform(0.9, 1.1))
            xp = int(gold * 2.0)
            schwierigkeit = 3.0
        elif raritaet == RARITAET_SELTEN:
            gold = int(basis * 1.2 * random.uniform(0.9, 1.1))
            xp = int(gold * 1.8)
            schwierigkeit = 2.0
        else:
            gold = int(basis * 0.6 * random.uniform(0.9, 1.1))
            xp = int(gold * 1.5)
            schwierigkeit = 1.0
        return {
            "name": random.choice(QUEST_NAMEN[raritaet]),
            "beschreibung": random.choice(QUEST_BESCHREIBUNGEN[raritaet]),
            "raritaet": raritaet,
            "schwierigkeit": schwierigkeit,
            "gold_belohnung": gold,
            "xp_belohnung": xp,
            "charakter_level": charakter_level
        }

    def reise_starten(self, charakter_id: int, charakter_level: int, max_dauer: int = 14400) -> dict:
        reise_id = self.datenbank.reise_starten(charakter_id, max_dauer)
        if reise_id is None:
            return {"erfolg": False, "nachricht": "Bereits auf Reisen"}
        quest = self._quest_generieren(charakter_level)
        jetzt = datetime.now()
        quest_zeit = jetzt + timedelta(minutes=random.randint(30, 60))
        self.datenbank.reise_quest_hinzufuegen(reise_id, quest, quest_zeit.isoformat())
        return {"erfolg": True, "reise_id": reise_id}

    def reise_quests_berechnen(self, charakter_id: int, snapshot: dict) -> list[dict]:
        reise = self.datenbank.reise_laden(charakter_id)
        if not reise:
            return []
        jetzt = datetime.now()
        ergebnisse = []
        for quest in reise["quests"]:
            quest_zeit = datetime.fromisoformat(quest["quest_zeit"])
            if quest_zeit <= jetzt and quest["kampf_ergebnis_json"] is None:
                kampf_engine = self.kampf_engine_klasse()
                char_daten = {
                    "name": snapshot.get("name", "Held"),
                    "level": snapshot.get("level", 1),
                    "klassen_id": snapshot.get("klassen_id", ""),
                    "staerke": snapshot.get("staerke", 10),
                    "beweglichkeit": snapshot.get("beweglichkeit", 10),
                    "weisheit": snapshot.get("weisheit", 10),
                    "vitalitaet": snapshot.get("vitalitaet", 10),
                    "glueck": snapshot.get("glueck", 10),
                    "charisma": snapshot.get("charisma", 10),
                    "max_lebenspunkte": snapshot.get("max_lebenspunkte", 100),
                    "angriff": snapshot.get("angriff", 10),
                    "verteidigung": snapshot.get("verteidigung", 5),
                    "skills": snapshot.get("ausgeruestete_skills", [])
                }
                gegner_level = quest["quest_json"]["charakter_level"] + random.randint(-1, 2)
                gegner_name = quest["quest_json"]["name"]
                gegner = {
                    "name": gegner_name,
                    "level": max(1, gegner_level),
                    "staerke": 8 + gegner_level * 2,
                    "beweglichkeit": 8 + gegner_level,
                    "weisheit": 5,
                    "vitalitaet": 10 + gegner_level * 3,
                    "glueck": 5,
                    "charisma": 5,
                    "max_lebenspunkte": 30 + gegner_level * 15,
                    "angriff": 5 + gegner_level * 2,
                    "verteidigung": 2 + gegner_level
                }
                ergebnis = kampf_engine.kampf_berechnen(char_daten, gegner, char_daten["name"], gegner_name)
                gold = 0
                xp = 0
                if ergebnis.get("gewonnen"):
                    gold = quest["quest_json"]["gold_belohnung"]
                    xp = quest["quest_json"]["xp_belohnung"]
                self.datenbank.reise_quest_ergebnis_speichern(quest["id"], ergebnis, gold, xp)
                ergebnisse.append(ergebnis)
                letzte_quest_zeit = quest_zeit
                while True:
                    naechste_zeit = letzte_quest_zeit + timedelta(minutes=random.randint(30, 60))
                    if naechste_zeit > jetzt:
                        break
                    neue_quest = self._quest_generieren(quest["quest_json"]["charakter_level"])
                    self.datenbank.reise_quest_hinzufuegen(reise["id"], neue_quest, naechste_zeit.isoformat())
                    letzte_quest_zeit = naechste_zeit
        return ergebnisse

    def reise_status(self, charakter_id: int) -> dict:
        reise = self.datenbank.reise_laden(charakter_id)
        if not reise:
            return {"aktiv": False}
        jetzt = datetime.now()
        quests_abgeschlossen = 0
        naechste_in = 0
        offene_belohnungen = 0
        for quest in reise["quests"]:
            if quest["kampf_ergebnis_json"] is not None:
                quests_abgeschlossen += 1
            if quest["kampf_ergebnis_json"] and not quest["abgeholt"]:
                offene_belohnungen += 1
            if quest["kampf_ergebnis_json"] is None:
                quest_zeit = datetime.fromisoformat(quest["quest_zeit"])
                if quest_zeit > jetzt:
                    naechste_in = max(naechste_in, int((quest_zeit - jetzt).total_seconds()))
        return {
            "aktiv": True,
            "gestartet_am": reise["gestartet_am"],
            "max_dauer": reise.get("max_dauer", 14400),
            "quests_abgeschlossen": quests_abgeschlossen,
            "naechste_quest_in": naechste_in,
            "offene_belohnungen": offene_belohnungen
        }

    def reise_beenden(self, charakter_id: int) -> dict:
        reise = self.datenbank.reise_laden(charakter_id)
        if reise:
            self.datenbank.reise_beenden(reise["id"])
        return {"erfolg": True}