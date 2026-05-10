"""
spiel/kern/ereignis_handler.py - Event-Sammlung und Filterung

Abhängigkeiten: pygame
"""

import pygame


class EreignisHandler:
    def __init__(self):
        self._events = []

    def events_sammeln(self) -> list:
        self._events = pygame.event.get()
        return self._events

    def ist_beenden_event(self, events) -> bool:
        for event in events:
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
        return False

    def tastendruck(self, events, taste) -> bool:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == taste:
                return True
        return False