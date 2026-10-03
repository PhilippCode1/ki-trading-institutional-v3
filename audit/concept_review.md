# Konzeptprüfung v3.0 – interne Gegenlese und Behandlung der Befunde

> **Betreiberfassung.** Vor der Selbstbewertung wurde das Paket in vier Blöcken streng gegen die Bedingungen des Bewertungsrasters gegengelesen, mit dem Auftrag, eher zu hart als zu milde zu urteilen, weil die Selbstbewertung von v2.0 weit über der unabhängigen Bewertung lag (EV-11). Die Gegenlese fand Fehler, die Ergebnisse änderten – vor allem die Margin-Rechnung auf dem ganzen Kapital statt auf dem Guthaben beim Broker und die Handelsaussetzung im Nickel-Szenario –, und sie sind behoben; die übrigen Lücken stehen als begründete Abzüge in `audit/scorecard_K.json`. Das größte Risiko bleibt, dass dieselbe Modellfamilie dieselben blinden Flecken hat, deshalb ersetzt diese Prüfung die unabhängige Gegenprüfung nicht. Offen ist deren Beauftragung (X-REVIEW). Für Go/No-Go heißt das: Die Korrekturen ändern keinen Befund – Echtgeld bleibt in <!--v:calc:gonogo_count/NO_GO|int-->24<!--/v--> von <!--v:calc:gonogo_cells|int-->24<!--/v--> Zellen No-Go. Nächster Schritt ist die Gegenprüfung mit `audit/independent_review_request.md`.

## 1 Vorgehen und Grenzen

Vier Prüfinstanzen haben parallel und nur lesend je einen Block geprüft (A–B, C–D, E–F, G–J): Für jede Bedingung „Vollpunkte nur, wenn …“ suchten sie den Nachweis im Paket, rechneten Stichproben nach, führten Rechner, Referenztests und Prüfphasen auf Kopien aus und urteilten mit „erfüllt“, „teilweise“ oder „nicht erfüllt“. Alle Instanzen gehören zur selben Modellfamilie wie der Autor des Pakets; ihre Befunde sind eine interne Gegenlese und keine unabhängige Prüfung nach §20.4. Jeder Befund ist unten mit Ursache, Behandlung, Nachweis, Restrisiko und Status erfasst (Vorlage „Befundeintrag“ aus Anhang C des Auftrags).

## 2 Behobene Befunde

| ID | Schwere | Befund | Ursache | Auflösung | Nachweis | Restrisiko | Status |
|---|---|---|---|---|---|---|---|
| CRV-01 | hoch | Margin-Level auf den gesamten NAV bezogen, obwohl nur ein Teil des Kapitals beim Broker liegt; Liquidationen und Nachschussbedarf wurden unterschätzt | Kapitalaufteilung (P-ECO-CASH-AT-BROKER) nur in der Wirtschaftsrechnung berücksichtigt | Margin-Level = Guthaben beim Broker / Initial Margin; nötiger Anteil beim Broker je Allokation und Profil; Grenze im Hebelrechner angepasst; Texte in §7.7 neu | `lib/calc.py::margin_loss_to_level`, `risk/stress_results.json`, T-RISK-MRG-001, MUT-58 | Planwert beim Broker reicht für die registrierte Allokation knapp nicht (nötig bis <!--v:calc:stress_margin/SYSTEM/required_max|pct1-->25,5 %<!--/v-->) | BEHOBEN |
| CRV-02 | hoch | Nickel-Szenario rechnete mit Abbau durch die Leiter trotz achttägiger Handelsaussetzung | Marktstruktur nur als Text im Szenario | Feld halt im Szenario; ausgesetzte Positionen tragen die volle Mehrtagesbewegung; schlimmstes Szenario der registrierten Allokation jetzt <!--v:stress:results/SYSTEM/H5/worst_scenario|raw-->SC-H-2022NI<!--/v--> mit <!--v:stress:results/SYSTEM/H5/worst_loss_with_ladder|pct1-->20,4 %<!--/v--> | `risk/stress_test_engine.py::ladder_path`, T-CALC-STRESS-001 | Übertragung der Nickel-Bewegung auf Industriemetalle bleibt eine konservative Annahme | BEHOBEN |
| CRV-03 | mittel | Brokerausfall ohne das beim Broker liegende Guthaben | Szenario rechnete nur die Marktbewegung | eigenes Feld für das nicht verfügbare Guthaben | `risk/stress_results.json` (SC-X-BROKER) | Einlagensicherung und Trennung der Kundengelder unbelegt | BEHOBEN |
| CRV-04 | hoch | Tor G1 wertete unzulässige Ergebniswerte und einen Rückfall bei KT-04 (ohne Rückfallvariante) als bestanden; das Flag ECHTGELD_GESPERRT wirkte nirgends | Regeltabelle ohne Wertebereich; Flag ohne Verbraucher | Regeln G1-R2A und G1-R2B; Voraussetzung PRE-G8-KT in G8; neue Torfälle | `research/evidence_gates.json`, T-GATE-001, MUT-57 | Killer-Tests weiterhin nicht je Börsengruppe | BEHOBEN |
| CRV-05 | hoch | Eine Handelsabsicht mit Erzeuger HERMES bestand Schema und Regeln | Erzeugerliste für alle Verträge gemeinsam | Verträge des Geldpfads nur mit Geldpfad-Erzeugern; ungültige Beispiele | `schemas/order_intent.schema.json`, `examples/invalid/order_intent_from_hermes.json`, T-CON-001, MUT-55 | Projektschnittstelle bleibt Pfad in den Geldpfad-Host (RK-32) | BEHOBEN |
| CRV-06 | mittel | Variantenbefund setzte DOMINATED_BY_ALTERNATIVE vor die Profilzulässigkeit; V4 stammte ohne Hinweis aus dem Sensitivitätsuniversum | Vergleich V1 gegen V4 getrennt von der Klassenregel | gemeinsame Regel `lib/calc.py::variant_decision` in der Prüfreihenfolge von §5.7; V4 aus dem registrierten Universum; G0-R3 (Klasse) vor G0-R4 (Dominanz) | T-CALC-DMC-002, GC-G0-102 | V2 und V3 nur genähert | BEHOBEN |
| CRV-07 | mittel | Marktwirkung wurde in zwei Rechnern direkt aus dem Kostenregister gelesen | fehlende Weitergabe über die Kostenergebnisse | Parameter der Marktwirkung aus `financials/cost_model_results.json`; semantische Regel gegen direkte Zugriffe | `validation/semantic_checks.py::check_costs`, MUT-60 | – | BEHOBEN |
| CRV-08 | mittel | Betreiberzeit in Paper und Pilot unterbewertet | Stufenaufwand ohne laufende Routinen | Kostenposten operator_routines für Paper, Pilot und Standardbetrieb; Aufbaukosten bis Pilotende jetzt <!--v:dmc:build_cost_until_pilot_eur|eur-->58.147 EUR<!--/v--> | `financials/stage_costs.py::ops_hours`, `implementation/build_stages.json` | Vertretung ohne Kostenposition | BEHOBEN |
| CRV-09 | mittel | Rückkehr einer ML-Komponente aus dem Rückfall ohne PBO-Hürde und unabhängige Validierung; Schattenbetrieb ohne Mindestdauer | Wächter ML-10 und ML-07 unvollständig | volle Hürden und zweite Freigabe für ML-10; Mindestdauer P-AI-ML-SHADOW-MIN-DAYS | TR-ML-002, TR-ML-004, MUT-59 | – | BEHOBEN |
| CRV-10 | mittel | Aufstieg auf der Hebel-Stufenleiter ohne Prüfung von Limitverletzungen und schweren Incidents | Wächter unvollständig gegenüber §7.8 | Wächter ergänzt; Abstieg bei harter Limitverletzung | TR-LEV-002, TR-LEV-003 | – | BEHOBEN |
| CRV-11 | mittel | Text behauptete Zustände für Handelsaussetzung und Preislimit, die es nicht gab | Aussage ohne Modell | Zustände HALTED und LIMIT_LOCKED im Datenautomaten mit Trace | TR-DATA-004, T-SM-001 | Limitschwellen je Kontrakt unbelegt | BEHOBEN |
| CRV-12 | mittel | Befunde EV-02 und EV-13 zu günstig eingestuft | Status nach Konzept statt nach Wirkung vergeben | beide auf TEILWEISE mit Begründung | `registers/resolution_matrix.json` | – | BEHOBEN |
| CRV-13 | mittel | Drei Testeinträge versprachen mehr, als die Tests prüften | Katalogtexte älter als die Tests | Texte korrigiert; Tests um Zwei-Positionen-Summe, Kelly-σ* und Margin-Basis erweitert | T-CALC-COST-001, T-CALC-KELLY-001, T-CALC-STRESS-001 | Statusprüfung bleibt strukturell (PG-Liste) | BEHOBEN |
| CRV-14 | niedrig | Eigentümer in Risiko- und Modellregister waren Rollen, die die RACI nicht kennt | Rollen des Auftragsteams statt der Betriebsorganisation | Eigentümer als RACI-Rollen; Rollen des Auftragsteams nur in den Rollenabnahmen | `registers/risk_register.json`, `registers/model_inventory.json` | Nahezu alle Risiken liegen beim Betreiber (RK-16) | BEHOBEN |
| CRV-15 | niedrig | Runbook „Betreiber nicht erreichbar“ gehörte dem Betreiber | Standardwert | Eigentümer Notfallvertretung | RB-35 | Vertretung nicht benannt | BEHOBEN |
| CRV-16 | hoch | Ein Umschlag enthielt Ersatzschlüssel, Sicherungsschlüssel und Wiederherstellungscodes des Kundenportals | Hinterlegung aus v2.0 übernommen | Verteilung auf getrennte Orte mit festem Öffnungsverfahren | `security/key_management.md`, DR-06 | Personen und Vollmacht offen (X-ORG-DEPUTY) | BEHOBEN |
| CRV-17 | mittel | Restrisiko des Ein-VPS-Betriebs und der Projektschnittstelle nicht im Register | nur im Konflikteintrag DEC-CF-04 erwähnt | RK-31, RK-32 und Angriffsbäume A3.6 bis A3.8 | `registers/risk_register.json`, `architecture/threat_model.md` | Entscheidung über Zonen und Pull-Modell offen | BEHOBEN |
| CRV-18 | niedrig | Nutzenbilanz der KI ohne Abo- und Korrekturkosten | Monitor-Eingabe zu grob | Nettonutzen als Rechnung im Monitor MON-AI | `research/evidence_gates.json` (MON-AI) | Basislinie ohne Agent nur geschätzt | BEHOBEN |
| CRV-19 | mittel | Proxy-Prüfung erkannte einen anderen Basiswert gleicher Klasse nicht | Prüfung nur auf Klasse und Währung | zusätzlich gleiche Notierung (P-DATA-PROXY-PRICE-TOL) | `validation/semantic_checks.py::check_proxy`, MUT-56 | Notierung ist ein Hilfskriterium | BEHOBEN |
| CRV-20 | mittel | Auslösezeit nur für den Kostendrift-Monitor belegt | Harm- und Volatilitätsmonitor nicht simuliert | `operations/monitor_simulation.py` (MOD-MON); Fenster und Band des Volatilitätsmonitors neu gewählt (Tabelle unten) | T-CALC-MON-001 | Harm-Monitor statistisch schwach (§16.5) | BEHOBEN |
| CRV-21 | niedrig | Ersparnis der Futility-Regel als Gewinn dargestellt, obwohl sie brauchbare Strategien kostet | Kennzahl ohne Gegenrechnung | Darstellung als Tausch mit Quoten am Endtor | §6.6, `research/research_plan.md` | – | BEHOBEN |
| CRV-22 | mittel | Überzogene Aussagen: „echte Instrumentdaten“, Limitarten, „vollständiges“ Zinsuniversum, keine Zwangsliquidation, nie Nachschuss | Texte vor den Rechnungen geschrieben | Aussagen korrigiert oder an Rechenwerte gebunden | §6.2, §7.2, §7.5, §7.7, §7.9 | – | BEHOBEN |
| CRV-23 | niedrig | Stresstabelle im Masterkonzept ohne H15; Modellinventar nannte eine falsche Szenariozahl | Auswahl der Spalten; Tippfehler | Spalte ergänzt; Text korrigiert | §7.9, `registers/model_inventory.json` | – | BEHOBEN |
| CRV-24 | niedrig | §7 nannte H10 bis H20 „in allen Stufen PROFILE_NOT_ADMISSIBLE“, die Go/No-Go-Tabelle zeigt in Stufen ohne zugelassenes Instrument NOT_VIABLE_AT_CAPITAL; die Regel dafür war nicht dokumentiert | Befundklasse bei leerem Universum nur im Rechner festgelegt; Aussage in Worten ohne Zählwert (PG-01) | Regel als DEC-DS-25 dokumentiert, Klassendefinition in `financials/economic_model.md` ergänzt, Wortlaut in §7 korrigiert, Zahl der Zellen ohne Instrument gebunden (calc:dmc_empty_cells) | DEC-DS-25, §5.7, §7 | weitere Aussagen in Worten ohne Zählwert möglich (PG-01) | BEHOBEN |

Auslegung des Volatilitätsmonitors (Grundlage von P-MON-VOL-WINDOW-D und P-MON-VOL-BAND):

<!-- GEN:BEGIN tab.vol_design -->
| Fenster (Handelstage) | Band | Fehlalarm im Jahr ohne Drift | Verdopplung: Median bis Auslösung | Verdopplung: erkannt in 63 Tagen |
|---|---|---|---|---|
| 63 | 30 % | 56,0 % | 17 Handelstage | 99,2 % |
| 63 | 40 % | 23,6 % | 25 Handelstage | 99,2 % |
| 63 | 50 % | 9,8 % | 30 Handelstage | 94,4 % |
| 126 | 30 % | 12,8 % | 36 Handelstage | 92,4 % |
| 126 | 40 % | 5,6 % | 48 Handelstage | 76,0 % |
| 126 | 50 % | 2,6 % | 60 Handelstage | 54,0 % |
<!-- GEN:END tab.vol_design -->

## 3 Offene Befunde (als Abzug in der Selbstbewertung)

| Bereich | Befund | Wirkung |
|---|---|---|
| A1 | Währungsumrechnungskosten fehlen; Börsen- und Clearinggebühren nur pauschal | Kosten eher zu niedrig; ändert keinen Befund, weil alle Zellen No-Go sind |
| A2, A3, A5, H1, H2 | Steuerszenarien, Betriebsmodelle und Anwendbarkeit fehlen nach BQ-02 und BQ-03 | Abzüge ohne Umdeutung des Rasters (R-09) |
| A4 | V2 und V3 nur genähert | Vergleich stützt sich auf V1 gegen V4 |
| B1, B2, B3, B4 | Kombination und Puffer ohne Implementierung; Prior-Annahmen unbelegt; Zinsuniversum unvollständig; Planwerte unbelegt; Open Interest ungerechnet | Forschung in BS-02 und BS-03 muss sie schließen |
| C1, C2, C3 | Purged CV nur benannt; Futility-Regel in der registrierten Konfiguration wirkungslos; Futility im Betrieb und Umschlagsdrift nicht simuliert | Tore trennen über die DSR-Schwelle; Schutz im Betrieb über die Leitern |
| D1, D2, D3, D4 | Kalibrierung auf Annahmewerten; Korrelationsschock nur als Volatilitätsregime; ES unvollständig; Netto-Hebel, VaR und Monatsverlust ohne eigene Grenze; viele Ersatzwerte in historischen Szenarien | Risikozahlen sind Planungswerte bis G2 |
| E1, E2, E3, E4 | Notfalljournal ohne Automat; Killer-Tests nicht je Börsengruppe; RTS-6-Zuordnung fehlt; Limitschwellen und Schätzverfahren für Schlupf fehlen | im Bau (BS-01, BS-05) zu schließen |
| F1, F2, F3 | Zonenschnitt offen; Pentest ohne Methode und Nachtest; KI-Verordnung nicht geprüft | X-INF-ZONES, T-SEC-014, X-AI-DPA |
| G1, G2, G3 | Risikofunktion und Vertretung unbesetzt; Runbooks teils Skelette; Auslagerungssteuerung ohne Überwachung | G8 und G9 bleiben gesperrt |
| I1, I2 | Vertretung ohne Kosten; Orakel oft nur Stichworte; Referenzmodelle für PBO, SPA und Romano-Wolf fehlen | Aufwand im Bau höher als geschätzt möglich |
| J1, J2 | Masterkonzept ohne Vorwissen schwer lesbar; Statusprüfung strukturell | Kurzfassung und Glossar als Einstieg |

## 4 Ergebnis

Die Korrekturen haben Zahlen verändert, aber keinen Befund: Die Entscheidung für Echtgeld bleibt in allen Stufen und Profilen No-Go (§5.7), und G0 bleibt heute wegen unbestätigter Eingaben gesperrt (GC-G0-101). Die Selbstbewertung ergibt danach K = <!--v:calc:score_k_total|d2-->64,75<!--/v--> und E = <!--v:calc:score_e_total|d0-->0<!--/v-->; sie wird erst durch die unabhängige Gegenprüfung belastbar.
