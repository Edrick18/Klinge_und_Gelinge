"""
spiel/szenen/skill_szene.py - Skill-Baum Darstellung

Abhängigkeiten: pygame, config, basis_szene, skill_definitionen
"""

import pygame
import config
from ..kern.basis_szene import BasisSzene
from netzwerk.nachrichten import (
    SKILLS_LADEN, SKILLS_ANTWORT,
    NODE_SKILLEN, NODE_GESKILLT,
    SKILL_AUSRUESTEN, SKILL_AUSGERUESTET,
    SKILL_ABLEGEN, SKILL_ABGELEGT,
    SCHLUESSEL_KLASSEN_ID, SCHLUESSEL_NODE_ID,
    SCHLUESSEL_SKILL_ID, SCHLUESSEL_SKILL_SLOT
)
from spiel.systeme.skill_definitionen import (
    basis_klasse_laden,
    spezialisierung_laden,
    spezialisierungen_fuer_basis,
    skill_beschreibung_mit_level,
    beschreibung_generieren
)


class SkillSzene(BasisSzene):
    GRUNDWERT_ZU_KLASSE = {
        "staerke":       "krieger",
        "vitalitaet":    "waechter",
        "weisheit":      "zauberer",
        "glueck":        "schicksalsritter",
        "beweglichkeit": "schatten",
        "charisma":      "herold"
    }

    def __init__(self, szenen_manager, netzwerk_client, charakter_daten=None):
        self.szenen_manager = szenen_manager
        self.netzwerk_client = netzwerk_client
        self.charakter_daten = charakter_daten

        self.skill_daten = None
        self.aktiver_baum_id = None
        self.geladen = False
        self.status_nachricht = ""
        self.status_timer = 0.0
        self.ausgewaehlter_skill = None

        self._layout_berechnen()
        self.netzwerk_client.nachricht_senden(SKILLS_LADEN, {})

    def _layout_berechnen(self):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE

        self.schrift_klein = pygame.font.Font(None, max(12, int(h * 0.018)))
        self.schrift_normal = pygame.font.Font(None, max(16, int(h * 0.025)))
        self.schrift_titel = pygame.font.Font(None, max(24, int(h * 0.035)))

        self.baum_auswahl_x = int(b * 0.01)
        self.baum_auswahl_breite = int(b * 0.13)
        self.baum_auswahl_hoehe = int(h * 0.72)

        self.node_bereich_start_x = int(b * 0.16)
        self.node_bereich_breite = int(b * 0.82)
        self.node_bereich_start_y = int(h * 0.08)
        self.node_bereich_hoehe = int(h * 0.64)

        self.node_radius = int(b * 0.022)
        self.node_abstand_x = int(b * 0.12)
        self.node_abstand_y = int(h * 0.12)
        self.hover_node = None

        self.skill_leiste_y = int(h * 0.75)
        self.skill_leiste_hoehe = int(h * 0.15)

        self.skill_rechteck_breite = int(b * 0.07)
        self.skill_rechteck_hoehe = int(h * 0.12)
        self.skill_abstand = int(b * 0.008)

        self.unten_y = int(h * 0.93)
        self.zurueck_button = pygame.Rect(
            int(b * 0.02), self.unten_y - int(h * 0.04),
            int(b * 0.1), int(h * 0.035)
        )

        self.baum_buttons = []

    def events_verarbeiten(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._zurueck_zur_uebersicht()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.zurueck_button.collidepoint(event.pos):
                        self._zurueck_zur_uebersicht()
                        return

                    for btn in self.baum_buttons:
                        if btn["rect"].collidepoint(event.pos):
                            self.aktiver_baum_id = btn["klassen_id"]
                            return

                    if self.ausgewaehlter_skill:
                        if self._panel_klick_verarbeiten(event.pos):
                            return

                    if self._skill_leiste_klick(event.pos):
                        return

                    self._node_klick_verarbeiten(event.pos)

    def _zurueck_zur_uebersicht(self):
        from .charakter_uebersicht_szene import CharakterUebersichtSzene
        self.szenen_manager.szene_wechseln(CharakterUebersichtSzene(
            self.szenen_manager, self.netzwerk_client, self.charakter_daten
        ))

    def _panel_klick_verarbeiten(self, pos) -> bool:
        skill = self.ausgewaehlter_skill
        skill_id = skill.get("id")
        skill_typ = skill.get("typ", "aktiv")
        slots = [1, 2, 3] if skill_typ == "aktiv" else [1, 2]
        panel_x = int(config.AUFLOESUNG_BREITE * 0.75)
        panel_y = int(config.AUFLOESUNG_HOEHE * 0.08)
        panel_breite = int(config.AUFLOESUNG_BREITE * 0.23)
        panel_hoehe = int(config.AUFLOESUNG_HOEHE * 0.64)

        for i, slot in enumerate(slots):
            btn = pygame.Rect(panel_x + 10, panel_y + 160 + i * 45,
                              panel_breite - 20, 35)
            if btn.collidepoint(pos):
                print(f"Slot-Button geklickt: {skill_typ} Slot {slot}")
                self.netzwerk_client.nachricht_senden(SKILL_AUSRUESTEN, {
                    SCHLUESSEL_SKILL_ID: skill_id,
                    SCHLUESSEL_SKILL_SLOT: skill_typ,
                    "slot_nummer": slot
                })
                return True

        ablegen_btn = pygame.Rect(panel_x + 10, panel_y + panel_hoehe - 50,
                                   panel_breite - 20, 35)
        if ablegen_btn.collidepoint(pos):
            self.netzwerk_client.nachricht_senden(SKILL_ABLEGEN, {
                SCHLUESSEL_SKILL_ID: skill_id
            })
            return True

        return False

    def _skill_leiste_klick(self, pos) -> bool:
        klasse_daten = self._active_klasse_daten()
        skills = klasse_daten.get("skill_baum", {}).get("skills", [])
        anzahl = len(skills)
        if anzahl == 0:
            return False

        h = config.AUFLOESUNG_HOEHE
        gesamt_breite = anzahl * self.skill_rechteck_breite + (anzahl - 1) * self.skill_abstand
        start_x = self.node_bereich_start_x + (int(config.AUFLOESUNG_BREITE * 0.82) - gesamt_breite) // 2

        for i, skill in enumerate(skills):
            rect_x = start_x + i * (self.skill_rechteck_breite + self.skill_abstand)
            rect = pygame.Rect(rect_x,
                self.skill_leiste_y + int(h * 0.02),
                self.skill_rechteck_breite,
                self.skill_rechteck_hoehe)
            if rect.collidepoint(pos):
                self.ausgewaehlter_skill = skill
                return True
        return False

    def _node_klick_verarbeiten(self, pos):
        if not self.geladen or not self.aktiver_baum_id:
            return
        klasse_daten = self._active_klasse_daten()
        nodes = klasse_daten.get("skill_baum", {}).get("nodes", [])
        for node in nodes:
            npos = self._node_position(node)
            abstand = ((pos[0] - npos[0])**2 + (pos[1] - npos[1])**2) ** 0.5
            if abstand <= self.node_radius:
                self._node_skillen(node)
                break

    def updaten(self, delta_zeit: float):
        if self.status_nachricht:
            self.status_timer += delta_zeit
            if self.status_timer >= 3.0:
                self.status_nachricht = ""
                self.status_timer = 0.0

        if self.geladen and self.aktiver_baum_id:
            klasse_daten = self._active_klasse_daten()
            nodes = klasse_daten.get("skill_baum", {}).get("nodes", [])
            maus_pos = pygame.mouse.get_pos()
            self.hover_node = None
            for node in nodes:
                npos = self._node_position(node)
                abstand = ((maus_pos[0] - npos[0])**2 + (maus_pos[1] - npos[1])**2) ** 0.5
                if abstand <= self.node_radius:
                    self.hover_node = node
                    break

        while True:
            nachricht = self.netzwerk_client.nachricht_holen()
            if not nachricht:
                break
            typ = nachricht.get("typ")
            daten = nachricht.get("daten", {})
            print(f"Nachricht empfangen: {typ}")
            print(f"Daten: {daten}")
            if typ == SKILLS_ANTWORT:
                self.skill_daten = daten
                self.geladen = True
                if not self.aktiver_baum_id and self.skill_daten.get("klassen"):
                    self.aktiver_baum_id = self.skill_daten["klassen"][0]["klassen_id"]
                self._baum_buttons_aktualisieren()
            elif typ == NODE_GESKILLT:
                if daten.get("erfolg"):
                    freigeschaltet = daten.get("freigeschaltet")
                    if freigeschaltet:
                        self.status_nachricht = f"Skill freigeschaltet: {freigeschaltet}!"
                    else:
                        self.status_nachricht = "Node geskillt!"
                    self.netzwerk_client.nachricht_senden(SKILLS_LADEN, {})
                else:
                    self.status_nachricht = daten.get("nachricht", "Fehler!")

            elif typ == SKILL_AUSGERUESTET:
                self.status_nachricht = "Skill ausgerüstet!"
                self.netzwerk_client.nachricht_senden(SKILLS_LADEN, {})

            elif typ == SKILL_ABGELEGT:
                self.status_nachricht = "Skill abgelegt!"
                self.netzwerk_client.nachricht_senden(SKILLS_LADEN, {})

    def _baum_buttons_aktualisieren(self):
        self.baum_buttons = []
        if not self.skill_daten or not self.skill_daten.get("klassen"):
            return

        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE

        klassen = self.skill_daten["klassen"]
        anzahl = len(klassen)
        if anzahl == 0:
            return

        btn_hoehe = int(h * 0.055)
        btn_abstand = int(h * 0.008)
        gesamt_hoehe = anzahl * btn_hoehe + (anzahl - 1) * btn_abstand
        start_y = int(h * 0.1)

        for i, klasse in enumerate(klassen):
            klassen_id = klasse.get("klassen_id", "")
            klassen_name = self._klassen_name(klassen_id)
            btn_y = start_y + i * (btn_hoehe + btn_abstand)
            self.baum_buttons.append({
                "klassen_id": klassen_id,
                "name": klassen_name,
                "rect": pygame.Rect(
                    self.baum_auswahl_x + int(b * 0.005),
                    btn_y,
                    self.baum_auswahl_breite - int(b * 0.01),
                    btn_hoehe
                )
            })

    def _klassen_name(self, klassen_id: str) -> str:
        klassen_id = self.GRUNDWERT_ZU_KLASSE.get(klassen_id, klassen_id)
        if klassen_id in ["krieger", "waechter", "zauberer",
                          "schicksalsritter", "schatten", "herold"]:
            basis = basis_klasse_laden(klassen_id)
            if basis:
                return basis.get("name", klassen_id.capitalize())
        spez = spezialisierung_laden(klassen_id)
        if spez:
            return spez.get("name", klassen_id)
        return klassen_id.capitalize()

    def _node_position(self, node: dict) -> tuple:
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE
        pos = node.get("position", {})
        spalte = pos.get("spalte", 0)
        reihe = pos.get("reihe", 0)
        x = self.node_bereich_start_x + spalte * self.node_abstand_x + self.node_radius
        y = self.node_bereich_start_y + reihe * self.node_abstand_y + self.node_radius
        return (x, y)

    def _node_status(self, node_id: str, node: dict) -> str:
        if not self.skill_daten or not self.aktiver_baum_id:
            return "gesperrt"

        echter_klassen_id = self.GRUNDWERT_ZU_KLASSE.get(
            self.aktiver_baum_id, self.aktiver_baum_id)
        nodes_data = self.skill_daten.get("nodes", {}).get(echter_klassen_id, {})
        stufe = nodes_data.get(node_id, 0)

        if stufe > 0:
            max_stufen = node.get("max_stufen", 1)
            return "voll" if stufe >= max_stufen else "teilweise"

        # Keine Punkte mehr → alles was nicht voll ist wird ausgegraut
        skill_punkte = self.skill_daten.get("skill_punkte", 0)
        if skill_punkte <= 0:
            return "gesperrt"

        benoetigt = node.get("benoetigt", [])
        if not benoetigt:
            return "verfuegbar"

        for vor_id in benoetigt:
            vor_stufe = nodes_data.get(vor_id, 0)
            if vor_stufe == 0:
                return "gesperrt"

        return "verfuegbar"

    def _node_skillen(self, node: dict):
        node_id = node.get("id")
        status = self._node_status(node_id, node)

        if status not in ("verfuegbar", "teilweise"):
            self.status_nachricht = "Node gesperrt oder bereits voll!"
            return

        skill_punkte = self.skill_daten.get("skill_punkte", 0)
        if skill_punkte <= 0:
            self.status_nachricht = "Keine Punkte übrig!"
            return

        klassen_id = self.GRUNDWERT_ZU_KLASSE.get(
            self.aktiver_baum_id, self.aktiver_baum_id)

        self.netzwerk_client.nachricht_senden(NODE_SKILLEN, {
            SCHLUESSEL_KLASSEN_ID: klassen_id,
            SCHLUESSEL_NODE_ID: node_id
        })

    def _skill_status(self, skill_id: str) -> str:
        if not self.skill_daten:
            return "gesperrt"

        freigeschaltet = [s.get("skill_id") for s in self.skill_daten.get("skills", [])]
        if skill_id not in freigeschaltet:
            return "gesperrt"

        ausgeruestet = self.skill_daten.get("ausgeruestet", {})
        alle = ausgeruestet.get("aktiv", []) + ausgeruestet.get("passiv", [])
        if any(s.get("skill_id") == skill_id for s in alle):
            return "ausgeruestet"

        return "freigeschaltet"

    def _slot_belegt(self, slot_typ, slot_nummer) -> bool:
        ausgeruestet = self.skill_daten.get("ausgeruestet", {})
        liste = ausgeruestet.get(slot_typ, [])
        return any(s.get("slot") == slot_nummer for s in liste)

    def _skill_in_slot(self, skill_id, slot_typ, slot_nummer) -> bool:
        ausgeruestet = self.skill_daten.get("ausgeruestet", {})
        liste = ausgeruestet.get(slot_typ, [])
        return any(
            s.get("skill_id") == skill_id and s.get("slot") == slot_nummer
            for s in liste
        )

    def _skill_slot_info(self, skill_id: str) -> str | None:
        """Gibt Slot-Info zurueck wie 'A1' oder 'P2' fuer ausgeruestete Skills."""
        if not self.skill_daten:
            return None
        ausgeruestet = self.skill_daten.get("ausgeruestet", {})
        for slot_typ, prefix in [("aktiv", "A"), ("passiv", "P")]:
            liste = ausgeruestet.get(slot_typ, [])
            for slot in liste:
                if slot and slot.get("skill_id") == skill_id:
                    return f"{prefix}{slot.get('slot', '?')}"
        return None

    def _text_umbrechen(self, text, max_breite, font) -> list:
        woerter = text.split()
        zeilen = []
        aktuelle = ""
        for wort in woerter:
            test = aktuelle + (" " if aktuelle else "") + wort
            if font.size(test)[0] <= max_breite:
                aktuelle = test
            else:
                if aktuelle:
                    zeilen.append(aktuelle)
                aktuelle = wort
        if aktuelle:
            zeilen.append(aktuelle)
        return zeilen

    def _verfuegbare_baeume(self) -> list:
        if not self.skill_daten:
            return []
        return [k["klassen_id"] for k in self.skill_daten.get("klassen", [])]

    def _active_klasse_daten(self) -> dict:
        if not self.aktiver_baum_id:
            return {}
        klassen_id = self.GRUNDWERT_ZU_KLASSE.get(
            self.aktiver_baum_id, self.aktiver_baum_id)
        basis = basis_klasse_laden(klassen_id)
        if basis:
            return basis
        spez = spezialisierung_laden(klassen_id)
        if spez:
            return spez
        return {}

    def zeichnen(self, flaeche: pygame.Surface):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE

        if not self.geladen:
            lade_text = self.schrift_normal.render("Lade...", True, config.FARBE_TEXT)
            text_rect = lade_text.get_rect(center=(b // 2, h // 2))
            flaeche.blit(lade_text, text_rect)
            return

        flaeche.fill(config.FARBE_HINTERGRUND)

        self._baum_auswahl_zeichnen(flaeche)
        self._titel_zeichnen(flaeche)
        if self.status_nachricht:
            msg = self.schrift_normal.render(
                self.status_nachricht, True, config.FARBE_AKZENT)
            msg_rect = msg.get_rect(
                center=(config.AUFLOESUNG_BREITE // 2, int(config.AUFLOESUNG_HOEHE * 0.06)))
            flaeche.blit(msg, msg_rect)
        self._nodes_zeichnen(flaeche)
        self._skill_leiste_zeichnen(flaeche)
        self._ausruestungs_panel_zeichnen(flaeche)
        self._zurueck_button_zeichnen(flaeche)
        self._zeichnen(flaeche)

    def _baum_auswahl_zeichnen(self, flaeche: pygame.Surface):
        pygame.draw.rect(flaeche, config.FARBE_DUNKELGRAU, (
            self.baum_auswahl_x, int(config.AUFLOESUNG_HOEHE * 0.05),
            self.baum_auswahl_breite, self.baum_auswahl_hoehe
        ))

        for btn in self.baum_buttons:
            rand_farbe = config.FARBE_AKZENT if btn["klassen_id"] == self.aktiver_baum_id else config.FARBE_RAND
            pygame.draw.rect(flaeche, rand_farbe, btn["rect"], 2)

            text = self.schrift_normal.render(btn["name"], True, config.FARBE_TEXT)
            text_rect = text.get_rect(center=btn["rect"].center)
            flaeche.blit(text, text_rect)

    def _titel_zeichnen(self, flaeche: pygame.Surface):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE

        klassen_name = self._klassen_name(self.aktiver_baum_id) if self.aktiver_baum_id else "Skill-Baum"
        titel_text = self.schrift_titel.render(klassen_name, True, config.FARBE_TEXT)
        flaeche.blit(titel_text, (int(b * 0.2), int(h * 0.01)))

        skill_punkte = self.skill_daten.get("skill_punkte", 0) if self.skill_daten else 0
        punkte_text = self.schrift_normal.render(f"Punkte: {skill_punkte}", True, config.FARBE_AKZENT)
        flaeche.blit(punkte_text, (int(b * 0.75), int(h * 0.01)))

        klasse_daten = self._active_klasse_daten()
        if klasse_daten:
            kern_name = klasse_daten.get("kern_mechanik", {}).get("name", "")
            if kern_name:
                kern_text = self.schrift_klein.render(f"Kern: {kern_name}", True, config.FARBE_TEXT_GEDIMMT)
                flaeche.blit(kern_text, (int(b * 0.2), int(h * 0.07)))

    def _nodes_zeichnen(self, flaeche: pygame.Surface):
        klasse_daten = self._active_klasse_daten()
        if not klasse_daten:
            return

        nodes = klasse_daten.get("skill_baum", {}).get("nodes", [])
        if not nodes:
            return

        linien_farbe = []
        for node in nodes:
            benoetigt = node.get("benoetigt", [])
            for vor_id in benoetigt:
                vor_node = None
                for n in nodes:
                    if n.get("id") == vor_id:
                        vor_node = n
                        break
                if vor_node:
                    pos1 = self._node_position(vor_node)
                    pos2 = self._node_position(node)
                    status = self._node_status(vor_id, vor_node)
                    farbe = config.FARBE_AKZENT if status == "voll" else config.FARBE_RAND
                    pygame.draw.line(flaeche, farbe, pos1, pos2, 2)

        for node in nodes:
            node_id = node.get("id", "")
            pos = self._node_position(node)
            status = self._node_status(node_id, node)

            if status == "gesperrt":
                farbe = (50, 50, 50)
                text_farbe = config.FARBE_TEXT_GEDIMMT
            elif status == "verfuegbar":
                farbe = (80, 80, 80)
                text_farbe = config.FARBE_HINTERGRUND
            elif status == "voll":
                farbe = config.FARBE_AKZENT
                text_farbe = config.FARBE_HINTERGRUND
            elif status == "teilweise":
                farbe = config.FARBE_MANA
                text_farbe = config.FARBE_HINTERGRUND
            else:
                farbe = (80, 80, 80)
                text_farbe = config.FARBE_HINTERGRUND

            pygame.draw.circle(flaeche, farbe, pos, self.node_radius)

            if node.get("schaltet_skill_frei"):
                pygame.draw.circle(flaeche, config.FARBE_ERFOLG, pos, self.node_radius + 2, 2)

            name = node.get("name", "")[:12]
            name_text = self.schrift_klein.render(name, True, text_farbe)
            name_rect = name_text.get_rect(center=(pos[0], pos[1] - int(self.node_radius * 0.4)))
            flaeche.blit(name_text, name_rect)

            echter_klassen_id = self.GRUNDWERT_ZU_KLASSE.get(
                self.aktiver_baum_id, self.aktiver_baum_id)
            nodes_data = self.skill_daten.get("nodes", {}).get(echter_klassen_id, {})
            stufe = nodes_data.get(node_id, 0)
            max_stufen = node.get("max_stufen", 1)
            stufe_text = self.schrift_klein.render(f"{stufe}/{max_stufen}", True, text_farbe)
            stufe_rect = stufe_text.get_rect(center=(pos[0], pos[1] + int(self.node_radius * 0.5)))
            flaeche.blit(stufe_text, stufe_rect)

    def _skill_leiste_zeichnen(self, flaeche: pygame.Surface):
        h = config.AUFLOESUNG_HOEHE

        pygame.draw.rect(flaeche, config.FARBE_DUNKELGRAU, (
            self.node_bereich_start_x, self.skill_leiste_y,
            int(config.AUFLOESUNG_BREITE * 0.82), self.skill_leiste_hoehe
        ))

        klasse_daten = self._active_klasse_daten()
        if not klasse_daten:
            return

        skills = klasse_daten.get("skill_baum", {}).get("skills", [])
        if not skills:
            return

        anzahl = len(skills)
        gesamt_breite = anzahl * self.skill_rechteck_breite + (anzahl - 1) * self.skill_abstand
        start_x = self.node_bereich_start_x + (int(config.AUFLOESUNG_BREITE * 0.82) - gesamt_breite) // 2

        for i, skill in enumerate(skills):
            skill_id = skill.get("id", "")
            skill_typ = skill.get("typ", "aktiv")
            skill_name = skill.get("name", "")[:10]
            status = self._skill_status(skill_id)

            rect_x = start_x + i * (self.skill_rechteck_breite + self.skill_abstand)
            rect = pygame.Rect(rect_x, self.skill_leiste_y + int(h * 0.02),
                              self.skill_rechteck_breite, self.skill_rechteck_hoehe)

            if status == "ausgeruestet":
                rand_farbe = config.FARBE_AKZENT
                rand_stärke = 3
            elif status == "freigeschaltet":
                rand_farbe = config.FARBE_ERFOLG
                rand_stärke = 1
            else:
                rand_farbe = config.FARBE_RAND
                rand_stärke = 1
                text_farbe = config.FARBE_TEXT_GEDIMMT

            pygame.draw.rect(flaeche, config.FARBE_DUNKELGRAU, rect)
            pygame.draw.rect(flaeche, rand_farbe, rect, rand_stärke)

            typ_text = "A" if skill_typ == "aktiv" else "P"
            typ_farbe = config.FARBE_AKZENT if skill_typ == "aktiv" else config.FARBE_MANA
            typ_render = self.schrift_klein.render(typ_text, True, typ_farbe)
            flaeche.blit(typ_render, (rect.x + 4, rect.y + 4))

            if status == "gesperrt":
                name_text = self.schrift_klein.render("???", True, config.FARBE_TEXT_GEDIMMT)
            else:
                name_text = self.schrift_klein.render(skill_name, True, config.FARBE_TEXT)
            name_rect = name_text.get_rect(center=(rect.centerx, rect.centery - int(h * 0.01)))
            flaeche.blit(name_text, name_rect)

            # Slot-Nummer bei ausgeruesteten Skills zeigen
            if status == "ausgeruestet":
                slot_info = self._skill_slot_info(skill_id)
                if slot_info:
                    slot_text = self.schrift_klein.render(slot_info, True, config.FARBE_AKZENT)
                    slot_rect = slot_text.get_rect(center=(rect.centerx, rect.bottom - int(h * 0.012)))
                    flaeche.blit(slot_text, slot_rect)
            else:
                lvl_text = self.schrift_klein.render("Lvl 1" if status != "gesperrt" else "???",
                                                   True, config.FARBE_TEXT_GEDIMMT if status == "gesperrt" else config.FARBE_TEXT)
                lvl_rect = lvl_text.get_rect(center=(rect.centerx, rect.bottom - int(h * 0.015)))
                flaeche.blit(lvl_text, lvl_rect)

    def _ausruestungs_panel_zeichnen(self, flaeche: pygame.Surface):
        if not self.ausgewaehlter_skill:
            return

        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE
        panel_x = int(b * 0.75)
        panel_y = int(h * 0.08)
        panel_breite = int(b * 0.23)
        panel_hoehe = int(h * 0.64)

        pygame.draw.rect(flaeche, config.FARBE_PANEL,
            (panel_x, panel_y, panel_breite, panel_hoehe))
        pygame.draw.rect(flaeche, config.FARBE_RAND,
            (panel_x, panel_y, panel_breite, panel_hoehe), 1)

        skill = self.ausgewaehlter_skill
        skill_id = skill.get("id", "")
        skill_typ = skill.get("typ", "aktiv")
        status = self._skill_status(skill_id)

        skill_level = 1
        if hasattr(self, 'ausgeruestete_skills'):
            for slot_list in self.ausgeruestete_skills.values():
                for slot in slot_list:
                    if slot and slot.get("skill_id") == skill_id:
                        skill_level = slot.get("skill_level", 1)
                        break

        name = self.schrift_normal.render(skill.get("name", ""), True, config.FARBE_TEXT)
        flaeche.blit(name, (panel_x + 10, panel_y + 10))

        typ_farbe = config.FARBE_AKZENT if skill_typ == "aktiv" else config.FARBE_MANA
        typ_text = self.schrift_klein.render(
            f"{'Aktiv' if skill_typ == 'aktiv' else 'Passiv'}", True, typ_farbe)
        flaeche.blit(typ_text, (panel_x + 10, panel_y + 35))

        beschreibung = skill_beschreibung_mit_level(skill, skill_level)
        zeilen = self._text_umbrechen(beschreibung, panel_breite - 20, self.schrift_klein)
        for i, zeile in enumerate(zeilen[:4]):
            txt = self.schrift_klein.render(zeile, True, config.FARBE_TEXT_GEDIMMT)
            flaeche.blit(txt, (panel_x + 10, panel_y + 60 + i * 20))

        if status == "gesperrt":
            gesperrt = self.schrift_klein.render(
                "Noch nicht freigeschaltet", True, config.FARBE_HP)
            flaeche.blit(gesperrt, (panel_x + 10, panel_y + 150))
            return

        if skill_typ == "aktiv":
            slots = [1, 2, 3]
            slot_label = "Aktiv-Slot"
        else:
            slots = [1, 2]
            slot_label = "Passiv-Slot"

        for i, slot in enumerate(slots):
            btn = pygame.Rect(panel_x + 10, panel_y + 160 + i * 45,
                              panel_breite - 20, 35)
            belegt = self._slot_belegt(skill_typ, slot)
            skill_in_slot = self._skill_in_slot(skill_id, skill_typ, slot)

            if skill_in_slot:
                farbe_rand = config.FARBE_AKZENT
                rand_breite = 2
                label = f"{slot_label} {slot} ✓ Ausgerüstet"
            elif belegt:
                farbe_rand = config.FARBE_WARNUNG
                rand_breite = 1
                label = f"{slot_label} {slot} (belegt)"
            else:
                farbe_rand = config.FARBE_RAND
                rand_breite = 1
                label = f"In {slot_label} {slot} ausrüsten"

            pygame.draw.rect(flaeche, config.FARBE_PANEL, btn)
            pygame.draw.rect(flaeche, farbe_rand, btn, rand_breite)
            txt = self.schrift_klein.render(label, True, config.FARBE_TEXT)
            flaeche.blit(txt, txt.get_rect(center=btn.center))

        if status == "ausgeruestet":
            ablegen_btn = pygame.Rect(panel_x + 10, panel_y + panel_hoehe - 50,
                                       panel_breite - 20, 35)
            pygame.draw.rect(flaeche, config.FARBE_HP, ablegen_btn)
            txt = self.schrift_klein.render("Ablegen", True, config.FARBE_TEXT)
            flaeche.blit(txt, txt.get_rect(center=ablegen_btn.center))

    def _zurueck_button_zeichnen(self, flaeche: pygame.Surface):
        pygame.draw.rect(flaeche, config.FARBE_RAND, self.zurueck_button, 1)
        text = self.schrift_normal.render("← Zurück", True, config.FARBE_TEXT)
        text_rect = text.get_rect(center=self.zurueck_button.center)
        flaeche.blit(text, text_rect)

    def _tooltip_zeichnen(self, flaeche: pygame.Surface, node: dict):
        if not node:
            return
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE
        pos = self._node_position(node)

        beschreibung = beschreibung_generieren(node)
        name = node.get("name", "")
        max_stufen = node.get("max_stufen", 1)

        tooltip_breite = int(b * 0.20)
        tooltip_hoehe = int(h * 0.12)
        tooltip_x = min(pos[0] + self.node_radius + 5, b - tooltip_breite - 5)
        tooltip_y = max(5, pos[1] - tooltip_hoehe // 2)

        pygame.draw.rect(flaeche, config.FARBE_PANEL,
            (tooltip_x, tooltip_y, tooltip_breite, tooltip_hoehe))
        pygame.draw.rect(flaeche, config.FARBE_AKZENT,
            (tooltip_x, tooltip_y, tooltip_breite, tooltip_hoehe), 1)

        name_txt = self.schrift_klein.render(name, True, config.FARBE_AKZENT)
        flaeche.blit(name_txt, (tooltip_x + 8, tooltip_y + 6))

        zeilen = self._text_umbrechen(beschreibung, tooltip_breite - 16, self.schrift_klein)
        for i, zeile in enumerate(zeilen[:3]):
            txt = self.schrift_klein.render(zeile, True, config.FARBE_TEXT)
            flaeche.blit(txt, (tooltip_x + 8, tooltip_y + 24 + i * 18))

        stufen_txt = self.schrift_klein.render(
            f"Max: {max_stufen} Stufen", True, config.FARBE_TEXT_GEDIMMT)
        flaeche.blit(stufen_txt, (tooltip_x + 8, tooltip_y + tooltip_hoehe - 20))

    def _zeichnen(self, flaeche: pygame.Surface):
        if not self.geladen:
            return
        if self.hover_node:
            self._tooltip_zeichnen(flaeche, self.hover_node)