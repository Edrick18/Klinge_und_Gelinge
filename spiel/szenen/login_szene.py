"""
spiel/szenen/login_szene.py - Login/Registrierungs-Szene

Abhängigkeiten: pygame, config, basis_szene
"""

import pygame
import config
from ..kern.basis_szene import BasisSzene
from netzwerk.nachrichten import (
    LOGIN, LOGIN_ERFOLG, LOGIN_FEHLER,
    REGISTRIEREN, REGISTRIEREN_ERFOLG, REGISTRIEREN_FEHLER,
    VERSION_ABGELEHNT,
    SCHLUESSEL_BENUTZERNAME, SCHLUESSEL_PASSWORT, SCHLUESSEL_NACHRICHT, SCHLUESSEL_SPIELER_ID,
    SCHLUESSEL_VERSION
)


class LoginSzene(BasisSzene):
    def __init__(self, szenen_manager, netzwerk_client):
        self.szenen_manager = szenen_manager
        self.netzwerk_client = netzwerk_client
        self.schrift_titel = pygame.font.Font(None, 48)
        self.schrift_label = pygame.font.Font(None, 32)
        self.schrift_button = pygame.font.Font(None, 36)
        self.benutzername_eingabe = ""
        self.passwort_eingabe = ""
        self.aktives_feld = 0
        self.status_nachricht = ""
        self.status_farbe = config.FARBE_TEXT

    def events_verarbeiten(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.aktives_feld = (self.aktives_feld + 1) % 2
                elif event.key == pygame.K_RETURN:
                    self.einloggen()
                elif event.key == pygame.K_BACKSPACE:
                    if self.aktives_feld == 0:
                        self.benutzername_eingabe = self.benutzername_eingabe[:-1]
                    else:
                        self.passwort_eingabe = self.passwort_eingabe[:-1]
                elif event.unicode and len(event.unicode) > 0:
                    if event.unicode.isprintable():
                        if self.aktives_feld == 0:
                            if len(self.benutzername_eingabe) < 20:
                                self.benutzername_eingabe += event.unicode
                        else:
                            if len(self.passwort_eingabe) < 20:
                                self.passwort_eingabe += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._buttons_pruefen(event.pos)

    def _buttons_pruefen(self, pos):
        feld_breite, feld_hoehe = 300, 40
        feld_x = (config.AUFLOESUNG_BREITE - feld_breite) // 2

        feld_benutzer = pygame.Rect(feld_x, 180, feld_breite, feld_hoehe)
        feld_passwort = pygame.Rect(feld_x, 290, feld_breite, feld_hoehe)

        if feld_benutzer.collidepoint(pos):
            self.aktives_feld = 0
        elif feld_passwort.collidepoint(pos):
            self.aktives_feld = 1

        einloggen_rect = pygame.Rect(config.AUFLOESUNG_BREITE // 2 - 200, config.AUFLOESUNG_HOEHE // 2 + 120, 180, 50)
        registrieren_rect = pygame.Rect(config.AUFLOESUNG_BREITE // 2 + 20, config.AUFLOESUNG_HOEHE // 2 + 120, 180, 50)
        if einloggen_rect.collidepoint(pos):
            self.einloggen()
        elif registrieren_rect.collidepoint(pos):
            self.registrieren()

    def einloggen(self):
        self.netzwerk_client.nachricht_senden(LOGIN, {
            SCHLUESSEL_BENUTZERNAME: self.benutzername_eingabe,
            SCHLUESSEL_PASSWORT: self.passwort_eingabe,
            SCHLUESSEL_VERSION: config.SPIEL_VERSION
        })

    def registrieren(self):
        self.netzwerk_client.nachricht_senden(REGISTRIEREN, {
            SCHLUESSEL_BENUTZERNAME: self.benutzername_eingabe,
            SCHLUESSEL_PASSWORT: self.passwort_eingabe,
            SCHLUESSEL_VERSION: config.SPIEL_VERSION
        })

    def updaten(self, delta_zeit: float):
        while True:
            nachricht = self.netzwerk_client.nachricht_holen()
            if not nachricht:
                break
            typ = nachricht.get("typ")
            daten = nachricht.get("daten", {})
            if typ == LOGIN_ERFOLG:
                self.status_nachricht = daten.get(SCHLUESSEL_NACHRICHT, "Eingeloggt!")
                self.status_farbe = config.FARBE_ERFOLG
                letzter_charakter_id = daten.get("letzter_charakter_id")
                from .charakter_auswahl_szene import CharakterAuswahlSzene
                self.szenen_manager.szene_wechseln(CharakterAuswahlSzene(self.szenen_manager, self.netzwerk_client, letzter_charakter_id))
            elif typ == LOGIN_FEHLER:
                self.status_nachricht = daten.get(SCHLUESSEL_NACHRICHT, "Fehler")
                self.status_farbe = config.FARBE_HP
            elif typ == REGISTRIEREN_ERFOLG:
                self.status_nachricht = daten.get(SCHLUESSEL_NACHRICHT, "Konto erstellt!")
                self.status_farbe = config.FARBE_ERFOLG
            elif typ == REGISTRIEREN_FEHLER:
                self.status_nachricht = daten.get(SCHLUESSEL_NACHRICHT, "Fehler")
                self.status_farbe = config.FARBE_HP
            elif typ == VERSION_ABGELEHNT:
                nachricht = daten.get(SCHLUESSEL_NACHRICHT, "Veraltete Version")
                self.status_nachricht = nachricht
                self.status_farbe = config.FARBE_WARNUNG
                self._pflicht_update_starten()

    def _pflicht_update_starten(self):
        """Zeigt Pflicht-Update-Fenster (kein Ueberspringen moeglich)"""
        import sys
        schrift = pygame.font.Font(None, 36)
        schrift_klein = pygame.font.Font(None, 26)
        uhr = pygame.time.Clock()
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE

        update_button = pygame.Rect(b // 2 - 120, h // 2 + 60, 240, 50)
        beenden_button = pygame.Rect(b // 2 - 80, h // 2 + 130, 160, 40)

        fenster = pygame.display.get_surface()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if update_button.collidepoint(event.pos):
                        from updater import update_durchfuehren
                        update_durchfuehren()
                        pygame.quit()
                        sys.exit()
                    if beenden_button.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

            fenster.fill(config.FARBE_HINTERGRUND)

            titel = schrift.render("Update erforderlich!", True, config.FARBE_WARNUNG)
            fenster.blit(titel, titel.get_rect(center=(b // 2, h // 2 - 60)))

            info1 = schrift_klein.render("Deine Version ist zu alt.", True, config.FARBE_TEXT_GEDIMMT)
            info2 = schrift_klein.render("Das Update wird automatisch installiert.", True, config.FARBE_TEXT_GEDIMMT)
            fenster.blit(info1, info1.get_rect(center=(b // 2, h // 2 - 15)))
            fenster.blit(info2, info2.get_rect(center=(b // 2, h // 2 + 15)))

            pygame.draw.rect(fenster, config.FARBE_ERFOLG, update_button)
            btn_text = schrift.render("Jetzt updaten", True, config.FARBE_WEISS)
            fenster.blit(btn_text, btn_text.get_rect(center=update_button.center))

            pygame.draw.rect(fenster, config.FARBE_DUNKELGRAU, beenden_button)
            end_text = schrift_klein.render("Beenden", True, config.FARBE_TEXT_GEDIMMT)
            fenster.blit(end_text, end_text.get_rect(center=beenden_button.center))

            pygame.display.flip()
            uhr.tick(60)

    def zeichnen(self, flaeche: pygame.Surface):
        flaeche.fill(config.FARBE_HINTERGRUND)

        titel_text = self.schrift_titel.render("Anmelden", True, config.FARBE_AKZENT)
        titel_rect = titel_text.get_rect(center=(config.AUFLOESUNG_BREITE // 2, 80))
        flaeche.blit(titel_text, titel_rect)

        feld_breite, feld_hoehe = 300, 40
        feld_x = (config.AUFLOESUNG_BREITE - feld_breite) // 2

        label_benutzer = self.schrift_label.render("Benutzername", True, config.FARBE_TEXT)
        flaeche.blit(label_benutzer, (feld_x, 150))

        rand_farbe_benutzer = config.FARBE_TEXT if self.aktives_feld == 0 else config.FARBE_RAND
        pygame.draw.rect(flaeche, rand_farbe_benutzer, (feld_x, 180, feld_breite, feld_hoehe), 2)
        benutzer_text = self.schrift_label.render(self.benutzername_eingabe, True, config.FARBE_TEXT)
        flaeche.blit(benutzer_text, (feld_x + 10, 190))

        label_passwort = self.schrift_label.render("Passwort", True, config.FARBE_TEXT)
        flaeche.blit(label_passwort, (feld_x, 260))

        rand_farbe_passwort = config.FARBE_TEXT if self.aktives_feld == 1 else config.FARBE_RAND
        pygame.draw.rect(flaeche, rand_farbe_passwort, (feld_x, 290, feld_breite, feld_hoehe), 2)
        passwort_verdeckt = "*" * len(self.passwort_eingabe)
        passwort_text = self.schrift_label.render(passwort_verdeckt, True, config.FARBE_TEXT)
        flaeche.blit(passwort_text, (feld_x + 10, 300))

        einloggen_rect = pygame.Rect(config.AUFLOESUNG_BREITE // 2 - 200, config.AUFLOESUNG_HOEHE // 2 + 120, 180, 50)
        pygame.draw.rect(flaeche, config.FARBE_PANEL, einloggen_rect)
        einloggen_text = self.schrift_button.render("Einloggen", True, config.FARBE_TEXT)
        einloggen_text_rect = einloggen_text.get_rect(center=einloggen_rect.center)
        flaeche.blit(einloggen_text, einloggen_text_rect)

        registrieren_rect = pygame.Rect(config.AUFLOESUNG_BREITE // 2 + 20, config.AUFLOESUNG_HOEHE // 2 + 120, 180, 50)
        pygame.draw.rect(flaeche, config.FARBE_PANEL, registrieren_rect)
        registrieren_text = self.schrift_button.render("Registrieren", True, config.FARBE_TEXT)
        registrieren_text_rect = registrieren_text.get_rect(center=registrieren_rect.center)
        flaeche.blit(registrieren_text, registrieren_text_rect)

        if self.status_nachricht:
            status_text = self.schrift_label.render(self.status_nachricht, True, self.status_farbe)
            status_rect = status_text.get_rect(center=(config.AUFLOESUNG_BREITE // 2, config.AUFLOESUNG_HOEHE // 2 + 200))
            flaeche.blit(status_text, status_rect)