"""
spiel/szenen/taverne_szene.py - Taverne mit Quest-Auswahl

Abhängigkeiten: pygame, config, basis_szene
"""

import pygame
import config
from datetime import datetime, timedelta
from ..kern.basis_szene import BasisSzene
from netzwerk.nachrichten import (
    QUESTS_LADEN, QUESTS_ANTWORT, QUEST_ANNEHMEN, QUEST_ANGENOMMEN,
    QUEST_AUFLOESEN, QUEST_ERGEBNIS, SCHLUESSEL_QUESTS, SCHLUESSEL_QUEST_ID,
    SCHLUESSEL_QUEST_ERGEBNIS,
    REISE_STATUS_LADEN, REISE_STATUS_ANTWORT
)
from spiel.systeme.quest_typen import RARITAET_FARBE


class TaverneSzene(BasisSzene):
    def __init__(self, szenen_manager, netzwerk_client, charakter_daten: dict):
        self.szenen_manager = szenen_manager
        self.netzwerk_client = netzwerk_client
        self.charakter_daten = charakter_daten

        self.quests = []
        self.geladen = False
        self.aktive_quest = None
        self.aufloesen_gesendet = False
        self.reise_aktiv = False
        self._erste_frames = 0   # Queue erst nach 2 Frames leeren, dann senden
        self._lade_timer = 0.0   # Retry-Timer bei hängendem Ladebildschirm

        self._layout_berechnen()

    def _layout_berechnen(self):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE

        self.schrift_klein = pygame.font.Font(None, max(14, int(h * 0.022)))
        self.schrift_normal = pygame.font.Font(None, max(18, int(h * 0.028)))
        self.schrift_gross = pygame.font.Font(None, max(32, int(h * 0.05)))
        self.schrift_titel = pygame.font.Font(None, max(40, int(h * 0.06)))

        self.titel_y = int(h * 0.08)
        self.karten_start_y = int(h * 0.18)
        self.karten_hoehe = int(h * 0.58)

        karten_breite = int(b * 0.28)
        abstand = int(b * 0.04)
        gesamt_breite = 3 * karten_breite + 2 * abstand
        self.karten_start_x = (b - gesamt_breite) // 2

        self.zurueck_button = pygame.Rect(20, h - 50, 120, 35)

    def updaten(self, delta_zeit: float):
        # Erste 2 Frames: Queue von alten Nachrichten leeren, erst dann senden
        if self._erste_frames < 2:
            self._erste_frames += 1
            while self.netzwerk_client.nachricht_holen():
                pass
            if self._erste_frames == 2:
                self.netzwerk_client.nachricht_senden(QUESTS_LADEN, {})
                self.netzwerk_client.nachricht_senden(REISE_STATUS_LADEN, {})
            return

        if not self.geladen:
            self._lade_timer += delta_zeit
            if self._lade_timer >= 1.5:
                self.netzwerk_client.nachricht_senden(QUESTS_LADEN, {})
                self.netzwerk_client.nachricht_senden(REISE_STATUS_LADEN, {})
                self._lade_timer = 0.0

        while True:
            nachricht = self.netzwerk_client.nachricht_holen()
            if not nachricht:
                break
            typ = nachricht.get("typ")
            daten = nachricht.get("daten", {})

            if typ == QUESTS_ANTWORT:
                self.quests = daten.get(SCHLUESSEL_QUESTS, [])
                self.aktive_quest = daten.get("aktive_quest")
                self.geladen = True

                if self.aktive_quest and not self.aufloesen_gesendet:
                    gestartet = datetime.fromisoformat(self.aktive_quest["gestartet_am"])
                    jetzt = datetime.now()
                    verbleibend = (gestartet - jetzt).total_seconds() + self.aktive_quest["timer_sekunden"]
                    if verbleibend <= 0:
                        self.netzwerk_client.nachricht_senden(QUEST_AUFLOESEN, {
                            SCHLUESSEL_QUEST_ID: self.aktive_quest["id"]
                        })
                        self.aufloesen_gesendet = True

            elif typ == REISE_STATUS_ANTWORT:
                war_aktiv = self.reise_aktiv
                self.reise_aktiv = daten.get("aktiv", False)

                if war_aktiv and not self.reise_aktiv:
                    self.geladen = False
                    self.netzwerk_client.nachricht_senden(QUESTS_LADEN, {})

            elif typ == QUEST_ANGENOMMEN:
                if daten.get("erfolg"):
                    self.aktive_quest = daten.get("quest")
                    for i, q in enumerate(self.quests):
                        if q["id"] == self.aktive_quest["id"]:
                            self.quests[i] = self.aktive_quest
                            break

            elif typ == QUEST_ERGEBNIS:
                ergebnis = daten.get(SCHLUESSEL_QUEST_ERGEBNIS, {})
                kampf_ergebnis = ergebnis.get("kampf_ergebnis")

                if kampf_ergebnis and ergebnis.get("erfolg"):
                    kampf_ergebnis["item_drop"] = ergebnis.get("item_drop")
                    kampf_ergebnis["gold"] = ergebnis.get("gold", 0)
                    kampf_ergebnis["xp"] = ergebnis.get("xp", 0)
                    spieler_name = kampf_ergebnis.get("spieler_name", "Spieler")
                    gegner_name = kampf_ergebnis.get("gegner_name", "Gegner")
                    from .kampf_anzeige_szene import KampfAnzeigeSzene
                    self.szenen_manager.szene_wechseln(KampfAnzeigeSzene(
                        self.szenen_manager, self.netzwerk_client,
                        kampf_ergebnis, spieler_name, gegner_name
                    ))
                    return

                if ergebnis.get("erfolg") and not kampf_ergebnis:
                    self.aktive_quest = None
                    self.aufloesen_gesendet = False
                    self.geladen = False

        # Kontinuierliche Timer-Prüfung: sofort auflösen wenn abgelaufen
        if self.aktive_quest and not self.aufloesen_gesendet and self.aktive_quest.get("gestartet_am"):
            gestartet = datetime.fromisoformat(self.aktive_quest["gestartet_am"])
            jetzt = datetime.now()
            verbleibend = (gestartet - jetzt).total_seconds() + self.aktive_quest["timer_sekunden"]
            if verbleibend <= 0:
                self.netzwerk_client.nachricht_senden(QUEST_AUFLOESEN, {
                    SCHLUESSEL_QUEST_ID: self.aktive_quest["id"]
                })
                self.aufloesen_gesendet = True

    def events_verarbeiten(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._zurueck_zur_uebersicht()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.zurueck_button.collidepoint(event.pos):
                        self._zurueck_zur_uebersicht()
                    elif not self.reise_aktiv:
                        self._quest_karten_klick(event.pos)

    def _quest_karten_klick(self, pos):
        if self.aktive_quest:
            return

        b = config.AUFLOESUNG_BREITE
        karten_breite = int(b * 0.28)

        for i, quest in enumerate(self.quests):
            karten_x = self.karten_start_x + i * (karten_breite + int(b * 0.04))
            karten_rect = pygame.Rect(karten_x, self.karten_start_y, karten_breite, self.karten_hoehe)

            if karten_rect.collidepoint(pos):
                self.netzwerk_client.nachricht_senden(QUEST_ANNEHMEN, {
                    SCHLUESSEL_QUEST_ID: quest["id"]
                })
                break

    def _zurueck_zur_uebersicht(self):
        from .charakter_uebersicht_szene import CharakterUebersichtSzene
        self.szenen_manager.szene_wechseln(CharakterUebersichtSzene(
            self.szenen_manager, self.netzwerk_client, None
        ))

    def _timer_format(self, sekunden: int) -> str:
        minuten = sekunden // 60
        sekunden = sekunden % 60
        return f"{minuten:02d}:{sekunden:02d}"

    def zeichnen(self, flaeche: pygame.Surface):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE

        flaeche.fill(config.FARBE_HINTERGRUND)

        if self.reise_aktiv:
            overlay = pygame.Surface((b, h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            flaeche.blit(overlay, (0, 0))

            msg1 = self.schrift_gross.render("Dein Held ist auf Reisen!", True, config.FARBE_AKZENT)
            msg2 = self.schrift_normal.render("Beende die Reise um Quests anzunehmen.", True, config.FARBE_TEXT_GEDIMMT)
            flaeche.blit(msg1, msg1.get_rect(center=(b // 2, h // 2 - 30)))
            flaeche.blit(msg2, msg2.get_rect(center=(b // 2, h // 2 + 20)))

            pygame.draw.rect(flaeche, config.FARBE_PANEL, self.zurueck_button)
            pygame.draw.rect(flaeche, config.FARBE_RAND, self.zurueck_button, 1)
            zurueck = self.schrift_klein.render("← Zurück", True, config.FARBE_TEXT)
            flaeche.blit(zurueck, zurueck.get_rect(center=self.zurueck_button.center))
            return

        titel_text = self.schrift_gross.render("Taverne", True, config.FARBE_TEXT)
        titel_rect = titel_text.get_rect(center=(b // 2, self.titel_y))
        flaeche.blit(titel_text, titel_rect)

        if self.aktive_quest:
            untertitel_text = self.schrift_normal.render("Quest läuft...", True, config.FARBE_WARNUNG)
        else:
            untertitel_text = self.schrift_normal.render("Wähle eine Quest", True, config.FARBE_TEXT_GEDIMMT)
        untertitel_rect = untertitel_text.get_rect(center=(b // 2, self.titel_y + 35))
        flaeche.blit(untertitel_text, untertitel_rect)

        if not self.geladen:
            lade_text = self.schrift_normal.render("Lade Quests...", True, config.FARBE_TEXT_GEDIMMT)
            lade_rect = lade_text.get_rect(center=(b // 2, h // 2))
            flaeche.blit(lade_text, lade_rect)
            return

        karten_breite = int(b * 0.28)
        abstand = int(b * 0.04)

        for i, quest in enumerate(self.quests):
            karten_x = self.karten_start_x + i * (karten_breite + abstand)
            self._quest_karte_zeichnen(flaeche, quest, karten_x, self.karten_start_y, karten_breite, self.karten_hoehe, i)

        pygame.draw.rect(flaeche, config.FARBE_PANEL, self.zurueck_button)
        pygame.draw.rect(flaeche, config.FARBE_RAND, self.zurueck_button, 1)
        zurueck_text = self.schrift_klein.render("← Zurück", True, config.FARBE_TEXT)
        zurueck_rect = zurueck_text.get_rect(center=self.zurueck_button.center)
        flaeche.blit(zurueck_text, zurueck_rect)


    def _quest_karte_zeichnen(self, flaeche, quest, x, y, breite, hoehe, index):
        rand_farbe = config.FARBE_RAND
        if self.aktive_quest and self.aktive_quest["id"] == quest["id"]:
            rand_farbe = config.FARBE_AKZENT

        pygame.draw.rect(flaeche, config.FARBE_PANEL, (x, y, breite, hoehe))
        pygame.draw.rect(flaeche, rand_farbe, (x, y, breite, hoehe), 2)

        raritaet = quest.get("raritaet", "normal")
        raritaet_farbe = RARITAET_FARBE.get(raritaet, (180, 180, 180))
        pygame.draw.rect(flaeche, raritaet_farbe, (x, y, breite, int(hoehe * 0.015)))

        name_text = self.schrift_normal.render(quest.get("name", ""), True, raritaet_farbe)
        flaeche.blit(name_text, (x + 15, y + int(hoehe * 0.04)))

        beschreibung = quest.get("beschreibung", "")
        beschreibung_wordwrap = self._text_wrap(beschreibung, breite - 30, self.schrift_klein)
        for j, zeile in enumerate(beschreibung_wordwrap[:3]):
            text = self.schrift_klein.render(zeile, True, config.FARBE_TEXT_GEDIMMT)
            flaeche.blit(text, (x + 15, y + int(hoehe * 0.14) + j * 20))

        trenner_y = y + int(hoehe * 0.35)
        pygame.draw.line(flaeche, config.FARBE_RAND, (x + 15, trenner_y), (x + breite - 15, trenner_y), 1)

        timer = quest.get("timer_sekunden", 0)
        if self.aktive_quest and self.aktive_quest.get("id") == quest.get("id") and quest.get("gestartet_am"):
            gestartet = datetime.fromisoformat(quest["gestartet_am"])
            jetzt = datetime.now()
            verbleibend = int((gestartet - jetzt).total_seconds() + timer)
            if verbleibend < 0:
                verbleibend = 0
            timer_text = f"⏱ {self._timer_format(verbleibend)}"
        else:
            timer_text = f"⏱ {self._timer_format(timer)}"

        timer_render = self.schrift_normal.render(timer_text, True, config.FARBE_TEXT)
        flaeche.blit(timer_render, (x + 15, trenner_y + 10))

        schwierigkeit = quest.get("schwierigkeit", 1.0)
        schwierigkeit_text = self.schrift_klein.render(f"⚔ Schwierigkeit: {schwierigkeit}x", True, config.FARBE_TEXT_GEDIMMT)
        flaeche.blit(schwierigkeit_text, (x + 15, trenner_y + 40))

        gold = quest.get("gold_belohnung", 0)
        gold_text = self.schrift_klein.render(f"💰 Gold: {gold}", True, config.FARBE_XP)
        flaeche.blit(gold_text, (x + 15, trenner_y + 65))

        xp = quest.get("xp_belohnung", 0)
        xp_text = self.schrift_klein.render(f"✨ XP: {xp}", True, config.FARBE_XP)
        flaeche.blit(xp_text, (x + 15, trenner_y + 90))

        item_chance = int(quest.get("item_drop_chance", 0) * 100)
        item_text = self.schrift_klein.render(f"📦 Item-Chance: {item_chance}%", True, config.FARBE_TEXT_GEDIMMT)
        flaeche.blit(item_text, (x + 15, trenner_y + 115))

        button_y = y + hoehe - 50
        button_rect = pygame.Rect(x + 15, button_y, breite - 30, 35)

        if self.aktive_quest:
            pygame.draw.rect(flaeche, config.FARBE_DUNKELGRAU, button_rect)
            button_farbe = config.FARBE_TEXT_GEDIMMT
        else:
            pygame.draw.rect(flaeche, config.FARBE_PANEL, button_rect)
            button_farbe = config.FARBE_TEXT

        pygame.draw.rect(flaeche, config.FARBE_RAND, button_rect, 1)

        button_text = self.schrift_klein.render("Annehmen", True, button_farbe)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        flaeche.blit(button_text, button_text_rect)

    def _text_wrap(self, text: str, max_width: int, font) -> list:
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return lines
