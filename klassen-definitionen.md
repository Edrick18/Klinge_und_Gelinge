# Klassen-Definitionen

Alle Basis-Klassen und Spezialisierungen des Spiels.
Dieses Dokument ist die Grundlage für klassen.json und skill_definitionen.py.
Balancing-Werte sind Platzhalter — werden später angepasst.

---

## Basis-Klassen

---

### Krieger (Stärke) — Kern-Mechanik: Rage

**Rage-Regeln:**
- Start: 0, Maximum: 100
- +10 pro eigenem Auto-Attack-Treffer
- +5 pro erhaltenem Treffer
- Verfällt nicht während des Kampfes

**Aktive Skills:**
- *Brutaler Hieb* — Verbraucht 30 Rage für +40% Schaden. Ohne Rage normaler Angriff.
- *Kriegsschrei* — Verbraucht 50 Rage, nächste 5 Angriffe kosten keine Rage und +25% Schaden.
- *Zermürben* — Kostet 20 Rage, reduziert Gegner-Rüstung für 8s. Mehr Rage = längere Dauer.
- *Raserei* — Verbraucht alle Rage, macht 3 schnelle Angriffe. Schaden skaliert mit verbrauchter Rage.
- *Todesstoß* — Nur nutzbar ab 80 Rage, verbraucht alles. Massiver Einzelschaden.

**Passive Skills:**
- *Blutdurst* — Jeder Treffer bei über 50 Rage heilt um 2% max HP.
- *Unaufhaltsam* — Bei über 70 Rage ignorieren Angriffe 20% Rüstung.
- *Kriegsinstinkt* — Erhaltene Treffer geben doppelt Rage (+10 statt +5).

**Nodes:**
- Rage-Aufbau: Auto-Attacks geben +2 Rage (3x)
- Rage-Schwelle: Passive Skills aktivieren 10 Rage früher (2x)
- Rage-Übertrag: Raserei behält 20% der verbrauchten Rage (2x)
- Kriegsschrei-Reichweite: +1 Angriff bei Kriegsschrei (2x)
- Zermürben-Intensität: Mehr Rage beim Einsatz = mehr Rüstungsreduktion (2x)
- Todesstoß-Schwelle: Todesstoß ab 70 statt 80 Rage nutzbar (1x)
- Raserei-Tempo: Raserei-Angriffe schneller (2x)

---

### Wächter (Vitalität) — Kern-Mechanik: Schild-Stapel

**Schild-Regeln:**
- Start: 0, Maximum: 5 Stapel
- Jeder Stapel absorbiert den nächsten Treffer um X% des max HP
- Stapel nur durch Skills aufgebaut
- Erhaltener Treffer verbraucht einen Stapel

**Aktive Skills:**
- *Schutzschild* — Erzeugt 2 Schild-Stapel sofort.
- *Eiserne Haut* — Erzeugt 1 Stapel, nächster Treffer komplett absorbiert.
- *Notreserve* — Verbraucht alle Stapel, heilt pro Stapel um 8% max HP.
- *Vergeltung* — Verbraucht 1 Stapel, kontert nächsten Gegner-Angriff mit 80% des absorbierten Schadens.
- *Versteinern* — Verbraucht 3 Stapel, 3s unverwundbar.

**Passive Skills:**
- *Lebensquell* — Wenn Stapel auf 0 sinkt regeneriert Charakter 3% HP/s für 5s.
- *Stachelhaut* — Jeder absorbierte Treffer gibt Gegner 5% des Schadens zurück.
- *Zähigkeit* — Bei 3+ aktiven Stapeln reduziert sich erlittener Schaden um 15%.

**Nodes:**
- Schild-Stärke: Jeder Stapel absorbiert mehr (3x)
- Stapel-Max: +1 maximaler Stapel (2x)
- Vergeltungs-Kraft: Vergeltung gibt mehr Schaden zurück (2x)
- Notreserve-Heilung: Mehr HP pro verbrauchtem Stapel (2x)
- Stapel-Erhalt: 20% Chance Stapel bei Treffer nicht zu verlieren (2x)
- Versteinern-Dauer: +0.5s Unverwundbarkeit (2x)
- Schild-Reaktion: Neue Stapel erscheinen schneller nach Schutzschild (2x)

---

### Zauberer (Weisheit) — Kern-Mechanik: Elementar-Ladungen

**Ladungs-Regeln:**
- Feuer, Eis, Blitz — je max 3 Stapel
- Nur durch Elementar-Skills aufgebaut
- Kombinations-Effekte:
  - Feuer+Eis → Explosion: +50% mag. Schaden sofort
  - Eis+Blitz → Schockfrost: Gegner Atk-Speed -30% für 5s
  - Feuer+Blitz → Plasma: DoT 3% HP/2s für 8s
- Nach Kombination: beide Ladungstypen auf 0

**Aktive Skills:**
- *Feuerball* — 140% mag. Schaden, fügt 1 Feuer-Ladung hinzu.
- *Eisnadeln* — 120% mag. Schaden, fügt 1 Eis-Ladung hinzu.
- *Blitzkette* — 160% mag. Schaden, fügt 1 Blitz-Ladung hinzu.
- *Arkane Explosion* — Verbraucht alle Ladungen, Schaden steigt mit Anzahl.
- *Elementar-Entladung* — Löst sofort eine Kombination aus wenn zwei verschiedene Ladungstypen vorhanden.

**Passive Skills:**
- *Manaschild* — Bei 2+ Ladungen eines Typs wirkt Mana als HP-Puffer.
- *Elementarmeister* — Kombinationseffekte dauern 2s länger.
- *Resonanz* — Jede neue Ladung die einen Typ auf 3 bringt gibt +20% mag. Schaden auf nächsten Angriff.

**Nodes:**
- Ladungs-Dauer: Ladungen verfallen 3s später (3x)
- Kombinations-Stärke: Kombinations-Effekte +10% stärker (3x)
- Schnelle Entladung: Elementar-Entladung kürzerer Cooldown (2x)
- Feuer-Intensität: Plasma DoT-Schaden höher (2x)
- Frost-Tiefe: Schockfrost-Verlangsamung stärker (2x)
- Blitz-Leitfähigkeit: Blitz-Ladungen geben +1 Blitz statt 1 (1x)
- Arkane-Effizienz: Arkane Explosion behält 1 Ladung pro Typ nach Einsatz (2x)

---

### Schicksalsritter (Glück) — Kern-Mechanik: Fortune-Stapel

**Fortune-Regeln:**
- Start: 0, Maximum: 10 Stapel
- +1 Stapel bei jedem Krit
- +2 Stapel bei jedem Ausweichen
- Bei 10 Stapeln: nächster Angriff garantiert Krit mit doppeltem Krit-Schaden, dann Reset auf 5

**Aktive Skills:**
- *Glücksschlag* — Angriff der bei Krit 2 Fortune-Stapel gibt statt 1.
- *Schicksalsdrehung* — Verbraucht 5 Fortune-Stapel, nächster Angriff garantiert Krit.
- *Doppelschlag* — Zwei schnelle Angriffe, jeder Krit gibt Fortune. Höhere Krit-Chance bei mehr Fortune.
- *Rächer* — Verbraucht alle Fortune-Stapel, Schaden = 20% pro verbrauchtem Stapel.
- *Glückssträhne* — Verbraucht 3 Fortune-Stapel, nächste 8s können Angriffe nicht ausgewichen werden.

**Passive Skills:**
- *Scharfes Auge* — Bei 5+ Fortune-Stapeln erhöht sich Krit-Chance um 10%.
- *Glückstreffer* — Krits bei 8+ Fortune-Stapeln machen zusätzlichen Schaden.
- *Schicksalsgunst* — Ausweichen bei 5+ Fortune gibt +3 Stapel statt +2.

**Nodes:**
- Fortune-Aufbau: Krits geben +1 Fortune zusätzlich (3x)
- Fortune-Schwelle: Passive Skills aktivieren bei 1 weniger Fortune-Stapel (2x)
- Rächer-Kraft: Rächer skaliert besser mit verbrauchten Stapeln (2x)
- Glückssträhne-Dauer: +1s Dauer (2x)
- Fortune-Erhalt: Nach Reset bleiben 6 statt 5 Stapel (2x)
- Schicksalsdrehung-Kosten: Kostet 4 statt 5 Stapel (1x)
- Doppelschlag-Fortune: Beide Treffer von Doppelschlag geben Fortune (2x)

---

### Schatten (Beweglichkeit) — Kern-Mechanik: Combo-Punkte

**Combo-Regeln:**
- Start: 0, Maximum: 5
- +1 Combo pro Auto-Attack-Treffer
- +2 Combo pro Skill-Treffer
- Verfallen nach 6s ohne Treffer
- Finisher-Skills verbrauchen alle Combo-Punkte, Schaden skaliert mit Anzahl

**Aktive Skills:**
- *Klingentanz* — Drei schnelle Treffer, jeder gibt +1 Combo.
- *Schattensprung* — Teleport-Angriff, gibt +2 Combo, ignoriert Rüstung.
- *Tödlicher Stich* — Finisher: verbraucht alle Combos, Schaden pro Combo steigt.
- *Dunkelheit* — Verbraucht 3 Combos, senkt Gegner Trefferchance für 6s.
- *Abschluss* — Finisher: verbraucht alle Combos, nur unter 25% Gegner-HP, massiver Execute-Schaden.

**Passive Skills:**
- *Schattenschritt* — Bei 3+ Combos hat jeder Angriff 15% Chance sofort +1 Combo zu geben.
- *Katzenpfoten* — Ausweichen gibt +1 Combo.
- *Präzision* — Bei 4+ Combos können Angriffe nicht ausgewichen werden.

**Nodes:**
- Combo-Verfall: Verfalls-Timer +2s (3x)
- Combo-Aufbau: Skill-Treffer geben +1 Combo zusätzlich (2x)
- Finisher-Kraft: Finisher-Schaden pro Combo höher (3x)
- Schattensprung-Combo: Gibt +3 statt +2 Combo (2x)
- Abschluss-Schwelle: Nutzbar unter 30% statt 25% HP (2x)
- Dunkelheit-Kosten: Kostet 2 statt 3 Combos (1x)
- Combo-Start: Beginnt Kampf mit 1 Combo (1x)

---

### Herold (Charisma) — Kern-Mechanik: Einfluss-Stapel

**Einfluss-Regeln:**
- Start: 0, Maximum: 8
- +1 pro aktivem Debuff auf Gegner
- +1 pro aktivem Buff auf sich selbst
- Bei 8 Stapeln: Dominanz — alle aktiven Buffs und Debuffs +50% stärker für 6s, Stapel auf 4
- Stapel sinken wenn Buffs/Debuffs ablaufen

**Aktive Skills:**
- *Schlachtruf* — Buff: eigener Schaden +20% für 8s, gibt +1 Einfluss.
- *Einschüchtern* — Debuff: Gegner Schaden -20% für 8s, gibt +1 Einfluss.
- *Inspiration* — Buff: Mana-Regen +150% für 6s, gibt +1 Einfluss.
- *Demütigung* — Debuff: Gegner Atk-Speed -30% für 8s, gibt +1 Einfluss.
- *Verderbnis* — Verbraucht 4 Einfluss-Stapel, entfernt alle Buffs vom Gegner, 100% mag. Schaden pro entferntem Buff.

**Passive Skills:**
- *Dunkle Ausstrahlung* — Bei 4+ Einfluss verlieren Gegner-Debuffs 2s später.
- *Angstfluch* — Bei 6+ Einfluss geben eigene Debuffs +1 Einfluss beim Auslösen.
- *Schattenpakt* — Dominanz-Aktivierung gibt sofort +30% Schaden für den ersten Angriff danach.

**Nodes:**
- Einfluss-Aufbau: Neue Buffs/Debuffs geben +0.5 Einfluss zusätzlich (3x)
- Einfluss-Max: +1 maximaler Stapel (2x)
- Dominanz-Dauer: +1s Dominanz-Effekt (2x)
- Verderbnis-Kosten: Kostet 3 statt 4 Stapel (2x)
- Buff-Verlängerung: Eigene Buffs dauern +1s (2x)
- Debuff-Verlängerung: Eigene Debuffs dauern +1s (2x)
- Dominanz-Reset: Reset auf 5 statt 4 nach Dominanz (1x)

---

## Spezialisierungen

---

### Krieger-Spezialisierungen

#### Berserker — Maximaler Schaden, Rage als Treibstoff

**Neue Mechanik: Blut-Rausch**
Bei 100 Rage und aktivem Berserk verliert der Charakter 2% HP/s aber Schaden steigt weiter +10% pro Sekunde im Rausch.

**Aktive Skills:**
- *Zerfleischen* — Verbraucht 40 Rage, 5 schnelle schwache Treffer, jeder gibt +3 Rage zurück.
- *Blutschrei* — Opfert 10% HP für sofort +50 Rage.
- *Hinrichtung* — Verbraucht alle Rage, Schaden = Rage × 3%, nur unter 30% Gegner-HP.
- *Wut-Entladung* — Verbraucht 60 Rage, nächste 4s kosten Skills keine Rage.

**Passive Skills:**
- *Blutgier* — Erhaltene Treffer geben +8 Rage statt +5.
- *Adrenalin* — Im Berserk-Modus steigt Rage-Aufbau um 50%.

**Nodes:**
- Blut-Rausch-Dauer: +1s (3x)
- Blut-Rausch-Schaden: +2% pro Sekunde (2x)
- HP-Verlust reduzieren: -0.5% HP/s im Rausch (2x)
- Zerfleischen-Rage: +1 Rage pro Treffer zurück (2x)
- Hinrichtungs-Schwelle: Nutzbar unter 35% statt 30% (2x)

---

#### Ritter — Ausgewogen, Rage für Angriff und Verteidigung

**Neue Mechanik: Kampf-Haltung**
- Angriffs-Haltung: Rage gibt +3% Schaden pro 10 Rage
- Verteidigungs-Haltung: Rage gibt +2% Schadensreduktion pro 10 Rage

**Aktive Skills:**
- *Haltungswechsel* — Wechselt zwischen Angriff und Verteidigung, kostet 20 Rage.
- *Schildschlag* — 100% Schaden + 1 Schild-Stapel wenn in Verteidigungs-Haltung.
- *Präzisionsschlag* — In Angriffs-Haltung: ignoriert 40% Rüstung, kostet 30 Rage.
- *Standhaft* — In Verteidigungs-Haltung: nächster Treffer gibt doppelt Rage.

**Passive Skills:**
- *Disziplin* — Haltungswechsel gibt +10 Rage.
- *Kampferfahrung* — Rage-Verlust beim Haltungswechsel reduziert.

**Nodes:**
- Haltungs-Bonus: +0.5% Effekt pro 10 Rage (3x)
- Haltungswechsel-Kosten: -5 Rage (2x)
- Schildschlag-Stapel: +1 Stapel bei Verteidigungs-Haltung (2x)
- Standhaft-Rage: +5 Rage zusätzlich (2x)
- Präzisionsschlag-Durchdringung: +5% Rüstungsignorierung (2x)

---

#### Paladin — Verteidigung und Heilung durch Rage

**Neue Mechanik: Heilige Wut**
Ab 70 Rage heilt jeder erhaltene Treffer den Charakter um 5% des erlittenen Schadens. Rage sinkt dabei um 10 pro Treffer.

**Aktive Skills:**
- *Heilsegen* — Verbraucht 40 Rage, heilt 25% max HP.
- *Göttlicher Schutz* — Verbraucht 50 Rage, erzeugt Schild der 20% max HP absorbiert.
- *Buße* — Verbraucht 30 Rage, entfernt einen Debuff.
- *Heilige Vergeltung* — Im Heilige-Wut-Zustand: nächster Angriff macht +60% Schaden.

**Passive Skills:**
- *Märtyrer* — Erlittener Schaden gibt +8 Rage statt +5.
- *Göttliche Gnade* — Heilige Wut aktiviert sich bereits ab 60 Rage.

**Nodes:**
- Heilige-Wut-Heilung: +1% Heilung pro Treffer (3x)
- Heilsegen-Wert: +3% Heilung (2x)
- Göttlicher-Schutz-Stärke: +2% Schild (2x)
- Buße-Kosten: -5 Rage (2x)
- Rage-Aufbau: Erhaltene Treffer geben +2 Rage zusätzlich (3x)

---

### Wächter-Spezialisierungen

#### Bastian — Maximale Absorption, Schaden durch Stapel

**Neue Mechanik: Festung**
Bei 5 Stapeln werden alle eingehenden Treffer um 50% reduziert zusätzlich zur normalen Absorption. Fällt weg sobald ein Stapel verbraucht wird.

**Aktive Skills:**
- *Mauerwerk* — Erzeugt sofort 3 Stapel.
- *Stachelpanzer* — Verbraucht 2 Stapel, nächste 6s reflektiert jeder Treffer 30% Schaden.
- *Unzerbrechlich* — Bei 4+ Stapeln: nächste 3 Treffer verbrauchen keinen Stapel.
- *Trümmerangriff* — Verbraucht alle Stapel, Schaden = Anzahl Stapel × 15%.

**Passive Skills:**
- *Granit* — Festungs-Zustand reduziert Schaden um 60% statt 50%.
- *Schild-Regeneration* — Alle 12s automatisch +1 Stapel wenn unter Maximum.

**Nodes:**
- Festungs-Schwelle: Aktiviert bei 4 statt 5 Stapeln (1x)
- Stachelpanzer-Reflektion: +5% Schaden zurück (3x)
- Mauerwerk-Stapel: +1 Stapel zusätzlich (2x)
- Unzerbrechlich-Treffer: +1 Treffer ohne Stapelverlust (2x)
- Schild-Regen-Timer: -2s (2x)

---

#### Blutmagier — HP opfern für Schaden, Stapel als Schutz

**Neue Mechanik: Blutpakt**
Wenn Charakter aktiv HP opfert und Schild-Stapel vorhanden sind werden die geopferten HP von den Stapeln absorbiert statt abgezogen. Ein Stapel absorbiert bis zu 15% max HP.

**Aktive Skills:**
- *Lebensopfer* — Opfert 15% HP für +40% Schaden für 8s, Stapel absorbieren wenn vorhanden.
- *Blutexplosion* — Verbraucht alle Stapel, Schaden = Stapel × 20% + 10% fehlende HP.
- *Seelenraub* — 120% Schaden, heilt um 40% des verursachten Schadens.
- *Blutschild* — Opfert 10% HP um 2 Stapel zu erzeugen.

**Passive Skills:**
- *Vampirismus* — Jeder Angriff heilt um 3% des Schadens wenn Stapel vorhanden.
- *Blutdruck* — Je weniger HP desto mehr Schaden — bis +30% bei unter 30% HP.

**Nodes:**
- Blutpakt-Absorption: Stapel absorbiert +3% mehr HP (3x)
- Lebensopfer-Schaden: +5% Schaden-Bonus (2x)
- Blutexplosion-Skalierung: +3% Schaden pro Stapel (2x)
- Seelenraub-Heilung: +5% Heilung (2x)
- Blutdruck-Schwelle: Bonus aktiviert bereits bei 35% HP (2x)

---

#### Kriegspriester — Heilung und Gegenangriffe durch Stapel

**Neue Mechanik: Heilige Absolution**
Wenn ein Stapel einen Treffer absorbiert hat der Charakter 2s Zeit um einen Skill zu aktivieren. Tut er das bekommt der Skill +30% Wirkung.

**Aktive Skills:**
- *Heilswelle* — Heilt 20% max HP, nach Absolution +30% Heilung.
- *Göttlicher Konter* — Verbraucht 1 Stapel, kontert mit 100% des absorbierten Schadens.
- *Läuterung* — Entfernt alle Debuffs, nach Absolution auch 4s immun gegen Debuffs.
- *Heiliger Zorn* — Nach Absolution: nächster Angriff macht +80% Schaden.

**Passive Skills:**
- *Segen* — Absolutions-Fenster dauert 3s statt 2s.
- *Göttliche Rüstung* — Bei 3+ Stapeln reduziert sich erlittener Schaden um 10%.

**Nodes:**
- Absolutions-Bonus: +5% Wirkung (3x)
- Heilswelle-Basis: +3% Heilung (2x)
- Göttlicher-Konter-Schaden: +10% Konterschaden (2x)
- Läuterungs-Immunität: +1s Immunität nach Absolution (2x)
- Stapel-Aufbau: Schutzschild gibt +1 Stapel zusätzlich (2x)

---

### Zauberer-Spezialisierungen

#### Pyromant — Feuer-Ladungen maximieren, Brennen als Hauptschaden

**Neue Mechanik: Inferno**
Bei 3 Feuer-Ladungen brennt der Gegner permanent mit verstärktem DoT (+50% Brennen-Schaden) solange Feuer-Ladungen auf 3 bleiben.

**Aktive Skills:**
- *Feuersturm* — 130% mag. Schaden, fügt 2 Feuer-Ladungen hinzu statt 1.
- *Ascheregen* — Verbraucht alle Feuer-Ladungen, Brennen-Schaden der nächsten 10s +80%.
- *Glutmantel* — 1 Feuer-Ladung, Gegner nimmt +15% mehr Brennen-Schaden für 8s.
- *Feuerwall* — Erzeugt 3s Brennen-Barriere — Gegner-Angriffe lösen schwaches Brennen aus.

**Passive Skills:**
- *Ewige Flamme* — Feuer-Ladungen verfallen 4s später als andere Ladungen.
- *Brandmeister* — Inferno-Bonus steigt auf +70% Brennen-Schaden.

**Nodes:**
- Inferno-Schwelle: Aktiviert bei 2 Feuer-Ladungen (1x)
- Feuersturm-Ladungen: +1 Feuer-Ladung zusätzlich (2x)
- Ascheregen-Bonus: +10% Brennen-Verstärkung (2x)
- Glutmantel-Dauer: +2s (2x)
- Brennen-Intensität: Basis-Brennen-Schaden höher (3x)

---

#### Frostmagier — Eis-Ladungen für Kontrolle

**Neue Mechanik: Einfrieren**
Bei 3 Eis-Ladungen und einer Kombination die Eis verbraucht wird der Gegner für 2s komplett eingefroren. Einmal pro Kampf, danach nur normale Verlangsamung.

**Aktive Skills:**
- *Eissturm* — 110% mag. Schaden, fügt 2 Eis-Ladungen hinzu, Gegner Atk-Speed -10% für 4s.
- *Frostpanzer* — 1 Eis-Ladung, eigene Rüstung +20% für 6s.
- *Gletscherschlag* — Verbraucht alle Eis-Ladungen, Schaden + Verlangsamung skaliert mit Anzahl.
- *Eiszeit* — Setzt alle Eis-Ladungen auf Maximum sofort.

**Passive Skills:**
- *Permafrost* — Verlangsamungs-Effekte dauern 2s länger.
- *Eisige Präsenz* — Bei 2+ Eis-Ladungen hat Gegner permanent -10% Atk-Speed.

**Nodes:**
- Einfrieren-Dauer: +0.5s (2x)
- Eissturm-Verlangsamung: +5% Atk-Speed-Reduktion (3x)
- Frostpanzer-Rüstung: +5% Rüstung (2x)
- Gletscherschlag-Skalierung: +5% Schaden pro Ladung (2x)
- Eiszeit-Cooldown: -4s (2x)

---

#### Sturmrufer — Blitz-Ladungen für Geschwindigkeit

**Neue Mechanik: Sturmform**
Bei 3 Blitz-Ladungen wechselt der Charakter in Sturmform — Auto-Attacks haben 30% Chance einen zweiten Treffer auszulösen. Dauert bis Blitz-Ladungen verbraucht werden.

**Aktive Skills:**
- *Blitzschlag* — 150% mag. Schaden, fügt 2 Blitz-Ladungen hinzu.
- *Sturmschritt* — 1 Blitz-Ladung, eigene Atk-Speed +25% für 6s.
- *Kettenblitz* — Verbraucht alle Blitz-Ladungen, Anzahl Treffer = Anzahl Ladungen.
- *Gewitterruf* — Setzt alle Blitz-Ladungen auf Maximum sofort.

**Passive Skills:**
- *Statisch* — In Sturmform geben Auto-Attacks +1 Blitz-Ladung.
- *Blitzreflexe* — In Sturmform +10% Ausweichen.

**Nodes:**
- Sturmform-Chance: +5% Doppeltreffer-Chance (3x)
- Blitzschlag-Ladungen: +1 Blitz-Ladung zusätzlich (2x)
- Sturmschritt-Dauer: +2s (2x)
- Kettenblitz-Treffer: +1 Treffer bei vollem Einsatz (2x)
- Gewitterruf-Cooldown: -3s (2x)

---

### Schicksalsritter-Spezialisierungen

#### Glücksbringer — Fortune maximieren, Krit-Burst

**Neue Mechanik: Schicksalsschlag**
Wenn Fortune bei 10 und der garantierte Krit ausgelöst wird bekommt der nächste Skill automatisch auch garantierten Krit.

**Aktive Skills:**
- *Glücksregen* — Gibt sofort +3 Fortune-Stapel.
- *Schicksalsspirale* — 120% Schaden, bei Krit gibt es +3 Fortune statt +1.
- *Goldener Moment* — Verbraucht 8 Fortune, nächste 5s jeder Angriff garantiert Krit.
- *Fortunas Klinge* — Schaden skaliert direkt mit Fortune-Stapeln × 15%.

**Passive Skills:**
- *Glücksmagnet* — Ausweichen gibt +3 Fortune statt +2.
- *Ewiges Glück* — Nach Fortune-Reset bleiben 7 statt 5 Stapel.

**Nodes:**
- Schicksalsschlag-Kette: +1 garantierter Krit nach Reset (2x)
- Glücksregen-Stapel: +1 Fortune zusätzlich (2x)
- Goldener-Moment-Dauer: +1s (2x)
- Fortunas-Klinge-Skalierung: +2% pro Stapel (2x)
- Fortune-Aufbau: Krits geben +1 Fortune zusätzlich (3x)

---

#### Schicksalsweber — Fortune kontrollieren, Zufall eliminieren

**Neue Mechanik: Schicksalskontrolle**
Spieler kann Fortune-Stapel "sperren" — gesperrte Stapel werden nicht beim Reset verbraucht und können manuell freigegeben werden.

**Aktive Skills:**
- *Stapel sperren* — Sperrt aktuelle Fortune-Stapel.
- *Schicksalsbruch* — Gibt alle gesperrten Stapel frei, jeder macht 10% Schaden.
- *Vorhersage* — Verbraucht 5 Fortune, nächster Angriff 200% Schaden, kein Krit aber trifft immer.
- *Zeitlinie verschieben* — Verbraucht alle Fortune, setzt alle Skill-Cooldowns um 50% zurück.

**Passive Skills:**
- *Schicksalskenner* — Gesperrte Stapel verfallen nie.
- *Kontrolleur* — Schicksalsbruch-Schaden +5% pro freigegebenem Stapel.

**Nodes:**
- Schicksalsbruch-Schaden: +2% pro Stapel (3x)
- Vorhersage-Schaden: +10% (2x)
- Zeitlinie-Cooldown-Reset: +5% Cooldown-Reduktion (2x)
- Stapel-Sperren-Bonus: Gesperrte Stapel geben +1% Schaden passiv (2x)
- Zeitlinie-Fortune-Kosten: -1 Fortune (2x)

---

#### Rächer — Ausweichen als Kern, Fortune durch Konter

**Neue Mechanik: Vergeltungsschlag**
Nach jedem Ausweichen hat der nächste Angriff innerhalb von 2s automatisch +50% Schaden und gibt +3 Fortune statt +2.

**Aktive Skills:**
- *Schattenausweichen* — Ausweichen +30% für 4s, nächstes Ausweichen gibt +4 Fortune.
- *Vergeltungsstoß* — Nur nach Ausweichen nutzbar, 160% Schaden + Fortune-Bonus.
- *Geisterform* — 3s lang kein Angriff trifft, danach Vergeltungsschlag auf alle verpassten Treffer.
- *Fortunas Rache* — Verbraucht alle Fortune, Schaden × Anzahl Ausweicher in diesem Kampf.

**Passive Skills:**
- *Spiegelreflexe* — Vergeltungsschlag-Fenster dauert 3s statt 2s.
- *Geisterhafte Präsenz* — Bei 5+ Fortune +10% Ausweichen-Chance.

**Nodes:**
- Vergeltungsschlag-Schaden: +5% (3x)
- Schattenausweichen-Fortune: +1 Fortune bei Ausweichen (2x)
- Vergeltungsstoß-Schaden: +10% (2x)
- Geisterform-Dauer: +0.5s (2x)
- Fortunas-Rache-Skalierung: +3% pro Ausweicher (2x)

---

### Schatten-Spezialisierungen

*(Wird ergänzt)*

---

### Herold-Spezialisierungen

*(Wird ergänzt)*

---

### Schatten-Spezialisierungen

#### Assassine — Execute und Gift, Combo für tödliche Finisher

**Neue Mechanik: Tödliche Konzentration**
Bei 5 Combos (Maximum) erhöht sich der Schaden des nächsten Finishers um +20% für jede Sekunde die Combos auf Maximum gehalten werden (bis +100%).

**Aktive Skills:**
- *Giftklinge* — 100% Schaden, vergiftet Gegner 3% HP/2s für 10s, gibt +2 Combo.
- *Hinterhalt* — Verbraucht 4 Combos, nächster Angriff immer Krit mit +60% Krit-Schaden.
- *Tödlicher Stich* — Finisher: Schaden + Konzentrations-Bonus + alle aktiven DoT-Schäden sofort als Burst.
- *Schleichgift* — Verbraucht 3 Combos, nächste 3 Auto-Attacks vergiften automatisch.

**Passive Skills:**
- *Meuchelmörder* — Finisher-Schaden +5% pro aktivem DoT auf dem Gegner.
- *Giftmeister* — Gift-Ticks geben +0.5 Combo.

**Nodes:**
- Konzentrations-Bonus: +5% pro Sekunde auf Maximum (3x)
- Giftklinge-Dauer: +2s Gift (2x)
- Hinterhalt-Krit-Schaden: +10% (2x)
- Schleichgift-Angriffe: +1 Auto-Attack (2x)
- Konzentrations-Maximum: Cap steigt auf +120% (1x)

---

#### Klingentänzer — Geschwindigkeit und Mehrfachtreffer

**Neue Mechanik: Tanz-Rhythmus**
Nach jedem Finisher werden die ersten 2 Auto-Attacks danach automatisch zu Combo-Aufbau-Skills — geben +2 Combo statt +1 und haben keinen Cooldown.

**Aktive Skills:**
- *Klingensturm* — Verbraucht alle Combos, macht Combos × 1 schnellen Treffer.
- *Wirbelklinge* — 3 Treffer die je +1 Combo geben und Atk-Speed kurz erhöhen.
- *Rhythmischer Schlag* — Gibt +3 Combo, nächster Finisher kostet 1 Combo weniger.
- *Tanz des Todes* — Verbraucht 4 Combos, nächste 4s jeder Auto-Attack gibt +2 Combo.

**Passive Skills:**
- *Flinke Klinge* — Tanz-Rhythmus gibt +3 Combo statt +2 bei den ersten Angriffen.
- *Ewiger Tanz* — Finisher-Cooldowns reduzieren sich um 1s pro aufgebautem Combo.

**Nodes:**
- Tanz-Rhythmus-Angriffe: +1 Angriff mit Bonus (2x)
- Klingensturm-Treffer: +1 Treffer pro Combo (2x)
- Wirbelklinge-Combo: +1 Combo pro Treffer (2x)
- Tanz-des-Todes-Dauer: +1s (2x)
- Rhythmischer-Schlag-Rabatt: Finisher kostet 1 Combo weniger (2x)

---

#### Phantom — Ausweichen und Gegenangriff

**Neue Mechanik: Schattenform**
Bei 5 Combos kann der Phantom in Schattenform wechseln — für 3s werden alle eingehenden Angriffe automatisch ausgewichen und jeder Ausweicher gibt +2 Combo. Nach Schattenform Reset auf 2 Combos.

**Aktive Skills:**
- *Schattentritt* — Ausweichen +40% für 4s, nächstes Ausweichen gibt +3 Combo.
- *Geisterklinge* — Verbraucht 3 Combos, 150% Schaden, ignoriert Rüstung komplett.
- *Schattenform aktivieren* — Löst Schattenform aus wenn 5 Combos vorhanden.
- *Phantomschlag* — Direkt nach Schattenform nutzbar, 200% Schaden + Combo-Multiplikator.

**Passive Skills:**
- *Nebelwandler* — Schattenform-Dauer +1s.
- *Schattentanz* — Combo-Verfall-Timer wird während Schattenform pausiert.

**Nodes:**
- Schattenform-Dauer: +0.5s (3x)
- Schattentritt-Combo: +1 Combo bei Ausweichen (2x)
- Geisterklinge-Schaden: +10% (2x)
- Phantomschlag-Multiplikator: +10% pro Combo (2x)
- Schattenform-Reset: Behält 3 statt 2 Combos nach Schattenform (2x)

---

### Herold-Spezialisierungen

#### Kriegsherr — Starke Selbst-Buffs, Einfluss durch eigene Stärke

**Neue Mechanik: Kriegsruf**
Bei Dominanz-Aktivierung macht der nächste Angriff zusätzlichen Schaden für jeden aktiven Buff × 15%.

**Aktive Skills:**
- *Berserkerruf* — Buff: eigener Schaden +30% für 10s, gibt +2 Einfluss.
- *Stahlwille* — Buff: eigene Rüstung +25% für 8s, gibt +1 Einfluss.
- *Kampfrausch* — Buff: Atk-Speed +20% für 6s, gibt +1 Einfluss.
- *Kriegsruf-Entladung* — Verbraucht alle Einfluss-Stapel, Schaden = Stapel × 20% + Buff-Bonus.

**Passive Skills:**
- *Ungebrochener Wille* — Jeder aktive Buff verlängert sich um 1s wenn Dominanz aktiviert.
- *Kriegserfahrung* — Buffs geben +0.5 Einfluss zusätzlich beim Auslösen.

**Nodes:**
- Kriegsruf-Schaden: +3% pro Buff (3x)
- Berserkerruf-Dauer: +2s (2x)
- Stahlwille-Rüstung: +5% (2x)
- Kampfrausch-Atk-Speed: +5% (2x)
- Kriegsruf-Entladung-Skalierung: +3% pro Stapel (2x)

---

#### Hexer — Starke Debuffs, Einfluss durch Gegner-Schwächung

**Neue Mechanik: Fluchverkettung**
Wenn 3+ verschiedene Debuffs gleichzeitig auf dem Gegner aktiv sind verstärken sie sich gegenseitig um 20%. Jeder weitere Debuff erhöht diesen Bonus um 10%.

**Aktive Skills:**
- *Verdammungsfluch* — Debuff: Gegner Schaden -25% für 10s, gibt +2 Einfluss.
- *Schwächefluch* — Debuff: Gegner Rüstung -30% für 8s, gibt +2 Einfluss.
- *Lähmungsfluch* — Debuff: Gegner Atk-Speed -35% für 6s, gibt +2 Einfluss.
- *Fluchexplosion* — Verbraucht alle Einfluss-Stapel, Schaden = Stapel × 15% × aktive Debuffs.

**Passive Skills:**
- *Meisterflücher* — Fluchverkettungs-Bonus steigt auf 25% pro Debuff-Typ.
- *Dunkle Resonanz* — Debuffs verlängern sich um 1s wenn Dominanz aktiv ist.

**Nodes:**
- Fluchverkettung-Basis: +5% Verstärkung (3x)
- Verdammungsfluch-Dauer: +2s (2x)
- Schwächefluch-Stärke: +5% Rüstungsreduktion (2x)
- Lähmungsfluch-Stärke: +5% Atk-Speed-Reduktion (2x)
- Fluchexplosion-Skalierung: +3% pro Stapel (2x)

---

#### Seelenbinder — Buffs und Debuffs kombinieren für Synergie

**Neue Mechanik: Seelenband**
Für jeden aktiven Debuff auf dem Gegner verstärkt sich ein zufällig ausgewählter eigener Buff um 15%. Umgekehrt: für jeden eigenen Buff verliert der Gegner 5% eines zufälligen Stats.

**Aktive Skills:**
- *Lebensband* — Buff auf sich: heilt 3% HP/s für 8s. Debuff auf Gegner: verliert 3% HP/s für 8s. Beide gleichzeitig. Gibt +2 Einfluss.
- *Krafttransfer* — Buff: eigene Atk-Speed +15% für 6s. Debuff: Gegner Atk-Speed -15% für 6s. Gibt +2 Einfluss.
- *Seelensog* — Verbraucht 3 Einfluss, stiehlt einen aktiven Buff vom Gegner.
- *Seelenband-Burst* — Bei Dominanz: alle Seelenband-Effekte feuern sofort einmal extra.

**Passive Skills:**
- *Harmonische Seele* — Seelenband-Verstärkung steigt auf 20% pro Debuff.
- *Gleichgewicht* — Wenn gleich viele Buffs wie Debuffs aktiv sind +10% zu allen Einfluss-Effekten.

**Nodes:**
- Seelenband-Stärke: +3% Verstärkung pro Debuff (3x)
- Lebensband-Intensität: +1% HP/s für beide Effekte (2x)
- Krafttransfer-Stärke: +5% für beide Effekte (2x)
- Seelensog-Einfluss: +1 Einfluss zusätzlich (2x)
- Gleichgewicht-Bonus: +3% zu allen Effekten (2x)
