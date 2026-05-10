---
name: skill-autor
description: >
  Muss konsultiert werden BEVOR der Agent einen neuen Skill schreibt oder einen
  bestehenden Skill aktualisiert. Definiert was ein Skill ist, wie er aufgebaut
  wird und wann er geschrieben wird. Trigger: "schreibe einen Skill", "aktualisiere
  einen Skill", "neues System ohne passenden Skill", Agent trifft dieselbe
  Entscheidung zum zweiten Mal.
---

# skill-autor

Ein Skill ist ein **Regelwerk für wiederkehrende Entscheidungen** — kein Bauplan,
kein Datensatz, kein Code-Template. Er beantwortet: wie entscheide ich in diesem
Bereich? Nicht: wie sieht das Ergebnis aus?

---

## Was ein Skill ist — und was nicht

| Skill enthält | Skill enthält NICHT |
|---|---|
| Entscheidungsregeln | Pixel-Werte oder Koordinaten |
| Wo Dateien hingehören | Vollständige Datendefinitionen |
| Wie Systeme strukturiert werden | Fertige JSON/Dict-Strukturen |
| Wann welche Lösung gewählt wird | Code der direkt kopiert wird |
| Pflichtprüfungen | Spielbalancing-Werte |

**Faustregel:** Wenn der Inhalt sich bei jedem Projekt ändert → gehört er nicht
in den Skill sondern in eine Datendatei (JSON, Python-Dict, Datenbank).

---

## Wann einen Skill schreiben

```
Frage 1: Habe ich einen Skill der diese Aufgabe abdeckt?
  JA  → Skill lesen, dann umsetzen.
  NEIN → weiter zu Frage 2.

Frage 2: Werde ich diese Entscheidung mehr als einmal treffen?
  JA  → Skill schreiben, dann umsetzen.
  NEIN → direkt umsetzen, kein Skill nötig.

Frage 3: Gibt es einen teilweise passenden Skill?
  JA  → bestehenden Skill erweitern, nicht neu schreiben.
  NEIN → neuen Skill schreiben.
```

---

## Skill-Datei Aufbau

```markdown
---
name: skill-[thema]
description: >
  Wann liest der Agent diesen Skill? Spezifische Trigger-Sätze.
  Schlüsselwörter die das Thema beschreiben.
---

# skill-[thema]

1-2 Sätze: Was regelt dieser Skill und warum existiert er?

---

## Kernregeln

Entscheidungsbäume oder Tabellen — keine Prosa.
Jede Regel hat einen kurzen Grund dahinter.

---

## Entscheidungsbaum

Konkrete Wenn-Dann-Regeln für häufige Situationen.

---

## Pflichtprüfung

Checkliste die nach jeder Implementierung abgehakt wird.
```

---

## Qualitätsregeln

| Regel | Grund |
|---|---|
| Maximal 200 Zeilen | Längere Skills werden nicht vollständig gelesen |
| Entscheidungsbäume statt Fließtext | Agent folgt Bäumen zuverlässiger |
| Jede Regel hat einen Grund | Regeln werden besser angewendet |
| Kein doppelter Inhalt zwischen Skills | Konflikte verwirren den Agenten |
| Name immer mit Präfix `skill-` | Eindeutig erkennbar |
| Keine Spielwerte oder Koordinaten | Skills veralten sonst sofort |

---

## Skill registrieren

Nach dem Schreiben:
1. Datei speichern unter `skills/skill-[thema].md`
2. Eintrag in `skills/skill-übersicht.md` hinzufügen
3. Eintrag in `FORTSCHRITT.md` schreiben

---

## Skill aktualisieren

Aktualisieren wenn eine Regel sich als falsch herausstellt, ein neues Pattern
entdeckt wird, oder der Entwickler eine Korrektur gibt.
Nie löschen ohne Entwickler zu fragen.

---

## Pflichtprüfung

- [ ] Enthält der Skill nur Regeln, keine Daten oder Werte?
- [ ] Ist er unter 200 Zeilen?
- [ ] Hat er mindestens einen Entscheidungsbaum oder eine Tabelle?
- [ ] Ist der Trigger in `description` spezifisch genug?
- [ ] Ist er in `skill-übersicht.md` eingetragen?
- [ ] Gibt es Konflikte mit anderen Skills?
