"""
spiel/kern/netzwerk_client.py - Client-Verbindung (Hintergrund-Thread)

Abhängigkeiten: socket, threading, queue, config, netzwerk.protokoll, netzwerk.nachrichten
"""

import socket
import threading
import queue

import config
from netzwerk.protokoll import Protokoll
from netzwerk.nachrichten import VERBINDUNG_HERSTELLEN, VERBINDUNG_BESTAETIGT, SCHLUESSEL_TYP


class NetzwerkClient:
    def __init__(self):
        self.socket = None
        self.verbunden = False
        self.empfangs_warteschlange = queue.Queue()

    def verbinden(self) -> bool:
        try:
            print(f"Verbinde mit {config.SERVER_HOST}:{config.SERVER_PORT}")
            try:
                self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
                self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
            except Exception:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((config.SERVER_HOST, config.SERVER_PORT))
            nachricht = Protokoll.nachricht_erstellen(VERBINDUNG_HERSTELLEN, {})
            Protokoll.senden(self.socket, nachricht)
            antwort = Protokoll.empfangen(self.socket)
            if antwort and antwort.get(SCHLUESSEL_TYP) == VERBINDUNG_BESTAETIGT:
                self.verbunden = True
                self._empfangs_thread = threading.Thread(target=self.empfangs_loop, daemon=True)
                self._empfangs_thread.start()
                return True
            else:
                self.socket.close()
                return False
        except Exception:
            if self.socket:
                self.socket.close()
            return False

    def empfangs_loop(self):
        while self.verbunden:
            nachricht = Protokoll.empfangen(self.socket)
            if nachricht is None:
                print("[NetzwerkClient] Verbindung getrennt (empfangs_loop)")
                self.verbunden = False
                break
            self.empfangs_warteschlange.put(nachricht)
        print(f"[NetzwerkClient] empfangs_loop beendet | verbunden={self.verbunden}")

    def nachricht_senden(self, typ: str, daten: dict) -> bool:
        print(f"Sende: {typ}")
        if not self.verbunden:
            return False
        nachricht = Protokoll.nachricht_erstellen(typ, daten)
        return Protokoll.senden(self.socket, nachricht)

    def nachricht_holen(self) -> dict | None:
        try:
            return self.empfangs_warteschlange.get_nowait()
        except queue.Empty:
            return None

    def trennen(self):
        self.verbunden = False
        if self.socket:
            self.socket.close()
            self.socket = None
