"""
spiel/systeme/item_typen.py - Item-Konstanten und Typen
"""

ITEM_RARITAET_NORMAL = "normal"
ITEM_RARITAET_MAGISCH = "magisch"
ITEM_RARITAET_SELTEN = "selten"
ITEM_RARITAET_EPISCH = "episch"
ITEM_RARITAET_LEGENDAER = "legendaer"

ITEM_RARITAET_FARBE = {
    "normal": (180, 180, 180),
    "magisch": (80, 120, 220),
    "selten": (220, 200, 40),
    "episch": (160, 80, 220),
    "legendaer": (220, 120, 40),
}

ITEM_SLOTS = [
    "helm", "brust", "handschuhe", "schuhe",
    "amulett", "ring_1", "ring_2", "waffe", "offhand"
]

SLOT_TYP = {
    "helm": "ruestung",
    "brust": "ruestung",
    "handschuhe": "ruestung",
    "schuhe": "ruestung",
    "amulett": "schmuck",
    "ring_1": "schmuck",
    "ring_2": "schmuck",
    "waffe": "waffe",
    "offhand": "offhand",
}

PREFIXE = {
    "staerke": {"min": 2, "max": 15, "einheit": ""},
    "vitalitaet": {"min": 2, "max": 15, "einheit": ""},
    "weisheit": {"min": 2, "max": 15, "einheit": ""},
    "glueck": {"min": 2, "max": 15, "einheit": ""},
    "beweglichkeit": {"min": 2, "max": 15, "einheit": ""},
    "charisma": {"min": 2, "max": 15, "einheit": ""},
    "physischer_schaden_bonus": {"min": 5, "max": 30, "einheit": "%"},
    "magischer_schaden_bonus": {"min": 5, "max": 30, "einheit": "%"},
    "max_hp_bonus": {"min": 10, "max": 80, "einheit": ""},
    "max_mana_bonus": {"min": 5, "max": 50, "einheit": ""},
}

SUFFIXE = {
    "krit_chance_bonus": {"min": 1, "max": 8, "einheit": "%"},
    "krit_schaden_bonus": {"min": 5, "max": 30, "einheit": "%"},
    "ausweichen_bonus": {"min": 1, "max": 8, "einheit": "%"},
    "mana_regen_bonus": {"min": 1, "max": 10, "einheit": ""},
    "gold_bonus": {"min": 5, "max": 25, "einheit": "%"},
    "xp_bonus": {"min": 3, "max": 15, "einheit": "%"},
    "angriffsgeschwindigkeit_bonus": {"min": 2, "max": 15, "einheit": "%"},
    "ruestung_bonus": {"min": 5, "max": 30, "einheit": "%"},
}

ADJEKTIVE = ["Glänzend", "Verzaubert", "Gehärtet", "Mystisch",
            "Verflucht", "Heilig", "Uralt", "Verdorben"]