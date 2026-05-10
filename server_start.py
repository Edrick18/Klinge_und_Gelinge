"""
server_start.py - Spiel-Server starten

Abhängigkeiten: server.kern.server_kern
"""

from server.kern.server_kern import Server


if __name__ == "__main__":
    server = Server()
    server.starten()