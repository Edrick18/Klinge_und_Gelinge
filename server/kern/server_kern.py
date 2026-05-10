"""
server/kern/server_kern.py - Haupt-Server-Thread

Abhängigkeiten: socket, threading, config, verbindung, datenbank
"""

import socket
import threading

import config
from .verbindung import Verbindung
from server.datenbank.datenbank import Datenbank


class Server:
    def __init__(self):
        # IPv6 mit dual-stack (akzeptiert auch IPv4-Verbindungen)
        try:
            self.server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        except Exception:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(("", config.SERVER_PORT))
        self.datenbank = Datenbank()
        self.verbindungen = {}
        self.naechste_id = 0
        self.laufend = False

    def starten(self):
        self.server_socket.listen(config.SERVER_MAX_VERBINDUNGEN)
        print(f"Server laeuft auf {config.SERVER_HOST}:{config.SERVER_PORT}")
        self.laufend = True
        self._verbindungs_loop()

    def _verbindungs_loop(self):
        print("Server wartet auf Verbindungen...")
        while self.laufend:
            try:
                client_socket, client_adresse = self.server_socket.accept()
                verbindungs_id = self.naechste_id
                self.naechste_id += 1
                neue_verbindung = Verbindung(client_socket, client_adresse, verbindungs_id, self.datenbank, self)
                self.verbindungen[verbindungs_id] = neue_verbindung
                neue_verbindung.starten()
                print(f"Neue Verbindung: {client_adresse} (ID: {verbindungs_id})")
            except Exception:
                if self.laufend:
                    pass

    def beenden(self):
        self.laufend = False
        for verbindung in self.verbindungen.values():
            verbindung.trennen()
        self.verbindungen.clear()
        self.server_socket.close()