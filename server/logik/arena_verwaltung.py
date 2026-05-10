"""
server/logik/arena_verwaltung.py - Arena-Verwaltung mit Kämpfen und Shop

Abhängigkeiten: uuid, random, datetime
"""

import uuid
import random
from datetime import datetime


RANG_GRENZEN = [
    (0, 99, "Bronze", "🥉"),
    (100, 299, "Silber", "🥈"),
    (300, 599, "Gold", "🥇"),
    (600, 999, "Platin", "💎"),
    (1000, 9999, "Diamant", "👑"),
]

SIEG_PUNKTE = 15
NIEDERLAGE_PUNKTE = 10


def rang_berechnen(punkte: int) -> dict:
    for min_p, max_p, name, symbol in RANG_GRENZEN:
        if min_p <= punkte <= max_p:
            return {"name": name, "symbol": symbol, "punkte": punkte, "naechster": max_p + 1}
    return {"name": "Diamant", "symbol": "👑", "punkte": punkte, "naechster": None}


ARENA_SHOP = {
    "erfahrungsschriftrolle": {"marken": 3, "typ": "schriftrolle", "effekt": "xp_bonus", "wert": 0.50, "dauer": 86400},
    "goldschriftrolle": {"marken": 3, "typ": "schriftrolle", "effekt": "gold_bonus", "wert": 0.25, "dauer": 86400},
    "waffenverzauberung": {"marken": 5, "typ": "verzauberung", "slot": "waffe"},
    "ruestungsverzauberung": {"marken": 5, "typ": "verzauberung", "slot": "ruestung"},
}


class ArenaVerwaltung:
    def __init__(self, datenbank, kampf_engine_klasse):
        self.datenbank = datenbank
        self.kampf_engine_klasse = kampf_engine_klasse

    def gegner_laden(self, charakter_id: int, charakter_level: int) -> list[dict]:
        snapshots = self.datenbank.arena_gegner_suchen(charakter_id, charakter_level)
        gegner_liste = []
        for snap in snapshots:
            stats = self.datenbank.arena_stats_laden(snap["charakter_id"])
            rang = rang_berechnen(stats["rang_punkte"])
            gegner_liste.append({
                **snap,
                "siege": stats["siege"],
                "niederlagen": stats["niederlagen"],
                "rang_punkte": stats["rang_punkte"],
                "rang": rang
            })
        return gegner_liste

    def kampf_starten(self, angreifer_id: int, verteidiger_id: int) -> dict:
        angreifer_snapshot = self.datenbank.snapshot_laden(angreifer_id)
        if not angreifer_snapshot:
            return {"erfolg": False, "nachricht": "Angreifer nicht gefunden"}

        verteidiger_snapshot = self.datenbank.snapshot_laden(verteidiger_id)
        if not verteidiger_snapshot:
            return {"erfolg": False, "nachricht": "Gegner nicht gefunden"}

        engine = self.kampf_engine_klasse()
        ergebnis = engine.kampf_berechnen(
            angreifer_snapshot, verteidiger_snapshot,
            angreifer_snapshot.get("name", "Spieler"),
            verteidiger_snapshot.get("name", "Gegner"))

        gewonnen = ergebnis.get("gewonnen", False)
        rang_delta = SIEG_PUNKTE if gewonnen else -NIEDERLAGE_PUNKTE

        if gewonnen:
            gold = random.randint(10, 30) * max(1, angreifer_snapshot.get("level", 1))
            xp = random.randint(15, 40) * max(1, angreifer_snapshot.get("level", 1))
            marken = random.randint(1, 3)
        else:
            gold = random.randint(2, 8) * max(1, angreifer_snapshot.get("level", 1))
            xp = random.randint(3, 10) * max(1, angreifer_snapshot.get("level", 1))
            marken = 0

        self.datenbank.arena_stats_aktualisieren(angreifer_id, rang_delta, gewonnen, gold, xp, marken)
        self.datenbank.arena_kampf_speichern(
            angreifer_id, verteidiger_id, 1 if gewonnen else 0, rang_delta, gold, xp, marken)
        self.datenbank.gold_hinzufuegen(angreifer_id, gold)
        self.datenbank.xp_hinzufuegen(angreifer_id, xp)

        aktuelle_stats = self.datenbank.arena_stats_laden(angreifer_id)
        rang = rang_berechnen(max(0, aktuelle_stats["rang_punkte"]))

        ergebnis["gold"] = gold
        ergebnis["xp"] = xp
        ergebnis["marken"] = marken
        ergebnis["rang_delta"] = rang_delta
        ergebnis["rang"] = rang
        ergebnis["erfolg"] = True
        ergebnis["nachricht"] = "Sieg!" if gewonnen else "Niederlage"

        return ergebnis

    def arena_shop_kaufen(self, charakter_id: int, artikel_id: str) -> dict:
        artikel = ARENA_SHOP.get(artikel_id)
        if not artikel:
            return {"erfolg": False, "nachricht": "Artikel nicht gefunden"}

        stats = self.datenbank.arena_stats_laden(charakter_id)
        if stats["ehrenmarken"] < artikel["marken"]:
            return {"erfolg": False, "nachricht": "Nicht genug Ehrenmarken"}

        self.datenbank.ehrenmarken_abziehen(charakter_id, artikel["marken"])

        if artikel["typ"] == "schriftrolle":
            schriftrolle = {
                "name": artikel_id,
                "typ": "schriftrolle",
                "effekt": artikel["effekt"],
                "wert": artikel["wert"],
                "dauer": artikel["dauer"],
                "raritaet": "selten"
            }
            item_id = str(uuid.uuid4())
            self.datenbank.item_hinzufuegen(charakter_id, item_id, schriftrolle)

        aktuelle_stats = self.datenbank.arena_stats_laden(charakter_id)
        return {"erfolg": True, "marken_rest": aktuelle_stats["ehrenmarken"], "nachricht": "Gekauft!"}

    def item_verzaubern(self, charakter_id: int, item_id: str) -> dict:
        cursor = self.datenbank.verbindung.cursor()
        cursor.execute("SELECT * FROM inventar WHERE id = ? AND charakter_id = ?", (item_id, charakter_id))
        item = cursor.fetchone()
        if not item:
            return {"erfolg": False, "nachricht": "Item nicht gefunden"}

        if self.datenbank.item_ist_verzaubert(item_id):
            return {"erfolg": False, "nachricht": "Item bereits verzaubert"}

        if self.datenbank.item_verzaubern(item_id, charakter_id):
            return {"erfolg": True, "nachricht": "Item verzaubert! +15% Stats"}
        return {"erfolg": False, "nachricht": "Verzauberung fehlgeschlagen"}