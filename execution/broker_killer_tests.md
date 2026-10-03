# Frühe Killer-Tests beim Broker (§8.3, EV-06)

> **Betreiberfassung.** Bevor Geld in den Systembau fließt, prüfen <!--v:calc:killer_tests_total|int-->16<!--/v--> kurze Tests im Demokonto und – nur wo das Demo nichts beweist – mit Minimalgröße im Echtgeldkonto, ob MT5 beim gewählten Broker sich so verhält, wie das Konzept es braucht. Jeder Test hat ein Orakel (woran man das Bestehen erkennt) und eine Rückfallvariante; manche Fehlschläge beenden das Projekt, andere sperren nur ein Instrument. Der kritischste Test ist KT-06: Liegt der Schutzstopp nicht beim Broker, ist Halten über Nacht und damit dein Haltehorizont nicht vertretbar. Die Tests kosten wenig, weil sie vor jeder weiteren Entwicklung laufen (Stufe BS-01). Für Go/No-Go heißt das: Ohne bestandene Killer-Tests kein Systembau (Tor G1). Nächster Schritt ist die Kontoeröffnung durch dich (X-BRK-ACCOUNT); das Paket selbst eröffnet kein Konto.

## Durchführung

- **Zeitpunkt:** Stufe BS-01, direkt nach dem Kontozugang, vor jeder weiteren Entwicklung; Ergebnis ist Voraussetzung für GATE-G1.
- **Konto:** Demo, sofern der Broker Futures im Demo anbietet (X-BRK-DEMO); Minimalgröße im Echtgeldkonto nur für Tests, bei denen das Demo nichts beweist (Ausführung, Kommission, Auszug: KT-04, KT-06, KT-14).
- **Echtgeldorders in BS-01:** Jede einzelne Echtgeldorder löst der Betreiber selbst aus; das Testskript sendet sie erst nach seiner signierten Bestätigung genau dieser Order (T-GOV-002, REQ-GOV-007). Jede Order hat einen Schutzstopp; der gesamte Verlust aller Echtgeldtests ist auf <!--v:param:P-EXE-KT-LOSS-CAP-EUR|eur-->250 EUR<!--/v--> gedeckelt (P-EXE-KT-LOSS-CAP-EUR), danach enden die Echtgeldtests. Es gibt dafür keinen Grant, keine Strategie und keinen automatischen Handel; die Ausnahme ist in `governance/grants_and_risk_acceptance.md` §4 geregelt. Das Paket selbst sendet keine Orders.
- **Ablage:** Protokoll mit Rohantworten der Schnittstelle, Zeitstempeln und Auszugszeilen im Journal; die Ergebnisse ersetzen Annahmen in `registers/instruments.json` und `external_inputs.json`.
- **Nie provozieren:** Margin-Nähe und Stop-out werden nur im Demo beobachtet, nie im Echtgeldkonto herbeigeführt.

## Tests

<!-- GEN:BEGIN tab.killer_tests -->
| ID | Thema | Durchführung | Orakel (bestanden, wenn …) | Rückfallvariante | Folge bei Scheitern | Konto |
|---|---|---|---|---|---|---|
| KT-01 | Symboleigenschaften | `symbol_info()` je Zielkontrakt: Ausführungs- und Füllmodus, Handelsmodus, Kontraktgröße, Tick, Tickwert, Mindest- und Schrittvolumen, Margins, Verfall | Werte stimmen mit `registers/instruments.json` und Börsenspezifikation überein; Tickwert = Kontraktgröße × Tick | Brokerwerte nach schriftlicher Bestätigung übernehmen | Instrument gesperrt bis zur Klärung | Demo |
| KT-02 | Kontoeigenschaften | `account_info()`: Margin-Modus (Hedging/Netting), FIFO-Regel, Margin-Call- und Stop-out-Level, Expertenhandel, Kontotyp | Hedging oder Netting eindeutig; Stop-out-Level lesbar und gleich der Brokerangabe (X-BRK-LIQ) | Netting-Variante des Adapters | ohne lesbares Stop-out-Level kein Echtgeld | Demo |
| KT-03 | Zeitstempel | Tick- und Deal-Zeiten gegen NTP-UTC, auch über eine Sommerzeitumstellung | konstanter, erklärbarer Versatz; keine Sprünge außer an Umstellungstagen | Versatztabelle je Datum; sonst nur Systemzeit | Datenzeitstempel nicht nutzbar für Kostenmessung | Demo |
| KT-04 | Order-Lebenszyklus | Limit- und Marktorder mit Minimalgröße; Retcode, `order`/`deal`, Latenz; `history_deals_get(position=…)`; Abgleich mit Auszug | jede Order über Order, Deal und Position bis zur Auszugszeile verfolgbar | keine | keine Automatisierung; nur V2 (manuell) | Demo und Echtgeld minimal |
| KT-05 | Zeitüberschreitung und Wiederholung | Netz während `order_send` trennen; Wiederverbindung; Korrelation über `magic` und `comment` | kein Doppel-Fill; UNKNOWN wird über die Historie eindeutig geklärt; `comment` unverändert | Korrelation über `magic` und Zeitfenster; Einstiege nie wiederholen | keine Automatisierung | Demo |
| KT-06 | serverseitiger Schutzstopp | SL der Position; Auslösepreis (Last oder Bid/Ask), Slippage; Verhalten bei geschlossenem Terminal und nach VPS-Neustart | SL löst bei geschlossenem Terminal aus; Ausführung dokumentiert | Netting-Konto mit Stop-Order beim Broker | ohne serverseitigen Schutz kein Halten über Nacht → Haltehorizont nicht vertretbar, Projektstopp | Demo, Bestätigung Echtgeld minimal |
| KT-07 | Modify-Semantik | SL enger setzen (TRADE_ACTION_SLTP), Pending Order ändern (MODIFY), stornieren; je Börsengruppe CME und Eurex | Änderung atomar; alter SL bleibt bis zur Bestätigung aktiv | Storno und Neuanlage nur für nicht schützende Orders | Schutzänderungen nur manuell; Einstiegssperre | Demo |
| KT-08 | Preisbänder, Tageslimits, Parkpreise | Limit außerhalb des Bands und am Tageslimit, besonders Agrar (CBOT) | dokumentierte Ablehnung mit eindeutigem Retcode | Preiskorridor enger als das Band (PTC-01) | Agrar-Kontrakte gesperrt | Demo |
| KT-09 | Teilausführungen | Limit größer als die angezeigte Menge; IOC und RETURN | Teilfills als eigene Deals, Restmenge korrekt | nur FOK für kleine Orders | Algo-Orders gesperrt | Demo |
| KT-10 | Stopps bei Limit-Moves | Beobachtung an einem Limit-Tag (nicht provozierbar); Wiedergabe mit Aufzeichnung | SL führt im gesperrten Markt nicht aus und löst bei Wiedereröffnung aus; Zustand bleibt konsistent | Lückenregel rechnet ohnehin mit Nichtausführung | keine; Befund dokumentiert | Demo |
| KT-11 | Rollen und Verfall | Schließen im alten, Eröffnen im neuen Kontrakt; Phase CLOSEONLY vor Verfall; Symbolschema | CLOSEONLY-Beginn passt zum Referenzkalender | manuell gepflegter Rollkalender | Instrument nur bis zur Klärung ohne Rollfenster handelbar | Demo |
| KT-12 | Wiederverbindung und Korrekturen | Terminal-Neustart, Deals seit dem Cursor, Korrektur- und Synchronisationsbuchungen | keine verlorenen oder doppelten Deals; Korrekturen erkennbar | Vollabgleich gegen den Auszug | Einstiegssperre bis Vollabgleich | Demo |
| KT-13 | Margin-Übergang | Übergang Intraday- zu Übernacht-Margin, Verhalten nahe am Stop-out | Zeitpunkt und Level wie X-BRK-MARGIN und X-BRK-LIQ | Größen ohnehin auf Übernacht-Margin | ohne Klarheit kein Echtgeld | nur Demo |
| KT-14 | Kommissionen | Kommission im Deal gegen Tagesauszug | Summe gleich dem Auszug | Kosten nur aus dem Auszug | Kostendrift nur monatlich messbar | Echtgeld minimal |
| KT-15 | Frequenzgrenzen | Abfrage- und Sendefrequenz steigern bis zur dokumentierten Grenze | Grenze ≥ P-PTC-MSG-PER-MIN (30 Aufrufe) und P-EXE-POLL-MS (500 Millisekunden) tragbar | Abfrageintervall verlängern | Echtzeitkontrollen eingeschränkt, Intraday-Risiko prüfen | Demo |
| KT-16 | Modus und Writer-Exklusivität | Kontotyp Demo/Echt auslesen; zweites Terminal mit gleichem Login; Passwortwechsel | Kontotyp eindeutig; altes Terminal nach Passwortwechsel abgewiesen | Lease und organisatorische Trennung | Fencing nur organisatorisch; Restore-Drill verschärfen | Demo |
<!-- GEN:END tab.killer_tests -->

Prozedur, Orakel, Bestehenskriterium, Rückfallvariante und Folge je Test sind im Testkatalog `implementation/test_catalog.json` die einzige Quelle (Einträge KT-01 bis KT-16, Reihenfolge nach Informationswert, §17.4); diese Tabelle ist daraus erzeugt.

## Abbruchregeln

- Die Auswertung ist maschinenlesbar in GATE-G1 (`research/evidence_gates.json`) und an Torfällen geprüft (`examples/valid/gate_cases/GC-G1-*.json`).
- KT-04, KT-05 oder KT-06 ohne tragfähige Rückfallvariante → Tor G1 nicht bestanden (Regel G1-R3); Projekt stoppt oder wechselt auf den Zweitkandidaten (AvaFutures, Netting) mit neuer Testrunde.
- KT-02 oder KT-13 gescheitert → Flag ECHTGELD_GESPERRT: kein Echtgeld, bis Stop-out-Level und Margin-Übergang geklärt sind.
- KT-01, KT-08, KT-09 oder KT-11 betreffen einzelne Instrumente oder Funktionen (Flag UNIVERSUM_VERKLEINERT); das Universum wird entsprechend verkleinert und die Wirtschaftlichkeit neu gerechnet.
- Jede Abweichung von einer Annahme wird mit Datum in das jeweilige Register übernommen; die Rechner laufen danach neu (`validation/run_calculators.py`).
