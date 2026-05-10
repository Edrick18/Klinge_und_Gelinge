"""
spiel/szenen/reise_szene.py - Offline-Reisen Szene

Abhängigkeiten: pygame, config, basis_szene
"""

import pygame
import config
from ..kern.basis_szene import BasisSzene
from netzwerk.nachrichten import (
    REISE_STARTEN, REISE_GESTARTET, REISE_BEENDEN, REISE_BEENDET,
    REISE_STATUS_LADEN, REISE_STATUS_ANTWORT,
    REISE_BELOHNUNGEN_LADEN, REISE_BELOHNUNGEN_ANTWORT,
    REISE_BELOHNUNGEN_ABHOLEN, REISE_BELOHNUNGEN_ABGEHOLT,
    SCHLUESSEL_KAMPF_ERGEBNISSE, SCHLUESSEL_GESAMT_GOLD, SCHLUESSEL_GESAMT_XP,
    SCHLUESSEL_ANZAHL_QUESTS
)
from spiel.szenen.kampf_anzeige_szene import KampfAnzeigeSzene


class ReiseSzene(BasisSzene):
    def __init__(self, szenen_manager, netzwerk_client, charakter_daten=None):
        self.szenen_manager = szenen_manager
        self.netzwerk_client = netzwerk_client
        self.charakter_daten = charakter_daten

        self.zustand = "status"
        self.reise_status = None
        self.kampf_ergebnisse = []
        self.aktueller_kampf_index = 0
        self.gesamt_gold = 0
        self.gesamt_xp = 0

        self.gewaehlte_dauer = 4 * 3600
        self.dauer_buttons = []

        self._layout_berechnen()
        self.geladen = False

        self.netzwerk_client.nachricht_senden(REISE_STATUS_LADEN, {})

    def _layout_berechnen(self):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE

        self.schrift_klein = pygame.font.Font(None, max(14, int(h * 0.022)))
        self.schrift_normal = pygame.font.Font(None, max(18, int(h * 0.028)))
        self.schrift_gross = pygame.font.Font(None, max(32, int(h * 0.05)))
        self.schrift_titel = pygame.font.Font(None, max(40, int(h * 0.06)))

        self.knopf_breite = int(b * 0.25)
        self.knopf_hoehe = int(h * 0.06)
        self.knopf_y = h - int(h * 0.15)

        self.zurueck_button = pygame.Rect(20, h - 60, 120, 40)

        self.dauer_optionen = [3600, 7200, 14400, 21600, 28800, 43200]
        self.dauer_labels = ["1h", "2h", "4h", "6h", "8h", "12h"]
        dauer_btn_breite = int(b * 0.12)
        dauer_btn_hoehe = int(h * 0.05)
        dauer_abstand = int(b * 0.02)
        gesamt_breite = 6 * dauer_btn_breite + 5 * dauer_abstand
        dauer_start_x = (b - gesamt_breite) // 2
        self.dauer_buttons = []
        for i in range(6):
            btn = pygame.Rect(
                dauer_start_x + i * (dauer_btn_breite + dauer_abstand),
                int(h * 0.45),
                dauer_btn_breite,
                dauer_btn_hoehe
            )
            self.dauer_buttons.append(btn)

    def nachricht_empfangen(self, nachricht):
        typ = nachricht.get("typ")
        daten = nachricht.get("daten", {})

        if typ == REISE_STATUS_ANTWORT:
            self.reise_status = daten
            self.geladen = True

        elif typ == REISE_GESTARTET:
            if daten.get("erfolg"):
                self.netzwerk_client.nachricht_senden(REISE_STATUS_LADEN, {})

        elif typ == REISE_BEENDET:
            if daten.get("erfolg"):
                self.netzwerk_client.nachricht_senden(REISE_STATUS_LADEN, {})

        elif typ == REISE_BELOHNUNGEN_ANTWORT:
            self.kampf_ergebnisse = daten.get(SCHLUESSEL_KAMPF_ERGEBNISSE, [])
            self.gesamt_gold = daten.get(SCHLUESSEL_GESAMT_GOLD, 0)
            self.gesamt_xp = daten.get(SCHLUESSEL_GESAMT_XP, 0)
            anzahl = daten.get(SCHLUESSEL_ANZAHL_QUESTS, 0)

            if anzahl > 0:
                self.zustand = "kampf"
                self.aktueller_kampf_index = 0
                self.kampf_anzeigen()
            else:
                self.netzwerk_client.nachricht_senden(REISE_BELOHNUNGEN_ABHOLEN, {})

        elif typ == REISE_BELOHNUNGEN_ABGEHOLT:
            self.zustand = "status"
            self.netzwerk_client.nachricht_senden(REISE_STATUS_LADEN, {})

    def kampf_anzeigen(self):
        if self.aktueller_kampf_index < len(self.kampf_ergebnisse):
            ergebnis = self.kampf_ergebnisse[self.aktueller_kampf_index]
            kampf_szene = KampfAnzeigeSzene(
                self.szenen_manager,
                self.netzwerk_client,
                ergebnis,
                self.charakter_daten,
                self,
                True
            )
            self.szenen_manager.szene_wechseln(kampf_szene)
        else:
            self.netzwerk_client.nachricht_senden(REISE_BELOHNUNGEN_ABHOLEN, {})

    def fortsetzen_nach_kampf(self):
        self.aktueller_kampf_index += 1
        if self.aktueller_kampf_index < len(self.kampf_ergebnisse):
            self.kampf_anzeigen()
        else:
            self.netzwerk_client.nachricht_senden(REISE_BELOHNUNGEN_ABHOLEN, {})

    def events_verarbeiten(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.zurueck()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._buttons_pruefen(event.pos)

    def _buttons_pruefen(self, pos):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE
        mitte_x = b // 2

        if self.zustand == "status" and self.reise_status:
            if not self.reise_status.get("aktiv"):
                for i, btn in enumerate(self.dauer_buttons):
                    if btn.collidepoint(pos):
                        self.gewaehlte_dauer = self.dauer_optionen[i]

                knopf_start = pygame.Rect(mitte_x - self.knopf_breite // 2, int(h * 0.52), self.knopf_breite, self.knopf_hoehe)
                if knopf_start.collidepoint(pos):
                    self.netzwerk_client.nachricht_senden(REISE_STARTEN, {"max_dauer": self.gewaehlte_dauer})
            else:
                if self.reise_status.get("offene_belohnungen", 0) > 0:
                    knopf_belohnung = pygame.Rect(mitte_x - self.knopf_breite // 2, int(h * 0.42), self.knopf_breite, self.knopf_hoehe)
                    if knopf_belohnung.collidepoint(pos):
                        self.netzwerk_client.nachricht_senden(REISE_BELOHNUNGEN_LADEN, {})

                    knopf_beenden = pygame.Rect(mitte_x - self.knopf_breite // 2, int(h * 0.42) + self.knopf_hoehe + 20, self.knopf_breite, self.knopf_hoehe)
                else:
                    knopf_beenden = pygame.Rect(mitte_x - self.knopf_breite // 2, int(h * 0.42), self.knopf_breite, self.knopf_hoehe)

                if knopf_beenden.collidepoint(pos):
                    self.netzwerk_client.nachricht_senden(REISE_BEENDEN, {})

        knopf_zurueck = pygame.Rect(20, h - 60, 120, 40)
        if knopf_zurueck.collidepoint(pos):
            self.zurueck()

    def updaten(self, delta_zeit: float):
        while True:
            nachricht = self.netzwerk_client.nachricht_holen()
            if not nachricht:
                break
            self.nachricht_empfangen(nachricht)

    def zeichnen(self, screen):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE

        screen.fill(config.FARBE_HINTERGRUND)

        if self.zustand == "status":
            self._zeichnen_status(screen, b, h)
        elif self.zustand == "kampf":
            self._zeichnen_kampf_warten(screen, b, h)

    def _zeichnen_status(self, screen, b, h):
        mitte_x = b // 2

        titel = self.schrift_titel.render("Auf Reisen", True, config.FARBE_TEXT)
        screen.blit(titel, (mitte_x - titel.get_width() // 2, int(h * 0.1)))

        if not self.reise_status or not self.reise_status.get("aktiv"):
            text = self.schrift_normal.render("Dein Held wartet auf Abenteuer", True, config.FARBE_TEXT)
            screen.blit(text, (mitte_x - text.get_width() // 2, int(h * 0.25)))

            info = self.schrift_klein.render("Dein Held erledigt alle 30-60 Min eine Quest", True, config.FARBE_TEXT_GEDIMMT)
            screen.blit(info, (mitte_x - info.get_width() // 2, int(h * 0.32)))

            dauer_titel = self.schrift_klein.render("Reisedauer wählen:", True, config.FARBE_TEXT_GEDIMMT)
            screen.blit(dauer_titel, (mitte_x - dauer_titel.get_width() // 2, int(h * 0.38)))

            for i, btn in enumerate(self.dauer_buttons):
                farbe = config.FARBE_PANEL
                rand = 1
                if self.dauer_optionen[i] == self.gewaehlte_dauer:
                    farbe = config.FARBE_AKZENT
                    rand = 3
                pygame.draw.rect(screen, farbe, btn)
                pygame.draw.rect(screen, config.FARBE_RAND, btn, rand)
                label = self.schrift_klein.render(self.dauer_labels[i], True, config.FARBE_TEXT)
                screen.blit(label, (btn.x + (btn.width - label.get_width()) // 2,
                                    btn.y + (btn.height - label.get_height()) // 2))

            knopf = pygame.Rect(mitte_x - self.knopf_breite // 2, int(h * 0.52), self.knopf_breite, self.knopf_hoehe)
            pygame.draw.rect(screen, config.FARBE_AKZENT, knopf)
            pygame.draw.rect(screen, config.FARBE_WEISS, knopf, 2)
            text = self.schrift_normal.render("Auf Reisen schicken", True, config.FARBE_WEISS)
            screen.blit(text, (mitte_x - text.get_width() // 2, int(h * 0.52) + (self.knopf_hoehe - text.get_height()) // 2))
        else:
            from datetime import datetime
            gestartet = self.reise_status.get("gestartet_am", "Unbekannt")
            text = self.schrift_gross.render(f"Held ist auf Reisen seit {gestartet[:10]}", True, config.FARBE_TEXT)
            screen.blit(text, (mitte_x - text.get_width() // 2, int(h * 0.12)))

            max_dauer = self.reise_status.get("max_dauer", 14400)
            try:
                start = datetime.fromisoformat(gestartet)
                jetzt = datetime.now()
                verbleibend = (jetzt - start).total_seconds()
                verbraucht = min(verbleibend, max_dauer)
            except:
                verbraucht = 0

            fortschritt = verbraucht / max_dauer if max_dauer > 0 else 0

            fortschritt_balken_x = int(b * 0.2)
            fortschritt_balken_y = int(h * 0.20)
            fortschritt_balken_b = int(b * 0.6)
            fortschritt_balken_h = int(h * 0.025)
            pygame.draw.rect(screen, config.FARBE_DUNKELGRAU, (fortschritt_balken_x, fortschritt_balken_y, fortschritt_balken_b, fortschritt_balken_h))
            pygame.draw.rect(screen, config.FARBE_AKZENT, (fortschritt_balken_x, fortschritt_balken_y, fortschritt_balken_b * fortschritt, fortschritt_balken_h))
            pygame.draw.rect(screen, config.FARBE_RAND, (fortschritt_balken_x, fortschritt_balken_y, fortschritt_balken_b, fortschritt_balken_h), 1)

            std_verbraucht = int(verbraucht // 3600)
            min_verbraucht = int((verbraucht % 3600) // 60)
            sek_verbraucht = int(verbraucht % 60)
            std_max = int(max_dauer // 3600)

            zeit_text = f"Auf Reisen: {std_verbraucht:02d}:{min_verbraucht:02d}:{sek_verbraucht:02d} / {std_max:02d}:00:00"
            zeit_render = self.schrift_klein.render(zeit_text, True, config.FARBE_TEXT)
            screen.blit(zeit_render, (fortschritt_balken_x, fortschritt_balken_y + fortschritt_balken_h + 5))

            quests = self.reise_status.get("quests_abgeschlossen", 0)
            text = self.schrift_normal.render(f"Quests abgeschlossen: {quests}", True, config.FARBE_TEXT)
            screen.blit(text, (mitte_x - text.get_width() // 2, int(h * 0.28)))

            naechste = self.reise_status.get("naechste_quest_in", 0)
            minuten = naechste // 60
            sekunden = naechste % 60
            text = self.schrift_normal.render(f"Nächste Quest in: {minuten:02d}:{sekunden:02d}", True, config.FARBE_AKZENT)
            screen.blit(text, (mitte_x - text.get_width() // 2, int(h * 0.35)))

            if self.reise_status.get("offene_belohnungen", 0) > 0:
                knopf = pygame.Rect(mitte_x - self.knopf_breite // 2, int(h * 0.42), self.knopf_breite, self.knopf_hoehe)
                pygame.draw.rect(screen, config.FARBE_AKZENT, knopf)
                text = self.schrift_normal.render("Belohnungen abholen", True, config.FARBE_WEISS)
                screen.blit(text, (mitte_x - text.get_width() // 2, int(h * 0.42) + (self.knopf_hoehe - text.get_height()) // 2))

                knopf_beenden = pygame.Rect(mitte_x - self.knopf_breite // 2, int(h * 0.42) + self.knopf_hoehe + 20, self.knopf_breite, self.knopf_hoehe)
            else:
                knopf_beenden = pygame.Rect(mitte_x - self.knopf_breite // 2, int(h * 0.42), self.knopf_breite, self.knopf_hoehe)

            pygame.draw.rect(screen, config.FARBE_PANEL, knopf_beenden)
            pygame.draw.rect(screen, config.FARBE_RAND, knopf_beenden, 1)
            text = self.schrift_normal.render("Reise beenden", True, config.FARBE_TEXT)
            screen.blit(text, (mitte_x - text.get_width() // 2, knopf_beenden.y + (self.knopf_hoehe - text.get_height()) // 2))

        pygame.draw.rect(screen, config.FARBE_PANEL, self.zurueck_button)
        pygame.draw.rect(screen, config.FARBE_RAND, self.zurueck_button, 1)
        text = self.schrift_klein.render("← Zurück", True, config.FARBE_TEXT)
        screen.blit(text, (self.zurueck_button.x + (self.zurueck_button.width - text.get_width()) // 2,
                           self.zurueck_button.y + (self.zurueck_button.height - text.get_height()) // 2))

    def _zeichnen_kampf_warten(self, screen, b, h):
        mitte_x = b // 2
        text = self.schrift_gross.render("Kampfanimation läuft...", True, config.FARBE_AKZENT)
        screen.blit(text, (mitte_x - text.get_width() // 2, h // 2))

        fortschritt = f"Kampf {self.aktueller_kampf_index + 1} von {len(self.kampf_ergebnisse)}"
        text = self.schrift_normal.render(fortschritt, True, config.FARBE_TEXT)
        screen.blit(text, (mitte_x - text.get_width() // 2, h // 2 + 50))

    def zurueck(self):
        from spiel.szenen.charakter_uebersicht_szene import CharakterUebersichtSzene
        zurueck = CharakterUebersichtSzene(self.szenen_manager, self.netzwerk_client)
        self.szenen_manager.szene_wechseln(zurueck)