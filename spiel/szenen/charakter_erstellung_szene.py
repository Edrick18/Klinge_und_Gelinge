"""
spiel/szenen/charakter_erstellung_szene.py - Charaktererstellungs-Szene

Abhängigkeiten: pygame, config, basis_szene
"""

import pygame
import config
from ..kern.basis_szene import BasisSzene
from netzwerk.nachrichten import (
    CHARAKTER_ERSTELLEN, CHARAKTER_ERSTELLT, CHARAKTER_ERSTELLEN_FEHLER,
    SCHLUESSEL_CHARAKTER_NAME, SCHLUESSEL_MASTERIE, SCHLUESSEL_STATS, SCHLUESSEL_NACHRICHT
)
from server.logik.charakter_verwaltung import VERFÜGBARE_MASTERIEN, MASTERIE_ANZEIGENAME
from spiel.systeme.skill_definitionen import basis_klasse_laden


class CharakterErstellungSzene(BasisSzene):
    GRUNDWERT_ZU_KLASSE = {
        "staerke":       "krieger",
        "vitalitaet":    "waechter",
        "weisheit":      "zauberer",
        "glueck":        "schicksalsritter",
        "beweglichkeit": "schatten",
        "charisma":      "herold"
    }
    def __init__(self, szenen_manager, netzwerk_client, gesperrte_masterien: list):
        self.szenen_manager = szenen_manager
        self.netzwerk_client = netzwerk_client
        self.gesperrte_masterien = gesperrte_masterien

        self.name_eingabe = ""
        self.gewaehlte_masterie = None
        self.verbleibende_punkte = 20
        self.stats = {
            "staerke": 10, "vitalitaet": 10, "weisheit": 10,
            "glueck": 10, "beweglichkeit": 10, "charisma": 10
        }
        self.status_nachricht = ""
        self.status_farbe = config.FARBE_TEXT

        self._layout_berechnen()

    def _layout_berechnen(self):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE

        self.schrift_klein = pygame.font.Font(None, max(16, int(h * 0.025)))
        self.schrift_normal = pygame.font.Font(None, max(20, int(h * 0.033)))
        self.schrift_gross = pygame.font.Font(None, max(28, int(h * 0.05)))
        self.schrift_button = pygame.font.Font(None, max(24, int(h * 0.038)))

        self.oben_h = int(h * 0.22)
        self.unten_h = int(h * 0.12)
        self.mitte_h = h - self.oben_h - self.unten_h
        self.mitte_y = self.oben_h
        self.name_y = int(h * 0.12)
        self.linie_y = self.oben_h - int(h * 0.01)
        self.ueberschrift_y = self.oben_h + int(h * 0.01)

        self.links_x = int(b * 0.05)
        self.links_breite = int(b * 0.42)
        self.rechts_x = int(b * 0.53)
        self.rechts_breite = int(b * 0.42)

        self.btn_breite = int(b * 0.03)
        self.btn_hoehe = int(h * 0.07)
        self.wert_breite = int(b * 0.04)
        self.abstand = int(b * 0.015)

        self.masterie_btn_h = int(h * 0.07)
        self.masterie_btn_b = int(self.links_breite * 0.9)
        self.masterie_abstand = int(h * 0.012)

        gesamt_h = 6 * self.masterie_btn_h + 5 * self.masterie_abstand
        start_y = self.mitte_y + int(h * 0.01)
        self.punkte_y = start_y

        self.masterie_buttons = []
        for i, masterie in enumerate(VERFÜGBARE_MASTERIEN):
            klassen_id = self.GRUNDWERT_ZU_KLASSE.get(masterie, masterie)
            klassen_daten = basis_klasse_laden(klassen_id)
            anzeige_name = klassen_daten.get("name", klassen_id.capitalize()) if klassen_daten else klassen_id.capitalize()
            btn_y = start_y + int(h * 0.035) + i * (self.masterie_btn_h + self.masterie_abstand)
            btn_x = self.links_x + (self.links_breite - self.masterie_btn_b) // 2
            self.masterie_buttons.append({
                "masterie": klassen_id,
                "anzeige": anzeige_name,
                "rect": pygame.Rect(btn_x, btn_y, self.masterie_btn_b, self.masterie_btn_h)
            })

        self.stat_zeilen = []
        stat_namen = list(self.stats.keys())

        for i, stat_name in enumerate(stat_namen):
            zeile_y = start_y + int(h * 0.035) + i * (self.btn_hoehe + self.masterie_abstand) + self.btn_hoehe // 2
            minus_x = self.rechts_x + int(self.rechts_breite * 0.45)
            wert_x = minus_x + self.btn_breite + self.abstand
            plus_x = wert_x + self.wert_breite + self.abstand

            self.stat_zeilen.append({
                "name": stat_name,
                "y": zeile_y,
                "minus_rect": pygame.Rect(minus_x, zeile_y - self.btn_hoehe // 2, self.btn_breite, self.btn_hoehe),
                "wert_x": wert_x,
                "plus_rect": pygame.Rect(plus_x, zeile_y - self.btn_hoehe // 2, self.btn_breite, self.btn_hoehe)
            })

        self.name_feld = pygame.Rect((b - 400) // 2, self.name_y, 400, 40)
        self.erstellen_button = pygame.Rect(b // 2 - 100, h - 80, 200, 50)

    def events_verarbeiten(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from .charakter_auswahl_szene import CharakterAuswahlSzene
                    self.szenen_manager.szene_wechseln(CharakterAuswahlSzene(self.szenen_manager, self.netzwerk_client))
                elif event.key == pygame.K_BACKSPACE:
                    self.name_eingabe = self.name_eingabe[:-1]
                elif event.key == pygame.K_RETURN:
                    self.erstellen_senden()
                elif event.unicode and len(event.unicode) > 0:
                    if event.unicode.isprintable() and len(self.name_eingabe) < 20:
                        self.name_eingabe += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._maus_klick_pruefen(event.pos)

    def _maus_klick_pruefen(self, pos):
        for btn in self.masterie_buttons:
            if btn["rect"].collidepoint(pos) and btn["masterie"] not in self.gesperrte_masterien:
                self.gewaehlte_masterie = btn["masterie"]

        for zeile in self.stat_zeilen:
            if zeile["minus_rect"].collidepoint(pos):
                stat_wert = self.stats[zeile["name"]]
                if stat_wert > 10 and self.verbleibende_punkte < 20:
                    self.stats[zeile["name"]] -= 1
                    self.verbleibende_punkte += 1
            elif zeile["plus_rect"].collidepoint(pos):
                stat_wert = self.stats[zeile["name"]]
                if stat_wert < 25 and self.verbleibende_punkte > 0:
                    self.stats[zeile["name"]] += 1
                    self.verbleibende_punkte -= 1

        if self.erstellen_button.collidepoint(pos):
            self.erstellen_senden()

    def erstellen_senden(self):
        if not self.name_eingabe or not self.gewaehlte_masterie or self.verbleibende_punkte > 0:
            return
        self.netzwerk_client.nachricht_senden(CHARAKTER_ERSTELLEN, {
            SCHLUESSEL_CHARAKTER_NAME: self.name_eingabe,
            SCHLUESSEL_MASTERIE: self.gewaehlte_masterie,
            SCHLUESSEL_STATS: self.stats
        })

    def updaten(self, delta_zeit: float):
        self._layout_berechnen()
        while True:
            nachricht = self.netzwerk_client.nachricht_holen()
            if not nachricht:
                break
            typ = nachricht.get("typ")
            daten = nachricht.get("daten", {})
            if typ == CHARAKTER_ERSTELLT:
                from .charakter_auswahl_szene import CharakterAuswahlSzene
                self.szenen_manager.szene_wechseln(CharakterAuswahlSzene(self.szenen_manager, self.netzwerk_client))
            elif typ == CHARAKTER_ERSTELLEN_FEHLER:
                self.status_nachricht = daten.get(SCHLUESSEL_NACHRICHT, "Fehler")
                self.status_farbe = config.FARBE_HP

    def zeichnen(self, flaeche: pygame.Surface):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE

        flaeche.fill(config.FARBE_HINTERGRUND)

        titel_text = self.schrift_gross.render("Charakter erstellen", True, config.FARBE_AKZENT)
        titel_rect = titel_text.get_rect(center=(b // 2, 40))
        flaeche.blit(titel_text, titel_rect)

        name_label = self.schrift_normal.render("Name:", True, config.FARBE_TEXT)
        name_label_rect = name_label.get_rect(center=(b // 2, 80))
        flaeche.blit(name_label, name_label_rect)

        pygame.draw.rect(flaeche, config.FARBE_TEXT, self.name_feld, 2)
        if self.name_eingabe:
            name_text = self.schrift_normal.render(self.name_eingabe, True, config.FARBE_TEXT)
            name_text_rect = name_text.get_rect(center=(b // 2, 115))
            flaeche.blit(name_text, name_text_rect)

        pygame.draw.line(flaeche, config.FARBE_RAND, (0, self.mitte_y), (b, self.mitte_y), 1)

        masterie_label = self.schrift_normal.render("Masterie:", True, config.FARBE_AKZENT)
        flaeche.blit(masterie_label, (self.links_x + 20, self.mitte_y + 5))

        for btn in self.masterie_buttons:
            masterie = btn["masterie"]
            gesperrt = masterie in self.gesperrte_masterien

            bg_farbe = config.FARBE_PANEL if not gesperrt else config.FARBE_DUNKELGRAU
            text_farbe = config.FARBE_TEXT if not gesperrt else config.FARBE_TEXT_GEDIMMT
            if masterie == self.gewaehlte_masterie:
                bg_farbe = config.FARBE_AKZENT
                text_farbe = config.FARBE_SCHWARZ

            pygame.draw.rect(flaeche, bg_farbe, btn["rect"])
            pygame.draw.rect(flaeche, config.FARBE_RAND if not gesperrt else config.FARBE_DUNKELGRAU, btn["rect"], 2)
            anzeige = btn.get("anzeige", MASTERIE_ANZEIGENAME.get(masterie, masterie))
            masterie_text = self.schrift_klein.render(anzeige, True, text_farbe)
            masterie_rect = masterie_text.get_rect(center=btn["rect"].center)
            flaeche.blit(masterie_text, masterie_rect)

        stats_label = self.schrift_normal.render("Stats:", True, config.FARBE_AKZENT)
        flaeche.blit(stats_label, (self.rechts_x + 20, self.ueberschrift_y))

        punkte_text = self.schrift_normal.render(f"Punkte: {self.verbleibende_punkte}", True, config.FARBE_AKZENT if self.verbleibende_punkte == 0 else config.FARBE_TEXT)
        punkte_rect = punkte_text.get_rect(right=self.rechts_x + self.rechts_breite - 20, top=self.punkte_y)
        flaeche.blit(punkte_text, punkte_rect)

        for zeile in self.stat_zeilen:
            stat_name = zeile["name"]
            stat_wert = self.stats[stat_name]

            stat_text = self.schrift_klein.render(MASTERIE_ANZEIGENAME.get(stat_name, stat_name), True, config.FARBE_TEXT)
            flaeche.blit(stat_text, (self.rechts_x + 20, zeile["y"] + 5))

            pygame.draw.rect(flaeche, config.FARBE_PANEL, zeile["minus_rect"])
            pygame.draw.rect(flaeche, config.FARBE_RAND, zeile["minus_rect"], 1)
            minus_text = self.schrift_klein.render("-", True, config.FARBE_TEXT if stat_wert > 10 else config.FARBE_DUNKELGRAU)
            flaeche.blit(minus_text, (zeile["minus_rect"].centerx - 5, zeile["minus_rect"].centery - 10))

            wert_text = self.schrift_klein.render(str(stat_wert), True, config.FARBE_AKZENT)
            wert_rect = wert_text.get_rect(center=(zeile["wert_x"] + self.wert_breite // 2, zeile["y"]))
            flaeche.blit(wert_text, wert_rect)

            pygame.draw.rect(flaeche, config.FARBE_PANEL, zeile["plus_rect"])
            pygame.draw.rect(flaeche, config.FARBE_RAND, zeile["plus_rect"], 1)
            plus_text = self.schrift_klein.render("+", True, config.FARBE_TEXT if stat_wert < 25 and self.verbleibende_punkte > 0 else config.FARBE_DUNKELGRAU)
            flaeche.blit(plus_text, (zeile["plus_rect"].centerx - 5, zeile["plus_rect"].centery - 10))

        unten_y = h - self.unten_h
        pygame.draw.line(flaeche, config.FARBE_RAND, (0, unten_y), (b, unten_y), 1)

        if self.status_nachricht:
            status_text = self.schrift_normal.render(self.status_nachricht, True, self.status_farbe)
            status_rect = status_text.get_rect(center=(b // 2, unten_y + 15))
            flaeche.blit(status_text, status_rect)

        erstellen_kann = bool(self.name_eingabe and self.gewaehlte_masterie and self.verbleibende_punkte == 0)
        erstellen_bg = config.FARBE_AKZENT if erstellen_kann else config.FARBE_DUNKELGRAU
        erstellen_farbe = config.FARBE_SCHWARZ if erstellen_kann else config.FARBE_TEXT_GEDIMMT
        pygame.draw.rect(flaeche, erstellen_bg, self.erstellen_button)
        pygame.draw.rect(flaeche, config.FARBE_RAND, self.erstellen_button, 2)
        erstellen_text = self.schrift_button.render("Erstellen", True, erstellen_farbe)
        erstellen_text_rect = erstellen_text.get_rect(center=self.erstellen_button.center)
        flaeche.blit(erstellen_text, erstellen_text_rect)