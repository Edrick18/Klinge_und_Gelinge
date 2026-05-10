"""
server/logik/shop_verwaltung.py - Shop-Verwaltung mit Items und Tränken

Abhängigkeiten: uuid, datetime, json
"""

import uuid
import random
from datetime import datetime, timedelta


TRANK_PREISE = {
    "klein": {"bonus": 0.10, "dauer": 86400},
    "mittel": {"bonus": 0.15, "dauer": 259200},
    "gross": {"bonus": 0.25, "dauer": 604800},
}


def reroll_kosten_berechnen(reroll_anzahl: int, level: int) -> int:
    if reroll_anzahl == 0:
        return level * 50
    if reroll_anzahl == 1:
        return level * 100
    if reroll_anzahl == 2:
        return level * 200
    basis = level * 200
    for _ in range(reroll_anzahl - 2):
        basis *= 2
    return basis


class ShopVerwaltung:
    def __init__(self, datenbank, item_generator):
        self.datenbank = datenbank
        self.item_generator = item_generator
        from server.logik.shop_generator import ShopGenerator
        self.shop_generator = ShopGenerator(item_generator, random.Random())

    def shop_daten_laden(self, charakter_id: int, charakter_level: int) -> dict:
        angebote = self.datenbank.shop_laden(charakter_id)
        if not angebote:
            gueltig_bis = self.datenbank.naechste_mitternacht()
            angebote = self.shop_generator.shop_generieren(charakter_level)
            angebote = self.datenbank.shop_generieren(charakter_id, angebote, gueltig_bis)
            angebote = self.datenbank.shop_laden(charakter_id)

        self.datenbank.abgelaufene_traenke_entfernen(charakter_id)
        aktive_traenke = self.datenbank.traeanke_laden(charakter_id)

        charakter = self.datenbank.charakter_laden(charakter_id)
        gold = charakter.get("gold", 0) if charakter else 0
        reroll_anzahl = self.datenbank.reroll_anzahl_laden(charakter_id)
        reroll_kosten = reroll_kosten_berechnen(reroll_anzahl, charakter_level)

        gueltig_bis = angebote[0]["gueltig_bis"] if angebote else self.datenbank.naechste_mitternacht()

        return {
            "angebote": angebote,
            "gold": gold,
            "reroll_anzahl": reroll_anzahl,
            "reroll_kosten": reroll_kosten,
            "gueltig_bis": gueltig_bis,
            "aktive_traenke": aktive_traenke
        }

    def shop_reroll(self, charakter_id: int, charakter_level: int, charakter_gold: int) -> dict:
        reroll_anzahl = self.datenbank.reroll_anzahl_laden(charakter_id)
        kosten = reroll_kosten_berechnen(reroll_anzahl, charakter_level)

        if charakter_gold < kosten:
            return {"erfolg": False, "nachricht": "Nicht genug Gold"}

        self.datenbank.gold_abziehen(charakter_id, kosten)

        gueltig_bis = self.datenbank.naechste_mitternacht()
        neue_angebote = self.shop_generator.shop_generieren(charakter_level)
        neue_angebote = self.datenbank.shop_generieren(charakter_id, neue_angebote, gueltig_bis)

        self.datenbank.reroll_erhoehen(charakter_id)

        charakter = self.datenbank.charakter_laden(charakter_id)
        gold_rest = charakter.get("gold", 0) if charakter else 0
        naechste_kosten = reroll_kosten_berechnen(reroll_anzahl + 1, charakter_level)

        return {
            "erfolg": True,
            "angebote": neue_angebote,
            "gold_rest": gold_rest,
            "naechste_kosten": naechste_kosten,
            "reroll_anzahl": reroll_anzahl + 1
        }

    def angebot_kaufen(self, charakter_id: int, slot: int, charakter_gold: int) -> dict:
        angebote = self.datenbank.shop_laden(charakter_id)
        angebot = next((a for a in angebote if a["slot"] == slot), None)

        if not angebot:
            return {"erfolg": False, "nachricht": "Angebot nicht gefunden"}

        preis = angebot["preis"]
        if charakter_gold < preis:
            return {"erfolg": False, "nachricht": "Nicht genug Gold"}

        self.datenbank.gold_abziehen(charakter_id, preis)

        if angebot["typ"] == "item":
            inventar_anzahl = self.datenbank.inventar_anzahl(charakter_id)
            if inventar_anzahl >= 20:
                self.datenbank.gold_abziehen(charakter_id, -preis)
                return {"erfolg": False, "nachricht": "Inventar voll (max 20 Items)"}

            item_id = str(uuid.uuid4())
            self.datenbank.item_hinzufuegen(charakter_id, item_id, angebot["inhalt"])

        elif angebot["typ"] == "trank":
            trank = angebot["inhalt"]
            aktive_anzahl = self.datenbank.aktive_trank_anzahl(charakter_id)
            if aktive_anzahl >= 3:
                self.datenbank.gold_abziehen(charakter_id, -preis)
                return {"erfolg": False, "nachricht": "Maximal 3 Tränke aktiv"}

            if self.datenbank.trank_aktiv_fuer_stat(charakter_id, trank["stat"]):
                self.datenbank.gold_abziehen(charakter_id, -preis)
                return {"erfolg": False, "nachricht": f"Bereits Trank für {trank['stat']} aktiv"}

            trank_id = str(uuid.uuid4())
            aktiv_bis = (datetime.now() + timedelta(seconds=trank["dauer"])).isoformat()
            self.datenbank.trank_hinzufuegen(charakter_id, trank_id, trank["stat"],
                                           trank["stufe"], trank["bonus"], aktiv_bis)

        self.datenbank.shop_angebot_kaufen(charakter_id, slot)

        charakter = self.datenbank.charakter_laden(charakter_id)
        gold_rest = charakter.get("gold", 0) if charakter else 0

        return {
            "erfolg": True,
            "nachricht": "Gekauft!",
            "gold_rest": gold_rest
        }