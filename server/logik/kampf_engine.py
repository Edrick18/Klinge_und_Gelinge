"""
server/logik/kampf_engine.py - Server-seitige Kampf-Logik

Abhängigkeiten: random, spiel.systeme.kampf_typen, kern_mechaniken
"""

import random
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from spiel.systeme.kampf_typen import (
    EREIGNIS_ANGRIFF, EREIGNIS_KRIT, EREIGNIS_AUSGEWICHEN,
    EREIGNIS_TOD, EREIGNIS_FAULE, EREIGNIS_KAMPFENDE,
    EREIGNIS_SKILL_AKTIV, EREIGNIS_KERN_MECHANIK,
    EREIGNIS_STATUS_EFFEKT
)
from server.logik.kern_mechaniken import kern_mechanik_erstellen


class KampfEngine:
    def __init__(self, seed: int = None):
        self.rng = random.Random(seed)
        self.spieler_kern = None
        self.spieler_status_effekte = []
        self.gegner_status_effekte = []
        self.spieler_mana = 0
        self.spieler_max_mana = 0
        self.spieler_mana_regen = 0

    def kampf_berechnen(self, kaempfer_a: dict, kaempfer_b: dict, spieler_name: str = "Spieler", gegner_name: str = "Gegner") -> dict:
        hp_a = kaempfer_a.get("max_hp", 100)
        hp_b = kaempfer_b.get("max_hp", 100)
        hp_max_a = hp_a
        hp_max_b = hp_b

        zeit = 0.0
        ereignisse = []

        spieler_klasse = kaempfer_a.get("klassen_id", "")
        self.spieler_kern = kern_mechanik_erstellen(spieler_klasse, self.rng)
        kern_ereignisse = self.spieler_kern.kampf_start()
        ereignisse.extend(kern_ereignisse)

        self.spieler_mana = kaempfer_a.get("max_mana", 100)
        self.spieler_max_mana = kaempfer_a.get("max_mana", 100)
        self.spieler_mana_regen = kaempfer_a.get("mana_regen", 1.0)

        ausgeruestete_skills = kaempfer_a.get("ausgeruestete_skills", {})
        aktive_skills = ausgeruestete_skills.get("aktiv", [])
        passive_skills = ausgeruestete_skills.get("passiv", [])

        skill_cooldowns = {}
        for skill_eintrag in aktive_skills:
            if skill_eintrag:
                skill_id = skill_eintrag.get("skill_id")
                if skill_id:
                    skill_cooldowns[skill_id] = 0.0

        for skill_eintrag in passive_skills:
            if not skill_eintrag:
                continue
            skill_def = skill_eintrag.get("definition", {})
            mechanik = skill_def.get("mechanik", "")
            if mechanik == "stapel_schwelle_reduktion":
                skalierung = skill_def.get("skalierung", {})
                basis = skalierung.get("basis", 0)
                kaempfer_a["schaden_reduktion"] = kaempfer_a.get("schaden_reduktion", 0) + basis

        atk_a = kaempfer_a.get("angriffsgeschwindigkeit", 1.0)
        atk_b = kaempfer_b.get("angriffsgeschwindigkeit", 1.0)

        naechster_angriff_a = 1.0 / max(atk_a, 0.1)
        naechster_angriff_b = 1.0 / max(atk_b, 0.1)

        naechste_faule_zeit = 60.0
        faule_stufe = 0
        max_atk = 5.0
        while hp_a > 0 and hp_b > 0:
            naechstes_ereignis = min(naechster_angriff_a, naechster_angriff_b)
            if naechstes_ereignis <= 0:
                naechstes_ereignis = 0.01
            zeit += naechstes_ereignis
            naechster_angriff_a -= naechstes_ereignis
            naechster_angriff_b -= naechstes_ereignis

            self.spieler_mana = min(
                self.spieler_max_mana,
                self.spieler_mana + self.spieler_mana_regen * naechstes_ereignis
            )

            if hasattr(self.spieler_kern, 'tick'):
                verfall_ereignisse = self.spieler_kern.tick(naechstes_ereignis)
                ereignisse.extend(verfall_ereignisse)

            for skill_id in skill_cooldowns:
                skill_cooldowns[skill_id] = max(0, skill_cooldowns[skill_id] - naechstes_ereignis)

            status_ereignisse = self._status_effekte_ticken(
                self.spieler_status_effekte, "spieler", hp_a, hp_max_a, zeit)
            for se in status_ereignisse:
                if se.get("schaden", 0) > 0:
                    hp_a = max(0, hp_a - se["schaden"])
                ereignisse.append(se)

            gegner_status_ereignisse = self._status_effekte_ticken(
                self.gegner_status_effekte, "gegner", hp_b, hp_max_b, zeit)
            for se in gegner_status_ereignisse:
                if se.get("schaden", 0) > 0:
                    hp_b = max(0, hp_b - se["schaden"])
            ereignisse.extend(gegner_status_ereignisse)

            if zeit >= naechste_faule_zeit:
                faule_stufe += 1
                naechste_faule_zeit += 10.0

                atk_a = min(max_atk, atk_a + 0.2)
                atk_b = min(max_atk, atk_b + 0.2)

                kaempfer_a = {**kaempfer_a, "angriffsgeschwindigkeit": atk_a}
                kaempfer_b = {**kaempfer_b, "angriffsgeschwindigkeit": atk_b}

                ereignisse.append({
                    "typ": EREIGNIS_FAULE,
                    "zeit": round(zeit, 2),
                    "stufe": faule_stufe
                })

            if naechster_angriff_a <= 0.001:
                schaden = self._schaden_berechnen(kaempfer_a, kaempfer_b)
                hp_b = max(0, hp_b - schaden["wert"])

                kern_ereignisse = self.spieler_kern.bei_eigenem_treffer(schaden["wert"])
                ereignisse.extend(kern_ereignisse)

                ereignis = {
                    "typ": schaden["typ"],
                    "zeit": round(zeit, 2),
                    "angreifer": "spieler",
                    "ziel": "gegner",
                    "schaden": schaden["wert"],
                    "hp_danach": hp_b,
                    "hp_max": hp_max_b
                }
                if schaden["typ"] == EREIGNIS_AUSGEWICHEN:
                    ereignis["schaden"] = 0
                    ereignis["hp_danach"] = hp_b
                ereignisse.append(ereignis)

                for skill_eintrag in aktive_skills:
                    if not skill_eintrag:
                        continue
                    skill_id = skill_eintrag.get("skill_id")
                    skill_def = skill_eintrag.get("definition", {})
                    if not skill_id or not skill_def:
                        continue

                    cooldown = skill_def.get("cooldown", 10.0)
                    mana_kosten = skill_def.get("mana_kosten", 0)

                    if skill_cooldowns.get(skill_id, 0) <= 0 and self.spieler_mana >= mana_kosten:
                        skill_ereignisse = self._skill_anwenden(
                            skill_id, skill_def, kaempfer_a, kaempfer_b,
                            hp_a, hp_b, hp_max_a, hp_max_b, zeit)
                        for se in skill_ereignisse:
                            if se.get("ziel") == "gegner" and se.get("schaden", 0) > 0:
                                hp_b = max(0, hp_b - se["schaden"])
                            elif se.get("ziel") == "spieler" and se.get("heilung", 0) > 0:
                                hp_a = min(hp_max_a, hp_a + se["heilung"])
                        self.spieler_mana -= mana_kosten
                        skill_cooldowns[skill_id] = cooldown
                        kern_ev = self.spieler_kern.bei_skill_aktivierung(skill_id)
                        ereignisse.extend(skill_ereignisse)
                        ereignisse.extend(kern_ev)
                        break

                naechster_angriff_a = 1.0 / max(atk_a, 0.1)

            if hp_b <= 0:
                break

            if naechster_angriff_b <= 0.001:
                schaden = self._schaden_berechnen(kaempfer_b, kaempfer_a)
                hp_a = max(0, hp_a - schaden["wert"])

                ereignis = {
                    "typ": schaden["typ"],
                    "zeit": round(zeit, 2),
                    "angreifer": "gegner",
                    "ziel": "spieler",
                    "schaden": schaden["wert"],
                    "hp_danach": hp_a,
                    "hp_max": hp_max_a
                }
                if schaden["typ"] == EREIGNIS_AUSGEWICHEN:
                    ereignis["schaden"] = 0
                    ereignis["hp_danach"] = hp_a
                ereignisse.append(ereignis)

                naechster_angriff_b = 1.0 / max(atk_b, 0.1)

        if self.spieler_kern:
            self.spieler_kern.kampf_ende()

        gewonnen = hp_a > 0

        ereignisse.append({
            "typ": EREIGNIS_KAMPFENDE,
            "zeit": round(zeit, 2),
            "gewonnen": gewonnen,
            "dauer": round(zeit, 2)
        })

        return {
            "gewonnen": gewonnen,
            "dauer": round(zeit, 2),
            "ereignisse": ereignisse,
            "gold": 10 if gewonnen else 0,
            "xp": 25 if gewonnen else 5,
            "spieler_name": spieler_name,
            "gegner_name": gegner_name,
            "ausgeruestete_skills": kaempfer_a.get("ausgeruestete_skills", {})
        }

    def _schaden_berechnen(self, angreifer: dict, ziel: dict) -> dict:
        if self.rng.random() * 100 < ziel.get("ausweichen", 0):
            return {"wert": 0, "typ": EREIGNIS_AUSGEWICHEN}

        schaden = angreifer.get("physischer_schaden", 10)

        if self.spieler_kern:
            schaden = int(schaden * self.spieler_kern.schaden_multiplikator())

        ruestung = ziel.get("ruestung", 0)
        reduzierung = ruestung / (ruestung + 100)
        schaden = int(schaden * (1 - reduzierung))

        schaden_reduktion = ziel.get("schaden_reduktion", 0)
        schaden = int(schaden * (1 - schaden_reduktion / 100))

        if self.rng.random() * 100 < angreifer.get("krit_chance", 0):
            schaden = int(schaden * angreifer.get("krit_schaden", 150) / 100)
            typ = EREIGNIS_KRIT
        else:
            typ = EREIGNIS_ANGRIFF

        return {"wert": max(1, schaden), "typ": typ}

    def _skill_anwenden(self, skill_id, skill_def, angreifer, ziel,
                        hp_a, hp_b, hp_max_a, hp_max_b, zeit) -> list[dict]:
        ereignisse = []
        mechanik = skill_def.get("mechanik", "")
        skalierung = skill_def.get("skalierung", {})
        skill_level = 1
        multiplikator = skalierung.get("basis", 1.0) + (skill_level - 1) * skalierung.get("pro_level", 0)

        schaden_basis = angreifer.get("physischer_schaden", 10)
        if skill_def.get("schaden_typ") == "magisch":
            schaden_basis = angreifer.get("magischer_schaden", 10)

        if self.spieler_kern:
            schaden_basis = int(schaden_basis * self.spieler_kern.schaden_multiplikator())

        if mechanik in ("rage_verbrauch", "basis_schaden"):
            schaden = int(schaden_basis * multiplikator)
            ruestung = ziel.get("ruestung", 0)
            reduzierung = ruestung / (ruestung + 100)
            schaden = max(1, int(schaden * (1 - reduzierung)))
            ereignisse.append({
                "typ": EREIGNIS_SKILL_AKTIV,
                "zeit": round(zeit, 2),
                "angreifer": "spieler",
                "ziel": "gegner",
                "skill_id": skill_id,
                "skill_name": skill_def.get("name", skill_id),
                "schaden": schaden,
                "hp_danach": max(0, hp_b - schaden),
                "hp_max": hp_max_b,
                "mana_danach": int(self.spieler_mana),
                "mana_max": self.spieler_max_mana,
            })

        elif mechanik == "stapel_erzeugen":
            stapel = skill_def.get("stapel", 1)
            kern_ev = self.spieler_kern.stapel_hinzufuegen(stapel) if hasattr(
                self.spieler_kern, 'stapel_hinzufuegen') else []
            ereignisse.extend(kern_ev)

        elif mechanik == "rage_alles_verbrauch":
            rage = self.spieler_kern.wert if self.spieler_kern else 0
            schaden = int(schaden_basis * multiplikator * (rage / 100 + 1))
            ruestung = ziel.get("ruestung", 0)
            reduzierung = ruestung / (ruestung + 100)
            schaden = max(1, int(schaden * (1 - reduzierung)))
            if self.spieler_kern:
                self.spieler_kern.wert = 0
            ereignisse.append({
                "typ": EREIGNIS_SKILL_AKTIV,
                "zeit": round(zeit, 2),
                "angreifer": "spieler",
                "ziel": "gegner",
                "skill_id": skill_id,
                "skill_name": skill_def.get("name", skill_id),
                "schaden": schaden,
                "hp_danach": max(0, hp_b - schaden),
                "hp_max": hp_max_b,
                "mana_danach": int(self.spieler_mana),
                "mana_max": self.spieler_max_mana,
            })

        return ereignisse

    def _status_effekte_ticken(self, effekte: list, ziel_name: str,
                                hp, hp_max, zeit) -> list[dict]:
        ereignisse = []
        abgelaufen = []
        for effekt in effekte:
            effekt["naechster_tick"] = effekt.get("naechster_tick", 0) - 0.1
            effekt["dauer"] -= 0.1
            if effekt["naechster_tick"] <= 0:
                schaden = int(hp_max * effekt.get("wert", 0))
                effekt["naechster_tick"] = effekt.get("intervall", 2.0)
                ereignisse.append({
                    "typ": EREIGNIS_STATUS_EFFEKT,
                    "zeit": round(zeit, 2),
                    "ziel": ziel_name,
                    "effekt_typ": effekt["typ"],
                    "schaden": schaden,
                    "hp_danach": max(0, hp - schaden),
                    "hp_max": hp_max
                })
            if effekt["dauer"] <= 0:
                abgelaufen.append(effekt)
        for e in abgelaufen:
            effekte.remove(e)
        return ereignisse