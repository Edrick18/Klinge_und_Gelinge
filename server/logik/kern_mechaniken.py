"""
server/logik/kern_mechaniken.py - Kern-Mechaniken für Kämpfe

Jede Basis-Klasse hat eine eigene Kern-Mechanik die im Kampf aktiviert wird.
"""

import random


class KernMechanik:
    def __init__(self, rng: random.Random):
        self.rng = rng
        self.wert = 0
        self.maximum = 100

    def bei_eigenem_treffer(self, schaden: int) -> list[dict]:
        return []

    def bei_erhaltenem_treffer(self, schaden: int) -> list[dict]:
        return []

    def bei_skill_aktivierung(self, skill_id: str) -> list[dict]:
        return []

    def kampf_start(self) -> list[dict]:
        self.wert = 0
        return []

    def kampf_ende(self) -> None:
        self.wert = 0

    def aktueller_wert(self) -> int:
        return self.wert

    def schaden_multiplikator(self) -> float:
        return 1.0

    def atk_speed_bonus(self) -> float:
        return 0.0


class Rage(KernMechanik):
    maximum = 100
    berserk_aktiv = False
    berserk_timer = 0.0

    def bei_eigenem_treffer(self, schaden: int) -> list[dict]:
        self.wert = min(self.maximum, self.wert + 10)
        if self.wert >= 100 and not self.berserk_aktiv:
            self.berserk_aktiv = True
            return [{"typ": "kern_mechanik", "name": "Rage", "ereignis": "berserk_aktiv", "wert": self.wert}]
        return []

    def bei_erhaltenem_treffer(self, schaden: int) -> list[dict]:
        self.wert = min(self.maximum, self.wert + 5)
        return []

    def bei_skill_aktivierung(self, skill_id: str) -> list[dict]:
        if hasattr(self, 'treffer_bonus'):
            self.wert = min(self.maximum, self.wert + 5)
        return []

    def kampf_start(self) -> list[dict]:
        self.wert = 0
        self.berserk_aktiv = False
        self.berserk_timer = 0.0
        return []

    def kampf_ende(self) -> None:
        self.wert = 0
        self.berserk_aktiv = False

    def schaden_multiplikator(self) -> float:
        basis = 1.0 + (self.wert / 10) * 0.01
        if self.berserk_aktiv:
            basis += 0.20
        return basis

    def atk_speed_bonus(self) -> float:
        basis = (self.wert / 10) * 0.02
        if self.berserk_aktiv:
            basis += 0.10
        return basis


class SchildStapel(KernMechanik):
    maximum = 5

    def __init__(self, rng: random.Random):
        super().__init__(rng)
        self.stapel = 0

    def bei_erhaltenem_treffer(self, schaden: int) -> list[dict]:
        if self.stapel > 0:
            self.stapel -= 1
            return [{
                "typ": "kern_mechanik",
                "name": "SchildStapel",
                "ereignis": "treffer_absorbiert",
                "stapel": self.stapel,
                "schaden": 0
            }]
        return []

    def stapel_hinzufuegen(self, anzahl: int) -> list[dict]:
        self.stapel = min(self.maximum, self.stapel + anzahl)
        return [{
            "typ": "kern_mechanik",
            "name": "SchildStapel",
            "ereignis": "stapel_hinzugefuegt",
            "stapel": self.stapel
        }]

    def aktueller_wert(self) -> int:
        return self.stapel


class ElementarLadungen(KernMechanik):
    maximum = 3

    def __init__(self, rng: random.Random):
        super().__init__(rng)
        self.feuer = 0
        self.eis = 0
        self.blitz = 0

    def ladung_hinzufuegen(self, typ: str, anzahl: int) -> list[dict]:
        if typ == "feuer":
            self.feuer = min(self.maximum, self.feuer + anzahl)
        elif typ == "eis":
            self.eis = min(self.maximum, self.eis + anzahl)
        elif typ == "blitz":
            self.blitz = min(self.maximum, self.blitz + anzahl)

        kombinations_ereignisse = []

        if self.feuer >= 1 and self.eis >= 1:
            kombinations_ereignisse.append({
                "typ": "kern_mechanik",
                "name": "ElementarLadungen",
                "ereignis": "explosion",
                "schaden": 50,
                "beschreibung": "Feuer + Eis = Explosion"
            })
            self.feuer = 0
            self.eis = 0

        if self.eis >= 1 and self.blitz >= 1:
            kombinations_ereignisse.append({
                "typ": "kern_mechanik",
                "name": "ElementarLadungen",
                "ereignis": "schockfrost",
                "schaden": 40,
                "beschreibung": "Eis + Blitz = Schockfrost"
            })
            self.eis = 0
            self.blitz = 0

        if self.feuer >= 1 and self.blitz >= 1:
            kombinations_ereignisse.append({
                "typ": "kern_mechanik",
                "name": "ElementarLadungen",
                "ereignis": "plasma",
                "schaden": 45,
                "beschreibung": "Feuer + Blitz = Plasma"
            })
            self.feuer = 0
            self.blitz = 0

        return [{
            "typ": "kern_mechanik",
            "name": "ElementarLadungen",
            "ereignis": "ladung_hinzugefuegt",
            "feuer": self.feuer,
            "eis": self.eis,
            "blitz": self.blitz
        }] + kombinations_ereignisse

    def aktueller_wert(self) -> int:
        return self.feuer + self.eis + self.blitz


class FortuneStapel(KernMechanik):
    maximum = 10
    garantierter_krit = False

    def __init__(self, rng: random.Random):
        super().__init__(rng)
        self.stapel = 0

    def bei_krit(self) -> list[dict]:
        self.stapel = min(self.maximum, self.stapel + 1)
        if self.stapel >= 10:
            self.garantierter_krit = True
            self.stapel = 5
            return [{
                "typ": "kern_mechanik",
                "name": "FortuneStapel",
                "ereignis": "garantierter_krit",
                "stapel": self.stapel
            }]
        return []

    def bei_ausweichen(self) -> list[dict]:
        self.stapel = min(self.maximum, self.stapel + 2)
        if self.stapel >= 10:
            self.garantierter_krit = True
            self.stapel = 5
            return [{
                "typ": "kern_mechanik",
                "name": "FortuneStapel",
                "ereignis": "garantierter_krit",
                "stapel": self.stapel
            }]
        return []

    def kampf_start(self) -> list[dict]:
        self.stapel = 0
        self.garantierter_krit = False
        return []

    def aktueller_wert(self) -> int:
        return self.stapel


class ComboPlunkte(KernMechanik):
    maximum = 5
    verfall_timer = 0.0
    verfall_dauer = 6.0

    def bei_eigenem_treffer(self, schaden: int) -> list[dict]:
        self.wert = min(self.maximum, self.wert + 1)
        self.verfall_timer = 0.0
        return []

    def bei_skill_aktivierung(self, skill_id: str) -> list[dict]:
        self.wert = min(self.maximum, self.wert + 2)
        self.verfall_timer = 0.0
        return []

    def tick(self, delta_zeit: float) -> list[dict]:
        self.verfall_timer += delta_zeit
        if self.verfall_timer >= self.verfall_dauer:
            self.wert = 0
            self.verfall_timer = 0.0
            return [{
                "typ": "kern_mechanik",
                "name": "ComboPlunkte",
                "ereignis": "verfallen",
                "wert": 0
            }]
        return []

    def kampf_start(self) -> list[dict]:
        self.wert = 0
        self.verfall_timer = 0.0
        return []

    def kampf_ende(self) -> None:
        self.wert = 0


class EinflusStapel(KernMechanik):
    maximum = 8
    aktive_buffs = 0
    aktive_debuffs = 0
    dominanz_aktiv = False

    def __init__(self, rng: random.Random):
        super().__init__(rng)
        self.aktive_buffs = 0
        self.aktive_debuffs = 0

    def wert_berechnen(self) -> int:
        return self.aktive_buffs + self.aktive_debuffs

    def buff_hinzufuegen(self, anzahl: int = 1) -> list[dict]:
        self.aktive_buffs += anzahl
        ereignisse = []
        if self.aktive_buffs + self.aktive_debuffs >= 8 and not self.dominanz_aktiv:
            self.dominanz_aktiv = True
            ereignisse.append({
                "typ": "kern_mechanik",
                "name": "EinflusStapel",
                "ereignis": "dominanz_aktiv",
                "wert": self.wert_berechnen()
            })
        return ereignisse

    def debuff_hinzufuegen(self, anzahl: int = 1) -> list[dict]:
        self.aktive_debuffs += anzahl
        ereignisse = []
        if self.aktive_buffs + self.aktive_debuffs >= 8 and not self.dominanz_aktiv:
            self.dominanz_aktiv = True
            ereignisse.append({
                "typ": "kern_mechanik",
                "name": "EinflusStapel",
                "ereignis": "dominanz_aktiv",
                "wert": self.wert_berechnen()
            })
        return ereignisse

    def aktueller_wert(self) -> int:
        return self.wert_berechnen()

    def kampf_start(self) -> list[dict]:
        self.aktive_buffs = 0
        self.aktive_debuffs = 0
        self.dominanz_aktiv = False
        return []


def kern_mechanik_erstellen(klassen_id: str, rng: random.Random) -> KernMechanik:
    mapping = {
        "krieger": Rage,
        "waechter": SchildStapel,
        "zauberer": ElementarLadungen,
        "schicksalsritter": FortuneStapel,
        "schatten": ComboPlunkte,
        "herold": EinflusStapel,
    }
    klasse = mapping.get(klassen_id)
    if klasse:
        return klasse(rng)
    return KernMechanik(rng)