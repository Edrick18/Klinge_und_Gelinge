class GildeVerwaltung:
    def __init__(self, datenbank):
        self.datenbank = datenbank

    def gilde_erstellen(self, charakter_id: int, name: str, beschreibung: str) -> dict:
        if self.datenbank.gilde_mitglied_laden(charakter_id):
            return {"erfolg": False, "nachricht": "Bereits in einer Gilde"}

        if not 3 <= len(name) <= 30:
            return {"erfolg": False, "nachricht": "Name muss 3-30 Zeichen haben"}

        gilden_id = self.datenbank.gilde_erstellen(name, beschreibung, charakter_id)
        if not gilden_id:
            return {"erfolg": False, "nachricht": "Gildenname bereits vergeben"}

        self.datenbank.gilde_log_hinzufuegen(gilden_id, "", "Gilde gegründet")
        return {"erfolg": True, "gilden_id": gilden_id}

    def gilde_beitreten(self, charakter_id: int, gilden_id: int, charakter_name: str) -> dict:
        if self.datenbank.gilde_mitglied_laden(charakter_id):
            return {"erfolg": False, "nachricht": "Bereits in einer Gilde"}

        gilde = self.datenbank.gilde_laden(gilden_id)
        if not gilde:
            return {"erfolg": False, "nachricht": "Gilde nicht gefunden"}

        if gilde["mitglieder_anzahl"] >= 50:
            return {"erfolg": False, "nachricht": "Gilde ist voll (max 50)"}

        if not self.datenbank.gilde_beitreten(charakter_id, gilden_id):
            return {"erfolg": False, "nachricht": "Beitritt fehlgeschlagen"}

        self.datenbank.gilde_log_hinzufuegen(gilden_id, charakter_name, "ist der Gilde beigetreten")
        return {"erfolg": True}

    def gilde_verlassen(self, charakter_id: int, charakter_name: str) -> dict:
        mitglied = self.datenbank.gilde_mitglied_laden(charakter_id)
        if not mitglied:
            return {"erfolg": False, "nachricht": "Nicht in einer Gilde"}

        if mitglied["rang"] == "gildenmeister":
            mitglieder = self.datenbank.gilde_mitglieder_laden(mitglied["gilden_id"])
            if len(mitglieder) > 1:
                return {"erfolg": False, "nachricht": "Gildenmeister muss zuerst Nachfolger ernennen"}

        if not self.datenbank.gilde_verlassen(charakter_id):
            return {"erfolg": False, "nachricht": "Verlassen fehlgeschlagen"}

        self.datenbank.gilde_log_hinzufuegen(mitglied["gilden_id"], charakter_name, "hat die Gilde verlassen")
        return {"erfolg": True}

    def steuer_setzen(self, charakter_id: int, steuer: int) -> dict:
        mitglied = self.datenbank.gilde_mitglied_laden(charakter_id)
        if not mitglied or mitglied["rang"] not in ("gildenmeister", "offizier"):
            return {"erfolg": False, "nachricht": "Keine Berechtigung"}

        if not 0 <= steuer <= 20:
            return {"erfolg": False, "nachricht": "Steuer muss zwischen 0 und 20% liegen"}

        if not self.datenbank.gilde_steuer_setzen(mitglied["gilden_id"], steuer):
            return {"erfolg": False, "nachricht": "Fehler beim Setzen der Steuer"}

        return {"erfolg": True}

    def stufe_kosten_berechnen(self, aktuelle_stufe: int) -> int:
        return int(5000 * (4 ** aktuelle_stufe))

    def stufe_aufsteigen(self, charakter_id: int) -> dict:
        mitglied = self.datenbank.gilde_mitglied_laden(charakter_id)
        if not mitglied or mitglied["rang"] not in ("gildenmeister", "offizier"):
            return {"erfolg": False, "nachricht": "Keine Berechtigung"}

        gilde = self.datenbank.gilde_laden(mitglied["gilden_id"])
        kosten = self.stufe_kosten_berechnen(gilde["stufe"])

        if gilde["kasse"] < kosten:
            return {"erfolg": False, "nachricht": f"Nicht genug Gold in der Kasse ({kosten}G benötigt)"}

        self.datenbank.gilde_kasse_einzahlen(mitglied["gilden_id"], -kosten)
        if not self.datenbank.gilde_stufe_erhoehen(mitglied["gilden_id"]):
            return {"erfolg": False, "nachricht": "Fehler beim Aufsteigen"}

        neue_gilde = self.datenbank.gilde_laden(mitglied["gilden_id"])
        self.datenbank.gilde_log_hinzufuegen(mitglied["gilden_id"], "", f"Gilde auf Stufe {neue_gilde['stufe']} aufgestiegen!")

        return {"erfolg": True, "neue_stufe": neue_gilde["stufe"], "kosten": kosten}

    def rang_setzen(self, charakter_id: int, ziel_charakter_id: int, neuer_rang: str) -> dict:
        mitglied = self.datenbank.gilde_mitglied_laden(charakter_id)
        if not mitglied or mitglied["rang"] != "gildenmeister":
            return {"erfolg": False, "nachricht": "Nur Gildenmeister kann Ränge vergeben"}

        if neuer_rang not in ("offizier", "mitglied"):
            return {"erfolg": False, "nachricht": "Ungültiger Rang"}

        if not self.datenbank.gilde_rang_setzen(mitglied["gilden_id"], ziel_charakter_id, neuer_rang):
            return {"erfolg": False, "nachricht": "Fehler beim Setzen des Ranges"}

        return {"erfolg": True}

    def mitglied_kicken(self, charakter_id: int, ziel_charakter_id: int) -> dict:
        mitglied = self.datenbank.gilde_mitglied_laden(charakter_id)
        if not mitglied or mitglied["rang"] not in ("gildenmeister", "offizier"):
            return {"erfolg": False, "nachricht": "Keine Berechtigung"}

        ziel = self.datenbank.gilde_mitglied_laden(ziel_charakter_id)
        if not ziel or ziel["gilden_id"] != mitglied["gilden_id"]:
            return {"erfolg": False, "nachricht": "Mitglied nicht gefunden"}

        if ziel["rang"] == "gildenmeister":
            return {"erfolg": False, "nachricht": "Gildenmeister kann nicht gekickt werden"}

        if not self.datenbank.gilde_mitglied_kicken(mitglied["gilden_id"], ziel_charakter_id):
            return {"erfolg": False, "nachricht": "Kick fehlgeschlagen"}

        return {"erfolg": True}

    def gilde_daten_laden(self, charakter_id: int) -> dict:
        mitglied = self.datenbank.gilde_mitglied_laden(charakter_id)
        if not mitglied:
            return {"in_gilde": False, "gilden_liste": self.datenbank.gilden_liste_laden()}

        gilde = self.datenbank.gilde_laden(mitglied["gilden_id"])
        mitglieder = self.datenbank.gilde_mitglieder_laden(mitglied["gilden_id"])
        log = self.datenbank.gilde_log_laden(mitglied["gilden_id"])

        return {
            "in_gilde": True,
            "gilde": gilde,
            "mitglied": mitglied,
            "mitglieder": mitglieder,
            "log": log
        }

    def steuer_einziehen(self, charakter_id: int, gold_belohnung: int) -> int:
        mitglied = self.datenbank.gilde_mitglied_laden(charakter_id)
        if not mitglied:
            return 0

        gilde = self.datenbank.gilde_laden(mitglied["gilden_id"])
        if not gilde or gilde["steuer"] == 0:
            return 0

        steuer_betrag = int(gold_belohnung * gilde["steuer"] / 100)
        if steuer_betrag > 0:
            self.datenbank.gilde_kasse_einzahlen(mitglied["gilden_id"], steuer_betrag)

        return steuer_betrag