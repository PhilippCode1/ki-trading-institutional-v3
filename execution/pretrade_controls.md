# Pre-Trade-Kontrollen und Kill-Switch (§7.5, §8.5)

> **Betreiberfassung.** Jede Order läuft vor dem Senden durch vierzehn automatische Prüfungen: Preis, Menge, Nominal, Nachrichtenrate, Duplikate, Positionsgrenzen, Margin, Datenfrische, Demo/Echtgeld, Ereignissperren, Haltedauer, Lückenregel sowie gültiger Grant und Writer. Scheitert eine Prüfung, wird die Order abgelehnt oder verkleinert und im Journal begründet; kein Mensch und keine KI kann die Prüfungen im laufenden Betrieb abschalten. Die Kontrollen sind an MiFID II Art. 17 und der Delegierten Verordnung (EU) 2017/589 ausgerichtet, ohne dass diese für dein Eigenkonto gelten müssen; die Zuordnung einzelner Artikel ist nicht geprüft. Der Kill-Switch storniert alle Orders in höchstens <!--v:param:P-RISK-KILL-CANCEL-S|d0-->5<!--/v--> Sekunden. Für Go/No-Go heißt das: Die Kontrollen sind vollständig spezifiziert und werden in BS-05 mit Abnahmetests gebaut. Nächster Schritt ist die Bestätigung der Brokergrenzen für Orderfrequenz (X-BRK-API).

## Kontrollen

| ID | Kontrolle | Regel | Wert | Reaktion |
|---|---|---|---|---|
| PTC-01 | Preiskorridor | Limitpreis höchstens k · σ_Tag vom Referenzkurs; Referenzkurs höchstens P-EXE-QUOTE-MAX-AGE-S alt | k = <!--v:param:P-PTC-COLLAR-SIGMA|d1-->0,5<!--/v-->; Kursalter <!--v:param:P-EXE-QUOTE-MAX-AGE-S|d0-->5<!--/v--> Sekunden | Ablehnung (REJECTED_BY_RISK) |
| PTC-02 | Höchstmenge je Order | Menge ≤ Zielabweichung aus dem Risikomotor und ≤ Anteil am Tagesvolumen | <!--v:param:P-RISK-MAX-ADV-SHARE|pct0-->1 %<!--/v--> des Tagesvolumens | Verkleinerung, sonst Ablehnung |
| PTC-03 | Höchstnominal je Order (Fat-Finger) | Nominal der Order ≤ Anteil der Profilobergrenze L_g × NAV | <!--v:param:P-PTC-NOTIONAL-SHARE-OF-CAP|pct0-->25 %<!--/v--> | Ablehnung und Alarm |
| PTC-04 | Instrument und Sitzung | Instrument zugelassen, nicht gesperrt, Handelsmodus FULL, Sitzung offen, keine Handelsaussetzung | Referenzdaten, `symbol_info` | Ablehnung |
| PTC-05 | Nachrichtendrosselung | sendende Aufrufe je Minute und Konto begrenzt | <!--v:param:P-PTC-MSG-PER-MIN|d0-->30<!--/v--> je Minute | Warteschlange; bei Rückstau Einstiegssperre |
| PTC-06 | Duplikaterkennung | gleiche Command-ID mit anderem Payload-Hash oder gleiche Instrument-Seite-Menge ohne neue Absicht im Zeitfenster | <!--v:param:P-PTC-DUP-WINDOW-S|d0-->60<!--/v--> Sekunden | Ablehnung (ERR-EXE-PAYLOAD-MISMATCH bzw. DUPLICATE) |
| PTC-07 | Positionsgrenzen | Position nach Order ≤ Anteil am Open Interest; Klassen-Hebeldeckel; Profilobergrenze L_g | <!--v:param:P-RISK-MAX-OI-SHARE|pct1-->0,5 %<!--/v--> des Open Interest; `class_caps`; P-LEV-{PROFIL}-CAP | Verkleinerung, sonst Ablehnung |
| PTC-08 | Margin | M/E nach Order ≤ Profilgrenze und Margin-Level ≥ De-Risking-Schwelle, gerechnet mit Übernacht-Margin | P-LEV-{PROFIL}-ME; <!--v:param:P-MRG-DERISK-TRIGGER|pct0-->150 %<!--/v--> | Ablehnung |
| PTC-09 | Datenfrische | Datenzustand des Instruments HEALTHY; Snapshot höchstens P-EXE-SNAPSHOT-MAX-S alt | <!--v:param:P-EXE-SNAPSHOT-MAX-S|d0-->60<!--/v--> Sekunden; Kurse veraltet nach <!--v:param:P-DATA-STALE-S|d0-->10<!--/v--> Sekunden | Einstiegssperre für das Instrument |
| PTC-10 | Moduskontrolle | Kontotyp (Demo/Echtgeld) laut Broker gleich dem vom Betreiber signierten Modus; Echtgeld nur mit aktivem Grant | P-OP-MODE-AUTHORITY | Ablehnung und Sperrgrund, Alarm an den Betreiber (RK-21) |
| PTC-11 | Ereignissperre | keine neuen Einstiege vor registrierten Ereignissen (Notenbank, Verfall, Berichte) | <!--v:param:P-RISK-EVENT-BLACKOUT-MIN|d0-->30<!--/v--> Minuten | Ablehnung von Einstiegen |
| PTC-12 | Haltedauer und Rollfenster | kein Einstieg, dessen Zeitstopp nach dem Rollfenster läge; keine Einstiege im Rollfenster | P-OP-HOLD-MAX-H; <!--v:param:P-UNI-ROLL-DAYS|d0-->5<!--/v--> Geschäftstage vor FND/LTD | Ablehnung von Einstiegen |
| PTC-13 | Lückenregel und Tagesverlust | Lückenstress aller Positionen nach Order + Tagesverlust ≤ Tagesgrenze − Reserve; Wochenendfaktor | <!--v:calc:gap_budget|pct0-->8 %<!--/v-->; Faktor <!--v:param:P-RISK-WEEKEND-FACTOR|d1-->1,5<!--/v--> | Verkleinerung, sonst Ablehnung |
| PTC-14 | Grant, Writer, Sicherheitszustand | aktiver Grant mit passender Umgebung, aktiver Writer mit gültiger Lease, Aktion im Sicherheitszustand erlaubt (SM-SAFETY) | P-EXE-LEASE-S | Ablehnung |

Reihenfolge: PTC-14 und PTC-10 zuerst (darf überhaupt gehandelt werden?), dann PTC-04, PTC-09, PTC-11, PTC-12 (darf dieses Instrument jetzt?), dann PTC-13, PTC-07, PTC-08 (passt die Größe?), zuletzt PTC-01, PTC-02, PTC-03, PTC-05, PTC-06 (ist die Order formal richtig?). Schutz- und Abbauorders durchlaufen nur PTC-14, PTC-10, PTC-01 und PTC-06; sie werden nie durch Größen- oder Ereignisregeln blockiert.

## Kill-Switch

| Stufe | Wirkung | Auslöser | Zielzeit |
|---|---|---|---|
| 1 | alle offenen Orders stornieren (außer Schutzstopps offener Positionen), Einstiegssperre | Betreiber (Cockpit, mobile Notfallansicht), Prüfmodul, Risikomotor bei L3, Sicherheitszustand HALTED | <!--v:param:P-RISK-KILL-CANCEL-S|d0-->5<!--/v--> Sekunden |
| 2 | zusätzlich geordnet glattstellen über `position=Ticket` | Betreiber oder L3-Leiter | nach Liquidität, Abbau über Child-Orders |

Tests: Der Kill-Switch wird quartalsweise im Demokonto geprobt und in BS-06 abgenommen (`operations/drills.md`, `implementation/test_catalog.json`). Eine Probe gilt als bestanden, wenn alle Orders in der Zielzeit storniert sind, kein Schutzstopp verloren ging und das Journal jede Aktion enthält.

## Überwachung und Nachweise

Jede Ablehnung erzeugt einen Journaleintrag mit Kontroll-ID, Eingangswerten und Grenzwert. Das Prüfmodul rechnet PTC-07, PTC-08 und PTC-13 unabhängig aus Brokerdaten nach; eine Abweichung setzt den Sperrgrund DECISION_AUDIT_MISMATCH (übernommen aus v2.0). Die Grenzwerte stehen ausschließlich in `parameters.json` und `registers/limits.json` (LIM-PT-PRICE, LIM-PT-QTY, LIM-PT-RATE verweisen auf PTC-01, PTC-02 und PTC-05).
