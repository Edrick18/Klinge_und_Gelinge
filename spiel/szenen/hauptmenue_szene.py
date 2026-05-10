"""
spiel/szenen/hauptmenue_szene.py - Hauptmenü-Szene

Abhängigkeiten: pygame, config, basis_szene, login_szene
"""

import pygame
import config
from ..kern.basis_szene import BasisSzene
from .login_szene import LoginSzene


class HauptmenueSzene(BasisSzene):
    def __init__(self, szenen_manager, netzwerk_client):
        self.szenen_manager = szenen_manager
        self.netzwerk_client = netzwerk_client
        self.schrift_titel = pygame.font.Font(None, 72)
        self.schrift_menu = pygame.font.Font(None, 48)
        self.menu_punkte = ["Spielen", "Einstellungen", "Beenden"]
        self.ausgewaehlter_index = 0

    def events_verarbeiten(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.ausgewaehlter_index = (self.ausgewaehlter_index - 1) % len(self.menu_punkte)
                elif event.key == pygame.K_DOWN:
                    self.ausgewaehlter_index = (self.ausgewaehlter_index + 1) % len(self.menu_punkte)
                elif event.key == pygame.K_RETURN:
                    self._aktion_ausfuehren()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._maus_klick_pruefen(event.pos)

    def _maus_klick_pruefen(self, pos):
        start_y = config.AUFLOESUNG_HOEHE // 2 - 50
        abstand = 60
        for i in range(len(self.menu_punkte)):
            menu_text = self.schrift_menu.render(self.menu_punkte[i], True, config.FARBE_TEXT)
            menu_rect = pygame.Rect(
                config.AUFLOESUNG_BREITE // 2 - 100,
                start_y + i * abstand - 20,
                200,
                40
            )
            if menu_rect.collidepoint(pos):
                self.ausgewaehlter_index = i
                self._aktion_ausfuehren()
                break

    def _aktion_ausfuehren(self):
        if self.menu_punkte[self.ausgewaehlter_index] == "Spielen":
            login_szene = LoginSzene(self.szenen_manager, self.netzwerk_client)
            self.szenen_manager.szene_wechseln(login_szene)
        elif self.menu_punkte[self.ausgewaehlter_index] == "Beenden":
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def updaten(self, delta_zeit: float):
        pass

    def zeichnen(self, flaeche: pygame.Surface):
        flaeche.fill(config.FARBE_HINTERGRUND)

        titel_text = self.schrift_titel.render("PROJEKT RPG", True, config.FARBE_AKZENT)
        titel_rect = titel_text.get_rect(center=(config.AUFLOESUNG_BREITE // 2, 100))
        flaeche.blit(titel_text, titel_rect)

        start_y = config.AUFLOESUNG_HOEHE // 2 - 50
        abstand = 60

        for i, punkt in enumerate(self.menu_punkte):
            if i == self.ausgewaehlter_index:
                farbe = config.FARBE_TEXT
            else:
                farbe = config.FARBE_TEXT_GEDIMMT

            menu_text = self.schrift_menu.render(punkt, True, farbe)
            menu_rect = menu_text.get_rect(center=(config.AUFLOESUNG_BREITE // 2, start_y + i * abstand))
            flaeche.blit(menu_text, menu_rect)

            if i == self.ausgewaehlter_index:
                pfeil_text = self.schrift_menu.render(">", True, farbe)
                pfeil_rect = pfeil_text.get_rect(right=menu_rect.left - 20, centery=menu_rect.centery)
                flaeche.blit(pfeil_text, pfeil_rect)