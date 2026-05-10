"""
spiel/systeme/stat_berechnung.py - Abgeleitete Stats berechnen

Abhängigkeiten: keine externen Dependencies
"""

class StatBerechnung:
    @staticmethod
    def alle_berechnen(charakter: dict) -> dict:
        staerke = charakter.get("staerke", 10)
        vitalitaet = charakter.get("vitalitaet", 10)
        weisheit = charakter.get("weisheit", 10)
        glueck = charakter.get("glueck", 10)
        beweglichkeit = charakter.get("beweglichkeit", 10)
        charisma = charakter.get("charisma", 10)
        level = charakter.get("level", 1)

        max_hp = int(vitalitaet * 10 * (1 + (level - 1) * 0.3))
        max_mana = int(weisheit * 8 * (1 + (level - 1) * 0.3))
        mana_regen = round(weisheit * 0.5, 1)

        physischer_schaden = staerke * 2
        magischer_schaden = weisheit * 2

        ruestung = int(vitalitaet * 1.5)

        ausweichen = min(round(beweglichkeit * 0.8, 1), 75.0)
        krit_chance = min(round(glueck * 0.5, 1), 50.0)
        krit_schaden = 150 + (glueck * 0.3)

        angriffsgeschwindigkeit = round(1.0 + (beweglichkeit * 0.02), 2)
        gold_bonus = round(charisma * 0.5, 1)

        return {
            "max_hp": max_hp,
            "max_mana": max_mana,
            "mana_regen": mana_regen,
            "physischer_schaden": physischer_schaden,
            "magischer_schaden": magischer_schaden,
            "ruestung": ruestung,
            "ausweichen": ausweichen,
            "krit_chance": krit_chance,
            "krit_schaden": round(krit_schaden, 1),
            "angriffsgeschwindigkeit": angriffsgeschwindigkeit,
            "gold_bonus": gold_bonus
        }

    @staticmethod
    def xp_fuer_naechstes_level(level: int) -> int:
        return int(100 * (level ** 1.5))

    @staticmethod
    def stats_mit_traenken(charakter: dict, traeenke: list[dict]) -> dict:
        from datetime import datetime
        jetzt = datetime.now().isoformat()
        stats_mit_bonus = {}
        for stat in ["staerke", "vitalitaet", "weisheit", "glueck", "beweglichkeit", "charisma"]:
            basis = charakter.get(stat, 10)
            gesamt_bonus = 0.0
            for trank in traeenke:
                if trank.get("stat") == stat and trank.get("aktiv_bis", "") > jetzt:
                    gesamt_bonus += trank.get("bonus", 0.0)
            stats_mit_bonus[stat] = int(basis * (1 + gesamt_bonus))
        stats_mit_bonus["level"] = charakter.get("level", 1)
        abgeleitete_stats = StatBerechnung.alle_berechnen(stats_mit_bonus)
        for key, value in abgeleitete_stats.items():
            stats_mit_bonus[key] = value
        return stats_mit_bonus


def schriftrollen_bonus(items: list[dict]) -> tuple[float, float]:
    from datetime import datetime
    jetzt = datetime.now().isoformat()
    xp_bonus = 0.0
    gold_bonus = 0.0
    for item in items:
        if item.get("typ") == "schriftrolle":
            dauer = item.get("dauer", 0)
            if dauer > 0:
                if item.get("effekt") == "xp_bonus":
                    xp_bonus += item.get("wert", 0.0)
                elif item.get("effekt") == "gold_bonus":
                    gold_bonus += item.get("wert", 0.0)
    return xp_bonus, gold_bonus