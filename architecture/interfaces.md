# Schnittstellen und Verträge (§10.1)

> **Betreiberfassung.** Jede Komponente spricht mit den anderen nur über festgelegte Verträge, die als JSON Schema im Paket liegen und mit gültigen und ungültigen Beispielen geprüft werden. So kann der Kern unverändert zwischen Simulation, Demo und Echtgeld wechseln, und ein anderer Broker ließe sich über einen neuen Adapter anbinden. Der KI-Agent erreicht das System nur über eine Liste erlaubter Werkzeuge; eine Order ist darin nicht enthalten und wird abgewiesen. Signierte Betreiberaktionen und signierte Torergebnisse sind die einzigen Wege, geldwirksame Zustände zu ändern. Für Go/No-Go heißt das: Die Verträge sind spezifiziert; ihre Einhaltung prüft die Paketprüfung an Beispielen. Nächster Schritt ist der Bau des Adapters gegen diese Verträge in BS-05.

Alle Schemas liegen unter `schemas/` (JSON Schema 2020-12); gültige und ungültige Beispiele unter `examples/`. Geldbeträge sind Dezimalzeichenketten, Mengen ganze Kontrakte, Zeitstempel UTC im ISO-Format mit Zeitzone; jede Nachricht trägt Schema-Version, Korrelationskennung und Erzeuger.

## 1 Übersicht

| ID | Schnittstelle | Richtung | Vertrag (Schema) | Authentifizierung |
|---|---|---|---|---|
| IF-01 | Adapter-Befehle | Kern → Adapter | `order_intent`, `order_attempt` | prozessintern, nur aktiver Writer |
| IF-02 | Broker-Ereignisse (aus Abfragen erzeugt) | Adapter → Kern | `broker_event`, `account_snapshot`, `position` | prozessintern |
| IF-03 | Risikoentscheidung | Risikomotor → Journal | `risk_decision`, `decision_record` | prozessintern |
| IF-04 | Betreiberaktionen | Cockpit → Kern | `operator_action` (Ed25519-Signatur, Gültigkeit P-SEC-SIG-EXPIRY-MIN) | Hardware-Schlüssel, WireGuard |
| IF-05 | Grants | Betreiber → Grant-Register | `live_grant` | Signatur des Betreibers |
| IF-06 | Torergebnisse | Prüfmodul → Geldpfad | `gate_result` (Signatur des Evaluators) | mTLS über WireGuard |
| IF-07 | Projektschnittstelle des Agenten | KI-Zone → Geldpfad | `mcp_request`, `mcp_response`, `change_proposal`, `work_item` (Werkzeug-Allowlist) | Dienstidentität, Token, mTLS |
| IF-08 | Referenzdaten | Referenzdatendienst → Kern | `contract_spec` | lesend |
| IF-09 | Daten- und Experimentmanifeste | Forschung → Prüfmodul | `data_manifest`, `experiment_manifest` | mTLS |
| IF-10 | Wissen | Agent und Betreiber → Wissensregister | `knowledge_entry` | Projektschnittstelle |
| IF-11 | Releases | CI → Geldpfad | `release_manifest` (Digest, SBOM, Signatur) | Signatur |
| IF-12 | Incidents und Beobachtungen | alle → Journal | `incident`, `safety_observation` | je Dienstidentität |
| IF-13 | FIX mit Drop-Copy (nur Vertrag) | Kern ↔ FCM | nicht umgesetzt (B3/B4 ausgeschlossen) | – |

## 2 Adapter-Vertrag (IF-01, IF-02)

**Befehle:** `place_order` (Parent- oder Child-Order mit Command-ID, Payload-Hash, Instrument, Seite, Menge, Ordertyp, Limit, Gültigkeit, Strategie-Kennung), `modify_protection` (SL einer Position absolut und nur enger), `cancel_order`, `close_position` (Positions-Ticket, bestätigte Menge), `snapshot` (Positionen, Orders, Deals seit Cursor, Salden, Margins).

**Ereignisse:** `ACK`, `PARTIAL_FILL`, `FILL`, `REJECT`, `CANCELLED`, `EXPIRED`, `POSITION_CHANGED`, `SESSION_UP`, `SESSION_DOWN`, `CORRECTION` (Broker-Synchronisation oder Stornierung der Börse). Der MT5-Adapter erzeugt sie aus Differenzen aufeinanderfolgender Abfragen und dedupliziert über Deal- und Order-Tickets (`execution/oms_ems.md`).

**Zusicherungen (übernommen aus v2.0):** Einstiege höchstens einmal senden; nach Zeitüberschreitung UNKNOWN statt Wiederholung; jeder Befehl ist vor dem Senden im Journal; der Adapter ändert nie selbstständig Mengen oder Preise.

## 3 Projektschnittstelle des Agenten (IF-07, übernommen aus v2.0)

Erlaubte Werkzeuge: `get_health`, `get_metrics`, `get_incident`, `get_release`, `get_gate_results`, `create_proposal`, `submit_experiment`, `get_experiment`, `submit_candidate`, `append_note`, `report_safety_observation`, `request_maintenance`, `list_work_items`, `update_work_item`. Serverseitig geprüft: Identität, Schema, Idempotenzschlüssel, Nutzlast höchstens <!--v:param:P-AI-PAYLOAD-MAX-MIB|d0-->1<!--/v--> MiB, Frist. Jede andere Anfrage – insbesondere jede Order – wird abgewiesen und als Sicherheitsereignis protokolliert.

## 4 Signierte Aktionen

Geldwirksame und sicherheitsrelevante Aktionen (Pause, Fortsetzen, Abbau, Quittung eines Sperrgrunds, Grant, Widerruf, Moduswechsel Demo/Echtgeld, Release-Freigabe, Credential-Rotation, Ankündigung eines Eingriffs, Incident-Abschluss, Projektende) sind signierte Betreiberaktionen über den Payload-Hash, gültig <!--v:param:P-SEC-SIG-EXPIRY-MIN|d0-->15<!--/v--> Minuten, idempotent über eine Aktionskennung und gebunden an den Snapshot, wenn die Wirkung vom Bestand abhängt (übernommen aus v2.0). Chattext wird nie in Brokerbefehle oder Freigaben übersetzt.

## 5 Versionierung der Verträge

Jede Vertragsänderung ist eine Änderung der Klasse B (abwärtskompatibel) oder C (nicht kompatibel) mit Beispielen und Tests; Nachrichten mit unbekannter Schema-Version werden abgewiesen.

## 6 Verträge, Beispiele und semantische Regeln

<!--v:calc:contracts_total|int-->21<!--/v--> Verträge teilen gemeinsame Definitionen aus `schemas/common.schema.json` (Kennungen der Form `urn:ki-trading-v3:<name>`, aufgelöst über ein Schema-Register ohne Netzzugriff). JSON Schema prüft Form und bedingte Pflichtfelder; Beziehungen zwischen Feldern und gegen `parameters.json` prüfen die semantischen Regeln R-EX-01 bis R-EX-12 in `validation/example_rules.py` (zum Beispiel: Verkleinerung rundet ab, Signaturgültigkeit höchstens P-SEC-SIG-EXPIRY-MIN, Entwicklungsfenster endet vor dem Holdout, Autor ungleich Prüfer, Summe der Teilpositionen gleich Brokerposition, Negativnachweis nur mit P-EXE-NEGPROOF-CYCLES sauberen Zyklen). Jedes ungültige Beispiel nennt in `examples/EXAMPLES.json` die erwartete Verletzung (Schema oder Regel); die Paketprüfung verlangt, dass genau diese eintritt. Gültige Beispiele: <!--v:calc:examples_valid|int-->31<!--/v-->, ungültige: <!--v:calc:examples_invalid|int-->56<!--/v-->.

<!-- GEN:BEGIN tab.contracts -->
| Vertrag (schemas/…) | gültige Beispiele | ungültige Beispiele | semantische Regeln |
|---|---|---|---|
| `account_snapshot` | 1 | 2 | R-EX-12 |
| `broker_event` | 1 | 2 | – |
| `change_proposal` | 1 | 1 | – |
| `contract_spec` | 1 | 2 | R-EX-09 |
| `data_manifest` | 1 | 2 | R-EX-04 |
| `decision_record` | 1 | 1 | – |
| `experiment_manifest` | 1 | 2 | R-EX-05 |
| `gate_result` | 1 | 2 | – |
| `incident` | 1 | 2 | – |
| `knowledge_entry` | 2 | 2 | – |
| `live_grant` | 2 | 5 | R-EX-03 |
| `mcp_request` | 1 | 3 | R-EX-08 |
| `mcp_response` | 2 | 1 | – |
| `operator_action` | 3 | 6 | R-EX-02 |
| `order_attempt` | 3 | 4 | R-EX-11 |
| `order_intent` | 3 | 7 | – |
| `position` | 1 | 2 | R-EX-10 |
| `release_manifest` | 1 | 4 | R-EX-06 |
| `risk_decision` | 2 | 3 | R-EX-01 |
| `safety_observation` | 1 | 1 | – |
| `work_item` | 1 | 2 | R-EX-07 |
<!-- GEN:END tab.contracts -->
