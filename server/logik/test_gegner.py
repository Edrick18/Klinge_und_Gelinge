"""
server/logik/test_gegner.py - Testgegner für Debug-Kämpfe

Abhängigkeiten: keine externen Dependencies
"""


def testkampfer_erstellen(level: int) -> dict:
    return {
        "name": f"Testgegner (Lvl {level})",
        "max_hp": 80 + level * 20,
        "max_mana": 50 + level * 10,
        "physischer_schaden": 8 + level * 3,
        "magischer_schaden": 5 + level * 2,
        "angriffsgeschwindigkeit": 1.0,
        "ruestung": 5 + level * 2,
        "ausweichen": 5.0,
        "krit_chance": 5.0,
        "krit_schaden": 150.0,
        "gold_bonus": 0
    }


def faeule_testkampfer_erstellen(level: int) -> dict:
    return {
        "name": f"Fäule-Testgegner (Lvl {level})",
        "max_hp": 500,
        "max_mana": 50 + level * 10,
        "physischer_schaden": 5,
        "magischer_schaden": 5 + level * 2,
        "angriffsgeschwindigkeit": 1.0,
        "ruestung": 5 + level * 2,
        "ausweichen": 5.0,
        "krit_chance": 5.0,
        "krit_schaden": 150.0,
        "gold_bonus": 0
    }