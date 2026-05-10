"""
spiel/szenen/arena_szene.py - Arena Szene mit PvP-Kämpfen

Abhängigkeiten: pygame, config, basis_szne
"""

import pygame
import config
from datetime import datetime
from ..kern.basis_szene import BasisSzene
from netzwerk.nachrichten import (
    ARENA_LADEN, ARENA_ANTWORT, ARENA_KAMPF_STARTEN, ARENA_KAMPF_ERGEBNIS,
    ARENA_SHOP_KAUFEN, ARENA_SHOP_GEKAUFT,
    SCHLUESSEL_GEGNER_ID, SCHLUESSEL_ARTIKEL_ID
)


class ArenaSzene(BasisSzene):
    def __init__(self, szenen_manager, netzwerk_client, charakter_daten=None):
        self.szenen_manager = szenen_manager
        self.netzwerk_client = netzwerk_client
        self.charakter_daten = charakter_daten

        self.zustand = "auswahl"
        self.gegner = []
        self.ausgewaehlter_gegner = None
        self.arena_stats = {}
        self.rang = {}
        self.letztes_ergebnis = None
        self.arena_shop = {}
        self.start_delay = 0.0
        self.angefragt = False
        self.arena_geladen = False

        self._layout_berechnen()

    def _layout_berechnen(self):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE

        self.schrift_klein = pygame.font.Font(None, max(12, int(h * 0.018)))
        self.schrift_normal = pygame.font.Font(None, max(16, int(h * 0.024)))
        self.schrift_gross = pygame.font.Font(None, max(28, int(h * 0.04)))
        self.schrift_titel = pygame.font.Font(None, max(36, int(h * 0.05)))

        self.titel_y = int(h * 0.08)
        self.karten_start_x = int(b * 0.05)
        self.karten_start_y = int(h * 0.15)
        self.karten_breite = int(b * 0.28)
        self.karten_hoehe = int(h * 0.50)
        self.karten_abstand = int(b * 0.04)

        self.zurueck_button = pygame.Rect(20, h - 50, 100, 35)

    def updaten(self, delta_zeit: float):
        if not self.arena_geladen:
            self.start_delay += delta_zeit
            if self.start_delay >= 0.1:
                self.netzwerk_client.nachricht_senden(ARENA_LADEN, {})
                self.arena_geladen = True
                self.angefragt = True

        while True:
            nachricht = self.netzwerk_client.nachricht_holen()
            if not nachricht:
                break
            self.nachricht_empfangen(nachricht)

    def nachricht_empfangen(self, nachricht):
        typ = nachricht.get("typ")
        daten = nachricht.get("daten", {})

        if typ == ARENA_ANTWORT:
            self.gegner = daten.get("gegner", [])
            self.arena_stats = daten.get("stats", {})
            self.rang = daten.get("rang", {})
            self.arena_shop = daten.get("arena_shop", {})

        elif typ == ARENA_KAMPF_ERGEBNIS:
            self.letztes_ergebnis = daten
            self.zustand = "ergebnis"

        elif typ == ARENA_SHOP_GEKAUFT:
            if daten.get("erfolg"):
                self.arena_stats["ehrenmarken"] = daten.get("marken_rest", 0)

    def events_verarbeiten(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.zurueck()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.ausgewaehlter_gegner and hasattr(self, 'detail_popup_rect'):
                        if self.close_button_rect and self.close_button_rect.collidepoint(event.pos):
                            self.ausgewaehlter_gegner = None
                            return
                        if self.challenge_button_rect and self.challenge_button_rect.collidepoint(event.pos):
                            self._herausfordern(event.pos)
                            return
                        if not self.detail_popup_rect.collidepoint(event.pos):
                            self.ausgewaehlter_gegner = None
                            return

                    if self.zurueck_button.collidepoint(event.pos):
                        self.zurueck()
                    elif self.zustand == "auswahl":
                        self._gegner_karten_pruefen(event.pos)
                    elif self.zustand == "ergebnis":
                        if hasattr(self, 'neue_gegner_btn') and self.neue_gegner_btn.collidepoint(event.pos):
                            self.zustand = "auswahl"
                            self.netzwerk_client.nachricht_senden(ARENA_LADEN, {})

    def _gegner_karten_pruefen(self, pos):
        for i in range(len(self.gegner)):
            x = self.karten_start_x + i * (self.karten_breite + self.karten_abstand)
            if x <= pos[0] <= x + self.karten_breite and self.karten_start_y <= pos[1] <= self.karten_start_y + self.karten_hoehe:
                self.ausgewaehlter_gegner = self.gegner[i]
                return

    def _herausfordern(self, pos=None):
        if not self.ausgewaehlter_gegner:
            return
        self.netzwerk_client.nachricht_senden(ARENA_KAMPF_STARTEN, {
            SCHLUESSEL_GEGNER_ID: self.ausgewaehlter_gegner["charakter_id"]
        })

    def zeichnen(self, screen):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE
        screen.fill(config.FARBE_HINTERGRUND)

        if self.zustand == "auswahl":
            self._zeichnen_auswahl(screen, b, h)
        elif self.zustand == "ergebnis":
            self._zeichnen_ergebnis(screen, b, h)

    def _zeichnen_auswahl(self, screen, b, h):
        titel = self.schrift_titel.render("Arena", True, config.FARBE_TEXT)
        screen.blit(titel, (20, 20))

        rang_symbol = self.rang.get("symbol", "🥉")
        rang_name = self.rang.get("name", "Bronze")
        rang_punkte = self.rang.get("punkte", 0)
        rang_text = f"{rang_symbol} {rang_name} {rang_punkte}"
        rang_render = self.schrift_normal.render(rang_text, True, config.FARBE_TEXT)
        screen.blit(rang_render, (b - 200, 20))

        marken = self.arena_stats.get("ehrenmarken", 0)
        marken_text = f"⚔ {marken} Marken"
        marken_render = self.schrift_klein.render(marken_text, True, config.FARBE_XP)
        screen.blit(marken_render, (b - 200, 50))

        ausgewaehlt_index = -1
        if self.ausgewaehlter_gegner and self.ausgewaehlter_gegner in self.gegner:
            ausgewaehlt_index = self.gegner.index(self.ausgewaehlter_gegner)

        for i, g in enumerate(self.gegner):
            x = self.karten_start_x + i * (self.karten_breite + self.karten_abstand)
            self._zeichnen_gegner_karte(screen, x, self.karten_start_y, g, i == ausgewaehlt_index)

        if self.ausgewaehlter_gegner:
            self._zeichnen_gegner_detail(screen, b, h, self.ausgewaehlter_gegner)

        pygame.draw.rect(screen, config.FARBE_PANEL, self.zurueck_button)
        pygame.draw.rect(screen, config.FARBE_RAND, self.zurueck_button, 1)
        zurueck_text = self.schrift_klein.render("← Zurück", True, config.FARBE_TEXT)
        screen.blit(zurueck_text, (self.zurueck_button.x + (self.zurueck_button.width - zurueck_text.get_width()) // 2,
                                   self.zurueck_button.y + (self.zurueck_button.height - zurueck_text.get_height()) // 2))

    def _zeichnen_gegner_karte(self, screen, x, y, gegner, ausgewaehlt):
        bg = config.FARBE_AKZENT if ausgewaehlt else config.FARBE_PANEL
        pygame.draw.rect(screen, bg, (x, y, self.karten_breite, self.karten_hoehe))
        pygame.draw.rect(screen, config.FARBE_RAND, (x, y, self.karten_breite, self.karten_hoehe), 2 if ausgewaehlt else 1)

        rang = gegner.get("rang", {})
        rang_text = f"{rang.get('symbol', '')} {rang.get('name', '')}"
        text = self.schrift_klein.render(rang_text, True, config.FARBE_AKZENT)
        screen.blit(text, (x + 10, y + 10))

        name = gegner.get("name", "Unbekannt")
        name_text = self.schrift_gross.render(name[:15], True, config.FARBE_TEXT)
        screen.blit(name_text, (x + 10, y + 35))

        level = gegner.get("level", 1)
        level_text = self.schrift_normal.render(f"Level {level}", True, config.FARBE_TEXT_GEDIMMT)
        screen.blit(level_text, (x + 10, y + 70))

        klasse = gegner.get("klassen_id", "Krieger")
        klasse_text = self.schrift_klein.render(klasse, True, config.FARBE_TEXT_GEDIMMT)
        screen.blit(klasse_text, (x + 10, y + 95))

        siege = gegner.get("siege", 0)
        nl = gegner.get("niederlagen", 0)
        stats_text = self.schrift_klein.render(f"S: {siege} | N: {nl}", True, config.FARBE_TEXT)
        screen.blit(stats_text, (x + 10, y + 130))

        punkte = gegner.get("rang_punkte", 0)
        punkte_text = self.schrift_klein.render(f"{punkte} Punkte", True, config.FARBE_TEXT_GEDIMMT)
        screen.blit(punkte_text, (x + 10, y + 155))

    def _zeichnen_gegner_detail(self, screen, b, h, gegner):
        overlay = pygame.Surface((b, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        panel_breite = 600
        panel_hoehe = 450
        panel_x = (b - panel_breite) // 2
        panel_y = (h - panel_hoehe) // 2
        self.detail_popup_rect = pygame.Rect(panel_x, panel_y, panel_breite, panel_hoehe)

        pygame.draw.rect(screen, config.FARBE_PANEL, (panel_x, panel_y, panel_breite, panel_hoehe))
        pygame.draw.rect(screen, config.FARBE_RAND, (panel_x, panel_y, panel_breite, panel_hoehe), 2)

        y = panel_y + 20

        name = self.schrift_gross.render(gegner.get("name", "Unbekannt")[:20], True, config.FARBE_TEXT)
        screen.blit(name, (panel_x + 20, y))
        y += 35

        klasse = gegner.get("klassen_id", "Krieger")
        level = gegner.get("level", 1)
        level_text = self.schrift_normal.render(f"Level {level} - {klasse}", True, config.FARBE_TEXT_GEDIMMT)
        screen.blit(level_text, (panel_x + 20, y))
        y += 30

        rang = gegner.get("rang", {})
        rang_symbol = rang.get("symbol", "🥉")
        rang_name = rang.get("name", "Bronze")
        rang_punkte = gegner.get("rang_punkte", 0)
        rang_text = self.schrift_normal.render(f"{rang_symbol} {rang_name} ({rang_punkte} Punkte)", True, config.FARBE_AKZENT)
        screen.blit(rang_text, (panel_x + 20, y))
        y += 30

        siege = gegner.get("siege", 0)
        niederlagen = gegner.get("niederlagen", 0)
        bilanz_text = self.schrift_klein.render(f"Siege: {siege} | Niederlagen: {niederlagen}", True, config.FARBE_TEXT_GEDIMMT)
        screen.blit(bilanz_text, (panel_x + 20, y))
        y += 30

        pygame.draw.line(screen, config.FARBE_RAND, (panel_x + 20, y), (panel_x + panel_breite - 20, y), 1)
        y += 20

        stats_text = self.schrift_klein.render("Stats:", True, config.FARBE_TEXT)
        screen.blit(stats_text, (panel_x + 20, y))
        y += 22
        hp = gegner.get('max_hp', gegner.get('max_lebenspunkte', 0))
        angriff = gegner.get('physischer_schaden', gegner.get('angriff', 0))
        verteidigung = gegner.get('ruestung', gegner.get('verteidigung', 0))
        krit = gegner.get('krit_chance', 0)
        ausweichen = gegner.get('ausweichen', 5)
        stats_line1 = f"HP: {hp} | Angriff: {angriff} | Verteidigung: {verteidigung}"
        stats_line2 = f"Krit: {krit}% | Ausweichen: {ausweichen}%"
        screen.blit(self.schrift_klein.render(stats_line1, True, config.FARBE_AKZENT), (panel_x + 20, y))
        y += 20
        screen.blit(self.schrift_klein.render(stats_line2, True, config.FARBE_AKZENT), (panel_x + 20, y))
        y += 30

        pygame.draw.line(screen, config.FARBE_RAND, (panel_x + 20, y), (panel_x + panel_breite - 20, y), 1)
        y += 20

        skills = gegner.get("ausgeruestete_skills", {})
        if skills:
            aktiv = skills.get("aktiv", [])
            passiv = skills.get("passiv", [])
            aktiv_names = [s.get("skill_id", "?") for s in aktiv if s]
            passiv_names = [s.get("skill_id", "?") for s in passiv if s]
            if aktiv_names:
                screen.blit(self.schrift_klein.render(f"Aktiv: {', '.join(aktiv_names)}", True, config.FARBE_TEXT), (panel_x + 20, y))
                y += 20
            if passiv_names:
                screen.blit(self.schrift_klein.render(f"Passiv: {', '.join(passiv_names)}", True, config.FARBE_TEXT), (panel_x + 20, y))
                y += 20
        else:
            screen.blit(self.schrift_klein.render("Keine Skills ausgerüstet", True, config.FARBE_TEXT_GEDIMMT), (panel_x + 20, y))
            y += 20

        y += 20
        pygame.draw.line(screen, config.FARBE_RAND, (panel_x + 20, y), (panel_x + panel_breite - 20, y), 1)
        y += 25

        btn_breite = 180
        btn_hoehe = 40
        btn_abstand = 20

        close_btn = pygame.Rect(panel_x + (panel_breite // 2) - btn_breite - btn_abstand // 2, y, btn_breite, btn_hoehe)
        pygame.draw.rect(screen, config.FARBE_DUNKELGRAU, close_btn)
        pygame.draw.rect(screen, config.FARBE_RAND, close_btn, 1)
        close_text = self.schrift_klein.render("✕ Schließen", True, config.FARBE_TEXT)
        screen.blit(close_text, (close_btn.x + (btn_breite - close_text.get_width()) // 2,
                                close_btn.y + (btn_hoehe - close_text.get_height()) // 2))
        self.close_button_rect = close_btn

        challenge_btn = pygame.Rect(panel_x + (panel_breite // 2) + btn_abstand // 2, y, btn_breite, btn_hoehe)
        pygame.draw.rect(screen, config.FARBE_AKZENT, challenge_btn)
        pygame.draw.rect(screen, config.FARBE_WEISS, challenge_btn, 2)
        challenge_text = self.schrift_klein.render("⚔ Herausfordern", True, config.FARBE_WEISS)
        screen.blit(challenge_text, (challenge_btn.x + (btn_breite - challenge_text.get_width()) // 2,
                                     challenge_btn.y + (btn_hoehe - challenge_text.get_height()) // 2))
        self.challenge_button_rect = challenge_btn

    def _zeichnen_shop(self, screen, b, h):
        titel = self.schrift_titel.render("Arena-Shop", True, config.FARBE_TEXT)
        screen.blit(titel, (20, 20))

        marken = self.arena_stats.get("ehrenmarken", 0)
        marken_text = self.schrift_normal.render(f"Ehrenmarken: {marken}", True, config.FARBE_XP)
        screen.blit(marken_text, (b - 200, 25))

        artikel_liste = list(self.arena_shop.items())
        for i, (artikel_id, artikel) in enumerate(artikel_liste):
            x = int(b * 0.1) + i * int(b * 0.22)
            y = int(h * 0.20)
            breite = int(b * 0.20)
            hoehe = int(h * 0.40)

            pygame.draw.rect(screen, config.FARBE_PANEL, (x, y, breite, hoehe))
            pygame.draw.rect(screen, config.FARBE_RAND, (x, y, breite, hoehe), 1)

            name = artikel_id.replace("_", " ").title()
            name_text = self.schrift_normal.render(name[:20], True, config.FARBE_TEXT)
            screen.blit(name_text, (x + 10, y + 10))

            marken_preis = artikel.get("marken", 0)
            preis_text = self.schrift_klein.render(f"{marken_preis} Marken", True, config.FARBE_XP if marken >= marken_preis else config.FARBE_HP)
            screen.blit(preis_text, (x + 10, y + 40))

            typ = artikel.get("typ", "")
            effekt_text = self.schrift_klein.render(f"Typ: {typ}", True, config.FARBE_TEXT_GEDIMMT)
            screen.blit(effekt_text, (x + 10, y + 70))

        pygame.draw.rect(screen, config.FARBE_PANEL, self.zurueck_button)
        pygame.draw.rect(screen, config.FARBE_RAND, self.zurueck_button, 1)
        zurueck_text = self.schrift_klein.render("← Zurück", True, config.FARBE_TEXT)
        screen.blit(zurueck_text, (self.zurueck_button.x + (self.zurueck_button.width - zurueck_text.get_width()) // 2,
                                   self.zurueck_button.y + (self.zurueck_button.height - zurueck_text.get_height()) // 2))

    def _zeichnen_ergebnis(self, screen, b, h):
        if not self.letztes_ergebnis:
            return

        gewonnen = self.letztes_ergebnis.get("gewonnen", False)

        if gewonnen:
            ergebnis_text = self.schrift_gross.render("SIEG!", True, config.FARBE_ERFOLG)
        else:
            ergebnis_text = self.schrift_gross.render("NIEDERLAGE", True, config.FARBE_HP)
        screen.blit(ergebnis_text, (b // 2 - ergebnis_text.get_width() // 2, int(h * 0.2)))

        rang_delta = self.letztes_ergebnis.get("rang_delta", 0)
        if rang_delta >= 0:
            delta_text = self.schrift_normal.render(f"+{rang_delta} Rang-Punkte", True, config.FARBE_ERFOLG)
        else:
            delta_text = self.schrift_normal.render(f"{rang_delta} Rang-Punkte", True, config.FARBE_HP)
        screen.blit(delta_text, (b // 2 - delta_text.get_width() // 2, int(h * 0.35)))

        gold = self.letztes_ergebnis.get("gold", 0)
        xp = self.letztes_ergebnis.get("xp", 0)
        marken = self.letztes_ergebnis.get("marken", 0)

        belohnung_text = self.schrift_normal.render(f"Gold: {gold} | XP: {xp} | Marken: {marken}", True, config.FARBE_XP)
        screen.blit(belohnung_text, (b // 2 - belohnung_text.get_width() // 2, int(h * 0.45)))

        rang = self.letztes_ergebnis.get("rang", {})
        rang_text = self.schrift_normal.render(f"Rang: {rang.get('symbol', '')} {rang.get('name', '')}", True, config.FARBE_AKZENT)
        screen.blit(rang_text, (b // 2 - rang_text.get_width() // 2, int(h * 0.55)))

        b_btn = int(b * 0.30)
        self.neue_gegner_btn = pygame.Rect((b - b_btn) // 2, int(h * 0.65), b_btn, 45)
        pygame.draw.rect(screen, config.FARBE_AKZENT, self.neue_gegner_btn)
        pygame.draw.rect(screen, config.FARBE_WEISS, self.neue_gegner_btn, 2)
        neue_text = self.schrift_normal.render("Neue Gegner", True, config.FARBE_WEISS)
        screen.blit(neue_text, (self.neue_gegner_btn.x + (b_btn - neue_text.get_width()) // 2,
                                self.neue_gegner_btn.y + (45 - neue_text.get_height()) // 2))

        pygame.draw.rect(screen, config.FARBE_PANEL, self.zurueck_button)
        pygame.draw.rect(screen, config.FARBE_RAND, self.zurueck_button, 1)
        zurueck_text = self.schrift_klein.render("← Zurück", True, config.FARBE_TEXT)
        screen.blit(zurueck_text, (self.zurueck_button.x + (self.zurueck_button.width - zurueck_text.get_width()) // 2,
                                   self.zurueck_button.y + (self.zurueck_button.height - zurueck_text.get_height()) // 2))

    def zurueck(self):
        from .charakter_uebersicht_szene import CharakterUebersichtSzene
        zurueck = CharakterUebersichtSzene(self.szenen_manager, self.netzwerk_client)
        self.szenen_manager.szene_wechseln(zurueck)