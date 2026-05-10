"""
server/logik/quest_generator.py - Quest-Generierung mit Rarität

Abhängigkeiten: uuid, random, spiel.systeme.quest_typen
"""

import uuid
import random
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from spiel.systeme.quest_typen import (
    RARITAET_NORMAL, RARITAET_SELTEN, RARITAET_EPISCH, RARITAET_LEGENDAER,
    RARITAET_GEWICHT, QUEST_TIMER, QUEST_SCHWIERIGKEIT,
    GOLD_MULTIPLIKATOR, XP_MULTIPLIKATOR, ITEM_DROP_CHANCE
)


QUEST_NAMEN = {
    "normal": [
        "Goblin-Lager säubern", "Wölfe vertreiben", "Banditenpatrouille",
        "Rattenplage im Keller", "Verlorene Handelsware"
    ],
    "selten": [
        "Trollbrücke befreien", "Verfluchter Friedhof", "Schmugglerhöhle",
        "Entführte Händler", "Oger-Territorium"
    ],
    "episch": [
        "Drachennest erkunden", "Nekromanten-Turm", "Vergessene Ruinen",
        "Dämonenbeschwörung stoppen", "Antikes Labyrinth"
    ],
    "legendaer": [
        "Uralter Drache", "Lich-König", "Portal der Verdammnis",
        "Gefallener Halbgott", "Endloses Dungeon"
    ]
}

QUEST_BESCHREIBUNGEN = {
    "normal": [
        "Eine Gruppe Goblins terrorisiert die Umgebung.",
        "Wölfe haben sich in der Nähe des Dorfes niedergelassen.",
        "Banditen überfallen Reisende auf der Straße.",
        "Ratten im Keller machen das Wirtshaus unsicher.",
        "Ein Händler hat seine Ware verloren."
    ],
    "selten": [
        "Ein Troll blockiert die einzige Brücke.",
        "Tote stehen nachts aus dem Friedhof auf.",
        "Schmuggler haben eine geheime Höhle.",
        "Händler wurden entführt und gefangen gehalten.",
        "Ein Oger hat sein Territorium erweitert."
    ],
    "episch": [
        "Ein Jungdrache hat sein Nest in der Nähe.",
        "Ein Nekromant experimentiert mit dunkler Magie.",
        "Ruinen aus längst vergessener Zeit.",
        "Dämonen werden in einen ritual beschworen.",
        "Ein Labyrinth aus der Vorzeit."
    ],
    "legendaer": [
        "Der älteste aller Drachen wurde geweckt.",
        "Ein mächtiger Lich hat die Kontrolle übernommen.",
        "Ein Portal zur Hölle wurde geöffnet.",
        "Ein gefallener Gott erhebt sich.",
        "Ein Dungeon ohne Ende."
    ]
}


class QuestGenerator:
    def __init__(self, rng: random.Random = None):
        self.rng = rng or random.Random()

    def raritaet_wuerfeln(self) -> str:
        total = sum(RARITAET_GEWICHT.values())
        wert = self.rng.randint(1, total)
        kumuliert = 0
        for raritaet, gewicht in RARITAET_GEWICHT.items():
            kumuliert += gewicht
            if wert <= kumuliert:
                return raritaet
        return RARITAET_NORMAL

    def quest_generieren(self, spieler_id: int, charakter_id: int, charakter_level: int) -> dict:
        raritaet = self.raritaet_wuerfeln()

        schwierigkeit_min, schwierigkeit_max = QUEST_SCHWIERIGKEIT[raritaet]
        schwierigkeit = self.rng.uniform(schwierigkeit_min, schwierigkeit_max)

        timer_min, timer_max = QUEST_TIMER[raritaet]
        timer_sekunden = self.rng.randint(timer_min, timer_max)

        basis = charakter_level * 10
        gold = int(basis * GOLD_MULTIPLIKATOR[raritaet] * self.rng.uniform(0.8, 1.2))

        xp = int(basis * XP_MULTIPLIKATOR[raritaet] * self.rng.uniform(0.8, 1.2))

        item_chance = ITEM_DROP_CHANCE[raritaet]

        namen = QUEST_NAMEN[raritaet]
        beschreibungen = QUEST_BESCHREIBUNGEN[raritaet]

        return {
            "id": str(uuid.uuid4()),
            "spieler_id": spieler_id,
            "charakter_id": charakter_id,
            "name": self.rng.choice(namen),
            "beschreibung": self.rng.choice(beschreibungen),
            "raritaet": raritaet,
            "schwierigkeit": round(schwierigkeit, 2),
            "timer_sekunden": timer_sekunden,
            "gestartet_am": None,
            "gold_belohnung": gold,
            "xp_belohnung": xp,
            "item_drop_chance": item_chance,
            "abgeschlossen": False,
            "ergebnis": None
        }

    def drei_quests_generieren(self, spieler_id: int, charakter_id: int, charakter_level: int) -> list:
        quests = []
        legendaer_count = 0

        while len(quests) < 3:
            quest = self.quest_generieren(spieler_id, charakter_id, charakter_level)

            if quest["raritaet"] == RARITAET_LEGENDAER:
                if legendaer_count >= 1:
                    quest["raritaet"] = RARITAET_EPISCH
                else:
                    legendaer_count += 1

            quests.append(quest)

        return quests

        return quests