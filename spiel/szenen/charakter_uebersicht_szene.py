"""
spiel/szenen/charakter_uebersicht_szene.py - Charakter-Übersicht mit allen Stats

Abhängigkeiten: pygame, config, basis_szene
"""

import pygame
import config
from ..kern.basis_szene import BasisSzene
from ..kern.ui_helfer import button_zeichnen, balken_zeichnen
from netzwerk.nachrichten import (
    CHARAKTER_DETAILS_LADEN, CHARAKTER_DETAILS_ANTWORT,
    SCHLUESSEL_CHARAKTER_DATEN, SCHLUESSEL_CHARAKTER_ID,
    TESTKAMPF_STARTEN, KAMPF_ERGEBNIS, SCHLUESSEL_KAMPF_ERGEBNIS
)
from server.logik.charakter_verwaltung import MASTERIE_ANZEIGENAME
from spiel.systeme.stat_berechnung import StatBerechnung
from spiel.systeme.skill_definitionen import basis_klasse_laden


class CharakterUebersichtSzene(BasisSzene):
    def __init__(self, szenen_manager, netzwerk_client, charakter_id=None, charakter_daten=None):
        self.szenen_manager = szenen_manager
        self.netzwerk_client = netzwerk_client
        # Akzeptiere None-Werte, damit Aufruf aus anderen Szenen mit/ohne Daten funktioniert
        self.charakter_id = charakter_id
        self.charakter_daten = charakter_daten
        self.geladen = False

        # Animierte Balken: aktuell angezeigte Fuellmenge (0.0–1.0)
        self.xp_anzeige = 0.0
        self.hp_anzeige = 0.0

        self._details_angefordert = False  # Erst beim ersten updaten() laden
        self._layout_berechnen()

        if self.charakter_daten is not None:
            self.geladen = True

    def _layout_berechnen(self):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE

        self.schrift_klein = pygame.font.Font(None, max(14, int(h * 0.022)))
        self.schrift_normal = pygame.font.Font(None, max(18, int(h * 0.028)))
        self.schrift_gross = pygame.font.Font(None, max(32, int(h * 0.05)))
        self.schrift_titel = pygame.font.Font(None, max(40, int(h * 0.06)))

        self.links_x = int(b * 0.02)
        self.links_breite = int(b * 0.33)
        self.mitte_x = int(b * 0.37)
        self.mitte_breite = int(b * 0.25)
        self.rechts_x = int(b * 0.64)
        self.rechts_breite = int(b * 0.34)

        self.oben_y = int(h * 0.02)
        self.unten_y = int(h * 0.92)
        self.unten_hoehe = h - self.unten_y

        self.xp_balken_breite = int(b * 0.31)
        self.xp_balken_hoehe = int(h * 0.018)

        self.platzhalter_buttons = []
        button_labels = ["Arena", "Taverne", "Reisen", "Inventar", "Skills", "Shop", "Gilde"]
        self.testkampf_button_index = 0
        self.taverne_button_index = 1
        self.reise_button_index = 2
        self.inventar_button_index = 3
        self.skills_button_index = 4
        self.shop_button_index = 5
        self.gilde_button_index = 6
        btn_count = len(button_labels)
        btn_breite = int(b * 0.12)
        btn_abstand = int(b * 0.02)
        gesamt_breite = btn_count * btn_breite + (btn_count - 1) * btn_abstand
        start_x = (b - gesamt_breite) // 2

        for i, label in enumerate(button_labels):
            btn_x = start_x + i * (btn_breite + btn_abstand)
            self.platzhalter_buttons.append({
                "label": label,
                "rect": pygame.Rect(btn_x, self.unten_y - int(h * 0.06), btn_breite, int(h * 0.05))
            })

    def events_verarbeiten(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from .charakter_auswahl_szene import CharakterAuswahlSzene
                    self.szenen_manager.szene_wechseln(CharakterAuswahlSzene(self.szenen_manager, self.netzwerk_client))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, btn in enumerate(self.platzhalter_buttons):
                        if btn["rect"].collidepoint(event.pos):
                            if i == self.testkampf_button_index:
                                from .arena_szene import ArenaSzene
                                self.szenen_manager.szene_wechseln(ArenaSzene(
                                    self.szenen_manager, self.netzwerk_client, self.charakter_daten
                                ))
                            elif i == self.taverne_button_index:
                                from .taverne_szene import TaverneSzene
                                self.szenen_manager.szene_wechseln(TaverneSzene(
                                    self.szenen_manager, self.netzwerk_client, self.charakter_daten
                                ))
                            elif i == self.inventar_button_index:
                                from .inventar_szene import InventarSzene
                                self.szenen_manager.szene_wechseln(InventarSzene(
                                    self.szenen_manager, self.netzwerk_client, self.charakter_daten
                                ))
                            elif i == self.skills_button_index:
                                from .skill_szene import SkillSzene
                                self.szenen_manager.szene_wechseln(SkillSzene(
                                    self.szenen_manager, self.netzwerk_client, self.charakter_daten
                                ))
                            elif i == self.reise_button_index:
                                from .reise_szene import ReiseSzene
                                self.szenen_manager.szene_wechseln(ReiseSzene(
                                    self.szenen_manager, self.netzwerk_client, self.charakter_daten
                                ))
                            elif i == self.shop_button_index:
                                from .shop_szene import ShopSzene
                                self.szenen_manager.szene_wechseln(ShopSzene(
                                    self.szenen_manager, self.netzwerk_client, self.charakter_daten
                                ))
                            elif i == self.gilde_button_index:
                                from .gilde_szene import GildeSzene
                                self.szenen_manager.szene_wechseln(GildeSzene(
                                    self.szenen_manager, self.netzwerk_client, self.charakter_daten
                                ))
                            elif i == self.arena_button_index:
                                from .arena_szene import ArenaSzene
                                self.szenen_manager.szene_wechseln(ArenaSzene(
                                    self.szenen_manager, self.netzwerk_client, self.charakter_daten
                                ))

    def updaten(self, delta_zeit: float):
        # Daten erst anfordern wenn Szene wirklich aktiv ist (nach Fade)
        if not self._details_angefordert and self.charakter_daten is None:
            self.netzwerk_client.nachricht_senden(CHARAKTER_DETAILS_LADEN, {})
            self._details_angefordert = True

        # Balken-Animation: sanft zum Zielwert interpolieren
        if self.geladen and self.charakter_daten:
            char = self.charakter_daten
            from spiel.systeme.stat_berechnung import StatBerechnung
            xp_max = StatBerechnung.xp_fuer_naechstes_level(char.get("level", 1))
            xp_ziel = char.get("erfahrung", 0) / xp_max if xp_max > 0 else 0.0
            hp_ziel = char.get("hp", char.get("max_hp", 1)) / max(1, char.get("max_hp", 1))

            geschwindigkeit = 3.0 * delta_zeit
            self.xp_anzeige += (xp_ziel - self.xp_anzeige) * min(1.0, geschwindigkeit * 4)
            self.hp_anzeige += (hp_ziel - self.hp_anzeige) * min(1.0, geschwindigkeit * 4)

        while True:
            nachricht = self.netzwerk_client.nachricht_holen()
            if not nachricht:
                break
            typ = nachricht.get("typ")
            daten = nachricht.get("daten", {})
            if typ == CHARAKTER_DETAILS_ANTWORT:
                self.charakter_daten = daten.get(SCHLUESSEL_CHARAKTER_DATEN)
                self.geladen = True
            if typ == KAMPF_ERGEBNIS:
                kampf_ergebnis = daten.get(SCHLUESSEL_KAMPF_ERGEBNIS)
                if kampf_ergebnis:
                    spieler_name = kampf_ergebnis.get("spieler_name", "Spieler")
                    gegner_name = kampf_ergebnis.get("gegner_name", "Gegner")
                    from .kampf_anzeige_szene import KampfAnzeigeSzene
                    self.szenen_manager.szene_wechseln(KampfAnzeigeSzene(
                        self.szenen_manager, self.netzwerk_client, kampf_ergebnis,
                        spieler_name, gegner_name
                    ))

    def zeichnen(self, flaeche: pygame.Surface):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE

        flaeche.fill(config.FARBE_HINTERGRUND)

        if not self.geladen or not self.charakter_daten:
            lade_text = self.schrift_gross.render("Lade...", True, config.FARBE_TEXT_GEDIMMT)
            lade_rect = lade_text.get_rect(center=(b // 2, h // 2))
            flaeche.blit(lade_text, lade_rect)
            return

        char = self.charakter_daten

        name = char.get("name", "Unbekannt")
        level = char.get("level", 1)
        masterie_1 = char.get("masterie_1", "---")
        masterie_2 = char.get("masterie_2") or "---"

        klassen_daten_1 = basis_klasse_laden(masterie_1) if masterie_1 != "---" else None
        masterie_1_anzeige = klassen_daten_1.get("name", masterie_1.capitalize()) if klassen_daten_1 else (masterie_1 if masterie_1 == "---" else masterie_1.capitalize())

        klassen_daten_2 = basis_klasse_laden(masterie_2) if masterie_2 != "---" else None
        masterie_2_anzeige = klassen_daten_2.get("name", masterie_2.capitalize()) if klassen_daten_2 else (masterie_2 if masterie_2 == "---" else masterie_2.capitalize())

        erfahrung = char.get("erfahrung", 0)
        gold = char.get("gold", 0)

        name_text = self.schrift_gross.render(name, True, config.FARBE_TEXT)
        flaeche.blit(name_text, (self.links_x + 10, self.oben_y))

        level_text = self.schrift_normal.render(f"Lvl {level}", True, config.FARBE_AKZENT)
        flaeche.blit(level_text, (self.links_x + 10, self.oben_y + 45))

        masterie_text = self.schrift_normal.render(masterie_1_anzeige, True, config.FARBE_AKZENT)
        flaeche.blit(masterie_text, (self.links_x + 10, self.oben_y + 80))

        masterie2_text = self.schrift_klein.render(masterie_2_anzeige, True, config.FARBE_TEXT_GEDIMMT)
        flaeche.blit(masterie2_text, (self.links_x + 10, self.oben_y + 110))

        xp_max = StatBerechnung.xp_fuer_naechstes_level(level)
        xp_text = self.schrift_klein.render(f"XP: {erfahrung} / {xp_max}", True, config.FARBE_TEXT)
        flaeche.blit(xp_text, (self.links_x + 10, self.oben_y + 150))

        # Animierter XP-Balken
        xp_balken_y = self.oben_y + 170
        xp_fuell = int(self.xp_balken_breite * self.xp_anzeige)
        balken_zeichnen(flaeche, self.links_x + 10, xp_balken_y,
                        self.xp_balken_breite, self.xp_balken_hoehe,
                        xp_fuell, self.xp_balken_breite, config.FARBE_XP)

        # Animierter HP-Balken
        max_hp = char.get("max_hp", 1)
        hp_text = self.schrift_klein.render(f"HP: {max_hp}", True, config.FARBE_TEXT_GEDIMMT)
        flaeche.blit(hp_text, (self.links_x + 10, xp_balken_y + 28))
        hp_fuell = int(self.xp_balken_breite * self.hp_anzeige)
        balken_zeichnen(flaeche, self.links_x + 10, xp_balken_y + 46,
                        self.xp_balken_breite, self.xp_balken_hoehe,
                        hp_fuell, self.xp_balken_breite, config.FARBE_HP)

        gold_text = self.schrift_normal.render(f"💰 {gold} Gold", True, config.FARBE_XP)
        flaeche.blit(gold_text, (self.links_x + 10, xp_balken_y + 72))

        grundwert_label = self.schrift_normal.render("GRUNDWERTE", True, config.FARBE_AKZENT)
        flaeche.blit(grundwert_label, (self.mitte_x + 10, self.oben_y))

        grundwerte = [
            ("Stärke", char.get("staerke", 10)),
            ("Vitalität", char.get("vitalitaet", 10)),
            ("Weisheit", char.get("weisheit", 10)),
            ("Glück", char.get("glueck", 10)),
            ("Beweglichkeit", char.get("beweglichkeit", 10)),
            ("Charisma", char.get("charisma", 10))
        ]

        start_y = self.oben_y + 35
        abstand = 28
        for i, (name, wert) in enumerate(grundwerte):
            text = self.schrift_klein.render(f"{name}: {wert}", True, config.FARBE_TEXT)
            flaeche.blit(text, (self.mitte_x + 10, start_y + i * abstand))

        kampfwert_label = self.schrift_normal.render("KAMPFWERTE", True, config.FARBE_AKZENT)
        flaeche.blit(kampfwert_label, (self.rechts_x + 10, self.oben_y))

        kampfwerte = [
            ("HP", char.get("max_hp", 0)),
            ("Mana", char.get("max_mana", 0)),
            ("Mana-Regen", f"{char.get('mana_regen', 0)}/s"),
            ("Phy. Schaden", char.get("physischer_schaden", 0)),
            ("Mag. Schaden", char.get("magischer_schaden", 0)),
            ("Rüstung", char.get("ruestung", 0)),
            ("Ausweichen", f"{char.get('ausweichen', 0)}%"),
            ("Krit-Chance", f"{char.get('krit_chance', 0)}%"),
            ("Krit-Schaden", f"{char.get('krit_schaden', 0)}%"),
            ("Atk/Sek", char.get("angriffsgeschwindigkeit", 0)),
            ("Gold-Bonus", f"{char.get('gold_bonus', 0)}%")
        ]

        for i, (name, wert) in enumerate(kampfwerte):
            text = self.schrift_klein.render(f"{name}: {wert}", True, config.FARBE_TEXT)
            flaeche.blit(text, (self.rechts_x + 10, start_y + i * abstand))

        pygame.draw.line(flaeche, config.FARBE_RAND, (0, self.unten_y), (b, self.unten_y), 1)

        for btn in self.platzhalter_buttons:
            button_zeichnen(flaeche, btn["rect"], btn["label"], self.schrift_klein,
                            farbe_bg=config.FARBE_DUNKELGRAU)

        zurueck_button = pygame.Rect(20, h - 40, 100, 30)
        button_zeichnen(flaeche, zurueck_button, "← Zurück", self.schrift_klein,
                        farbe_bg=config.FARBE_PANEL)
