"""
spiel/szenen/charakter_auswahl_szene.py - Charakterauswahl-Szene

Abhängigkeiten: pygame, config, basis_szene
"""

import pygame
import config
from ..kern.basis_szene import BasisSzene
from netzwerk.nachrichten import (
    CHARAKTERE_LADEN, CHARAKTERE_ANTWORT,
    CHARAKTER_WAEHLEN, CHARAKTER_GEWAEHLT,
    SCHLUESSEL_CHARAKTERE, SCHLUESSEL_CHARAKTER_ID
)
from server.logik.charakter_verwaltung import VERFÜGBARE_MASTERIEN
from spiel.systeme.skill_definitionen import basis_klasse_laden
from .stadt import StadtSzene


class CharakterAuswahlSzene(BasisSzene):
    GRUNDWERT_ZU_KLASSE = {
        "staerke":       "krieger",
        "vitalitaet":    "waechter",
        "weisheit":      "zauberer",
        "glueck":        "schicksalsritter",
        "beweglichkeit": "schatten",
        "charisma":      "herold"
    }

    def __init__(self, szenen_manager, netzwerk_client, letzter_charakter_id=None):
        self.szenen_manager = szenen_manager
        self.netzwerk_client = netzwerk_client
        self.letzter_charakter_id = letzter_charakter_id
        self.charaktere = []
        self.geladen = False
        self.gesperrte_masterien = []
        self.schrift_titel = pygame.font.Font(None, 48)
        self.schrift_name = pygame.font.Font(None, 32)
        self.schrift_level = pygame.font.Font(None, 24)
        self.schrift_button = pygame.font.Font(None, 36)

        self._layout_berechnen()
        self.netzwerk_client.nachricht_senden(CHARAKTERE_LADEN, {})

    def _layout_berechnen(self):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE
        self.schrift_klein = pygame.font.Font(None, max(14, int(h * 0.022)))

    def events_verarbeiten(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._maus_klick_pruefen(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    from .login_szene import LoginSzene
                    self.szenen_manager.szene_wechseln(LoginSzene(self.szenen_manager, self.netzwerk_client))

    def _maus_klick_pruefen(self, pos):
        slot_start_x = 100
        slot_abstand = 200
        slot_y = 150

        for i, masterie in enumerate(VERFÜGBARE_MASTERIEN):
            klasse_id = self.GRUNDWERT_ZU_KLASSE.get(masterie, masterie)
            klassen_daten = basis_klasse_laden(klasse_id)
            anzeige_name = klassen_daten.get("name", klasse_id.capitalize()) if klassen_daten else klasse_id.capitalize()
            slot_x = slot_start_x + i * slot_abstand
            slot_rect = pygame.Rect(slot_x, slot_y, 180, 220)

            if slot_rect.collidepoint(pos):
                charakter = next((c for c in self.charaktere if c["masterie_1"] == klasse_id), None)
                if charakter:
                    self.netzwerk_client.nachricht_senden(CHARAKTER_WAEHLEN, {
                        SCHLUESSEL_CHARAKTER_ID: charakter["id"]
                    })
                elif klasse_id not in self.gesperrte_masterien:
                    from .charakter_erstellung_szene import CharakterErstellungSzene
                    self.szenen_manager.szene_wechseln(CharakterErstellungSzene(
                        self.szenen_manager, self.netzwerk_client, self.gesperrte_masterien
                    ))

        zuruück_button = pygame.Rect(50, config.AUFLOESUNG_HOEHE - 80, 120, 40)
        if zuruück_button.collidepoint(pos):
            from .login_szene import LoginSzene
            self.szenen_manager.szene_wechseln(LoginSzene(self.szenen_manager, self.netzwerk_client))

    def updaten(self, delta_zeit: float):
        while True:
            nachricht = self.netzwerk_client.nachricht_holen()
            if not nachricht:
                break
            typ = nachricht.get("typ")
            daten = nachricht.get("daten", {})
            if typ == CHARAKTERE_ANTWORT:
                self.charaktere = daten.get(SCHLUESSEL_CHARAKTERE, [])
                self.gesperrte_masterien = [c["masterie_1"] for c in self.charaktere]
                self.geladen = True
            elif typ == CHARAKTER_GEWAEHLT:
                charakter_id = daten.get(SCHLUESSEL_CHARAKTER_ID)
                if charakter_id:
                    from .charakter_uebersicht_szene import CharakterUebersichtSzene
                    self.szenen_manager.szene_wechseln(CharakterUebersichtSzene(self.szenen_manager, self.netzwerk_client, charakter_id))

    def zeichnen(self, flaeche: pygame.Surface):
        flaeche.fill(config.FARBE_HINTERGRUND)

        titel_text = self.schrift_titel.render("Charakter wählen", True, config.FARBE_AKZENT)
        titel_rect = titel_text.get_rect(center=(config.AUFLOESUNG_BREITE // 2, 80))
        flaeche.blit(titel_text, titel_rect)

        slot_start_x = 100
        slot_abstand = 200
        slot_y = 150
        slot_breite, slot_hoehe = 180, 220

        for i, masterie in enumerate(VERFÜGBARE_MASTERIEN):
            klasse_id = self.GRUNDWERT_ZU_KLASSE.get(masterie, masterie)
            klassen_daten = basis_klasse_laden(klasse_id)
            anzeige_name = klassen_daten.get("name", klasse_id.capitalize()) if klassen_daten else klasse_id.capitalize()

            slot_x = slot_start_x + i * slot_abstand

            masterie_gesperrt = klasse_id in self.gesperrte_masterien
            charakter = next((c for c in self.charaktere if c["masterie_1"] == klasse_id), None)

            if charakter:
                if self.letzter_charakter_id and charakter.get("id") == self.letzter_charakter_id:
                    rand_farbe = config.FARBE_AKZENT
                else:
                    rand_farbe = config.FARBE_AKZENT
            elif masterie_gesperrt:
                rand_farbe = config.FARBE_DUNKELGRAU
            else:
                rand_farbe = config.FARBE_RAND

            pygame.draw.rect(flaeche, config.FARBE_PANEL, (slot_x, slot_y, slot_breite, slot_hoehe))
            pygame.draw.rect(flaeche, rand_farbe, (slot_x, slot_y, slot_breite, slot_hoehe), 2)

            klasse_text = self.schrift_klein.render(anzeige_name, True, config.FARBE_TEXT_GEDIMMT)
            klasse_rect = klasse_text.get_rect(center=(slot_x + slot_breite // 2, slot_y + 30))
            flaeche.blit(klasse_text, klasse_rect)

            if charakter:
                name_text = self.schrift_name.render(charakter["name"], True, config.FARBE_TEXT)
                name_rect = name_text.get_rect(center=(slot_x + slot_breite // 2, slot_y + 60))
                flaeche.blit(name_text, name_rect)

                level_text = self.schrift_level.render(f"Level {charakter['level']}", True, config.FARBE_TEXT_GEDIMMT)
                level_rect = level_text.get_rect(center=(slot_x + slot_breite // 2, slot_y + 90))
                flaeche.blit(level_text, level_rect)
            else:
                plus_text = self.schrift_titel.render("+", True, config.FARBE_TEXT if not masterie_gesperrt else config.FARBE_DUNKELGRAU)
                plus_rect = plus_text.get_rect(center=(slot_x + slot_breite // 2, slot_y + slot_hoehe // 2))
                flaeche.blit(plus_text, plus_rect)

        zuruück_button = pygame.Rect(50, config.AUFLOESUNG_HOEHE - 80, 120, 40)
        pygame.draw.rect(flaeche, config.FARBE_PANEL, zuruück_button)
        pygame.draw.rect(flaeche, config.FARBE_RAND, zuruück_button, 2)
        zuruück_text = self.schrift_button.render("Zurück", True, config.FARBE_TEXT)
        zuruück_rect = zuruück_text.get_rect(center=zuruück_button.center)
        flaeche.blit(zuruück_text, zuruück_rect)