"""
spiel/szenen/gilde_szene.py - Gilde Szene mit Übersicht, Erstellen, Suchen
"""

import pygame
import config
from ..kern.basis_szene import BasisSzene
from netzwerk.nachrichten import (
    GILDE_LADEN, GILDE_ANTWORT, GILDE_ERSTELLEN, GILDE_ERSTELLT,
    GILDE_BEITRETEN, GILDE_BEIGETRETEN, GILDE_VERLASSEN, GILDE_VERLASSEN_OK,
    GILDE_STEUER_SETZEN, GILDE_STEUER_OK, GILDE_RANG_SETZEN, GILDE_RANG_OK,
    GILDE_KICK, GILDE_KICK_OK, GILDE_AUFSTEIGEN, GILDE_AUFGESTIEGEN,
    SCHLUESSEL_GILDEN_NAME, SCHLUESSEL_GILDEN_ID,
    SCHLUESSEL_STEUER, SCHLUESSEL_ZIEL_ID, SCHLUESSEL_RANG
)


class GildeSzene(BasisSzene):
    def __init__(self, szenen_manager, netzwerk_client, charakter_daten=None):
        self.szenen_manager = szenen_manager
        self.netzwerk_client = netzwerk_client
        self.charakter_daten = charakter_daten

        self.zustand = "laden"
        self.in_gilde = False
        self.gilde = {}
        self.mitglied = {}
        self.mitglieder = []
        self.log = []
        self.gilden_liste = []
        self.ausgewaehlte_gilde = None
        self.status_nachricht = ""
        self.status_farbe = config.FARBE_TEXT

        self.name_eingabe = ""
        self.beschreibung_eingabe = ""
        self.aktives_feld = None

        self._laden_angefordert = False
        self._layout_berechnen()

    def _layout_berechnen(self):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE

        self.schrift_gross = pygame.font.Font(None, 48)
        self.schrift_normal = pygame.font.Font(None, 32)
        self.schrift_klein = pygame.font.Font(None, 24)
        self.schrift_sehr_klein = pygame.font.Font(None, 18)

        self.zurueck_btn = pygame.Rect(20, h - 50, 100, 35)
        btn_breite = 180
        btn_abstand = 20
        gesamt_btn_breite = 3 * btn_breite + 2 * btn_abstand
        start_x = (b - gesamt_btn_breite) // 2
        self.erstellen_btn = pygame.Rect(start_x, int(h * 0.55), btn_breite, 45)
        self.suchen_btn = pygame.Rect(start_x + btn_breite + btn_abstand, int(h * 0.55), btn_breite, 45)
        self.aktualisieren_btn = pygame.Rect(start_x + 2 * (btn_breite + btn_abstand), int(h * 0.55), btn_breite, 45)
        self.panel_x = int(b * 0.05)
        self.panel_y = 80
        self.panel_breite = int(b * 0.90)
        self.panel_hoehe = int(h * 0.75)

        self.verlassen_btn = pygame.Rect(self.panel_x + self.panel_breite - 160, self.panel_y + self.panel_hoehe - 50, 150, 40)
        self.aufsteigen_btn = pygame.Rect(self.panel_x + 80, self.panel_y + 145, 200, 30)

        self.name_feld = pygame.Rect(self.panel_x + 20, self.panel_y + 95, self.panel_breite - 40, 40)
        self.besch_feld = pygame.Rect(self.panel_x + 20, self.panel_y + 180, self.panel_breite - 40, 80)

        btn_breite = 150
        self.erstellen_feld_btn = pygame.Rect(self.panel_x + (self.panel_breite - btn_breite * 2 - 20) // 2, self.panel_y + 280, btn_breite, 45)
        self.abbrechen_btn = pygame.Rect(self.erstellen_feld_btn.right + 20, self.panel_y + 280, btn_breite, 45)

        self.steuer_minus_btn = pygame.Rect(self.panel_x + 20, 0, 40, 35)
        self.steuer_plus_btn = pygame.Rect(self.panel_x + 70, 0, 40, 35)

    def nachricht_empfangen(self, nachricht):
        typ = nachricht.get("typ")
        daten = nachricht.get("daten", {})

        if typ == GILDE_ANTWORT:
            self.in_gilde = daten.get("in_gilde", False)
            if self.in_gilde:
                self.gilde = daten.get("gilde", {})
                self.mitglied = daten.get("mitglied", {})
                self.mitglieder = daten.get("mitglieder", [])
                self.log = daten.get("log", [])
                self.zustand = "übersicht"
            else:
                self.gilden_liste = daten.get("gilden_liste", [])
                self.zustand = "suchen"

        elif typ == GILDE_ERSTELLT:
            if daten.get("erfolg"):
                self.status_nachricht = "Gilde erstellt!"
                self.status_farbe = config.FARBE_ERFOLG
                self.netzwerk_client.nachricht_senden(GILDE_LADEN, {})
            else:
                self.status_nachricht = daten.get("nachricht", "Fehler")
                self.status_farbe = config.FARBE_WARNUNG

        elif typ == GILDE_BEIGETRETEN:
            if daten.get("erfolg"):
                self.status_nachricht = "Erfolgreich beigetreten!"
                self.status_farbe = config.FARBE_ERFOLG
                self.netzwerk_client.nachricht_senden(GILDE_LADEN, {})
            else:
                self.status_nachricht = daten.get("nachricht", "Fehler")
                self.status_farbe = config.FARBE_WARNUNG

        elif typ == GILDE_VERLASSEN_OK:
            if daten.get("erfolg"):
                self.in_gilde = False
                self.zustand = "suchen"
                self.netzwerk_client.nachricht_senden(GILDE_LADEN, {})
            else:
                self.status_nachricht = daten.get("nachricht", "Fehler")
                self.status_farbe = config.FARBE_WARNUNG

        elif typ in (GILDE_STEUER_OK, GILDE_RANG_OK, GILDE_KICK_OK, GILDE_AUFGESTIEGEN):
            if daten.get("erfolg"):
                if typ == GILDE_AUFGESTIEGEN:
                    neue_stufe = daten.get("neue_stufe", 0)
                    kosten = daten.get("kosten", 0)
                    self.status_nachricht = f"Gilde auf Stufe {neue_stufe} aufgestiegen! ({kosten}G)"
                    self.status_farbe = config.FARBE_ERFOLG
                self.netzwerk_client.nachricht_senden(GILDE_LADEN, {})
            else:
                self.status_nachricht = daten.get("nachricht", "Fehler")
                self.status_farbe = config.FARBE_WARNUNG

    def events_verarbeiten(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.zustand == "erstellen":
                        self.zustand = "suchen"
                    else:
                        self.zurueck()
                elif self.zustand == "erstellen":
                    if event.key == pygame.K_BACKSPACE:
                        if self.aktives_feld == "name":
                            self.name_eingabe = self.name_eingabe[:-1]
                        elif self.aktives_feld == "beschreibung":
                            self.beschreibung_eingabe = self.beschreibung_eingabe[:-1]
                    elif event.key == pygame.K_RETURN:
                        self._erstellen_klick()
                    elif event.unicode:
                        if self.aktives_feld == "name":
                            if len(self.name_eingabe) < 30:
                                self.name_eingabe += event.unicode
                        elif self.aktives_feld == "beschreibung":
                            if len(self.beschreibung_eingabe) < 100:
                                self.beschreibung_eingabe += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.zurueck_btn.collidepoint(event.pos):
                        if self.zustand == "erstellen":
                            self.zustand = "suchen"
                        else:
                            self.zurueck()
                    elif self.zustand == "suchen":
                        self._suchen_klicks(event.pos)
                    elif self.zustand == "erstellen":
                        self._erstellen_klicks(event.pos)
                    elif self.zustand == "übersicht":
                        self._übersicht_klicks(event.pos)

    def _suchen_klicks(self, pos):
        if self.erstellen_btn.collidepoint(pos):
            self.zustand = "erstellen"
        elif self.suchen_btn.collidepoint(pos):
            self.netzwerk_client.nachricht_senden(GILDE_LADEN, {})
        elif self.aktualisieren_btn.collidepoint(pos):
            self.netzwerk_client.nachricht_senden(GILDE_LADEN, {})

        for i, gilde in enumerate(self.gilden_liste):
            y = 130 + i * 50
            if self.panel_x + 20 <= pos[0] <= self.panel_x + self.panel_breite - 20 and y <= pos[1] <= y + 40:
                self.netzwerk_client.nachricht_senden(GILDE_BEITRETEN, {
                    SCHLUESSEL_GILDEN_ID: gilde["id"]
                })
                break

    def _erstellen_klicks(self, pos):
        if self.name_feld.collidepoint(pos):
            self.aktives_feld = "name"
        elif self.besch_feld.collidepoint(pos):
            self.aktives_feld = "beschreibung"
        elif self.erstellen_feld_btn.collidepoint(pos):
            self._erstellen_klick()
        elif self.abbrechen_btn.collidepoint(pos):
            self.zustand = "suchen"
            self.name_eingabe = ""
            self.beschreibung_eingabe = ""
            self.aktives_feld = None

    def _erstellen_klick(self):
        if not self.name_eingabe or len(self.name_eingabe) < 3:
            self.status_nachricht = "Name muss mindestens 3 Zeichen haben"
            self.status_farbe = config.FARBE_WARNUNG
            return

        self.netzwerk_client.nachricht_senden(GILDE_ERSTELLEN, {
            "gilden_name": self.name_eingabe,
            "beschreibung": self.beschreibung_eingabe
        })

    def _übersicht_klicks(self, pos):
        if self.verlassen_btn.collidepoint(pos):
            self.netzwerk_client.nachricht_senden(GILDE_VERLASSEN, {})
        elif self.mitglied.get("rang") in ("gildenmeister", "offizier"):
            if hasattr(self, 'minus_button') and self.minus_button.collidepoint(pos):
                steuer = max(0, self.gilde.get("steuer", 0) - 1)
                self.netzwerk_client.nachricht_senden(GILDE_STEUER_SETZEN, {"steuer": steuer})
            elif hasattr(self, 'plus_button') and self.plus_button.collidepoint(pos):
                steuer = min(20, self.gilde.get("steuer", 0) + 1)
                self.netzwerk_client.nachricht_senden(GILDE_STEUER_SETZEN, {"steuer": steuer})
        if self.aufsteigen_btn.collidepoint(pos) and self.mitglied.get("rang") in ("gildenmeister", "offizier"):
            self.netzwerk_client.nachricht_senden(GILDE_AUFSTEIGEN, {})

    def updaten(self, delta_zeit: float):
        if not self._laden_angefordert:
            self.netzwerk_client.nachricht_senden(GILDE_LADEN, {})
            self._laden_angefordert = True

        while True:
            nachricht = self.netzwerk_client.nachricht_holen()
            if not nachricht:
                break
            self.nachricht_empfangen(nachricht)

    def zeichnen(self, screen):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE
        screen.fill(config.FARBE_HINTERGRUND)

        if self.zustand == "laden":
            text = self.schrift_normal.render("Lade Gilde...", True, config.FARBE_TEXT_GEDIMMT)
            screen.blit(text, text.get_rect(center=(b // 2, h // 2)))
            return

        pygame.draw.rect(screen, config.FARBE_PANEL, (self.panel_x, self.panel_y, self.panel_breite, self.panel_hoehe))
        pygame.draw.rect(screen, config.FARBE_RAND, (self.panel_x, self.panel_y, self.panel_breite, self.panel_hoehe), 1)

        pygame.draw.rect(screen, config.FARBE_PANEL, self.zurueck_btn)
        pygame.draw.rect(screen, config.FARBE_RAND, self.zurueck_btn, 1)
        zurueck_text = self.schrift_klein.render("← Zurück", True, config.FARBE_TEXT)
        screen.blit(zurueck_text, (self.zurueck_btn.x + (self.zurueck_btn.width - zurueck_text.get_width()) // 2,
                                    self.zurueck_btn.y + (self.zurueck_btn.height - zurueck_text.get_height()) // 2))

        if self.status_nachricht:
            status_text = self.schrift_normal.render(self.status_nachricht, True, self.status_farbe)
            screen.blit(status_text, (b // 2 - status_text.get_width() // 2, h - 90))

        if self.zustand == "suchen":
            self._zeichnen_suchen(screen, b, h)
        elif self.zustand == "erstellen":
            self._zeichnen_erstellen(screen, b, h)
        elif self.zustand == "übersicht":
            self._zeichnen_übersicht(screen, b, h)

    def _zeichnen_suchen(self, screen, b, h):
        titel = self.schrift_gross.render("Gilde", True, config.FARBE_TEXT)
        screen.blit(titel, (self.panel_x + 20, self.panel_y + 10))

        text = self.schrift_normal.render("Du bist in keiner Gilde", True, config.FARBE_TEXT_GEDIMMT)
        screen.blit(text, (self.panel_x + 20, self.panel_y + 70))

        pygame.draw.rect(screen, config.FARBE_AKZENT, self.erstellen_btn)
        pygame.draw.rect(screen, config.FARBE_WEISS, self.erstellen_btn, 2)
        erstellen_text = self.schrift_klein.render("Gilde erstellen", True, config.FARBE_WEISS)
        screen.blit(erstellen_text, (self.erstellen_btn.x + (self.erstellen_btn.width - erstellen_text.get_width()) // 2,
                                      self.erstellen_btn.y + (self.erstellen_btn.height - erstellen_text.get_height()) // 2))

        pygame.draw.rect(screen, config.FARBE_PANEL, self.suchen_btn)
        pygame.draw.rect(screen, config.FARBE_RAND, self.suchen_btn, 1)
        suchen_text = self.schrift_klein.render("Gilde suchen", True, config.FARBE_TEXT)
        screen.blit(suchen_text, (self.suchen_btn.x + (self.suchen_btn.width - suchen_text.get_width()) // 2,
                                   self.suchen_btn.y + (self.suchen_btn.height - suchen_text.get_height()) // 2))

        pygame.draw.rect(screen, config.FARBE_PANEL, self.aktualisieren_btn)
        pygame.draw.rect(screen, config.FARBE_RAND, self.aktualisieren_btn, 1)
        aktualisieren_text = self.schrift_klein.render("Aktualisieren", True, config.FARBE_TEXT)
        screen.blit(aktualisieren_text, (self.aktualisieren_btn.x + (self.aktualisieren_btn.width - aktualisieren_text.get_width()) // 2,
                                          self.aktualisieren_btn.y + (self.aktualisieren_btn.height - aktualisieren_text.get_height()) // 2))

        y = 130
        for gilde in self.gilden_liste:
            pygame.draw.rect(screen, config.FARBE_DUNKELGRAU, (self.panel_x + 20, y, self.panel_breite - 40, 40))
            pygame.draw.rect(screen, config.FARBE_RAND, (self.panel_x + 20, y, self.panel_breite - 40, 40), 1)

            name_text = self.schrift_klein.render(gilde["name"], True, config.FARBE_TEXT)
            screen.blit(name_text, (self.panel_x + 30, y + 5))

            info_text = self.schrift_sehr_klein.render(f"Mitglieder: {gilde['mitglieder_anzahl']} | Kasse: {gilde['kasse']}G", True, config.FARBE_TEXT_GEDIMMT)
            screen.blit(info_text, (self.panel_x + 30, y + 22))

            beitreten_text = self.schrift_sehr_klein.render("[Beitreten]", True, config.FARBE_AKZENT)
            screen.blit(beitreten_text, (self.panel_x + self.panel_breite - 100, y + 12))

            y += 50

    def _zeichnen_erstellen(self, screen, b, h):
        titel = self.schrift_gross.render("Gilde erstellen", True, config.FARBE_TEXT)
        screen.blit(titel, (self.panel_x + 20, self.panel_y + 10))

        name_label = self.schrift_klein.render("Gildenname (3-30 Zeichen)", True, config.FARBE_TEXT_GEDIMMT)
        screen.blit(name_label, (self.panel_x + 20, self.panel_y + 70))

        name_farbe = config.FARBE_AKZENT if self.aktives_feld == "name" else config.FARBE_DUNKELGRAU
        pygame.draw.rect(screen, config.FARBE_PANEL, self.name_feld)
        pygame.draw.rect(screen, name_farbe, self.name_feld, 2)
        if self.name_eingabe:
            name_text = self.schrift_normal.render(self.name_eingabe, True, config.FARBE_TEXT)
        else:
            name_text = self.schrift_normal.render("Gildenname eingeben...", True, config.FARBE_TEXT_GEDIMMT)
        screen.blit(name_text, (self.name_feld.x + 10, self.name_feld.y + 15))

        besch_label = self.schrift_klein.render("Beschreibung (optional)", True, config.FARBE_TEXT_GEDIMMT)
        screen.blit(besch_label, (self.panel_x + 20, self.panel_y + 150))

        besch_farbe = config.FARBE_AKZENT if self.aktives_feld == "beschreibung" else config.FARBE_DUNKELGRAU
        pygame.draw.rect(screen, config.FARBE_PANEL, self.besch_feld)
        pygame.draw.rect(screen, besch_farbe, self.besch_feld, 2)
        if self.beschreibung_eingabe:
            besch_text = self.schrift_klein.render(self.beschreibung_eingabe, True, config.FARBE_TEXT)
        else:
            besch_text = self.schrift_klein.render("Beschreibung (optional)", True, config.FARBE_TEXT_GEDIMMT)
        screen.blit(besch_text, (self.besch_feld.x + 10, self.besch_feld.y + 30))

        pygame.draw.rect(screen, config.FARBE_ERFOLG, self.erstellen_feld_btn)
        pygame.draw.rect(screen, config.FARBE_WEISS, self.erstellen_feld_btn, 2)
        erstellen_text = self.schrift_klein.render("✓ Erstellen", True, config.FARBE_WEISS)
        screen.blit(erstellen_text, (self.erstellen_feld_btn.x + (self.erstellen_feld_btn.width - erstellen_text.get_width()) // 2,
                                      self.erstellen_feld_btn.y + (self.erstellen_feld_btn.height - erstellen_text.get_height()) // 2))

        pygame.draw.rect(screen, config.FARBE_HP, self.abbrechen_btn)
        pygame.draw.rect(screen, config.FARBE_RAND, self.abbrechen_btn, 1)
        abbrechen_text = self.schrift_klein.render("✕ Abbrechen", True, config.FARBE_TEXT)
        screen.blit(abbrechen_text, (self.abbrechen_btn.x + (self.abbrechen_btn.width - abbrechen_text.get_width()) // 2,
                                      self.abbrechen_btn.y + (self.abbrechen_btn.height - abbrechen_text.get_height()) // 2))

        if self.status_nachricht and self.zustand == "erstellen":
            status_text = self.schrift_klein.render(self.status_nachricht, True, self.status_farbe)
            screen.blit(status_text, (self.panel_x + 20, self.panel_y + 350))

    def _zeichnen_übersicht(self, screen, b, h):
        gilde_name = self.schrift_gross.render(self.gilde.get("name", "Gilde"), True, config.FARBE_AKZENT)
        screen.blit(gilde_name, (self.panel_x + 20, self.panel_y + 20))

        beschreibung = self.schrift_klein.render(self.gilde.get("beschreibung", ""), True, config.FARBE_TEXT_GEDIMMT)
        screen.blit(beschreibung, (self.panel_x + 20, self.panel_y + 55))

        info_y = self.panel_y + 85
        steuer = self.gilde.get("steuer", 0)
        ist_führer = self.mitglied.get("rang") in ("gildenmeister", "offizier")

        kasse_text = self.schrift_klein.render(f"Kasse: {self.gilde.get('kasse', 0)}G", True, config.FARBE_TEXT)
        screen.blit(kasse_text, (self.panel_x + 80, info_y))

        trenn1 = self.schrift_klein.render("|", True, config.FARBE_TEXT_GEDIMMT)
        screen.blit(trenn1, (self.panel_x + 170, info_y))

        steuer_x = self.panel_x + 200
        steuer_label = self.schrift_klein.render("Steuer:", True, config.FARBE_TEXT)
        screen.blit(steuer_label, (steuer_x, info_y))

        self.minus_button = pygame.Rect(steuer_x + 65, info_y - 2, 20, 20)
        if ist_führer:
            pygame.draw.rect(screen, config.FARBE_PANEL, self.minus_button)
            pygame.draw.rect(screen, config.FARBE_RAND, self.minus_button, 1)
            minus_text = self.schrift_klein.render("-", True, config.FARBE_TEXT)
            screen.blit(minus_text, (steuer_x + 70, info_y))
            self.steuer_minus_btn = self.minus_button

        self.aktuelle_steuer = steuer
        steuer_zahl = self.schrift_klein.render(f"{steuer}%", True, config.FARBE_TEXT)
        screen.blit(steuer_zahl, (self.minus_button.right + 5, info_y))

        self.plus_button = pygame.Rect(self.minus_button.right + 5 + steuer_zahl.get_width() + 5, info_y - 2, 20, 20)
        if ist_führer:
            pygame.draw.rect(screen, config.FARBE_PANEL, self.plus_button)
            pygame.draw.rect(screen, config.FARBE_RAND, self.plus_button, 1)
            plus_text = self.schrift_klein.render("+", True, config.FARBE_TEXT)
            screen.blit(plus_text, (self.plus_button.x + 4, info_y))
            self.steuer_plus_btn = self.plus_button

        trenn2_x = steuer_x + 150
        trenn2 = self.schrift_klein.render("|", True, config.FARBE_TEXT_GEDIMMT)
        screen.blit(trenn2, (trenn2_x, info_y))

        mitglieder_text = self.schrift_klein.render(f"Mitglieder: {len(self.mitglieder)}/50", True, config.FARBE_TEXT)
        screen.blit(mitglieder_text, (trenn2_x + 15, info_y))

        pygame.draw.rect(screen, config.FARBE_HP if self.mitglied.get("rang") == "gildenmeister" else config.FARBE_DUNKELGRAU,
                         self.verlassen_btn)
        pygame.draw.rect(screen, config.FARBE_RAND, self.verlassen_btn, 1)
        verlassen_text = self.schrift_klein.render("Gilde verlassen", True, config.FARBE_TEXT)
        screen.blit(verlassen_text, (self.verlassen_btn.x + (self.verlassen_btn.width - verlassen_text.get_width()) // 2,
                                     self.verlassen_btn.y + (self.verlassen_btn.height - verlassen_text.get_height()) // 2))

        stufe = self.gilde.get("stufe", 0)
        xp_bonus = int(self.gilde.get("xp_bonus", 0) * 100)
        gold_bonus = int(self.gilde.get("gold_bonus", 0) * 100)
        stufen_text = self.schrift_klein.render(f"Stufe {stufe} | XP-Bonus: +{xp_bonus}% | Gold-Bonus: +{gold_bonus}%", True, config.FARBE_AKZENT)
        screen.blit(stufen_text, (self.panel_x + 20, self.panel_y + 115))

        kosten = int(5000 * (4 ** stufe))
        kann_aufsteigen = self.gilde.get("kasse", 0) >= kosten and self.mitglied.get("rang") in ("gildenmeister", "offizier")
        if kann_aufsteigen:
            btn_farbe = config.FARBE_AKZENT
            btn_rand = config.FARBE_WEISS
            text_farbe = config.FARBE_WEISS
        else:
            btn_farbe = config.FARBE_DUNKELGRAU
            btn_rand = config.FARBE_TEXT_GEDIMMT
            text_farbe = config.FARBE_TEXT_GEDIMMT
        pygame.draw.rect(screen, btn_farbe, self.aufsteigen_btn)
        pygame.draw.rect(screen, btn_rand, self.aufsteigen_btn, 1)
        aufsteigen_text = self.schrift_klein.render(f"⬆ Aufsteigen ({kosten}G)", True, text_farbe)
        screen.blit(aufsteigen_text, (self.aufsteigen_btn.x + 10, self.aufsteigen_btn.y + 8))

        y = self.panel_y + 190
        mitglieder_titel = self.schrift_normal.render("Mitglieder", True, config.FARBE_TEXT)
        screen.blit(mitglieder_titel, (self.panel_x + 20, y))
        y += 25

        for m in self.mitglieder:
            rang_symbol = "👑" if m["rang"] == "gildenmeister" else ("⭐" if m["rang"] == "offizier" else "•")
            info = f"{rang_symbol} {m['name']} (Lv.{m['level']} {m['klasse']})"
            text = self.schrift_klein.render(info, True, config.FARBE_TEXT)
            screen.blit(text, (self.panel_x + 30, y))
            y += 25

        if self.log:
            y += 20
            log_titel = self.schrift_normal.render("Log", True, config.FARBE_TEXT)
            screen.blit(log_titel, (self.panel_x + 20, y))
            y += 25

            for eintrag in self.log[:10]:
                log_text = self.schrift_sehr_klein.render(f"{eintrag['charakter_name']}: {eintrag['aktion']}", True, config.FARBE_TEXT_GEDIMMT)
                screen.blit(log_text, (self.panel_x + 30, y))
                y += 18

    def zurueck(self):
        from .charakter_uebersicht_szene import CharakterUebersichtSzene
        zurueck = CharakterUebersichtSzene(self.szenen_manager, self.netzwerk_client, None)
        self.szenen_manager.szene_wechseln(zurueck)