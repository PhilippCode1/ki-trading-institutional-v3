# Start für den Coding-Agenten (§17.2)

> **Betreiberfassung.** Diese Datei gibst du dem Coding-Agenten, der das System baut, als erste Anweisung; sie legt fest, was er zuerst tut, was er nie tut und wann er anhält. Der Agent eröffnet keine Konten, schließt keine Verträge, bewegt kein Geld und sendet keine Echtgeldorders; er arbeitet nur im Repository und im Demokonto, und jede Änderung liest ein Mensch, bevor sie zusammengeführt wird. Vor G0 wird nur das Paket geprüft und die Liste der G0-Eingaben übergeben; dafür braucht es weder einen Coding-Agenten noch Geld, du kannst beides selbst ausführen. Repository, CI und Secret-Scan kommen zu Beginn von BS-01, bevor das erste Zugangsdatum existiert; alles Weitere beginnt erst, wenn G0 mit signiertem PASS vorliegt. Für Go/No-Go heißt das: Heute sind nur die Schritte 1 und 2 zulässig. Nächster Schritt: Schritt 1.

## 1 Regeln, die immer gelten

1. **Kein Geld, keine Konten, keine Verträge.** Kontoeröffnung, Datenkauf, Abos, Zahlungen und Echtgeldorders sind Handlungen des Betreibers. Der Agent bereitet sie höchstens vor und hält an.
2. **Kein Sprachmodell im Geldpfad.** Kern, Risikomotor, Auftragsverwaltung und Adapter enthalten keinen Aufruf eines Sprachmodells und keine Abhängigkeit darauf (T-AI-001 bis T-AI-004, REQ-AI-*).
3. **Eine Quelle der Wahrheit.** Schwellen, Grenzen und Kosten kommen aus `parameters.json` und den Registern dieses Pakets, nie als Zahl im Code. Neue Werte werden als Parameter mit Status und Begründung angelegt, nicht erfunden (R-04).
4. **Keine erfundenen Angaben.** Betreiberangaben, Brokerwerte, Gebühren, Wohnsitz, Kundeneinstufung, Datenrechte und rechtliche Freigaben kommen nur als bestätigte externe Eingaben (`external_inputs.json`); fehlt eine, bleibt die abhängige Arbeit gesperrt (BLOCKED_EXTERNAL).
5. **Verträge vor Code.** Jede Schnittstelle folgt dem Schema unter `schemas/`; die Beispiele unter `examples/` sind Testfälle, die Zustandsautomaten mit ihren Traces sind die Referenzsemantik (`architecture/state_machines.json`, `examples/valid/state_traces/`).
6. **Tests zuerst.** Jedes Arbeitspaket beginnt mit den Tests seiner Stufe aus `implementation/test_catalog.json` (Prozedur, Orakel, Bestehenskriterium); fertig ist es erst, wenn sie bestehen und ein Mensch die Änderung gelesen hat.
7. **Anhalten an Toren.** Nach jeder Stufe hält der Agent an. Das Tor wertet nur der Evaluator im Prüfmodul aus (`research/evidence_gates.json`); der Agent liefert Eingaben und Laufbelege, nie das Ergebnis.
8. **Geheimnisse bleiben draußen.** Keine Zugangsdaten, Schlüssel oder Kontokennungen im Repository, in Logs, in Tickets oder im Kontext des Agenten; der Secret-Scan läuft vor jedem Commit (T-SEC-008).

## 2 Erste Schritte vor G0 (BS-00, ohne Geldausgabe)

**Schritt 1 – Paket prüfen.** Paket in ein frisches Verzeichnis entpacken, Prüfsumme gegen die `.sha256`-Datei vergleichen und im Paketverzeichnis ausführen:

```
python validation/validate_package.py --root . --strict --stage full
python validation/render_blocks.py --root . --check
python validation/run_calculators.py --check
python validation/state_engine.py --root .
python validation/gate_engine.py --root .
python validation/example_rules.py --root .
```

Alle Befehle müssen mit Exitcode 0 enden. Ein Fehler wird gemeldet, nicht umgangen.

**Schritt 2 – Übergabe an den Betreiber.** Liste der G0-Eingaben mit Zweck und Format: X-BRK-FEES, X-OP-RATE, X-OP-BUDGET, X-BRK-INTEREST, X-V1-PRODUCTS (`external_inputs.json`). Danach anhalten. Mit den bestätigten Werten wird `validation/run_calculators.py` neu gerechnet; das Ergebnis von GATE-G0 signiert der Evaluator.

## 3 Erste Schritte nach G0 (Beginn BS-01, vor dem ersten Zugangsdatum)

**Schritt 3 – Repository anlegen.** Neues privates Repository mit diesem Paket unverändert im Ordner `contract/` (Vertrag, nur lesend) und dem Code unter `src/` mit den Komponenten aus `implementation/build_program.md` (C-MT5, C-OMS, C-RISK, C-STRAT, C-DATA, C-BT, C-EVAL, C-NAV, C-OBS, C-UI, C-SEC, C-AI). Python-Versionen 3.11 bis 3.13; Abhängigkeiten mit Versionen und Hashes in einer Lock-Datei; keine Abhängigkeit aus NautilusTrader, LEAN oder pysystemtrade im Geldpfad (DEC-DS-22, T-REL-003).

**Schritt 4 – CI einrichten.** Jeder Commit führt aus: die Paketprüfung aus Schritt 1 gegen `contract/`, Linter ohne Befund, Tests unter allen drei Python-Versionen mit Warnungen als Fehler (T-QA-CI-001), Secret-Scan (T-SEC-008). Ein roter Lauf blockiert das Zusammenführen. Erst wenn der Secret-Scan läuft, legt der Betreiber Zugangsdaten an (T-SEC-008).

## 4 Weitere Stufen

| Schritt | Stufe | Inhalt | Tests | Anhalten bei |
|---|---|---|---|---|
| 5 | BS-01 | Testskripte der Killer-Tests KT-01 bis KT-16 im Demokonto; Echtgeldorders (KT-04, KT-06, KT-14) sendet das Skript nur nach signierter Bestätigung des Betreibers je Order | KT-01 bis KT-16, T-GOV-002, T-SEC-007 | GATE-G1 |
| 6 | BS-02 | Datenpfad: Import, Abgleich zweier Quellen, Versiegelung des Holdouts per Hash, Leckagetests, Rollkalender gegen pysystemtrade | T-DAT-001, T-DAT-004, T-DAT-LEAK-001 | GATE-G2 |
| 7 | BS-03 | Forschung nach Vorregistrierung (`experiment_manifest`) mit den Rechnern des Pakets als Referenz (`research/statistical_calculator.py`, `research/operating_characteristics.py`) | T-RES-PREREG-001 | GATE-G3 |
| 8 | BS-04 | einmalige Holdout-Prüfung im Prüfmodul | T-RES-HOLDOUT-001 | GATE-G4 |
| 9 | BS-05 | Systembau je Komponente in der Reihenfolge C-OMS und C-MT5 (gegen die Traces), C-RISK, C-DATA, C-STRAT (gegen `research/reference_strategies/`), C-BT, C-EVAL, C-NAV, C-OBS, C-SEC, C-UI, C-AI | alle Tests der Stufe BS-05 | GATE-G5 |

Ab Schritt 5 gilt je Arbeitspaket dieses Format: Kennung, Ziel, Anforderungen (`requirements.json`), Tests (`implementation/test_catalog.json`), berührte Verträge, Definition of Done der Stufe, Soll-Aufwand aus `implementation/build_stages.json` und gemessener Ist-Aufwand.

## 5 Anweisung zum Kopieren

> Du baust das System aus dem Konzeptpaket unter `contract/`. Das Paket ist der Vertrag: Zahlen nur aus `parameters.json` und den Registern, Schnittstellen nur nach `schemas/`, Verhalten nach `architecture/state_machines.json` und den Traces. Du eröffnest keine Konten, kaufst nichts, bewegst kein Geld und sendest keine Echtgeldorders; im Geldpfad gibt es keinen Aufruf eines Sprachmodells. Beginne mit Schritt 3 aus `implementation/CODING_AGENT_START.md`, sobald G0 mit signiertem PASS vorliegt, arbeite Tests zuerst, lass jede Änderung von einem Menschen lesen und halte an jedem Tor an. Fehlt eine externe Eingabe, meldest du sie und wartest.
