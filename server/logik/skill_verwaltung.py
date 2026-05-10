"""
server/logik/skill_verwaltung.py - Skill-Verwaltung

Verwaltet Klassen, Skill-Bäume, Punkt-Investitionen und Skill-Ausrüstung.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from spiel.systeme.skill_definitionen import (
    basis_klasse_laden,
    spezialisierung_laden,
    klassen_index_laden,
    spezialisierungen_fuer_basis,
    node_laden,
    skill_laden
)


class SkillVerwaltung:
    GRUNDWERT_ZU_KLASSE = {
        "staerke":       "krieger",
        "vitalitaet":    "waechter",
        "weisheit":      "zauberer",
        "glueck":        "schicksalsritter",
        "beweglichkeit": "schatten",
        "charisma":      "herold"
    }

    def __init__(self, datenbank):
        self.datenbank = datenbank

    def charakter_initialisieren(self, charakter_id: int, klassen_id: str):
        echter_name = self.GRUNDWERT_ZU_KLASSE.get(klassen_id, klassen_id)
        self.datenbank.klasse_hinzufuegen(charakter_id, echter_name, "basis")

    def spezialisierung_waehlen(self, charakter_id: int, spez_id: str, charakter_level: int) -> dict:
        if charakter_level < 25:
            return {"erfolg": False, "nachricht": "Spezialisierung erst ab Level 25 wählbar"}

        klassen = self.datenbank.klassen_laden(charakter_id)
        if not klassen:
            return {"erfolg": False, "nachricht": "Keine Basis-Klasse gefunden"}

        basis_id = klassen[0].get("klassen_id")
        if not basis_id:
            return {"erfolg": False, "nachricht": "Keine Basis-Klasse gefunden"}

        index = klassen_index_laden()
        basis_eintrag = index["basis_klassen"].get(basis_id)
        if not basis_eintrag:
            return {"erfolg": False, "nachricht": "Basis-Klasse nicht im Index"}

        if spez_id not in basis_eintrag["spezialisierungen"]:
            return {"erfolg": False, "nachricht": "Spezialisierung gehört nicht zur Basis-Klasse"}

        for klasse in klassen:
            if klasse.get("typ") == "spezialisierung":
                return {"erfolg": False, "nachricht": "Spezialisierung bereits gewählt"}

        spez_daten = spezialisierung_laden(spez_id)
        if not spez_daten or not spez_daten.get("skill_baum"):
            return {"erfolg": False, "nachricht": "Spezialisierung nicht gefunden oder unvollständig"}

        self.datenbank.klasse_hinzufuegen(charakter_id, spez_id, "spezialisierung")
        return {"erfolg": True, "nachricht": f"{spez_daten.get('name', 'Spezialisierung')} gewählt"}

    def node_skillen(self, charakter_id: int, klassen_id: str, node_id: str) -> dict:
        try:
            node = node_laden(klassen_id, node_id)
            if not node:
                return {"erfolg": False, "nachricht": "Node nicht gefunden"}

            charakter = self.datenbank.charakter_laden(charakter_id)
            if not charakter or charakter.get("skill_punkte", 0) <= 0:
                return {"erfolg": False, "nachricht": "Keine Skill-Punkte verfügbar"}

            benoetigt = node.get("benoetigt", [])
            for vor_id in benoetigt:
                stufe = self.datenbank.node_stufe_laden(charakter_id, klassen_id, vor_id)
                if stufe < 1:
                    return {"erfolg": False, "nachricht": "Voraussetzung nicht erfüllt"}

            aktuelle_stufe = self.datenbank.node_stufe_laden(charakter_id, klassen_id, node_id)
            max_stufen = node.get("max_stufen", 1)
            if aktuelle_stufe >= max_stufen:
                return {"erfolg": False, "nachricht": "Maximale Stufe erreicht"}

            self.datenbank.node_skillen(charakter_id, klassen_id, node_id)
            self.datenbank.skill_punkte_reduzieren(charakter_id)

            freigeschaltet = None
            skill_id = node.get("schaltet_skill_frei")
            if skill_id:
                self.datenbank.skill_hinzufuegen(charakter_id, skill_id, klassen_id)
                freigeschaltet = skill_id

            return {
                "erfolg": True,
                "nachricht": f"{node.get('name')} auf Stufe {aktuelle_stufe + 1}",
                "freigeschaltet": freigeschaltet
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {"erfolg": False, "nachricht": str(e)}

    def skills_laden(self, charakter_id: int) -> dict:
        klassen = self.datenbank.klassen_laden(charakter_id)
        skills = self.datenbank.skills_laden(charakter_id)

        nodes = {}
        for klasse in klassen:
            klassen_id = klasse.get("klassen_id")
            if klassen_id:
                nodes[klassen_id] = self.datenbank.nodes_laden(charakter_id, klassen_id)

        skill_punkte = self.datenbank.skill_punkte_laden(charakter_id)
        ausgeruestet = self.datenbank.ausgeruestete_skills_laden(charakter_id)

        return {
            "klassen": klassen,
            "nodes": nodes,
            "skills": skills,
            "ausgeruestet": ausgeruestet,
            "skill_punkte": skill_punkte
        }

    def skill_ausruesten(self, charakter_id: int, skill_id: str, slot_typ: str, slot_nummer: int) -> dict:
        if not self.datenbank.skill_freigeschaltet(charakter_id, skill_id):
            return {"erfolg": False, "nachricht": "Skill nicht freigeschaltet"}

        skill = skill_laden(None, skill_id)
        if not skill:
            skill = {"typ": slot_typ, "mana_reserviert": 0}

        if skill.get("typ") != slot_typ:
            return {"erfolg": False, "nachricht": f"Skill ist {skill.get('typ')}, Slot ist {slot_typ}"}

        if slot_typ == "passiv":
            max_mana = self.datenbank.max_mana_laden(charakter_id)
            akt_reserviert = self.datenbank.passiv_reserviert_laden(charakter_id)
            neu_reserviert = akt_reserviert + (skill.get("mana_reserviert") or 0)
            if neu_reserviert > max_mana * 0.8:
                return {"erfolg": False, "nachricht": "Mana-Reservierung würde 80% überschreiten"}

        self.datenbank.skill_ausruesten(charakter_id, skill_id, slot_typ, slot_nummer)
        return {"erfolg": True, "nachricht": "Skill ausgerüstet"}

    def skill_ablegen(self, charakter_id: int, skill_id: str) -> dict:
        self.datenbank.skill_ablegen(charakter_id, skill_id)
        return {"erfolg": True}