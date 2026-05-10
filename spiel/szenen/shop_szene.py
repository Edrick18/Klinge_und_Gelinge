"""
spiel/szenen/shop_szene.py - Shop Szene mit 12 Slots + Details + Tränke

Abhängigkeiten: pygame, config, basis_szne
"""

import pygame
import config
from datetime import datetime
from ..kern.basis_szene import BasisSzene
from netzwerk.nachrichten import (
    SHOP_LADEN, SHOP_ANTWORT, SHOP_REROLL, SHOP_REROLL_ANTWORT,
    SHOP_KAUFEN, SHOP_GEKAUFT, SHOP_KAUFEN_FEHLER,
    TRANK_ENTFERNEN, TRANK_ENTFERNT,
    SCHLUESSEL_SHOP_SLOT, SCHLUESSEL_ANGEBOTE, SCHLUESSEL_TRANK_ID, SCHLUESSEL_AKTIVE_TRAENKE,
    ARENA_LADEN, ARENA_ANTWORT, ARENA_SHOP_KAUFEN, ARENA_SHOP_GEKAUFT, ARENA_SHOP_KAUFEN_FEHLER
)


ITEM_RARITAET_FARBEN = {
    "normal": (160, 160, 160),
    "magisch": (30, 200, 30),
    "selten": (30, 100, 255),
    "episch": (180, 70, 255),
    "legendaer": (255, 180, 30),
}

STAT_ANZEIGEN = {
    "staerke": "STÄRKE",
    "vitalitaet": "VITALITÄT",
    "weisheit": "WEISHEIT",
    "glueck": "GLÜCK",
    "beweglichkeit": "BEWEGL.",
    "charisma": "CHARISMA"
}

TRANK_STAT_ANZEIGEN = {
    "staerke": "Stärke",
    "vitalitaet": "Vitalität",
    "weisheit": "Weisheit",
    "glueck": "Glück",
    "beweglichkeit": "Beweglichkeit",
    "charisma": "Charisma"
}


class ShopSzene(BasisSzene):
    def __init__(self, szenen_manager, netzwerk_client, charakter_daten=None):
        self.szenen_manager = szenen_manager
        self.netzwerk_client = netzwerk_client
        self.charakter_daten = charakter_daten

        self.angebote = []
        self.aktive_traenke = []
        self.gold = 0
        self.ehrenmarken = 0
        self.reroll_anzahl = 0
        self.reroll_kosten = 0
        self.gueltig_bis = ""
        self.ausgewaehlter_slot = None
        self.entfernen_buttons = []
        self.kaufen_button_rect = None
        self.arena_shop_buttons = []

        self._layout_berechnen()
        self.netzwerk_client.nachricht_senden(SHOP_LADEN, {})
        import threading
        def send_arena_laden():
            import time
            time.sleep(0.1)
            self.netzwerk_client.nachricht_senden(ARENA_LADEN, {})
        threading.Thread(target=send_arena_laden, daemon=True).start()

    def _layout_berechnen(self):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE

        self.schrift_klein = pygame.font.Font(None, max(12, int(h * 0.018)))
        self.schrift_normal = pygame.font.Font(None, max(16, int(h * 0.024)))
        self.schrift_gross = pygame.font.Font(None, max(28, int(h * 0.04)))
        self.schrift_titel = pygame.font.Font(None, max(36, int(h * 0.05)))
        self.schrift_sehr_klein = pygame.font.Font(None, max(10, int(h * 0.015)))

        self.slot_breite = int(b * 0.17)
        self.slot_hoehe = int(h * 0.15)
        self.slot_abstand = int(b * 0.01)
        self.grid_start_x = int(b * 0.01)
        self.grid_start_y = int(h * 0.10)
        self.spalten = 3
        self.reihen = 4

        self.detail_x = int(b * 0.60)
        self.detail_breite = int(b * 0.38)

        self.zurueck_btn = pygame.Rect(10, h - 35, 90, 28)

    def nachricht_empfangen(self, nachricht):
        typ = nachricht.get("typ")
        daten = nachricht.get("daten", {})

        if typ == SHOP_ANTWORT:
            self.angebote = daten.get(SCHLUESSEL_ANGEBOTE, [])
            self.gold = daten.get("gold", 0)
            self.reroll_anzahl = daten.get("reroll_anzahl", 0)
            self.reroll_kosten = daten.get("reroll_kosten", 0)
            self.gueltig_bis = daten.get("gueltig_bis", "")
            self.aktive_traenke = daten.get(SCHLUESSEL_AKTIVE_TRAENKE, [])

        elif typ == SHOP_REROLL_ANTWORT:
            if daten.get("erfolg"):
                self.angebote = daten.get(SCHLUESSEL_ANGEBOTE, [])
                self.gold = daten.get("gold_rest", 0)
                self.reroll_anzahl = daten.get("reroll_anzahl", 0)
                self.reroll_kosten = daten.get("naechste_kosten", 0)
                self.ausgewaehlter_slot = None

        elif typ == SHOP_GEKAUFT:
            if daten.get("erfolg"):
                self.gold = daten.get("gold_rest", 0)
                self.ausgewaehlter_slot = None
                self.netzwerk_client.nachricht_senden(SHOP_LADEN, {})

        elif typ == SHOP_KAUFEN_FEHLER:
            self.status_nachricht = daten.get("nachricht", "Fehler")
            self.status_farbe = config.FARBE_WARNUNG

        elif typ == TRANK_ENTFERNT:
            if daten.get("erfolg"):
                self.netzwerk_client.nachricht_senden(SHOP_LADEN, {})

        elif typ == ARENA_ANTWORT:
            stats = daten.get("stats", {})
            self.ehrenmarken = stats.get("ehrenmarken", 0)
            self.arena_shop_daten = daten.get("arena_shop", {})

        elif typ == ARENA_SHOP_GEKAUFT:
            if daten.get("erfolg"):
                self.ehrenmarken = daten.get("marken_rest", 0)
                self.status_nachricht = "Gekauft!"
                self.status_farbe = config.FARBE_ERFOLG
            else:
                self.status_nachricht = daten.get("nachricht", "Fehler")
                self.status_farbe = config.FARBE_WARNUNG

        elif typ == ARENA_SHOP_KAUFEN_FEHLER:
            self.status_nachricht = daten.get("nachricht", "Nicht genug Marken!")
            self.status_farbe = config.FARBE_WARNUNG

    def events_verarbeiten(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.zurueck()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._slots_pruefen(event.pos)
                    self._trank_entfernen_pruefen(event.pos)
                    self._buttons_pruefen(event.pos)
                    self._arena_shop_pruefen(event.pos)

    def _slots_pruefen(self, pos):
        for angebot in self.angebote:
            slot = angebot.get("slot", 0)
            row = slot // self.spalten
            col = slot % self.spalten
            x = self.grid_start_x + col * (self.slot_breite + self.slot_abstand)
            y = self.grid_start_y + row * (self.slot_hoehe + self.slot_abstand)
            if x <= pos[0] <= x + self.slot_breite and y <= pos[1] <= y + self.slot_hoehe:
                self.ausgewaehlter_slot = slot
                return

    def _trank_entfernen_pruefen(self, pos):
        for btn_rect, trank_id in self.entfernen_buttons:
            if btn_rect.collidepoint(pos):
                self.netzwerk_client.nachricht_senden(TRANK_ENTFERNEN, {
                    SCHLUESSEL_TRANK_ID: trank_id
                })
                return

    def _buttons_pruefen(self, pos):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE

        if self.ausgewaehlter_slot is not None and self.kaufen_button_rect:
            if self.kaufen_button_rect.collidepoint(pos):
                angebot = next((a for a in self.angebote if a.get("slot") == self.ausgewaehlter_slot), None)
                if angebot and self.gold >= angebot.get("preis", 0):
                    self.netzwerk_client.nachricht_senden(SHOP_KAUFEN, {
                        SCHLUESSEL_SHOP_SLOT: self.ausgewaehlter_slot
                    })

        reroll_btn = pygame.Rect(int(b * 0.60), int(h * 0.02), int(b * 0.15), 35)
        if reroll_btn.collidepoint(pos) and self.gold >= self.reroll_kosten:
            self.netzwerk_client.nachricht_senden(SHOP_REROLL, {})

        if self.zurueck_btn.collidepoint(pos):
            self.zurueck()

    def _arena_shop_pruefen(self, pos):
        for btn_rect, artikel_id in self.arena_shop_buttons:
            if btn_rect.collidepoint(pos):
                kosten = 3
                if self.ehrenmarken >= kosten:
                    self.netzwerk_client.nachricht_senden(ARENA_SHOP_KAUFEN, {
                        SCHLUESSEL_ARTIKEL_ID: artikel_id
                    })
                else:
                    self.status_nachricht = "Nicht genug Ehrenmarken!"
                    self.status_farbe = config.FARBE_WARNUNG
                return

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

        self._zeichnen_header(screen, b, h)
        self._zeichnen_grid(screen, b, h)
        self._zeichnen_detail_panel(screen, b, h)
        self._zeichnen_traenke_panel(screen, b, h)
        self._zeichnen_arena_bereich(screen, b, h)
        self._zeichnen_buttons(screen, b, h)

    def _zeichnen_header(self, screen, b, h):
        titel = self.schrift_titel.render("SHOP", True, config.FARBE_TEXT)
        screen.blit(titel, (20, 20))

        gold_text = self.schrift_gross.render(f"Gold: {self.gold}", True, config.FARBE_XP)
        screen.blit(gold_text, (b - gold_text.get_width() - 20, 20))

        marken_text = self.schrift_gross.render(f"⚔ {self.ehrenmarken}", True, config.FARBE_AKZENT)
        screen.blit(marken_text, (b - gold_text.get_width() - 150, 20))

        if self.gueltig_bis:
            try:
                gueltig = datetime.fromisoformat(self.gueltig_bis)
                jetzt = datetime.now()
                verbleibend = (gueltig - jetzt).total_seconds()
                stunden = int(verbleibend / 3600)
                if stunden < 0:
                    stunden = 0
                info = self.schrift_klein.render(f"Erneuert sich in {stunden}h", True, config.FARBE_TEXT_GEDIMMT)
                screen.blit(info, (20, 60))
            except:
                pass

    def _zeichnen_grid(self, screen, b, h):
        for angebot in self.angebote:
            slot = angebot.get("slot", 0)
            row = slot // self.spalten
            col = slot % self.spalten
            x = self.grid_start_x + col * (self.slot_breite + self.slot_abstand)
            y = self.grid_start_y + row * (self.slot_hoehe + self.slot_abstand)

            self._zeichnen_slot(screen, x, y, angebot)

    def _zeichnen_slot(self, screen, x, y, angebot):
        inhalt = angebot.get("inhalt", {})
        preis = angebot.get("preis", 0)
        typ = angebot.get("typ", "item")

        bg_farbe = config.FARBE_PANEL
        if self.ausgewaehlter_slot == angebot.get("slot"):
            bg_farbe = config.FARBE_AKZENT

        pygame.draw.rect(screen, bg_farbe, (x, y, self.slot_breite, self.slot_hoehe))
        pygame.draw.rect(screen, config.FARBE_RAND, (x, y, self.slot_breite, self.slot_hoehe), 1)

        if typ == "item":
            raritaet = inhalt.get("raritaet", "normal")
            farbe = ITEM_RARITAET_FARBEN.get(raritaet, (160, 160, 160))
            pygame.draw.rect(screen, farbe, (x, y, self.slot_breite, 6))

            typ_text = self.schrift_klein.render("ITEM", True, config.FARBE_TEXT_GEDIMMT)
            screen.blit(typ_text, (x + self.slot_breite - 40, y + 8))

            name = inhalt.get("name", "Unbekannt")[:15]
            name_text = self.schrift_klein.render(name, True, config.FARBE_TEXT)
            screen.blit(name_text, (x + 5, y + 25))

            basis = inhalt.get("basis_stats", {})
            stats_text = ""
            if "staerke" in basis:
                stats_text = f"+{basis['staerke']} STÄ"
            elif "vitalitaet" in basis:
                stats_text = f"+{basis['vitalitaet']} VIT"
            if stats_text:
                stat_text = self.schrift_klein.render(stats_text, True, config.FARBE_AKZENT)
                screen.blit(stat_text, (x + 5, y + 45))

        else:
            pygame.draw.rect(screen, config.FARBE_AKZENT, (x, y, self.slot_breite, 6))

            typ_text = self.schrift_klein.render("TRANK", True, config.FARBE_TEXT_GEDIMMT)
            screen.blit(typ_text, (x + self.slot_breite - 50, y + 8))

            stat = inhalt.get("stat", "")
            stufe = inhalt.get("stufe", "")
            bonus = int(inhalt.get("bonus", 0) * 100)

            stat_name = TRANK_STAT_ANZEIGEN.get(stat, stat)
            name_text = f"{stat_name}"
            text = self.schrift_klein.render(name_text, True, config.FARBE_TEXT)
            screen.blit(text, (x + 5, y + 25))

            bonus_text = f"+{bonus}% für {stufe}"
            btext = self.schrift_klein.render(bonus_text, True, config.FARBE_AKZENT)
            screen.blit(btext, (x + 5, y + 45))

        preis_farbe = config.FARBE_XP if self.gold >= preis else config.FARBE_HP
        preis_text = self.schrift_normal.render(f"{preis}G", True, preis_farbe)
        screen.blit(preis_text, (x + 5, y + self.slot_hoehe - 25))

    def _zeichnen_detail_panel(self, screen, b, h):
        panel_y = int(h * 0.08)
        panel_hoehe = int(h * 0.64)

        pygame.draw.rect(screen, config.FARBE_PANEL, (self.detail_x, panel_y, self.detail_breite, panel_hoehe))
        pygame.draw.rect(screen, config.FARBE_RAND, (self.detail_x, panel_y, self.detail_breite, panel_hoehe), 1)

        if self.ausgewaehlter_slot is None:
            text = self.schrift_normal.render("Klicke ein Item", True, config.FARBE_TEXT_GEDIMMT)
            screen.blit(text, (self.detail_x + (self.detail_breite - text.get_width()) // 2,
                               panel_y + panel_hoehe // 2))
            return

        angebot = next((a for a in self.angebote if a.get("slot") == self.ausgewaehlter_slot), None)
        if not angebot:
            return

        inhalt = angebot.get("inhalt", {})
        typ = angebot.get("typ", "item")
        preis = angebot.get("preis", 0)

        y = panel_y + 15

        if typ == "item":
            raritaet = inhalt.get("raritaet", "normal")
            rar_farbe = ITEM_RARITAET_FARBEN.get(raritaet, (160, 160, 160))
            pygame.draw.rect(screen, rar_farbe, (self.detail_x + 10, y, self.detail_breite - 20, 8))
            y += 20

            name = inhalt.get("name", "Unbekannt")
            name_text = self.schrift_gross.render(name[:25], True, rar_farbe)
            screen.blit(name_text, (self.detail_x + 10, y))
            y += 40

            typ_text = self.schrift_klein.render(f"Typ: {inhalt.get('typ', 'Unbekannt')}", True, config.FARBE_TEXT)
            screen.blit(typ_text, (self.detail_x + 10, y))
            y += 25

            level = inhalt.get("level", 1)
            level_text = self.schrift_klein.render(f"Level: {level}", True, config.FARBE_TEXT)
            screen.blit(level_text, (self.detail_x + 10, y))
            y += 25

            basis = inhalt.get("basis_stats", {})
            if basis:
                basis_text = self.schrift_normal.render("Basis-Stats:", True, config.FARBE_TEXT)
                screen.blit(basis_text, (self.detail_x + 10, y))
                y += 25

            for stat, wert in basis.items():
                stat_text = self.schrift_klein.render(f"+{wert} {STAT_ANZEIGEN.get(stat, stat.upper())}", True, config.FARBE_AKZENT)
                screen.blit(stat_text, (self.detail_x + 10, y))
                y += 20

            prefixe = inhalt.get("prefixe", [])
            if prefixe:
                y += 10
                pref_text = self.schrift_normal.render("Prefixe:", True, config.FARBE_ERFOLG)
                screen.blit(pref_text, (self.detail_x + 10, y))
                y += 25

            for p in prefixe:
                einheit = p.get("einheit", "")
                typ_name = p.get("typ", "").replace("_", " ").replace("bonus", "").strip()
                pref = self.schrift_klein.render(f"+ {p.get('wert', 0)}{einheit} {typ_name}", True, config.FARBE_ERFOLG)
                screen.blit(pref, (self.detail_x + 10, y))
                y += 20

            suffixe = inhalt.get("suffixe", [])
            if suffixe:
                y += 10
                suf_text = self.schrift_normal.render("Suffixe:", True, config.FARBE_MANA)
                screen.blit(suf_text, (self.detail_x + 10, y))
                y += 25

            for s in suffixe:
                einheit = s.get("einheit", "")
                typ_name = s.get("typ", "").replace("_bonus", "").replace("_", " ").strip()
                suf = self.schrift_klein.render(f"+ {s.get('wert', 0)}{einheit} {typ_name}", True, config.FARBE_MANA)
                screen.blit(suf, (self.detail_x + 10, y))
                y += 20

        else:
            stat = inhalt.get("stat", "")
            stufe = inhalt.get("stufe", "")
            bonus = int(inhalt.get("bonus", 0) * 100)
            dauer = inhalt.get("dauer", 0)

            pygame.draw.rect(screen, config.FARBE_AKZENT, (self.detail_x + 10, y, self.detail_breite - 20, 8))
            y += 20

            stat_name = TRANK_STAT_ANZEIGEN.get(stat, stat)
            name_text = self.schrift_gross.render(f"{stufe.capitalize()} {stat_name}-Trank", True, config.FARBE_TEXT)
            screen.blit(name_text, (self.detail_x + 10, y))
            y += 40

            bonus_text = self.schrift_normal.render(f"+{bonus}% auf {stat_name}", True, config.FARBE_AKZENT)
            screen.blit(bonus_text, (self.detail_x + 10, y))
            y += 30

            tage = dauer // 86400
            dauer_text = self.schrift_klein.render(f"Dauer: {tage} Tag(e)", True, config.FARBE_TEXT)
            screen.blit(dauer_text, (self.detail_x + 10, y))

        y += 15

        btn_breite = int(self.detail_breite * 0.70)
        btn_x = self.detail_x + (self.detail_breite - btn_breite) // 2
        btn_hoehe = int(h * 0.05)
        kaufen_btn = pygame.Rect(btn_x, y, btn_breite, btn_hoehe)
        self.kaufen_button_rect = kaufen_btn
        kaufen_farbe = config.FARBE_AKZENT if self.gold >= preis else config.FARBE_DUNKELGRAU
        pygame.draw.rect(screen, kaufen_farbe, kaufen_btn)
        pygame.draw.rect(screen, config.FARBE_RAND, kaufen_btn, 1)
        kaufen_text = self.schrift_normal.render(f"Kaufen für {preis} Gold", True, config.FARBE_WEISS)
        screen.blit(kaufen_text, (kaufen_btn.x + (kaufen_btn.width - kaufen_text.get_width()) // 2,
                                  kaufen_btn.y + (kaufen_btn.height - kaufen_text.get_height()) // 2))

    def _zeichnen_traenke_panel(self, screen, b, h):
        panel_y = int(h * 0.74)
        panel_hoehe = int(h * 0.21)
        abstand = 10
        panel_breite = (self.detail_breite - abstand) // 2

        pygame.draw.rect(screen, config.FARBE_PANEL, (self.detail_x, panel_y, panel_breite, panel_hoehe))
        pygame.draw.rect(screen, config.FARBE_RAND, (self.detail_x, panel_y, panel_breite, panel_hoehe), 1)

        y = panel_y + 10

        titel = self.schrift_normal.render(f"Tränke ({len(self.aktive_traenke)}/3)", True, config.FARBE_TEXT)
        screen.blit(titel, (self.detail_x + 10, y))
        y += 30

        self.entfernen_buttons = []
        jetzt = datetime.now()

        trank_breite = int(panel_breite / 3) - 5
        trank_hoehe = int(h * 0.13)

        for i, trank in enumerate(self.aktive_traenke):
            try:
                aktiv_bis = datetime.fromisoformat(trank.get("aktiv_bis", ""))
                verbleibend = (aktiv_bis - jetzt).total_seconds()
                tage = int(verbleibend // 86400)
                stunden = int((verbleibend % 86400) // 3600)
                minuten = int((verbleibend % 3600) // 60)
                sekunden = int(verbleibend % 60)
                if tage > 0:
                    zeit_text = f"{tage}d {stunden}h"
                    farbe = config.FARBE_ERFOLG
                elif stunden > 0:
                    zeit_text = f"{stunden}:{minuten:02d}"
                    farbe = config.FARBE_AKZENT
                elif minuten > 0:
                    zeit_text = f"{minuten}:{sekunden:02d}"
                    farbe = config.FARBE_WARNUNG
                else:
                    zeit_text = f"00:{sekunden:02d}"
                    farbe = config.FARBE_WARNUNG
            except:
                zeit_text = "00:00:00"
                farbe = config.FARBE_TEXT_GEDIMMT

            tx = self.detail_x + 10 + i * (trank_breite + 5)
            ty = y

            pygame.draw.rect(screen, config.FARBE_DUNKELGRAU, (tx, ty, trank_breite, trank_hoehe))
            pygame.draw.rect(screen, config.FARBE_RAND, (tx, ty, trank_breite, trank_hoehe), 1)

            stat = trank.get("stat", "")
            stufe = trank.get("stufe", "")
            bonus = int(trank.get("bonus", 0) * 100)
            trank_id = trank.get("id", "")

            stat_name = TRANK_STAT_ANZEIGEN.get(stat, stat)
            info_text = f"{stat_name} {stufe}"
            text = self.schrift_klein.render(info_text, True, config.FARBE_TEXT)
            screen.blit(text, (tx + 5, ty + 5))

            bonus_text = f"+{bonus}%"
            btext = self.schrift_klein.render(bonus_text, True, config.FARBE_AKZENT)
            screen.blit(btext, (tx + 5, ty + 22))

            zeit = self.schrift_klein.render(f"⏱ {zeit_text}", True, farbe)
            screen.blit(zeit, (tx + 5, ty + 42))

            x_groesse = int(trank_breite * 0.15)
            close_btn = pygame.Rect(tx + trank_breite - x_groesse - 3, ty + 3, x_groesse, x_groesse)
            pygame.draw.rect(screen, config.FARBE_HP, close_btn)
            pygame.draw.rect(screen, config.FARBE_RAND, close_btn, 1)
            x_text = self.schrift_klein.render("X", True, config.FARBE_WEISS)
            screen.blit(x_text, (close_btn.x + (close_btn.width - x_text.get_width()) // 2,
                                 close_btn.y + (close_btn.height - x_text.get_height()) // 2))

            self.entfernen_buttons.append((close_btn, trank_id))

    def _zeichnen_arena_bereich(self, screen, b, h):
        panel_y = int(h * 0.74)
        panel_hoehe = int(h * 0.21)
        abstand = 10
        panel_breite = (self.detail_breite - abstand) // 2

        arena_x = self.detail_x + panel_breite + abstand

        pygame.draw.rect(screen, config.FARBE_PANEL, (arena_x, panel_y, panel_breite, panel_hoehe))
        pygame.draw.rect(screen, config.FARBE_RAND, (arena_x, panel_y, panel_breite, panel_hoehe), 1)

        y = panel_y + 5
        titel = self.schrift_normal.render("⚔ Arena-Shop", True, config.FARBE_AKZENT)
        screen.blit(titel, (arena_x + 10, y))
        y += 25

        marken_text = self.schrift_klein.render(f"Marken: {self.ehrenmarken}", True, config.FARBE_XP)
        screen.blit(marken_text, (arena_x + 10, y))
        y += 20

        self.arena_shop_buttons = []

        btn_breite = panel_breite - 20
        btn_hoehe = int(h * 0.045)
        btn_x = arena_x + 10

        erfahrung_btn = pygame.Rect(btn_x, y, btn_breite, btn_hoehe)
        pygame.draw.rect(screen, config.FARBE_DUNKELGRAU, erfahrung_btn)
        pygame.draw.rect(screen, config.FARBE_AKZENT, erfahrung_btn, 2)

        name1 = self.schrift_klein.render("Erfahrungsrolle — 3M", True, config.FARBE_TEXT)
        screen.blit(name1, (btn_x + 10, y + (btn_hoehe - name1.get_height()) // 2))
        y += btn_hoehe + 2

        self.arena_shop_buttons.append((erfahrung_btn, "erfahrungsschriftrolle"))

        gold_btn = pygame.Rect(btn_x, y, btn_breite, btn_hoehe)
        pygame.draw.rect(screen, config.FARBE_DUNKELGRAU, gold_btn)
        pygame.draw.rect(screen, config.FARBE_AKZENT, gold_btn, 2)

        name2 = self.schrift_klein.render("Goldrolle — 3M", True, config.FARBE_TEXT)
        screen.blit(name2, (btn_x + 10, y + (btn_hoehe - name2.get_height()) // 2))

        self.arena_shop_buttons.append((gold_btn, "goldschriftrolle"))

    def _zeichnen_buttons(self, screen, b, h):
        reroll_btn = pygame.Rect(int(b * 0.60), int(h * 0.02), int(b * 0.15), 35)
        reroll_farbe = config.FARBE_PANEL if self.gold >= self.reroll_kosten else config.FARBE_DUNKELGRAU
        pygame.draw.rect(screen, reroll_farbe, reroll_btn)
        pygame.draw.rect(screen, config.FARBE_RAND, reroll_btn, 1)
        reroll_text = self.schrift_normal.render(f"Reroll ({self.reroll_kosten}G)", True, config.FARBE_TEXT)
        screen.blit(reroll_text, (reroll_btn.x + (reroll_btn.width - reroll_text.get_width()) // 2,
                                  reroll_btn.y + (reroll_btn.height - reroll_text.get_height()) // 2))

        pygame.draw.rect(screen, config.FARBE_PANEL, self.zurueck_btn)
        pygame.draw.rect(screen, config.FARBE_RAND, self.zurueck_btn, 1)
        zurueck_text = self.schrift_klein.render("← Zurück", True, config.FARBE_TEXT)
        screen.blit(zurueck_text, (self.zurueck_btn.x + (self.zurueck_btn.width - zurueck_text.get_width()) // 2,
                                   self.zurueck_btn.y + (self.zurueck_btn.height - zurueck_text.get_height()) // 2))

    def zurueck(self):
        from .charakter_uebersicht_szene import CharakterUebersichtSzene
        zurueck = CharakterUebersichtSzene(self.szenen_manager, self.netzwerk_client)
        self.szenen_manager.szene_wechseln(zurueck)