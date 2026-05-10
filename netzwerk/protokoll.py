"""
netzwerk/protokoll.py - JSON-Nachrichten mit Längen-Header

Abhängigkeiten: socket, json, struct
"""

import json
import struct

import config
from netzwerk.nachrichten import SCHLUESSEL_TYP, SCHLUESSEL_DATEN


class Protokoll:
    @staticmethod
    def nachricht_erstellen(typ: str, daten: dict) -> dict:
        return {SCHLUESSEL_TYP: typ, SCHLUESSEL_DATEN: daten}

    @staticmethod
    def senden(socket, nachricht: dict) -> bool:
        try:
            json_daten = json.dumps(nachricht).encode("utf-8")
            laenge = len(json_daten)
            header = struct.pack(">I", laenge)
            socket.sendall(header + json_daten)
            return True
        except Exception:
            return False

    @staticmethod
    def empfangen(socket) -> dict | None:
        try:
            header = b""
            while len(header) < 4:
                chunk = socket.recv(4 - len(header))
                if not chunk:
                    return None
                header += chunk
            laenge = struct.unpack(">I", header)[0]
            daten = b""
            while len(daten) < laenge:
                chunk = socket.recv(min(config.NETZWERK_PUFFER, laenge - len(daten)))
                if not chunk:
                    return None
                daten += chunk
            return json.loads(daten.decode("utf-8"))
        except Exception:
            return None