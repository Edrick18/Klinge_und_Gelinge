"""
server/logik/quest_verwaltung.py - Quest-Logik (annehmen, auflösen)

Abhängigkeiten: datetime, random, secrets
"""

import secrets
import random
from datetime import datetime
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.logik.quest_generator import QuestGenerator
from server.logik.test_gegner import testkampfer_erstellen
from server.logik.kampf_engine import KampfEngine


class QuestVerwaltung:
    def __init__(self, datenbank, kampf_engine_klasse=KampfEngine):
        self.datenbank = datenbank
        self.kampf_engine_klasse = kampf_engine_klasse
        self.generator = QuestGenerator()

    def quests_laden_oder_generieren(self, spieler_id: int, charakter_id: int, charakter_level: int) -> list:
        quests = self.datenbank.quests_laden(spieler_id, charakter_id)

        while len(quests) < 3:
            quest = self.generator.quest_generieren(spieler_id, charakter_id, charakter_level)
            self.datenbank.quest_speichern(quest)
            quests.append(quest)

        return quests[:3]

    def quest_annehmen(self, quest_id: str, spieler_id: int) -> dict:
        quest = self.datenbank.quest_laden(quest_id)
        if not quest:
            return {"erfolg": False, "nachricht": "Quest nicht gefunden"}

        if quest["spieler_id"] != spieler_id:
            return {"erfolg": False, "nachricht": "Quest gehört nicht dem Spieler"}

        if quest.get("gestartet_am"):
            return {"erfolg": False, "nachricht": "Quest bereits gestartet"}

        jetzt = datetime.now().isoformat()
        self.datenbank.quest_starten(quest_id, jetzt)

        quest["gestartet_am"] = jetzt
        return {"erfolg": True, "quest": quest}

    def quest_aufloesen(self, quest_id: str, spieler_id: int, charakter_snapshot: dict) -> dict:
        quest = self.datenbank.quest_laden(quest_id)
        if not quest:
            return {"erfolg": False, "nachricht": "Quest nicht gefunden"}

        if quest["spieler_id"] != spieler_id:
            return {"erfolg": False, "nachricht": "Quest gehört nicht dem Spieler"}

        if not quest.get("gestartet_am"):
            return {"erfolg": False, "nachricht": "Quest nicht gestartet"}

        gestartet = datetime.fromisoformat(quest["gestartet_am"])
        jetzt = datetime.now()
        verbleibend = (gestartet - jetzt).total_seconds() + quest["timer_sekunden"]

        if verbleibend > 0:
            return {"erfolg": False, "nachricht": f"Quest läuft noch {int(verbleibend)} Sekunden"}

        charakter_level = charakter_snapshot.get("level", 1)
        schwierigkeit = quest["schwierigkeit"]

        gegner_level = int(charakter_level * schwierigkeit)
        gegner = testkampfer_erstellen(gegner_level)
        gegner["max_hp"] = int(gegner["max_hp"] * schwierigkeit)
        gegner["name"] = f"{quest['name']} - Gegner"

        seed = secrets.randbits(32)
        engine = self.kampf_engine_klasse(seed=seed)

        spieler_name = charakter_snapshot.get("name", "Spieler")
        kampf_ergebnis = engine.kampf_berechnen(charakter_snapshot, gegner, spieler_name, gegner["name"])

        item_drop = None
        if kampf_ergebnis["gewonnen"]:
            drop_chance = quest["item_drop_chance"]
            rng_drop = random.Random(secrets.randbits(32))
            if rng_drop.random() < drop_chance:
                from server.logik.item_generator import ItemGenerator
                item_gen = ItemGenerator(rng_drop)
                item_drop = item_gen.item_generieren(quest["raritaet"], charakter_level)

        if kampf_ergebnis["gewonnen"]:
            ergebnis = "sieg"
            gold = quest["gold_belohnung"]
            xp = quest["xp_belohnung"]
        else:
            ergebnis = "niederlage"
            gold = 0
            xp = int(quest["xp_belohnung"] * 0.1)

        self.datenbank.quest_abschliessen(quest_id, ergebnis)

        charakter_id = quest["charakter_id"]
        self.datenbank.alle_quests_loeschen(spieler_id, charakter_id)

        neue_quests = self.generator.drei_quests_generieren(spieler_id, charakter_id, charakter_level)
        for q in neue_quests:
            self.datenbank.quest_speichern(q)

        return {
            "erfolg": True,
            "kampf_ergebnis": kampf_ergebnis,
            "gold": gold,
            "xp": xp,
            "neue_quests": neue_quests,
            "item_drop": item_drop
        }