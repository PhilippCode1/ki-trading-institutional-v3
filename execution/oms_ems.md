# OMS/EMS und MT5-Adapter (§8.1, §8.2, §8.6, §8.7)

> **Betreiberfassung.** Das OMS ist der Teil, der aus einer Handelsabsicht genau eine richtige Order beim Broker macht, sie überwacht und jede Abweichung erkennt. MT5 erschwert das an drei Stellen: Die Python-Schnittstelle meldet nichts von selbst, kennt keine eigene Order-ID des Kunden und ist bei Zeitstempeln widersprüchlich dokumentiert; deshalb fragt das OMS den Zustand regelmäßig ab, markiert jede Order mit Kennungen und wiederholt nie blind. Einstiege werden höchstens einmal gesendet; bei Unklarheit gilt der Zustand „unbekannt“, bis ein Abgleich ihn klärt. Das Konto hält je Instrument genau eine Brokerposition, die Strategien werden intern geführt und verrechnet. Für Go/No-Go heißt das: Die Ausführung ist spezifiziert, ihre Tragfähigkeit hängt an den Killer-Tests in BS-01. Nächster Schritt ist ein Demokonto mit Futures (X-BRK-DEMO) und die Python-Erlaubnis (X-BRK-API).

## 1 Grundsätze

- Der Geldpfad ist deterministisch; kein Sprachmodell erzeugt, ändert oder storniert Orders (D3-05, DEC-DS-03).
- **Persistenz vor Netzwerk:** Absicht, Command-ID, Payload-Hash, Risikoreservierung und Versuchs-ID sind mit fsync im Journal, bevor der Adapter sendet (SQLite im WAL-Modus mit `synchronous=FULL`, SRC-SQLITE-WAL; übernommen aus v2.0).
- **Genau ein Writer** je Konto: Lease des Guardians (<!--v:param:P-EXE-LEASE-S|d0-->15<!--/v--> Sekunden), Exklusivität der Brokersitzung und Credential-Rotation mit Ablehnungsnachweis nach Host-Wechsel oder Restore (übernommen aus v2.0; für MT5 über Wechsel des Hauptpassworts, Killer-Test KT-16).
- **Brokerneutral:** Kern und Risikomotor sprechen nur mit der Adapterschnittstelle (`architecture/interfaces.md`); der MT5-Adapter ist die erste Implementierung, ein FIX-Adapter mit Drop-Copy ist als Vertrag beschrieben, aber nicht Teil des Umfangs (BQ-02).

## 2 Komponenten und Fluss

| Komponente | Aufgabe | Bereich |
|---|---|---|
| Portfoliomotor | Zielpositionen je Strategie und Instrument aus Prognosen, Risikobudget und Lückenregel | Geldpfad |
| Netting | Summe der Zielpositionen je Instrument; interne Kreuzung gegenläufiger Strategien zum Mittelkurs | Geldpfad |
| EMS | Parent-Order je Instrument; Zerlegung in Child-Orders ab <!--v:param:P-EXE-ALGO-THRESHOLD|d0-->10<!--/v--> Kontrakten im Abstand von mindestens <!--v:param:P-EXE-ALGO-INTERVAL-S|d0-->60<!--/v--> Sekunden; Wahl von Ordertyp, Limitpreis und Zeitfenster | Geldpfad |
| Risikomotor | Pre-Trade-Kontrollen PTC-01 bis PTC-14, Intraday-Überwachung, Leitern | Geldpfad |
| OMS | Zustandsautomaten SM-ORDER und SM-POSITION, Journal, Abgleich, Klärung von UNKNOWN | Geldpfad |
| MT5-Adapter | Übersetzung in `order_send`, Abfragen per Polling alle <!--v:param:P-EXE-POLL-MS|d0-->500<!--/v--> Millisekunden, Normalisierung von Retcodes und Zeitstempeln | Geldpfad |
| Prüfmodul (Evaluator) | rechnet Limits und Positionen unabhängig aus Brokerdaten nach; kann nur stoppen | eigener Bereich |

Fluss: Prognose → Zielposition je Strategie → Netting → Parent-Order → Pre-Trade-Kontrollen → Journal (PERSISTED) → Adapter sendet (SUBMITTING) → Abfragen liefern Order-, Deal- und Positionsänderungen → Zustandsübergänge → Zuordnung der Fills zu Strategien → P&L und Risiko neu.

## 3 MT5-Semantik und Folgen für das OMS

| Thema | Verhalten laut Quelle (SRC-MT5-API, SRC-MT5-PYPI) | Folge im Konzept |
|---|---|---|
| Plattform | Python-Paket nur für Windows, Terminal muss laufen (Kopplung per Interprozesskommunikation) | Geldpfad auf Windows-VPS; Heartbeat des Terminals; Neustart als Drill (RK-18) |
| Ereignisse | keine Handelsereignisse in Python; Zustand nur per Abfrage (`orders_get`, `positions_get`, `history_orders_get`, `history_deals_get`) | Polling mit P-EXE-POLL-MS; Ereignisse werden aus Differenzen erzeugt und dedupliziert |
| Client-Order-ID | kein eindeutiges Kundenfeld; nur `magic` und `comment`, Tickets vergibt der Server | `magic` kodiert Strategie und Absicht, `comment` trägt eine gekürzte Command-ID; ob der Broker `comment` ändert, prüft KT-05 |
| Ergebnis von `order_send` | Erfolg bei DEAL heißt nur „platziert“; `deal` und `order` können leer sein; Retcode `10012` = Zeitüberschreitung | kein Rückschluss auf Ausführung ohne Abfrage; Zeitüberschreitung → UNKNOWN |
| Ausführungsmodus | Exchange Execution: Ausführung zu aktuellen Börsenangeboten; Füllart laut Symbol (FOK/IOC), RETURN für Pending Orders | Einstiege als marktfähige Limit-Order mit Preiskorridor (PTC-01) und Gültigkeit bis Fensterende (ORDER_TIME_SPECIFIED), damit ein Negativnachweis möglich ist |
| Schutzstopp | SL/TP bei Börseninstrumenten nach Börsenregeln ausgelöst (meist Last), Ausführung zu Bid/Ask; bei einem Referenzbroker serverseitig als MIT | Schutzstopp als SL der Position, bestätigt binnen <!--v:param:P-EXE-STOP-CONFIRM-S|d0-->30<!--/v--> Sekunden (DEC-DS-20); Verhalten beim Primärbroker prüft KT-06 |
| Konto-Modus | Hedging: mehrere Positionen je Symbol, Schließen nur mit Positions-Ticket; Netting: eine Position je Symbol | Hedging-Konto (laut Broker) mit interner Nettung: genau eine Brokerposition je Instrument; Schließen immer mit `position=Ticket`, nie als freie Gegenorder (DEC-DS-11) |
| Zeitstempel | Python-Doku: UTC ohne Verschiebung; MT5-Hilfe: Zeitzone des Broker-Servers (Widerspruch) | Journal führt Systemzeit in UTC und Brokerzeit getrennt; Offset wird in KT-03 gemessen, auch über eine Sommerzeitumstellung |
| Handelszeiten | in Python nicht verfügbar | aus dem Referenzdatendienst (`data/reference_data_spec.md`) |
| Kommissionen | bei einem Referenzbroker nicht in MT5, nur im Tagesauszug | Abgleich der Kosten gegen den Auszug; Kostendrift auf Auszugsbasis |

## 4 Ordertypen und Ausstiege

- **Einstieg:** marktfähige Limit-Order (BUY_LIMIT/SELL_LIMIT) mit Limit im Preiskorridor, Gültigkeit bis Ende des Liquiditätsfensters; Menge aus der Zielabweichung.
- **Schutz:** SL der Position über die volle Menge; Stopänderungen nur absolut und nur enger (übernommen aus v2.0); unbestätigte Änderungen lassen den alten Stop aktiv.
- **Schließen** (Signal, Zeitstopp, Leiter, Rollfenster, Kill-Switch Stufe 2): Gegen-Deal mit `position=Ticket` über die im frischen Snapshot bestätigte Menge. Eine freie Gegenorder ohne Ticket würde im Hedging-Konto eine neue Gegenposition eröffnen und ist verboten.
- **Rollen:** Schließen im alten Kontrakt; neuer Einstieg nur, wenn die Haltedauerrechnung es noch erlaubt (meist nicht, weil die Höchsthaltedauer vorher greift). Kalenderspreads bietet MT5 nicht als eine Order (DEC-DS-12).

## 5 Zustandsautomaten

SM-ORDER führt jeden Sendeversuch durch INTENT → RESERVED → PERSISTED → SUBMITTING → ACKNOWLEDGED → PARTIALLY_FILLED/FILLED bzw. CANCEL_PENDING, CANCELLED, EXPIRED, REJECTED, REJECTED_BY_RISK, FAILED_BEFORE_SEND, UNKNOWN und NOT_EXECUTED_PROVEN (übernommen aus v2.0). SM-POSITION führt je Instrument die Brokerposition und die virtuellen Teilpositionen der Strategien. Die maschinenlesbaren Automaten mit Traces stehen in `architecture/state_machines.json` und werden mit `validation/state_engine.py` geprüft.

**Abbildung der MT5-Rückgaben:** `10008` (PLACED) und `10009` (DONE) → ACKNOWLEDGED, danach Abfrage; `10010` (DONE_PARTIAL) → PARTIALLY_FILLED; `10006` (REJECT), `10013` bis `10015` (ungültige Anfrage, Menge oder Preis) → REJECTED; `10012` (TIMEOUT) und Fehler der Interprozesskommunikation → UNKNOWN; ein Fehler vor dem Senden → FAILED_BEFORE_SEND.

**Klärung von UNKNOWN:** Abfragen nach <!--v:param:P-EXE-UNKNOWN-POLL-S/0|d0-->5<!--/v-->, <!--v:param:P-EXE-UNKNOWN-POLL-S/1|d0-->15<!--/v--> und <!--v:param:P-EXE-UNKNOWN-POLL-S/2|d0-->60<!--/v--> Sekunden, danach alle <!--v:param:P-EXE-UNKNOWN-POLL-LATER-S|d0-->300<!--/v--> Sekunden bis <!--v:param:P-EXE-UNKNOWN-MAX-H|d0-->24<!--/v--> Stunden, dann Eskalation. Negativnachweis (NOT_EXECUTED_PROVEN) nur, wenn die Gültigkeit der Order abgelaufen ist und <!--v:param:P-EXE-NEGPROOF-CYCLES|d0-->2<!--/v--> saubere Abfragezyklen (P-EXE-NEGPROOF-CYCLES) weder eine offene Order noch einen historischen Auftrag noch einen Deal mit passender `magic`/`comment`-Kennung noch eine Positionsänderung zeigen. Ein Einstieg wird nie erneut gesendet; das Signal gilt als verbraucht. Ein später Fill wird angenommen, geschützt und als Incident gemeldet.

## 6 Mehrere Strategien auf einem Konto

Jede Strategie hat je Instrument eine virtuelle Teilposition; die Brokerposition ist deren Summe (Invariante, im Abgleich geprüft). Gegenläufige Absichten werden intern gekreuzt, verbucht zum Mittelkurs des Entscheidungszeitpunkts, ohne Kosten; an den Markt geht nur die Nettodifferenz. Fills werden den Strategien im Verhältnis ihrer beabsichtigten Änderung zugeordnet; Kosten und Slippage ebenso. Die Risikobudgets bleiben je Strategie getrennt (LIM-STR-BUDGET).

## 7 Abgleich, Deduplizierung, Notfall

- Vollständiger Snapshot (Positionen, offene Orders mit Rolle, Salden, Margin, Deal-Cursor) ist für Risikoentscheidungen höchstens <!--v:param:P-EXE-SNAPSHOT-MAX-S|d0-->60<!--/v--> Sekunden alt; Vollabgleich alle <!--v:param:P-EXE-RECON-ACTIVE-S|d0-->30<!--/v--> Sekunden bei offenen Orders oder UNKNOWN, sonst alle <!--v:param:P-EXE-RECON-IDLE-S|d0-->300<!--/v--> Sekunden in Handelszeiten.
- Deals werden über ihr Ticket dedupliziert; Korrekturen des Brokers (etwa Saldo-Synchronisationen) werden als eigene Ereignisse geführt (übernommen aus v2.0; Deal-Ticket statt Ausführungs-ID).
- Unbekannte Positionen oder Orders führen zum Sperrgrund FOREIGN_POSITION; das System schließt sie nie still.
- Ist das Journal nicht beschreibbar, schreibt der Kern in ein Notfalljournal auf eigenem Datenträger; scheitert auch das, beendet er sich (Fail-Stop). Mit Notfalljournal sind nur Schutzaktionen erlaubt (übernommen aus v2.0).

## 8 Broker-Auswahl und Due Diligence

Primärkandidat ist FXFlat (DEC-DS-16), Zweitkandidat AvaFutures; AMP dient als technische Referenz (§8.2 des Masterkonzepts). Vor einer Kontoeröffnung durch den Betreiber sind schriftlich zu klären: Kontraktliste in MT5 (X-BRK-CONTRACTS), Gebühren (X-BRK-FEES), Margins (X-BRK-MARGIN), Liquidationsregel (X-BRK-LIQ), Nachschussausschluss (X-BRK-NACHSCHUSS), Python/EA-Erlaubnis und Frequenzgrenzen (X-BRK-API), Futures im Demo (X-BRK-DEMO) und Verzinsung (X-BRK-INTEREST). Das Paket eröffnet kein Konto und schließt keinen Vertrag.
