"""
spiel/systeme/quest_typen.py - Quest-Konstanten und Typen
"""

RARITAET_NORMAL = "normal"
RARITAET_SELTEN = "selten"
RARITAET_EPISCH = "episch"
RARITAET_LEGENDAER = "legendaer"

RARITAET_FARBE = {
    "normal": (180, 180, 180),
    "selten": (80, 120, 220),
    "episch": (160, 80, 220),
    "legendaer": (220, 160, 40),
}

RARITAET_GEWICHT = {
    "normal": 60,
    "selten": 25,
    "episch": 12,
    "legendaer": 3,
}

QUEST_TIMER = {
    "normal": (180, 300),
    "selten": (300, 480),
    "episch": (480, 720),
    "legendaer": (720, 1200),
}

QUEST_SCHWIERIGKEIT = {
    "normal": (0.8, 1.2),
    "selten": (1.2, 1.6),
    "episch": (1.6, 2.0),
    "legendaer": (2.0, 2.5),
}

GOLD_MULTIPLIKATOR = {
    "normal": 1,
    "selten": 2,
    "episch": 4,
    "legendaer": 10,
}

XP_MULTIPLIKATOR = {
    "normal": 1,
    "selten": 2.5,
    "episch": 5,
    "legendaer": 12,
}

ITEM_DROP_CHANCE = {
    "normal": 0.10,
    "selten": 0.25,
    "episch": 0.50,
    "legendaer": 1.00,
}