"""
server/logik/item_generator.py - Item-Generierung mit Rarität und Affixen
"""

import uuid
import random
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from spiel.systeme.item_typen import (
    ITEM_RARITAET_NORMAL, ITEM_RARITAET_MAGISCH, ITEM_RARITAET_SELTEN,
    ITEM_RARITAET_EPISCH, ITEM_RARITAET_LEGENDAER,
    PREFIXE, SUFFIXE, ADJEKTIVE, SLOT_TYP
)


ITEM_NAMEN = {
    "helm": ["Eiserner Helm", "Lederkappe", "Kriegshelm", "Mystischer Hut",
             "Drachenschuppe", "Schattenmaske"],
    "brust": ["Kettenhemd", "Lederrüstung", "Plattenrüstung", "Schattenweste",
              "Magiermantel", "Drachenpanzer"],
    "handschuhe": ["Eisenhandschuhe", "Lederhandschuhe", "Kampfhandschuhe",
                   "Schattenhandschuhe", "Magierfäustlinge"],
    "schuhe": ["Eisenstiefel", "Lederschuhe", "Kriegsstiefel",
               "Schattenstiefel", "Magiertreter"],
    "amulett": ["Bronzeamulett", "Silberamulett", "Goldamulett",
                "Mystisches Amulett", "Drachenamulett"],
    "ring_1": ["Bronzering", "Silberring", "Goldring", "Kampfring",
               "Schattenring"],
    "ring_2": ["Bronzering", "Silberring", "Goldring", "Kampfring",
               "Schattenring"],
    "waffe": ["Kurzschwert", "Streitaxt", "Kriegshammer", "Zauberstab",
              "Dolch", "Lanze", "Drachenschwert"],
    "offhand": ["Holzschild", "Eisenschild", "Turmschild", "Fokus",
                "Spellbook", "Parierklinge"],
}

BASIS_STATS_PRO_SLOT = {
    "helm": {"ruestung": (8, 20)},
    "brust": {"ruestung": (15, 40)},
    "handschuhe": {"ruestung": (6, 15)},
    "schuhe": {"ruestung": (6, 15)},
    "amulett": {},
    "ring_1": {},
    "ring_2": {},
    "waffe": {"physischer_schaden": (5, 25)},
    "offhand": {"ruestung": (5, 15), "blockchance": (5, 20)},
}

AFFIX_ANZAHL_PRO_RARITAET = {
    "normal": {"prefixe": 0, "suffixe": 0},
    "magisch": {"prefixe": 1, "suffixe": 1},
    "selten": {"prefixe": 2, "suffixe": 2},
    "episch": {"prefixe": 3, "suffixe": 3},
    "legendaer": {"prefixe": 4, "suffixe": 4},
}

QUEST_RARITAET_ITEM_CHANCE = {
    "normal": {"normal": 70, "magisch": 25, "selten": 5},
    "selten": {"normal": 40, "magisch": 40, "selten": 15, "episch": 5},
    "episch": {"magisch": 30, "selten": 40, "episch": 25, "legendaer": 5},
    "legendaer": {"selten": 30, "episch": 45, "legendaer": 25},
}


class ItemGenerator:
    def __init__(self, rng: random.Random = None):
        self.rng = rng or random.Random()

    def item_raritaet_wuerfeln(self, quest_raritaet: str) -> str:
        chance_dict = QUEST_RARITAET_ITEM_CHANCE.get(quest_raritaet, QUEST_RARITAET_ITEM_CHANCE["normal"])
        total = sum(chance_dict.values())
        wert = self.rng.randint(1, total)
        kumuliert = 0
        for raritaet, chance in chance_dict.items():
            kumuliert += chance
            if wert <= kumuliert:
                return raritaet
        return ITEM_RARITAET_NORMAL

    def _affix_wert_berechnen(self, raritaet: str, min_val: int, max_val: int) -> int:
        if raritaet == ITEM_RARITAET_MAGISCH:
            return self.rng.randint(min_val, int(max_val * 0.6))
        elif raritaet == ITEM_RARITAET_SELTEN:
            return self.rng.randint(int(min_val * 0.8), int(max_val * 0.8))
        elif raritaet == ITEM_RARITAET_EPISCH:
            return self.rng.randint(int(min_val * 1.0), int(max_val * 0.9))
        elif raritaet == ITEM_RARITAET_LEGENDAER:
            return self.rng.randint(int(max_val * 0.8), max_val)
        else:
            return self.rng.randint(min_val, int(max_val * 0.5))

    def item_generieren(self, quest_raritaet: str, charakter_level: int) -> dict:
        slot = self.rng.choice(["helm", "brust", "handschuhe", "schuhe",
                                 "amulett", "ring_1", "ring_2", "waffe", "offhand"])
        raritaet = self.item_raritaet_wuerfeln(quest_raritaet)
        level = charakter_level

        basis_stats = {}
        if slot in BASIS_STATS_PRO_SLOT:
            for stat_name, (stat_min, stat_max) in BASIS_STATS_PRO_SLOT[slot].items():
                basis_wert = self.rng.randint(stat_min, stat_max)
                basis_wert = int(basis_wert * (1 + level * 0.1))
                basis_stats[stat_name] = basis_wert

        prefixe = []
        suffixe = []

        affix_anzahl = AFFIX_ANZAHL_PRO_RARITAET.get(raritaet, {"prefixe": 0, "suffixe": 0})

        if affix_anzahl["prefixe"] > 0:
            verfuegbare_prefixe = list(PREFIXE.keys())
            self.rng.shuffle(verfuegbare_prefixe)
            for i in range(min(affix_anzahl["prefixe"], len(verfuegbare_prefixe))):
                prefix_typ = verfuegbare_prefixe[i]
                prefix_data = PREFIXE[prefix_typ]
                wert = self._affix_wert_berechnen(raritaet, prefix_data["min"], prefix_data["max"])
                prefixe.append({"typ": prefix_typ, "wert": wert, "einheit": prefix_data["einheit"]})

        if affix_anzahl["suffixe"] > 0:
            verfuegbare_suffixe = list(SUFFIXE.keys())
            self.rng.shuffle(verfuegbare_suffixe)
            for i in range(min(affix_anzahl["suffixe"], len(verfuegbare_suffixe))):
                suffix_typ = verfuegbare_suffixe[i]
                suffix_data = SUFFIXE[suffix_typ]
                wert = self._affix_wert_berechnen(raritaet, suffix_data["min"], suffix_data["max"])
                suffixe.append({"typ": suffix_typ, "wert": wert, "einheit": suffix_data["einheit"]})

        item_name = self.rng.choice(ITEM_NAMEN.get(slot, ["Unbekannt"]))
        if raritaet != ITEM_RARITAET_NORMAL:
            adjektiv = self.rng.choice(ADJEKTIVE)
            item_name = f"{adjektiv} {item_name}"

        return {
            "id": str(uuid.uuid4()),
            "name": item_name,
            "slot": slot,
            "typ": SLOT_TYP.get(slot, "unbekannt"),
            "raritaet": raritaet,
            "level": level,
            "basis_stats": basis_stats,
            "prefixe": prefixe,
            "suffixe": suffixe,
        }