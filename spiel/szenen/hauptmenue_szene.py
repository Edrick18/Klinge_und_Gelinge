"""
spiel/szenen/hauptmenue_szene.py - Hauptmenü-Szene

Abhängigkeiten: pygame, config, basis_szene, login_szene
"""

import math
import random
import pygame
import config
from ..kern.basis_szene import BasisSzene
from .login_szene import LoginSzene


class HauptmenueSzene(BasisSzene):
    def __init__(self, szenen_manager, netzwerk_client):
        self.szenen_manager = szenen_manager
        self.netzwerk_client = netzwerk_client

        self.schrift_titel  = pygame.font.Font(None, 82)
        self.schrift_untertitel = pygame.font.Font(None, 30)
        self.schrift_menu   = pygame.font.Font(None, 52)
        self.schrift_klein  = pygame.font.Font(None, 22)

        self.menu_punkte = ["Spielen", "Einstellungen", "Beenden"]
        self.ausgewaehlter_index = 0
        self.zeit = 0.0

        # Schwebende Partikel im Hintergrund
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE
        self.partikel = [
            {
                "x": float(random.randint(0, b)),
                "y": float(random.randint(0, h)),
                "speed": random.uniform(15, 50),
                "size": random.randint(1, 3),
                "helligkeit": random.randint(40, 110),
            }
            for _ in range(60)
        ]

    # ------------------------------------------------------------------
    def _menu_rect(self, index: int) -> pygame.Rect:
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE
        start_y = int(h * 0.52)
        abstand = 62
        breite = 280
        return pygame.Rect(b // 2 - breite // 2, start_y + index * abstand - 26, breite, 52)

    # ------------------------------------------------------------------
    def events_verarbeiten(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.ausgewaehlter_index = (self.ausgewaehlter_index - 1) % len(self.menu_punkte)
                elif event.key == pygame.K_DOWN:
                    self.ausgewaehlter_index = (self.ausgewaehlter_index + 1) % len(self.menu_punkte)
                elif event.key == pygame.K_RETURN:
                    self._aktion_ausfuehren()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i in range(len(self.menu_punkte)):
                    if self._menu_rect(i).collidepoint(event.pos):
                        self.ausgewaehlter_index = i
                        self._aktion_ausfuehren()
                        break
            elif event.type == pygame.MOUSEMOTION:
                for i in range(len(self.menu_punkte)):
                    if self._menu_rect(i).collidepoint(event.pos):
                        self.ausgewaehlter_index = i
                        break

    def _aktion_ausfuehren(self):
        if self.menu_punkte[self.ausgewaehlter_index] == "Spielen":
            self.szenen_manager.szene_wechseln(LoginSzene(self.szenen_manager, self.netzwerk_client))
        elif self.menu_punkte[self.ausgewaehlter_index] == "Beenden":
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    # ------------------------------------------------------------------
    def updaten(self, delta_zeit: float):
        self.zeit += delta_zeit
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE
        for p in self.partikel:
            p["y"] -= p["speed"] * delta_zeit
            if p["y"] < -4:
                p["y"] = float(h + 4)
                p["x"] = float(random.randint(0, b))

    # ------------------------------------------------------------------
    def zeichnen(self, flaeche: pygame.Surface):
        b = config.AUFLOESUNG_BREITE
        h = config.AUFLOESUNG_HOEHE

        flaeche.fill(config.FARBE_HINTERGRUND)

        # --- Partikel ---
        for p in self.partikel:
            c = p["helligkeit"]
            pygame.draw.circle(flaeche, (c, int(c * 0.65), 15),
                               (int(p["x"]), int(p["y"])), p["size"])

        # --- Dekorations-Linie ---
        linie_y = int(h * 0.46)
        pygame.draw.line(flaeche, config.FARBE_RAND, (b // 2 - 180, linie_y), (b // 2 + 180, linie_y), 1)

        # --- Titel mit Bob-Animation ---
        bob = int(math.sin(self.zeit * 1.8) * 5)
        titel_text = self.schrift_titel.render("KLINGE & GELINGE", True, config.FARBE_AKZENT)
        flaeche.blit(titel_text, titel_text.get_rect(center=(b // 2, int(h * 0.22) + bob)))

        # --- Untertitel ---
        sub = self.schrift_untertitel.render("Ein Abenteuer beginnt...", True, config.FARBE_TEXT_GEDIMMT)
        flaeche.blit(sub, sub.get_rect(center=(b // 2, int(h * 0.33) + bob)))

        # --- Menü-Einträge ---
        maus_pos = pygame.mouse.get_pos()
        start_y = int(h * 0.52)
        abstand = 62

        for i, punkt in enumerate(self.menu_punkte):
            rect = self._menu_rect(i)
            ist_aktiv = (i == self.ausgewaehlter_index)
            ist_hover = rect.collidepoint(maus_pos)

            if ist_aktiv or ist_hover:
                pygame.draw.rect(flaeche, config.FARBE_PANEL, rect)
                pygame.draw.rect(flaeche, config.FARBE_AKZENT, rect, 1)

            farbe = config.FARBE_TEXT if (ist_aktiv or ist_hover) else config.FARBE_TEXT_GEDIMMT
            text_surf = self.schrift_menu.render(punkt, True, farbe)
            flaeche.blit(text_surf, text_surf.get_rect(center=rect.center))

            if ist_aktiv:
                pfeil = self.schrift_menu.render(">", True, config.FARBE_AKZENT)
                flaeche.blit(pfeil, pfeil.get_rect(right=rect.left - 12, centery=rect.centery))

        # --- Version unten rechts ---
        ver = self.schrift_klein.render(f"v{config.SPIEL_VERSION}", True, config.FARBE_TEXT_GEDIMMT)
        flaeche.blit(ver, (b - ver.get_width() - 12, h - ver.get_height() - 8))
