"""
server/logik/shop_generator.py - Shop-Generierung mit Items und Tränken

Abhängigkeiten: random, json
"""

import random
import json
from datetime import datetime, timedelta


ITEM_RARITAET_GEWICHTE = {
    "normal": 55,
    "magisch": 25,
    "selten": 12,
    "episch": 6,
    "legendaer": 2,
}

ITEM_PREIS_RANGE = {
    "normal": (10, 30),
    "magisch": (35, 65),
    "selten": (90, 150),
    "episch": (250, 350),
    "legendaer": (600, 1000),
}

TRANK_CHANCE = 0.15

TRANK_PREISE = {
    "klein": {"bonus": 0.10, "dauer": 86400},
    "mittel": {"bonus": 0.15, "dauer": 259200},
    "gross": {"bonus": 0.25, "dauer": 604800},
}

VERFUEGBARE_STATS = ["staerke", "vitalitaet", "weisheit", "glueck", "beweglichkeit", "charisma"]


class ShopGenerator:
    def __init__(self, item_generator, rng=None):
        self.item_generator = item_generator
        self.rng = rng or random.Random()

    def trank_anzahl_wuerfeln(self) -> int:
        wuerf = self.rng.random()
        if wuerf < 0.15:
            return 1
        elif wuerf < 0.70:
            return 2
        return 3

    def shop_generieren(self, charakter_level: int) -> list[dict]:
        angebote = []
        trank_anzahl = self.trank_anzahl_wuerfeln()
        trank_slots = self.rng.sample(range(12), min(trank_anzahl, 12))

        for slot in range(12):
            if slot in trank_slots:
                trank = self.trank_generieren(charakter_level)
                preis = self.trank_preis_berechnen(trank, charakter_level)
                angebote.append({
                    "slot": slot,
                    "typ": "trank",
                    "inhalt": trank,
                    "preis": preis
                })
            else:
                item = self.item_generator.item_generieren(
                    self.raritaet_wuerfeln(), charakter_level)
                preis = self.item_preis_berechnen(item, charakter_level)
                angebote.append({
                    "slot": slot,
                    "typ": "item",
                    "inhalt": item,
                    "preis": preis
                })

        return angebote

    def raritaet_wuerfeln(self) -> str:
        wuerf = self.rng.random() * 100
        kumuliert = 0
        for raritaet, gewicht in ITEM_RARITAET_GEWICHTE.items():
            kumuliert += gewicht
            if wuerf <= kumuliert:
                return raritaet
        return "normal"

    def item_preis_berechnen(self, item: dict, level: int) -> int:
        raritaet = item.get("raritaet", "normal")
        min_p, max_p = ITEM_PREIS_RANGE.get(raritaet, (10, 30))
        return int(self.rng.randint(min_p, max_p) * max(1, level / 5))

    def trank_generieren(self, charakter_level: int) -> dict:
        stat = self.rng.choice(VERFUEGBARE_STATS)
        stufe = self.rng.choices(
            ["klein", "mittel", "gross"],
            weights=[60, 30, 10])[0]
        daten = TRANK_PREISE[stufe]
        return {
            "stat": stat,
            "stufe": stufe,
            "bonus": daten["bonus"],
            "dauer": daten["dauer"],
        }

    def trank_preis_berechnen(self, trank: dict, level: int) -> int:
        basis = {"klein": 100, "mittel": 250, "gross": 500}
        return basis[trank["stufe"]] * max(1, level // 5 + 1)