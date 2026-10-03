# Masterkonzept v3.0 – KI-Trading Institutional

| Feld | Inhalt |
|---|---|
| Dokument | Gesamtdarstellung des Konzeptpakets v3.0 mit Betreiberfassung je Kapitel |
| Stand | 24.09.2026 |
| Auftrag | Masterprompt v3.0 (SRC-MASTERPROMPT-V3); Betreiberantworten BQ-01 … BQ-10 vom 24.09.2026 (DEC-OP-01 … DEC-OP-10) |
| Ausgangsbasis | Konzeptpaket v2.0 (SRC-V2-PAKET); Übernahmen sind im Text mit „übernommen aus v2.0“ markiert und in `audit/v2_to_v3_mapping.json` erfasst |
| Selbstbewertung | nur als solche gekennzeichnet (`audit/scorecard_K.json`, `audit/scorecard_E.json`); K = 100 erst nach unabhängiger Gegenprüfung (§20.4) |
| Sprache | Deutsch; keine Rechts-, Steuer- oder Anlageberatung (R-11) |

> **Leseweise.** Jede Zahl im Fließtext ist maschinell an einen Rechner oder ein Register gebunden (unsichtbare Wertmarkierungen im Quelltext, R-03) und wird mit `python validation/render_blocks.py --root . --check` geprüft. Tabellen zwischen `GEN`-Markierungen werden aus Rechnerergebnissen erzeugt. Rechenwege stehen in den Rechnern selbst; dieses Dokument erklärt Entscheidungen und Befunde. Die Kurzfassung für den Betreiber steht in `KURZFASSUNG_BETREIBER.md`.

**Gesamtbefund in einem Satz.** Unter den Betreibervorgaben (Haltedauer in der Regel <!--v:param:P-OP-HOLD-STD-MIN-H|d0-->4<!--/v--> h bis <!--v:calc:hold_std_max_days|d0-->4<!--/v--> Tage, höchstens <!--v:calc:hold_max_days|d0-->7<!--/v--> Tage; Tagesverlust niemals über <!--v:param:P-OP-DAILY-LOSS-CAP|pct0-->9 %<!--/v-->; Hebel bis <!--v:param:P-OP-LEV-MAX|x0-->20×<!--/v-->) ist kein Hebelprofil zulässig und keine Kapitalstufe wirtschaftlich – die Empfehlung für Echtgeld lautet daher in allen Stufen und Profilen **No-Go**; zulässig bleibt Demo- und Paper-Betrieb mit Ausgabendeckel; auch die langsame Trendfolge ohne Sieben-Tage-Grenze, die zusätzlich eine neue Betreiberentscheidung bräuchte, ist in <!--v:calc:dmc_class_count/U-KOSTEN-TFD1/PROFILE_NOT_ADMISSIBLE|int-->24<!--/v--> von <!--v:calc:dmc_cells/U-KOSTEN-TFD1|int-->24<!--/v--> Zellen nicht zulässig (§5.7).

## Inhalt

- §0–§3 Auftrag, Rangfolge, Betreiberentscheidungen und Konflikte
- §4 Zielbild · §5 Wirtschaftlichkeit · §6 Strategie und Forschung · §7 Hebel, Risiko und Kapital · §8 Ausführung · §9 Daten
- §10 Architektur · §11 KI-Schicht · §12 Sicherheit · §13 Governance · §14 Betrieb · §15 Recht und Steuern (Umfang nach BQ-03)
- §16 Tore · §17 Bauprogramm · §18–§20 Paket, Prüfung, Bewertung · §21 Befunde · Rollenabnahmen · Glossar

## §0–§3 Auftrag, Rangfolge, Betreiberentscheidungen

> **Betreiberfassung.** Das Paket folgt der Rangfolge Integritätsregeln → Betreiberentscheidungen → Masterprompt → Befunde → v2.0 → eigene Entwurfsentscheidungen. Deine Antworten vom 24.09.2026 gelten vor dem Masterprompt; wo sie ihm widersprechen, ist der Konflikt dokumentiert und ohne Umdeutung der Bewertungskriterien behandelt (<!--v:calc:conflicts_total|int-->8<!--/v--> Konflikte nach R-09). Das größte Risiko der Vorgaben ist die Kombination aus kurzer Haltedauer und harter Tagesgrenze: Sie macht Kosten und Kurslücken zur bindenden Größe. Offen sind alle <!--v:calc:external_inputs_total|int-->34<!--/v--> externen Eingaben; keine ist bestätigt. Für Go/No-Go heißt das: Ohne Änderung einer Vorgabe bleibt es bei No-Go für Echtgeld. Nächster Schritt ist deine Entscheidung zu den Konflikten DEC-CF-02 (Tagesgrenze) und zur Haltedauer (§5.7).

### Eingangsprüfung (E0)

Das Ausgangspaket v2.0 wurde mit dem vorgegebenen SHA-256 geprüft, sicher entpackt und mit seinem eigenen Validator erneut geprüft (alle Tests bestanden). Die Mängel aus EV-12 (ungültige Escape-Sequenz, unbenutzte Variable, Dateiname der Hash-Datei, kein Mehrversionslauf) sind bestätigt und in v3.0 behoben (§19).

### Betreiberentscheidungen (Rang 2)

<!-- GEN:BEGIN tab.operator_decisions -->
| ID | Frage | Antwort des Betreibers (Wortlaut) |
|---|---|---|
| DEC-OP-01 | BQ-01 Kapital | Irrelevant für das System, es kann im System auf Echtgeld und oder auf Demogeld laufen. Bedeutet es nimmt immer das Budget her was es hat und Trader damit, es passt daran intelligent seine Strategie an |
| DEC-OP-02 | BQ-02 Betriebsmodell | Irrelevant für system das gehört nicht zu ihren Aufgaben Bereich |
| DEC-OP-03 | BQ-03 Recht und Steuern | Irrelevant, das System wir nur handeln. Es ist nicht um rechtliches und steuerlich zu kümmern das wird extern von einer Person geregelt |
| DEC-OP-04 | BQ-04 Haltedauer und Verlustgrenze | Das Programm geht richtigung daytrading. Maximale halte dauer 7 Tage in der Regeln 4 h bis 4 Tage Haltedauer sind Standard Trades. Verlust pro Tag darf niemals mehr als 9 % des gesamt Kapitals sein |
| DEC-OP-05 | BQ-05 Hebel | Adaptiv bis 20× (empfohlen) |
| DEC-OP-06 | BQ-06 Ausschlüsse | Gesamtes Anlagenklassen Universum |
| DEC-OP-06A | BQ-06a Aktienindizes | Nur Indizes ohne Rüstung |
| DEC-OP-07 | BQ-07 Budget, KI-Abrechnung, Betrieb | Ich würde Hermes dafür nutzen dieser wird mit Abo Modellen betrieben um Kosten zu sparen. Geplant ist nicht direkt mit API kosten sondern Abo Modellen zu koppeln um Preis Leistung zu verbessern. Breites intraday Universum Wichtig das ist ein großer hochprofessionell ki Trading. Kein kleines Projekt. Es läuft auf einen eignen Windows vps |
| DEC-OP-08 | BQ-08 Broker | Ausschließlich mt5 als Broker |
| DEC-OP-08A | BQ-08a Plattform und Instrumente | Ausschließlich mt5 als Plattform, Futures bevorzugt aber auch andere als Option möglich |
| DEC-OP-09 | BQ-09 Team und Befugnis | Nur ich [Vorname entfernt, R-13] kann auf Demo oder Echtgeld schalten. Nur ich hab die Erlaubnis dazu |
| DEC-OP-10 | BQ-10 Rolle der KI | Hermes plus geprüfte ML-Modelle (empfohlen) |
<!-- GEN:END tab.operator_decisions -->

Die Auftragsentscheidungen D3-01 … D3-05 stehen als DEC-MP-D3-01 … DEC-MP-D3-05 im Entscheidungsregister. Den Vornamen aus BQ-09 enthält das Paket nicht (R-13).

### Konflikte zwischen Vorgaben (R-09)

<!-- GEN:BEGIN tab.conflicts -->
| ID | Konflikt | Behandlung (R-09) | Folgen und nötige Betreiberentscheidung |
|---|---|---|---|
| DEC-CF-01 | Recht/Steuern extern gegen §5.3, §15, §20 A2/H | Betreiberentscheidung gilt (Rang 2 vor Rang 3). Das Paket enthält keine Rechts- und Steuerprüfung; es liefert eine Übergabeliste und technische Rechtsgrenzen. | K-Abzüge A2 (Steueranteil), H1, H2, H3 (teilweise) ohne Umdeutung der Kriterien. Rechnungen werden „vor Steuern“ ausgewiesen; ein pauschaler Abschlag ist nur Sensitivität (P-ECO-TAX-SENS). Nötige Betreiberentscheidung: Beauftragung der externen Person mit den Punkten aus legal/handover_external.md (X-LEGAL-01, X-TAX-01). |
| DEC-CF-02 | „Niemals mehr als 9 % Tagesverlust“ gegen Kurslücken und Hebel bis 20× | Die Grenze wird als harte Größenregel umgesetzt: Lückenstress aller Positionen in ungünstigster Richtung plus bereits erlittener Tagesverlust ≤ 9 % − Reserve. Eine absolute Garantie gibt es nicht (Lücken jenseits der Historie, Handelsaussetzungen, Brokerausfall). | Die Größenregel begrenzt den erreichbaren Brutto-Hebel stark; hohe Profile sind nur mit Zinsfutures-Schwerpunkt und oft gar nicht zulässig (risk/leverage_results.json). Restwahrscheinlichkeit einer Überschreitung wird simuliert und ausgewiesen (risk/kelly_ruin_results.json). Nötige Betreiberentscheidung: Bestätigung der strengen Auslegung oder signierte Annahme einer Restwahrscheinlichkeit (X-OP-DLC-MODE). |
| DEC-CF-03 | Betriebsmodelle nicht Systemaufgabe gegen §4.2/D3-03 | Keine Bewertung von B1–B4; alle Rechnungen für ein Eigenkonto des Betreibers. | A5 = 0 Punkte, H1 = 0 Punkte; Nutzung für Dritte gesperrt (X-SCOPE-THIRD). |
| DEC-CF-04 | Ein eigener Windows-VPS gegen drei getrennte Vertrauensbereiche (§5.2, §12) | Empfehlung: Geldpfad auf dem Betreiber-VPS; Forschung/KI und Evaluator auf getrennten kleinen Instanzen. Falls der Betreiber nur einen VPS will: getrennte Windows-Konten, Firewall-Regeln und kein Hermes auf dem Geldpfad-Host – mit ausgewiesenem Restrisiko. | Kosten für zwei Zusatzinstanzen im Basisfall (registers/costs.json). Nötige Betreiberentscheidung X-INF-ZONES. |
| DEC-CF-05 | CFD als Option (BQ-08a) gegen „keine CFD“ (D3-01) | Futures sind Standard; der CFD-Pfad ist spezifiziert, aber standardmäßig abgeschaltet und nur mit signierter Betreiberfreigabe aktivierbar. Es gelten die ESMA/BaFin-Hebelgrenzen als harte Limits. | X-OP-CFD bleibt offen; ohne Freigabe kein CFD-Handel. |
| DEC-CF-06 | Einziger Befugter (BQ-09) gegen menschliches Vier-Augen-Prinzip und unabhängige Risikofunktion (§13, EV-13) | Die Befugnis des Betreibers bleibt unangetastet. Das Paket verlangt für Echtgeld-Standardbetrieb (G9) eine externe unabhängige Risikofunktion mit Leserechten und Vetorecht bei Profilaufstiegen; ohne sie bleibt G9 gesperrt. Pilot H5 (G8) ist mit dokumentiertem Restrisiko zulässig. | G1-Abzug im Raster; Sperre X-ORG-RISK für G9. Die Moduswahl Demo/Echtgeld bleibt allein beim Betreiber (SM-MODE). |
| DEC-CF-07 | LLM-Abo gegen Datenlizenzen | Keine Kurs-Rohdaten an LLM-Anbieter; Hermes erhält nur abgeleitete Kennzahlen und Metadaten. | X-AI-DPA: Datenschutz- und Lizenzprüfung durch die externe Person. |
| DEC-CF-08 | Markierte Rechenannahmen ohne ausdrückliche Zulassung von Standardwerten (R-07) | Der Betreiber hat keine Standardwerte ausdrücklich zugelassen. Die Rechner nutzen für acht offene Eingaben markierte Rechenannahmen (default_marked), die nie als Betreiberangabe gelten: Der Status bleibt UNBESTAETIGT, jedes abhängige Tor bleibt gesperrt, und jede Rechnung damit ist als Annahme ausgewiesen. | Keine Sperre wird durch eine Rechenannahme gelöst; validation/semantic_checks.py::check_operator prüft Status, Markierung und Verweise. Nötige Betreiberentscheidung: echte Werte liefern (X-OP-RATE, X-OP-BUDGET, X-OP-DLC-MODE, X-INF-ZONES) bzw. Broker- und Datenangaben beschaffen (X-BRK-LIQ, X-BRK-INTEREST, X-DATA-ND) oder die Rechenannahmen ausdrücklich zulassen; X-TAX-01 beantwortet die externe Person. |
<!-- GEN:END tab.conflicts -->

Jeder Konflikt nennt Befund, Folge, beste zulässige Alternative und die nötige Betreiberentscheidung; die Entscheidungen stehen als externe Eingaben mit Sperrwirkung in `external_inputs.json` (Registertechnik übernommen aus v2.0).

### Was ein Score von 100 hier bedeutet

K misst Qualität und Entscheidungsreife des Pakets, E die nachgewiesene Reife in der realen Welt; keiner der beiden misst Gewinne (§0.3). Weil BQ-02 und BQ-03 Betriebsmodelle, Recht und Steuern aus dem Systemumfang nehmen, sind die zugehörigen Unterkriterien (A5, H1, H2, Teile von A2 und H3) ohne Punkte bewertet; das ist eine Folge der Betreiberentscheidung, keine Lücke der Ausarbeitung, und wird in `audit/scorecard_K.json` begründet.

## §4 Zielbild v3.0

> **Betreiberfassung.** Das Zielbild ist eine institutionell gebaute Plattform für den Eigenhandel mit börsengehandelten Futures über MT5, in der ein deterministischer Kern alle Orders erzeugt und Hermes sowie geprüfte ML-Komponenten nur beraten. Alle zehn Bausteine aus §4.1 sind beschrieben; gebaut wird nur, was die Tore G0 bis G10 freigeben. Betriebsmodelle B1 bis B4 bewertet das Paket nach deiner Entscheidung BQ-02 nicht; es rechnet mit deinem Eigenkonto und nennt die Stellen, die sich bei einem anderen Modell ändern würden. Über alle Kapitalstufen bleibt das kostenfähige Universum für den geforderten Haltehorizont bei höchstens <!--v:calc:max_instruments_registered|int-->2<!--/v--> Instrumenten (höchstens <!--v:calc:max_instruments_breakeven|int-->4<!--/v--> bei der großzügigsten Kostenregel), weil Kosten je Risikoeinheit und Kontraktgrößen binden. Für Go/No-Go heißt das: Mehr Kapital allein löst das Problem nicht, der Engpass ist die Haltedauer-Vorgabe. Nächster Schritt ist deine Entscheidung zu DEC-CF-02 und zur Haltedauer (§5.7).

### 4.1 Plattformbausteine

Die Plattform trennt drei Vertrauensbereiche (DEC-DS-13, externe Eingabe X-INF-ZONES): den **Geldpfad** (Signal- und Portfoliomotor, Risikomotor, OMS, MT5-Adapter, Journal) auf einem eigenen Windows-VPS, weil die MT5-Python-Schnittstelle nur unter Windows läuft (SRC-MT5-PYPI); die **Forschungs- und KI-Zone** (Daten, Backtest, ML, Hermes) ohne Handelsrechte; und das **unabhängige Prüfmodul** (Evaluator), das Grenzwerte gegen Kontoauszüge und Brokerdaten nachrechnet und nur stoppen, nie handeln kann. Der Konflikt mit „ein eigener Windows-VPS“ aus BQ-07 ist als DEC-CF-04 dokumentiert.

| Nr. | Baustein | Aufgabe in v3.0 | Bereich | erste Stufe | Kapitel |
|---|---|---|---|---|---|
| 1 | Forschungsfabrik | Daten, Vorregistrierung, Experimente, Backtest mit dem Produktionskern, Validierung, Wissensregister | Forschung | BS-02 | §6, §9 |
| 2 | Prognose- und Portfoliomotor | Strategiefamilie S-TF/S-IM/S-REV/S-CA, Prognosekombination, Größenbestimmung mit Lückenregel, Pufferung | Geldpfad | BS-05 | §6.1, §7 |
| 3 | Risikomotor | Pre-Trade-, Intraday- und Post-Trade-Kontrollen; Hebel, Margin, VaR/ES, Stress, Limits, Verlust- und Drawdown-Leiter, Kill-Switch | Geldpfad und Prüfmodul | BS-05 | §7 |
| 4 | OMS/EMS | brokerneutrale Schnittstelle; erster Adapter MT5 (Exchange Execution), FIX/Drop-Copy nur als Schnittstellenvertrag | Geldpfad | BS-01 (Killer-Tests) | §8 |
| 5 | Markt- und Referenzdatendienst | Kontraktdaten, Kalender, Gebühren, Margins, Handels- und Liquiditätszeiten, versioniert mit Gültigkeitsdatum | Forschung, lesend im Geldpfad | BS-02 | §9 |
| 6 | Abgleich, NAV, Buchhaltung, Berichtswesen | Abgleich gegen Brokerauszug, NAV je Strategie im Hedging-Konto, P&L-Erklärung | Geldpfad (lesend) und Prüfmodul | BS-05 | §8.7, §14 |
| 7 | Überwachung, Alarmierung, Incident-Management | Heartbeats, Kosten- und Limitalarme, Runbooks | Betrieb | BS-05 | §14 |
| 8 | Governance-Werkzeuge | Grants, Freigaben, Register, unveränderliche Protokolle | Prüfmodul | BS-00 | §13 |
| 9 | KI-Copiloten | Hermes (Nous-Portal-Abo) für Forschung, Betrieb und Dokumentation; geprüfte ML-Komponenten nur nach §11.5 | Forschung/KI, außerhalb des Geldpfads | BS-05 | §11 |
| 10 | Betreibercockpit | Web-Ansicht und mobile Notfallansicht mit Nur-Abbau-Funktionen | Betrieb | BS-05 | §10 |

### 4.2 Betriebsmodelle

Deine Antwort zu BQ-02 nimmt die Bewertung der Betriebsmodelle aus dem Systemumfang. Das Paket rechnet deshalb ausschließlich mit dem **Eigenkonto des Betreibers** und empfiehlt kein Modell; die Pflicht aus §4.2 ist nach R-09 als nicht erfüllt dokumentiert (DEC-CF-03) und in der Selbstbewertung ohne Punkte geführt. Gelder Dritter sind ausgeschlossen, bis eine eigene Entscheidung vorliegt (X-SCOPE-THIRD). Damit eine spätere Entscheidung nicht bei null beginnt, hält die Tabelle fest, welche Plattformteile sich je Modell ändern würden; eine rechtliche oder steuerliche Aussage ist das nicht (BQ-03).

| ID | Modell | Status im Paket | Plattformteile, die sich ändern würden |
|---|---|---|---|
| B1 | Privater Eigenhandel | gerechneter Fall (Eigenkonto) | keine; Steuern nur als pauschale Sensitivität (§5.3) |
| B2 | Eigenhandel über eigene Gesellschaft | nicht bewertet | Kontoinhaber und Broker-Onboarding, Buchhaltungsexport, Kostenabzug in der Wirtschaftsrechnung |
| B3 | Verwaltung von Drittgeldern | ausgeschlossen (X-SCOPE-THIRD) | FCM mit FIX und Drop-Copy, NAV je Anleger, Berichtswesen, Aufsicht, Mindest-AUM |
| B4 | Softwareprodukt für Dritte | ausgeschlossen (X-SCOPE-THIRD) | Mandantentrennung, Produkthaftung, Abgrenzung zu Signalen und Beratung |

### 4.3 Skalierungsstufen

Die Entscheidungsrechnung läuft über die Kapitalstufen <!--v:param:P-ECO-CAPITAL-STAGES/0|mio-->0,25 Mio. EUR<!--/v--> bis <!--v:param:P-ECO-CAPITAL-STAGES/5|mio-->100 Mio. EUR<!--/v--> (P-ECO-CAPITAL-STAGES). Je Stufe entscheidet die Zulassung (§6.2), welche Kontrakte in Frage kommen: Die Zulassungsregel verlangt, dass die Kosten je Risikoeinheit höchstens <!--v:param:P-UNI-COST-SHARE-MAX|pct0-->33 %<!--/v--> des erwarteten Bruttoertrags der Strategie verzehren, dass ein einzelner Kontrakt höchstens <!--v:param:P-UNI-MAX-CONTRACT-RISK|pct0-->50 %<!--/v--> des Risikobudgets bindet und dass die Order an der Stufe gemessen höchstens <!--v:param:P-RISK-MAX-ADV-SHARE|pct0-->1 %<!--/v--> des Tagesvolumens erreicht.

<!-- GEN:BEGIN tab.stages -->
| Kapital (Mio. EUR) | Instrumente U-KOSTEN | U-BREAKEVEN | TF-D1-7T | TF-D1 | TF-D1: Micro / Standard | Fixkosten je Jahr EUR (inkl. Betreiberzeit) | Kommission je Monat EUR (TF-D1) | Befund TF-D1 H5 |
|---|---|---|---|---|---|---|---|---|
| 0,25 | 0 | 1 | 1 | 2 | 1 / 1 | 22.608 | 10 | PROFILE_NOT_ADMISSIBLE |
| 0,5 | 0 | 1 | 1 | 4 | 1 / 3 | 22.608 | 13 | PROFILE_NOT_ADMISSIBLE |
| 1 | 0 | 1 | 2 | 6 | 2 / 4 | 22.608 | 25 | PROFILE_NOT_ADMISSIBLE |
| 5 | 2 | 4 | 4 | 18 | 3 / 15 | 22.608 | 72 | PROFILE_NOT_ADMISSIBLE |
| 25 | 1 | 3 | 7 | 28 | 0 / 28 | 22.212 | 326 | PROFILE_NOT_ADMISSIBLE |
| 100 | 0 | 0 | 0 | 22 | 0 / 22 | 22.212 | 1.037 | PROFILE_NOT_ADMISSIBLE |
<!-- GEN:END tab.stages -->

Lesart: Für die schnellen, registrierten Strategien (U-KOSTEN) bleiben je Stufe null bis <!--v:calc:max_instruments_registered|int-->2<!--/v--> Instrumente; selbst die großzügige Regel U-BREAKEVEN (Kosten bis zum vollen Bruttoertrag) kommt nicht über <!--v:calc:max_instruments_breakeven|int-->4<!--/v-->. Micro-Kontrakte machen kleine Stufen erst möglich, kosten aber je Risikoeinheit mehr. In der höchsten Stufe verdrängt die Marktwirkung der größeren Orders die zuvor zugelassenen Kontrakte (Kapazitätsgrenze, DEC-DS-18). Personal: nur der Betreiber mit rund <!--v:dmc:operator_hours_per_year|d0-->314<!--/v--> Stunden im Jahr (Routine, Incidents, Quartalsprüfung; P-OPS-*) sowie ab G9 eine externe, unabhängige Risikofunktion (X-ORG-RISK). Betriebsmodell in allen Stufen: Eigenkonto.

### 4.4 Nicht-Ziele

- kein Hochfrequenzhandel und keine Latenzarbitrage;
- kein Handel durch Sprachmodelle (D3-05, DEC-DS-03);
- keine Garantie- oder Renditeversprechen und keine Anlageempfehlung;
- keine Umgehung von Broker-, Börsen- oder Aufsichtsregeln;
- keine Gelder Dritter und kein Softwareprodukt für Dritte (BQ-02, X-SCOPE-THIRD);
- keine Rechts- oder Steuerberatung; diese Fragen liegen bei einer externen Person (BQ-03, §15);
- keine Aktienindex-Futures ohne Nachweis, dass der Index rüstungsfrei ist (BQ-06a, DEC-DS-04);
- kein automatischer Wechsel zwischen Demo und Echtgeld; diesen Schalter bedient nur der Betreiber (BQ-09);
- kein erzwungener Mindesthebel (R-06, P-OP-LEV-MIN).

## §5 Wirtschaftlichkeit und Entscheidungsrechnung

> **Betreiberfassung.** Alle Handelskosten stammen aus einem einzigen Rechner mit belegter Brokergebühr (<!--v:costreg:COST-COMM-FXFLAT|eur2-->1,00 EUR<!--/v--> je Kontrakt und Seite), halbem Spread, Schlupf und Marktwirkung. Für den vorgegebenen Haltehorizont kosten die schnellen Strategien je Instrument fast immer mehr Sharpe-Ratio im Jahr, als die Literatur brutto erwarten lässt (Median <!--v:prior:median_gross/S-TF|d3-->0,092<!--/v--> je Instrument); nur <!--v:calc:cost_below_threshold_stf|int-->4<!--/v--> von <!--v:calc:instruments_access_primary|int-->65<!--/v--> handelbaren Kontrakten liegen unter der Kostenschwelle. Deshalb findet die Entscheidungsrechnung in keiner Kapitalstufe und keinem Profil einen zulässigen und wirtschaftlichen Weg: Der Befund lautet überall PROFILE_NOT_ADMISSIBLE oder NOT_VIABLE_AT_CAPITAL, die Empfehlung für Echtgeld überall No-Go. Auch die langsame Trendfolge TF-D1 ohne Sieben-Tage-Grenze ist in <!--v:calc:dmc_class_count/U-KOSTEN-TFD1/PROFILE_NOT_ADMISSIBLE|int-->24<!--/v--> von <!--v:calc:dmc_cells/U-KOSTEN-TFD1|int-->24<!--/v--> Zellen unzulässig: Mit dem Wochenendfaktor der eigenen Größenregel erreicht sie in H5 nur σ_p <!--v:lev:cells/U-KOSTEN-TFD1/5000000/H5/sigma_achieved|pct1-->2,5 %<!--/v--> statt mindestens <!--v:param:P-LEV-H5-SIGMA-MIN|pct0-->3 %<!--/v-->, und selbst ohne diese Grenze läge P(NPV > 0) in der Referenzstufe bei <!--v:dmc:table/U-KOSTEN-TFD1/5000000/H5/base/p_npv_positive|d2-->0,42<!--/v-->. Der Aufbau bis zum Pilot kostet rund <!--v:dmc:build_cost_until_pilot_eur|eur-->58.147 EUR<!--/v--> und überschreitet den markierten Ausgabendeckel von <!--v:param:P-ECO-SPEND-CAP|eur-->25.000 EUR<!--/v--> schon im Systembau. Nächster Schritt: Gebühren und Margins schriftlich vom Broker (X-BRK-FEES, X-BRK-MARGIN); eine längere Haltedauer allein ändert den Befund nicht.

Details: `financials/economic_model.md` (Kosten, Monte-Carlo, Sensitivitäten) und `financials/buy_vs_build.md` (Varianten V0–V4).

### 5.1 Kostenmodell je Instrument (eine Quelle der Wahrheit, EV-01)

`financials/cost_model.py` rechnet je Kontrakt die Kosten je Seite aus Kommission (FXFlat All-in, COST-COMM-FXFLAT; Sensitivität COST-COMM-FXFLAT-LOW), halbem Spread (Planwert in Ticks bis zur Messung, X-DATA-VOL), Schlupf von <!--v:costreg:COST-EXEC-SLIP-TICKS|d2-->0,25<!--/v--> Tick (COST-EXEC-SLIP-TICKS) und Marktwirkung nach dem Quadratwurzelmodell oberhalb einer freien Markttiefe (COST-EXEC-IMPACT-Y, COST-EXEC-IMPACT-FREE-SHARE). Rollkosten sind ein zusätzlicher Round-Turn je Roll, weil ohne Kalenderspread gerollt wird (DEC-DS-12). Daraus folgen die **Kosten je Risikoeinheit** c_RT (Round-Turn-Kosten geteilt durch die Jahresvolatilität des Kontrakts in Euro) und die Jahreskosten einer Strategie in Sharpe-Einheiten, C = (N_RT + N_Roll · τ) · c_RT / √τ, mit Umschlag N_RT und Zeit im Markt τ aus der Umschlagssimulation (§6.1).

Zulassungskriterium: C ≤ <!--v:param:P-UNI-COST-SHARE-MAX|pct0-->33 %<!--/v--> des erwarteten Bruttoertrags je Instrument, für S-TF also C ≤ <!--v:prior:admission_rule/cost_threshold_sr|d3-->0,030<!--/v-->. Die Schwelle folgt der Faustregel, dass Kosten höchstens ein Drittel des erwarteten Vorkostenertrags verzehren dürfen (SRC-LIT-CARVER-2015, SRC-LIT-CARVER-2023). Beispiele im Basisszenario: Gold (GC) kostet S-TF <!--v:costsym:GC/strategies/S-TF/sr_cost_per_year/base|d3-->0,025<!--/v--> im Jahr, der Euro-Schatz (FGBS) <!--v:costsym:FGBS/strategies/S-TF/sr_cost_per_year/base|d3-->0,591<!--/v-->, der günstigste kurzfristige Zinsfuture <!--v:calc:cheapest_stir_cost_stf|d3-->1,033<!--/v-->. Genau die volatilitätsarmen Zinskontrakte, die für hohen Brutto-Hebel nötig wären (§7.2), sind bei kurzer Haltedauer am teuersten. Intraday-Momentum (S-IM) kostet selbst im günstigsten Kontrakt <!--v:calc:cheapest_im_cost|d3-->0,112<!--/v--> im Jahr.

Jede andere Stelle (Aktivitätsmodell, Puffer, Stress, Pilot, Kostendrift) liest diese Ergebnisse aus `financials/cost_model_results.json`; die Paketprüfung scheitert bei abweichenden Werten (§19.2, Mutation „Spread ohne Kosten“).

### 5.2 Weitere Kostenarten

Marktdaten: Anzeige über den Broker <!--v:cost:fixed_costs/market_data_monthly_eur/ANZEIGE/monthly_eur|eur2-->53,00 EUR<!--/v--> im Monat; die Einstufung des automatisierten Handels als Non-Display-Nutzung ist offen (X-DATA-ND) und würde <!--v:cost:fixed_costs/market_data_monthly_eur/NON_DISPLAY_MANAGED/monthly_eur|eur2-->1.568,12 EUR<!--/v--> bis <!--v:cost:fixed_costs/market_data_monthly_eur/NON_DISPLAY_USER/monthly_eur|eur2-->2.440,96 EUR<!--/v--> im Monat kosten. Historische Daten einmalig <!--v:cost:fixed_costs/historical_data_once_eur|eur2-->3.477,35 EUR<!--/v-->; Infrastruktur für drei Instanzen, Sicherung und Alarmierung <!--v:cost:fixed_costs/infrastructure_monthly_eur|eur2-->135,00 EUR<!--/v--> im Monat; KI-Abo <!--v:cost:fixed_costs/ai_subscription_monthly_eur/SUPER|eur2-->87,63 EUR<!--/v--> im Monat. **Betreiberzeit** ist bewertet (EV-02): rund <!--v:dmc:operator_hours_per_year|d0-->314<!--/v--> Stunden im Jahr zu <!--v:param:P-ECO-HOURLY-RATE|d0-->50<!--/v--> EUR je Stunde (markierter Standard, X-OP-RATE). Die Summe der laufenden Kosten einschließlich Betreiberzeit und externer Risikofunktion beträgt in der Referenzstufe <!--v:dmc:table/U-KOSTEN-TFD1/5000000/H5/fixed_costs_annual/total_eur|eur-->22.608 EUR<!--/v--> im Jahr. Zinseffekt: Das beim Broker liegende Guthaben (<!--v:param:P-ECO-CASH-AT-BROKER|pct0-->25 %<!--/v--> des Kapitals, P-ECO-CASH-AT-BROKER) wird annahmegemäß nicht verzinst (X-BRK-INTEREST); gegenüber dem Geldmarktsatz (<!--v:param:P-ECO-CASH-RATE|pct2-->2,44 %<!--/v-->, SRC-ECB-ESTR) kostet das in der Referenzstufe <!--v:calc:cash_drag_ref|eur-->30.500 EUR<!--/v--> im Jahr. Versicherungen sind für das Eigenkonto nicht vorgesehen.

### 5.3 Steuern (Umfang nach BQ-03)

Nach BQ-03 regelt eine externe Person Recht und Steuern; das System handelt nur. Das Paket enthält deshalb keine Steuerszenarien für B1 oder B2, sondern eine pauschale **Sensitivität**: Positive Jahreswerte werden um <!--v:param:P-ECO-TAX-SENS|pct0-->30 %<!--/v--> gekürzt, Verluste bleiben ungekürzt (`financials/tax_scenarios.py`, X-TAX-01). Dieser Rechenwert ist keine Rechtsaussage. Ergebnisse stehen vor Steuern und nach Abschlag; die Übergabe an die externe Person beschreibt `legal/tax_matrix.md`. Der Konflikt mit §5.3 und §20 H ist als DEC-CF-01 dokumentiert.

### 5.4 Aufbaukosten

Menschliche Stunden und Agentenkosten je Baustufe stammen aus `implementation/build_stages.json` und `financials/stage_costs.py`. Das Bauprogramm BS-00 bis BS-10 ist im Basisfall mit <!--v:calc:build_agent_days_base|d0-->82<!--/v--> Agententagen und <!--v:calc:build_person_days_base|d0-->73<!--/v--> Personentagen geschätzt (Spanne <!--v:calc:build_agent_days_low|d0-->55<!--/v--> bis <!--v:calc:build_agent_days_high|d0-->118<!--/v--> Agententage); der größte Block ist der Systembau BS-05. Kosten bis zum Pilot: <!--v:dmc:build_cost_until_pilot_eur|eur-->58.147 EUR<!--/v-->; externes Audit zusätzlich <!--v:dmc:audit_cost_eur|eur-->17.381 EUR<!--/v-->.

<!-- GEN:BEGIN tab.stage_costs -->
| Stufe | Tor | Monate | Mensch (Projekt) EUR | Agent EUR | einmalig EUR | laufend EUR | Betreiberroutinen EUR | Risikofunktion EUR | gesamt EUR |
|---|---|---|---|---|---|---|---|---|---|
| BS-00 | GATE-G0 | 0,5 | 1.200 | 0 | 0 | 0 | 0 | 0 | 1.200 |
| BS-01 | GATE-G1 | 0,7 | 2.000 | 138 | 0 | 190 | 0 | 0 | 2.328 |
| BS-02 | GATE-G2 | 0,9 | 1.600 | 184 | 3.477 | 254 | 0 | 0 | 5.515 |
| BS-03 | GATE-G3 | 1,1 | 3.200 | 230 | 0 | 317 | 0 | 0 | 3.747 |
| BS-04 | GATE-G4 | 0,2 | 800 | 46 | 0 | 63 | 0 | 0 | 909 |
| BS-05 | GATE-G5 | 3,7 | 12.000 | 736 | 5.120 | 1.015 | 0 | 0 | 18.871 |
| BS-06 | GATE-G6 | 0,5 | 1.600 | 92 | 0 | 127 | 0 | 0 | 1.819 |
| BS-07 | GATE-G7 | 6,0 | 2.400 | 0 | 0 | 1.649 | 7.829 | 0 | 11.878 |
| BS-08 | GATE-G8 | 6,0 | 2.400 | 0 | 0 | 1.649 | 7.829 | 0 | 11.878 |
| BS-09 | GATE-G9 | 12,0 | 0 | 0 | 0 | 3.299 | 15.658 | 3.590 | 22.547 |
| BS-10 | GATE-G10 | 1,4 | 2.000 | 0 | 15.000 | 381 | 0 | 0 | 17.381 |
<!-- GEN:END tab.stage_costs -->

### 5.5 Kauf statt Bau und Varianten (EV-04)

Die Varianten V0 (Geldmarkt), V1 (Trendfolge-Fonds oder -ETF), V2 (Signal-Skript mit manuellen Orders), V3 (Framework plus eigene Strategie) und V4 (volle Eigenentwicklung) sind in `financials/buy_vs_build.md` bewertet. Maßstab ist der **Wert je Risikoeinheit** (erwarteter Jahreswert geteilt durch die Standardabweichung des Jahres-P&L).

<!-- GEN:BEGIN tab.variants -->
| Kapital (Mio. EUR) | V1 Wert je Risikoeinheit (Index 0,05/0,28) | V4 S-TF | V4 Alternative TF-D1 | Befund |
|---|---|---|---|---|
| 0,25 | 0,03 / 0,26 | – | -1,519 | NICHT_ZULASSUNGSFAEHIG |
| 0,5 | 0,04 / 0,27 | – | -1,058 | NICHT_ZULASSUNGSFAEHIG |
| 1 | 0,04 / 0,27 | – | -0,396 | NICHT_ZULASSUNGSFAEHIG |
| 5 | 0,05 / 0,28 | -0,084 | 0,063 | PROFILE_NOT_ADMISSIBLE |
| 25 | 0,05 / 0,28 | -0,042 | 0,206 | PROFILE_NOT_ADMISSIBLE |
| 100 | 0,05 / 0,28 | – | 0,210 | NICHT_ZULASSUNGSFAEHIG |
<!-- GEN:END tab.variants -->

V4 rechnet nur in <!--v:calc:variants_count/computed|int-->2<!--/v--> von <!--v:calc:variants_count/stages|int-->6<!--/v--> Kapitalstufen; dort ist die Eigenentwicklung schon wegen ihres Profils unzulässig (Prüfreihenfolge §5.7), und in <!--v:calc:variants_count/v1_better|int-->2<!--/v--> dieser Stufen läge die Untergrenze von V1 zusätzlich über V4: Ein Trendfolgeprodukt mit realisierter Netto-Sharpe-Ratio zwischen <!--v:param:P-ECO-V1-SR/0|d2-->0,05<!--/v--> und <!--v:param:P-ECO-V1-SR/1|d2-->0,28<!--/v--> (SRC-SG-TREND-TTU-2025, SRC-LIT-IDX-SGTREND-BABU-2020) braucht keinen Aufbau. Konkrete Produkte mit Kosten, Liquidität und Abbildungsqualität sind noch nicht recherchiert (X-V1-PRODUCTS).

### 5.6 Monte-Carlo-Entscheidungsrechnung (EV-03)

`financials/decision_montecarlo.py` zieht <!--v:dmc:draws_base|int-->20.000<!--/v--> Mal aus der Prior-Verteilung der Netto-Sharpe-Ratio (§6.3), der Kostenunsicherheit (P-ECO-COST-UNC-SD) und den Fixkosten und rechnet je Variante, Kapitalstufe und Hebelprofil den Jahreswert, den Kapitalwert über <!--v:param:P-ECO-HORIZON-Y|d0-->5<!--/v--> Jahre (Diskontsatz <!--v:param:P-ECO-DISCOUNT|pct0-->6 %<!--/v-->), P(NPV > 0), den Expected Shortfall des NPV, das Break-even-Kapital und den Wert je Risikoeinheit. Sensitivitäten: höhere Handelskosten (SZ-KOSTEN_X1_5, SZ-KOSTEN_X2, SZ-KOSTEN_X3), niedrigerer Prior (SZ-PRIOR_MINUS_0_05, SZ-PRIOR_MINUS_0_10), Fixkosten hoch, Betreiberzeit hoch, Non-Display-Daten, Steuer-Sensitivität, Guthaben vollständig beim Broker, Broker zahlt Geldmarktzins, Prior auf Indexniveau; die Definitionen stehen in `financials/assumptions.json`.

### 5.7 Entscheidungsregel, Befundklassen und Go/No-Go

Die Befundklassen folgen §5.7 des Auftrags; die Reihenfolge der Prüfung ist PROFILE_NOT_ADMISSIBLE → NON_POSITIVE_BASE → NOT_VIABLE_AT_CAPITAL → DOMINATED_BY_ALTERNATIVE → VIABLE/MARGINAL. VIABLE verlangt P(NPV > 0) ≥ <!--v:param:P-ECO-VIABLE-P|pct0-->80 %<!--/v--> und stabile Sensitivitäten, MARGINAL P(NPV > 0) ≥ <!--v:param:P-ECO-MARGINAL-P|pct0-->50 %<!--/v-->.

<!-- GEN:BEGIN tab.gonogo -->
| Kapital (Mio. EUR) | H5 | H10 | H15 | H20 | Alternative TF-D1 H5 (Betreiberentscheidung nötig) |
|---|---|---|---|---|---|
| 0,25 | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | PROFILE_NOT_ADMISSIBLE |
| 0,5 | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | PROFILE_NOT_ADMISSIBLE |
| 1 | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | PROFILE_NOT_ADMISSIBLE |
| 5 | NO_GO (PROFILE_NOT_ADMISSIBLE) | NO_GO (PROFILE_NOT_ADMISSIBLE) | NO_GO (PROFILE_NOT_ADMISSIBLE) | NO_GO (PROFILE_NOT_ADMISSIBLE) | PROFILE_NOT_ADMISSIBLE |
| 25 | NO_GO (PROFILE_NOT_ADMISSIBLE) | NO_GO (PROFILE_NOT_ADMISSIBLE) | NO_GO (PROFILE_NOT_ADMISSIBLE) | NO_GO (PROFILE_NOT_ADMISSIBLE) | PROFILE_NOT_ADMISSIBLE |
| 100 | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | NO_GO (NOT_VIABLE_AT_CAPITAL) | PROFILE_NOT_ADMISSIBLE |
<!-- GEN:END tab.gonogo -->

**Lesart.** Registriert ist die Strategiefamilie aus §6.1 innerhalb deiner Vorgaben. Sie ist in keiner Zelle zulässig, weil zu wenige Instrumente die Kostenschwelle bestehen (Mindestdiversifikation <!--v:param:P-LEV-H5-MINDIV|int-->8<!--/v--> effektive Instrumente) und weil höhere Profile die <!--v:param:P-OP-DAILY-LOSS-CAP|pct0-->9 %<!--/v-->-Grenze verletzen (§7). In <!--v:calc:dmc_empty_cells/U-KOSTEN|int-->16<!--/v--> der <!--v:calc:dmc_cells/U-KOSTEN|int-->24<!--/v--> Zellen ist bei diesem Kapital gar kein Instrument zugelassen; dort lautet der Befund NOT_VIABLE_AT_CAPITAL, weil die Folge eine Kapitalentscheidung ist und kein Profil geprüft werden kann (DEC-DS-25). Die Mindestdiversifikation ist nicht der eigentliche Engpass: Auch ohne sie läge der erwartete Jahreswert der registrierten Familie in der Referenzstufe bei <!--v:dmc:table/U-KOSTEN/5000000/H5/base/expected_annual_value_eur|eur-->-24.145 EUR<!--/v-->, weil der Mehrertrag den entgangenen Geldmarktzins auf das Brokerguthaben und die Fixkosten nicht deckt; die Variante TF-D1-7T innerhalb deiner Vorgaben erreicht in der Stufe <!--v:param:P-ECO-CAPITAL-STAGES/4|mio-->25 Mio. EUR<!--/v--> einen Erwartungswert von <!--v:dmc:table/U-KOSTEN-TFD1-7T/25000000/H5/base/expected_annual_value_eur|eur-->-8.151 EUR<!--/v--> im Jahr und einen Wert je Risikoeinheit von <!--v:dmc:table/U-KOSTEN-TFD1-7T/25000000/H5/base/value_per_risk_unit|d3-->-0,008<!--/v--> (Untergrenze von V1: <!--v:param:P-ECO-V1-SR/0|d2-->0,05<!--/v-->). Die Spalte „Alternative TF-D1“ ist keine Empfehlung, sondern die beste gerechnete Alternative nach R-09: Sie verlangt, die Höchsthaltedauer von <!--v:calc:hold_max_days|d0-->7<!--/v--> Tagen aufzugeben (Median-Haltedauer der Alternative <!--v:turn:strategies/S-BASE-TFD1/holding_hours_median|d0-->362<!--/v--> Stunden), ihr Prior liegt über den realisierten Indexwerten (Plausibilitätsmarke in `research/prior_results.json`), und nach der Größenregel mit Wochenendfaktor (P-RISK-WEEKEND-FACTOR) ist sie in <!--v:calc:dmc_class_count/U-KOSTEN-TFD1/PROFILE_NOT_ADMISSIBLE|int-->24<!--/v--> von <!--v:calc:dmc_cells/U-KOSTEN-TFD1|int-->24<!--/v--> Zellen unzulässig.

### 5.8 Abbruchkriterien

Vor jeder kostenpflichtigen Stufe prüft das Tor: Befund nicht VIABLE, P(NPV > 0) unter Schwelle, DOMINATED_BY_ALTERNATIVE, Ausgabendeckel erreicht oder Höchstdauer bis G5 (<!--v:param:P-ECO-MAX-MONTHS-G5|d0-->12<!--/v--> Monate) überschritten → Stopp oder signierte Betreiberentscheidung. Mit dem markierten Deckel von <!--v:param:P-ECO-SPEND-CAP|eur-->25.000 EUR<!--/v--> (X-OP-BUDGET) reicht das Budget bis G4 (kumuliert <!--v:calc:spend_to_BS04|eur-->13.700 EUR<!--/v-->); der Systembau führt auf <!--v:calc:spend_to_BS05|eur-->32.572 EUR<!--/v--> und braucht deshalb eine ausdrückliche Budgetentscheidung. Im heutigen Stand greift das Abbruchkriterium schon an G0: Echtgeld ist nicht zu empfehlen, zulässig sind Demo- und Paper-Arbeit innerhalb des Deckels.

## §6 Strategie- und Forschungsprogramm

> **Betreiberfassung.** Registriert ist eine Strategiefamilie für deinen Haltehorizont: schnelle Trendfolge (S-TF), Intraday-Momentum (S-IM), Kurzfrist-Umkehr (S-REV) und ein Carry-Filter (S-CA); TF-D1 aus v2.0 dient nur als Vergleich. Die Erwartung ist aus der Literatur gerechnet und nicht erzählt: Brutto liegt der Median je Instrument für S-TF bei <!--v:prior:median_gross/S-TF|d3-->0,092<!--/v-->, nach Kosten bleibt davon bei den meisten Kontrakten nichts. Selbst eine echte Kante mit Sharpe-Ratio <!--v:param:P-RES-SR-USEFUL|d1-->0,3<!--/v--> bräuchte für einen statistischen Nachweis rund <!--v:stat:years_for_power/0.3|d0-->69<!--/v--> Jahre Daten, deshalb schützen die Tore vor allem vor teuren Irrtümern. In der registrierten Konfiguration erreicht eine wertlose Strategie den Systembau nur in <!--v:oc:registered/WERTLOS/ohne_futility/rates/reached_G5_build|pct2-->0,05 %<!--/v--> der Fälle, eine brauchbare allerdings auch nur in <!--v:oc:registered/BRAUCHBAR/ohne_futility/rates/reached_G5_build|pct2-->1,40 %<!--/v-->. Für Go/No-Go heißt das: Forschung mit historischen und Demodaten ist günstig und sinnvoll, Echtgeld ist es nicht. Nächster Schritt ist die Datenlizenz (X-DATA-LIC) und die Messung von Spreads und Volatilitäten in G2 (X-DATA-VOL).

Details: `research/strategy_family.md`, `research/research_plan.md`, Referenzimplementierungen in `research/reference_strategies/`.

### 6.1 Vorregistrierte Strategiefamilie

Die Familie ist vor jeder Ergebnisansicht festgelegt (DEC-DS-23 dokumentiert, dass die Geschwindigkeiten von S-TF nur anhand von Umschlag und Haltedauer auf synthetischen Preisen ohne Kante gewählt wurden, nie anhand eines Ertrags).

| ID | Mechanismus | Kernregel (Parameter) | Rolle |
|---|---|---|---|
| S-TF | Zeitreihen-Momentum über mehrere Geschwindigkeiten | EWMA-Crossover mit vier Geschwindigkeitspaaren (P-STR-TF-SPEEDS), Prognose skaliert und gekappt (P-STR-FC-SCALE, P-STR-FC-CAP), Einstieg und Ausstieg über Prognoseschwellen (P-STR-TF-ENTRY, P-STR-TF-EXIT), Schutzstopp (P-STR-STOP-ATR), Zeitstopp bei P-OP-HOLD-MAX-H | Kern |
| S-IM | Intraday-Momentum: Rendite des Sitzungsbeginns sagt die Rendite des Sitzungsendes voraus (SRC-LIT-INTRA-GHLZ-2018, SRC-LIT-INTRA-BDLM-2021) | Signal nach P-STR-IM-SIGNAL-MIN Minuten, Haltedauer P-STR-IM-HOLD-H | Ergänzung |
| S-REV | Kurzfrist-Umkehr nach extremen Bewegungen (SRC-LIT-REV-WY-2004, SRC-LIT-REV-KRT-2020) | Einstieg ab z-Wert P-STR-REV-Z, Haltedauer P-STR-REV-HOLD-H | Ergänzung, Prior bei null |
| S-CA | Carry (Terminstruktur, Rollrendite; SRC-LIT-CARRY-KMPV-2018) | Neigung der S-TF-Prognose um P-STR-CA-TILT | Filter, keine eigene Position |
| S-BASE | TF-D1 aus v2.0 und TF-D1-7T mit Sieben-Tage-Zeitstopp | unverändert aus v2.0 übernommen (`research/reference_strategies/tf_d1_baseline.py`) | Vergleichsbasis (D3-04, DEC-DS-08) |
| S-X | weitere Prämien | nicht registriert | – |
| S-ML | Meta-Labeling für die Größe (MOD-ML-META), Regimeerkennung (MOD-ML-REGIME) | nur nach §11.5: DSR ≥ P-AI-ML-DSR-MIN und Mehrwert ≥ P-AI-ML-UPLIFT-MIN gegenüber der Regel | optional |

Kombination: feste Risikoanteile je Strategie (P-STR-RISK-SHARES), Prognosediversifikation gedeckelt (P-STR-FDM-CAP), Instrumentdiversifikation gedeckelt (P-STR-IDM-CAP), Positionspuffer P-STR-BUFFER, Sperrfrist nach Stopp P-STR-REENTRY-COOLDOWN-H. Jede Strategie hat eine ausführbare Referenzimplementierung; die Umschlagssimulation (`research/reference_strategies/turnover_simulation.py`) misst Umschlag und Haltedauer auf synthetischen Preisen ohne Kante:

<!-- GEN:BEGIN tab.turnover -->
| Strategie | Round-Turns je Jahr und Instrument | Zeit im Markt | Median-Haltedauer | Anteil 4 h–4 T | Anteil Zeitstopp | längste Haltedauer | 7-Tage-Grenze eingehalten |
|---|---|---|---|---|---|---|---|
| S-TF schnelle Trendfolge | 81,2 | 62 % | 47,7 h | 73 % | 8,2 % | 168 h | ja |
| S-IM Intraday-Momentum | 113,5 | 5 % | 4,0 h | 99 % | 0,0 % | 4 h | ja |
| S-REV Kurzfrist-Umkehr | 8,1 | 7 % | 72,0 h | 90 % | 0,0 % | 106 h | ja |
| TF-D1 (v2.0, ohne Zeitstopp) | 6,8 | 46 % | 362,0 h | 20 % | 0,0 % | 6.120 h | nein |
| TF-D1-7T (mit 7-Tage-Zeitstopp) | 13,2 | 22 % | 168,0 h | 23 % | 61,9 % | 168 h | ja |
<!-- GEN:END tab.turnover -->

S-TF hält im Median <!--v:turn:strategies/S-TF/holding_hours_median|d0-->48<!--/v--> Stunden, <!--v:turn:strategies/S-TF/share_within_4h_4d|pct0-->73 %<!--/v--> der Trades liegen im Standardfenster <!--v:param:P-OP-HOLD-STD-MIN-H|d0-->4<!--/v--> h bis <!--v:calc:hold_std_max_days|d0-->4<!--/v--> Tage, und der Zeitstopp greift bei <!--v:turn:strategies/S-TF/share_timestop|pct1-->8,2 %<!--/v--> der Trades. TF-D1 ohne Zeitstopp verletzt die Höchsthaltedauer deutlich (Median <!--v:turn:strategies/S-BASE-TFD1/holding_hours_median|d0-->362<!--/v--> Stunden).

### 6.2 Universum und Zulassung

Die Kandidatenliste umfasst <!--v:calc:instruments_total|int-->78<!--/v--> Futures über alle Klassen (`registers/instruments.json`), darunter die gängigen kurzfristigen Zinsfutures (SOFR drei Monate und ein Monat, €STR drei Monate, Euribor, SONIA) und Staatsanleihen vom Euro-Schatz bis zum Ultra-Bond. Vollständig ist das Zinsuniversum nicht: Es fehlen unter anderem Fed-Funds-Futures, die dreijährige T-Note, kurze und mittlere BTP-Futures, der Swiss Conf und weitere Rendite-Kontrakte; sie werden in BS-02 mit Quelle und Datum nachgetragen, bevor die Zinsallokation kalibriert wird. Beim Primärbroker handelbar sind <!--v:calc:instruments_access_primary|int-->65<!--/v-->; ICE und Euronext bietet er nicht an (X-BRK-ALT), und Brent an der NYMEX ist wegen widersprüchlicher Tickdaten gesperrt. Aktienindizes sind nach BQ-06a nur zulässig, wenn der Index nachweislich rüstungsfrei ist: Keiner der <!--v:calc:index_candidates|int-->14<!--/v--> geprüften Kandidaten erbringt diesen Nachweis, deshalb ist die Variante mit Aktienindizes derzeit identisch mit der Variante ohne (X-EQ-INDEX). Volatilitätsfutures sind ausgeschlossen, weil ihre Sprünge und ihre strukturelle Rollrendite mit der Lückenregel (§7.4) unvereinbar sind.

<!-- GEN:BEGIN tab.universe -->
| Anlageklasse | Kandidaten | davon beim Primärbroker handelbar (Börse angeboten, nicht gesperrt) |
|---|---|---|
| AGRAR | 18 | 12 |
| ANLEIHE | 13 | 12 |
| ENERGIE | 11 | 7 |
| FX | 14 | 14 |
| KRYPTO | 4 | 4 |
| METALL | 11 | 11 |
| RENDITE | 2 | 2 |
| STIR | 5 | 3 |
<!-- GEN:END tab.universe -->

Zulassungsregeln je Kapitalstufe: Börsenzugang des Kontos (P-UNI-REQUIRE-ACCESS), Mindestvolumen (P-UNI-MIN-ADV), Kosten je Risikoeinheit einschließlich Marktwirkung bei Stufengröße (§5.1), Kontraktgröße gegenüber dem Instrumentbudget (P-UNI-MAX-CONTRACT-RISK), Datenhistorie mit Proxy-Regel (§6.5), Preislimits und Handelszeiten; je Basiswert nur ein Kontrakt, der günstigste zulässige.

**Datenhistorie.** Zugelassen wird nur, was mit dem geplanten Datensatz mindestens <!--v:prior:admission_rule/min_history_years|d0-->10<!--/v--> Jahre Intraday-Historie hat (Entwicklungsjahre plus Holdout) oder über einen Standardkontrakt auf denselben Basiswert rekonstruiert werden kann. Das schließt <!--v:calc:history_excluded_count|int-->16<!--/v--> handelbare Kontrakte aus: <!--v:calc:history_excluded_symbols|raw-->10Y, 2YY, BTC, ETH, MBT, MET, SR1, SR3, ALI, FBTP, FGBL, FGBM, FGBS, FGBX, FOAT, FST3<!--/v-->. Betroffen sind gerade die Kontrakte, die für Hebel zentral wären: SOFR- und €STR-Futures sowie alle Eurex-Anleihen, deren Historie beim geplanten Anbieter erst 2018 beginnt; die Listungsjahre neuerer Kontrakte sind Annahmen, die in G2 bestätigt werden (X-DATA-HIST).

Die Regel wird in fünf Varianten gerechnet, damit sichtbar ist, was an der Kostenschwelle hängt:

<!-- GEN:BEGIN tab.admission -->
| Variante | Kapital (Mio. EUR) | Instrumente | D | zugelassen | Netto-Sharpe Portfolio (Median) | P(> 0) |
|---|---|---|---|---|---|---|
| U-KOSTEN | 0,25 | 0 | 0,00 |  | – | – |
| U-KOSTEN | 0,5 | 0 | 0,00 |  | – | – |
| U-KOSTEN | 1 | 0 | 0,00 |  | – | – |
| U-KOSTEN | 5 | 2 | 1,38 | GC, RB | 0,092 | 0,98 |
| U-KOSTEN | 25 | 1 | 1,00 | GC | 0,068 | 0,99 |
| U-KOSTEN | 100 | 0 | 0,00 |  | – | – |
| U-BREAKEVEN | 0,25 | 1 | 1,00 | MGC | 0,039 | 0,84 |
| U-BREAKEVEN | 0,5 | 1 | 1,00 | MGC | 0,039 | 0,84 |
| U-BREAKEVEN | 1 | 1 | 1,00 | MGC | 0,039 | 0,84 |
| U-BREAKEVEN | 5 | 4 | 1,74 | HG, MGC, HO, RB | 0,088 | 0,92 |
| U-BREAKEVEN | 25 | 3 | 1,50 | GC, SI, CL | 0,058 | 0,84 |
| U-BREAKEVEN | 100 | 0 | 0,00 |  | – | – |
| U-KOSTEN-TFD1-7T | 0,25 | 1 | 1,00 | MGC | 0,079 | 1,00 |
| U-KOSTEN-TFD1-7T | 0,5 | 1 | 1,00 | MGC | 0,079 | 1,00 |
| U-KOSTEN-TFD1-7T | 1 | 2 | 1,38 | MGC, NG | 0,098 | 1,00 |
| U-KOSTEN-TFD1-7T | 5 | 4 | 1,74 | HG, MGC, HO, RB | 0,143 | 1,00 |
| U-KOSTEN-TFD1-7T | 25 | 7 | 1,87 | GC, HG, SI, CL, HO, NG, RB | 0,141 | 1,00 |
| U-KOSTEN-TFD1-7T | 100 | 0 | 0,00 |  | – | – |
| U-KOSTEN-TFD1 | 0,25 | 2 | 1,38 | 6N, MCL | 0,238 | 1,00 |
| U-KOSTEN-TFD1 | 0,5 | 4 | 1,62 | 6B, 6C, 6N, MCL | 0,277 | 1,00 |
| U-KOSTEN-TFD1 | 1 | 6 | 2,00 | ZL, 6A, 6B, 6J, MGC, MCL | 0,358 | 1,00 |
| U-KOSTEN-TFD1 | 5 | 18 | 2,50 | KE, UB, ZL, ZM, ZS, ZW, 6A, 6B, 6E … (+9) | 0,434 | 1,00 |
| U-KOSTEN-TFD1 | 25 | 28 | 2,50 | KE, TN, UB, ZB, ZC, ZF, ZL, ZM, ZN … (+19) | 0,412 | 1,00 |
| U-KOSTEN-TFD1 | 100 | 22 | 2,50 | TN, UB, ZB, ZF, ZL, ZN, ZS, ZW, 6A … (+13) | 0,392 | 1,00 |
| U-ALLE | 0,25 | 6 | 1,93 | M6B, M6E, MJY, 1OZ, MCL, MNG | -1,064 | 0,00 |
| U-ALLE | 0,5 | 10 | 2,18 | ZF, ZT, 6C, 6M, M6B, M6E, MJY, 1OZ, MCL … (+1) | -0,986 | 0,00 |
| U-ALLE | 1 | 15 | 2,37 | ZC, ZF, ZM, ZN, ZT, 6A, 6B, 6C, 6M … (+6) | -0,775 | 0,00 |
| U-ALLE | 5 | 25 | 2,50 | KE, TN, UB, ZB, ZC, ZF, ZL, ZM, ZN … (+16) | -0,453 | 0,00 |
| U-ALLE | 25 | 32 | 2,50 | KE, TN, UB, ZB, ZC, ZF, ZL, ZM, ZN … (+23) | -0,477 | 0,00 |
| U-ALLE | 100 | 32 | 2,50 | KE, TN, UB, ZB, ZC, ZF, ZL, ZM, ZN … (+23) | -0,754 | 0,00 |
<!-- GEN:END tab.admission -->

### 6.3 Prior rechnerisch hergeleitet (CR-5)

`research/prior_derivation.py` leitet die Erwartung aus der Literaturtabelle (`research/sources/R3_literature_prior.json`) ab. Anker: Zwölf-Monats-Trendfolge je Instrument mit Sharpe-Ratio <!--v:prior:anchors/tf12_per_instrument/0|d2-->0,34<!--/v--> bis <!--v:prior:anchors/tf12_per_instrument/1|d2-->0,40<!--/v--> (SRC-LIT-TF-BABU-2020-JOIM, SRC-LIT-TF-HOP-2017), Verhältnis der Ein-Monats- zur Zwölf-Monats-Trendfolge <!--v:prior:anchors/ratio_1m_12m/1|d2-->0,56<!--/v--> bis <!--v:prior:anchors/ratio_1m_12m/0|d2-->0,83<!--/v--> (SRC-LIT-TF-MOP-2012, SRC-LIT-TF-LP-2016), Intraday-Momentum je Klasse (Anleihen <!--v:prior:anchors/im_class_sr/ANLEIHE|d2-->1,62<!--/v-->, Rohstoffe <!--v:prior:anchors/im_class_sr/ROHSTOFF|d2-->1,42<!--/v-->, Devisen <!--v:prior:anchors/im_class_sr/FX|d2-->0,87<!--/v-->; SRC-LIT-INTRA-LSU-2022). Abschläge als Verteilungen: Übertragung auf den kürzeren Horizont (P-PRI-H-TF, P-PRI-H-IM), Veröffentlichungseffekt mit Untergrenze <!--v:prior:anchors/decay_lower_bound_literature|d2-->0,42<!--/v--> (SRC-LIT-DECAY-MP-2016), Mehrfachtest (P-PRI-MT-TF, P-PRI-MT-IM; SRC-LIT-DECAY-HLZ-2016), Umsetzung (P-PRI-IMPL). Korrelationen innerhalb und zwischen Klassen sowie zwischen Strategien stehen in P-PRI-RHO-*. Die Konsistenzprüfungen gegen die Literaturwerte sind im Ergebnis vermerkt.

<!-- GEN:BEGIN tab.prior_gross -->
| Strategie (je Instrument, brutto) | 5 %-Quantil | Median | 95 %-Quantil | Mittel |
|---|---|---|---|---|
| S-TF mit Carry-Filter | 0,036 | 0,092 | 0,185 | 0,099 |
| S-TF ohne Carry-Filter | 0,018 | 0,066 | 0,158 | 0,074 |
| S-REV | -0,166 | 0,000 | 0,164 | 0,000 |
| TF-D1 | 0,120 | 0,197 | 0,291 | 0,199 |
| TF-D1-7T | 0,050 | 0,094 | 0,166 | 0,099 |
| S-IM Zinsen/Anleihen | 0,078 | 0,196 | 0,428 | 0,217 |
| S-IM Rohstoffe/Krypto | 0,067 | 0,169 | 0,370 | 0,187 |
| S-IM Devisen | 0,044 | 0,112 | 0,244 | 0,124 |
<!-- GEN:END tab.prior_gross -->

Plausibilität: Der Median des Portfolio-Priors der Alternative TF-D1 (<!--v:prior:portfolio/U-KOSTEN-TFD1/5000000/S-BASE-TFD1/p50|d2-->0,43<!--/v--> netto) liegt über der Spanne realisierter Trendfolge-Indizes (<!--v:param:P-ECO-V1-SR/0|d2-->0,05<!--/v--> bis <!--v:param:P-ECO-V1-SR/1|d2-->0,28<!--/v-->); der Rechner markiert das, und die Entscheidungsrechnung prüft deshalb zusätzlich SZ-PRIOR_AUF_INDEXNIVEAU. Die Betriebscharakteristik der Tore rechnet mit einem skeptischen Prior (P-OC-PRIOR-MODE, P-OC-PRIOR-SD).

### 6.4 Forschungsprotokoll

Vorregistrierung im Experiment-Manifest vor jeder Ergebnisansicht, Mehrfachtest-Budget je Kampagne (P-OC-TRIALS); Deflated Sharpe Ratio mindestens <!--v:param:P-RES-DSR-MIN|d2-->0,95<!--/v-->; PBO mit CSCV höchstens <!--v:param:P-RES-PBO-MAX|pct0-->20 %<!--/v-->; Reality Check, SPA-Test und Romano-Wolf-Schrittverfahren (SRC-LIT-WHITE-2000, SRC-LIT-HANSEN-2005, SRC-LIT-RW-2005); für ML bereinigte Kreuzvalidierung mit Embargo (P-RES-EMBARGO-H; SRC-LIT-LDP-2018); Walk-forward, Parameternachbarschaft, Teilperioden, Regime, Kostenszenarien und Kapazität; versiegelter Holdout (P-RES-HOLDOUT-YEARS) nach Entwicklungsjahren (P-RES-DEV-YEARS), dann Paper-Forward (P-RES-PAPER-MONTHS) und Posterior-Aktualisierung. Hürde für neue Faktoren ohne Literatur-Prior: t > <!--v:param:P-RES-T-HURDLE|d1-->3,0<!--/v--> nach Korrektur. `research/statistical_calculator.py` reproduziert den Quellenwert der DSR aus dem Beispiel von Bailey und López de Prado (<!--v:stat:dsr_source_example/N46|d4-->0,9505<!--/v--> gegenüber <!--v:stat:dsr_source_example/source_value_N46|d4-->0,9505<!--/v-->; SRC-LIT-BLP-2014-DSR) und zeigt an synthetischen Daten, dass PBO, Reality Check und SPA reines Rauschen erkennen.

Teststärke: Der Nachweis einer Netto-Sharpe-Ratio verlangt bei α = <!--v:param:P-RES-ALPHA|d2-->0,05<!--/v--> und Teststärke <!--v:param:P-RES-POWER|pct0-->80 %<!--/v-->:

<!-- GEN:BEGIN tab.power -->
| Netto-Sharpe p. a. | Jahre Daten für α = 5 %, Teststärke 80 % |
|---|---|
| 0,05 | 2.473,0 |
| 0,1 | 618,3 |
| 0,2 | 154,6 |
| 0,3 | 68,7 |
| 0,5 | 24,7 |
| 0,75 | 11,0 |
| 1,0 | 6,2 |
<!-- GEN:END tab.power -->

### 6.5 Datenhistorie und Proxy-Regel (EV-08)

Micro- und neu gelistete Kontrakte werden über den Standardkontrakt auf **denselben** Basiswert rekonstruiert (Feld `standard_ref` im Instrumentregister); Abweichungen bei Multiplikator, Tick, Liquidität und Handelszeiten werden ausgewiesen. Ein Proxy mit anderem Basiswert ist ohne Nachweis unzulässig; das Beispiel aus v2.0 (Micro Ultra 10-Year gegenüber der 10-Year Note, SRC-CBOT-MTN) ist ausdrücklich ausgeschlossen. Regeln und Prüfungen: `data/proxy_rules.md`.

### 6.6 Frühe Futility-Regel (EV-05)

Nach G3 und G4 berechnet das Tor die prädiktive Wahrscheinlichkeit, das Endtor zu bestehen; liegt sie unter <!--v:param:P-RES-FUTILITY|pct0-->10 %<!--/v-->, stoppt das Projekt vor dem Systembau (DEC-DS-21). `research/operating_characteristics.py` simuliert je <!--v:param:P-RES-OC-STRATEGIES|int-->4.000<!--/v--> schädliche (wahre Sharpe-Ratio <!--v:param:P-RES-SR-HARMFUL|d1-->-0,2<!--/v-->), wertlose und brauchbare Strategien (<!--v:param:P-RES-SR-USEFUL|d1-->0,3<!--/v-->) mit gemeinsamen Zufallszahlen, mit und ohne Futility-Regel:

<!-- GEN:BEGIN tab.oc -->
| Konfiguration | Klasse | Futility | besteht G3 | erreicht Bau (G5) | besteht G8 | Endtor | erwartete Kosten EUR |
|---|---|---|---|---|---|---|---|
| registriert | SCHAEDLICH | ohne futility | 0,0 % | 0,0 % | 0,0 % | 0,0 % | 12.791 |
| registriert | SCHAEDLICH | mit futility | 0,0 % | 0,0 % | 0,0 % | 0,0 % | 12.791 |
| registriert | WERTLOS | ohne futility | 0,1 % | 0,1 % | 0,0 % | 0,0 % | 12.811 |
| registriert | WERTLOS | mit futility | 0,1 % | 0,1 % | 0,0 % | 0,0 % | 12.811 |
| registriert | BRAUCHBAR | ohne futility | 2,2 % | 1,4 % | 0,9 % | 0,9 % | 13.416 |
| registriert | BRAUCHBAR | mit futility | 2,2 % | 1,4 % | 0,9 % | 0,9 % | 13.416 |
| SKEPTISCH\|DSR0.8 | SCHAEDLICH | ohne futility | 0,2 % | 0,1 % | 0,0 % | 0,0 % | 12.812 |
| SKEPTISCH\|DSR0.8 | SCHAEDLICH | mit futility | 0,2 % | 0,1 % | 0,0 % | 0,0 % | 12.812 |
| SKEPTISCH\|DSR0.8 | WERTLOS | ohne futility | 1,6 % | 0,7 % | 0,3 % | 0,2 % | 13.095 |
| SKEPTISCH\|DSR0.8 | WERTLOS | mit futility | 1,6 % | 0,7 % | 0,3 % | 0,2 % | 13.086 |
| SKEPTISCH\|DSR0.8 | BRAUCHBAR | ohne futility | 13,4 % | 8,9 % | 6,1 % | 3,9 % | 16.700 |
| SKEPTISCH\|DSR0.8 | BRAUCHBAR | mit futility | 13,4 % | 8,3 % | 5,7 % | 3,9 % | 16.428 |
| SKEPTISCH\|DSR0.5 | SCHAEDLICH | ohne futility | 3,6 % | 1,4 % | 0,8 % | 0,1 % | 13.408 |
| SKEPTISCH\|DSR0.5 | SCHAEDLICH | mit futility | 3,6 % | 0,2 % | 0,1 % | 0,1 % | 12.904 |
| SKEPTISCH\|DSR0.5 | WERTLOS | ohne futility | 14,3 % | 6,9 % | 3,6 % | 1,0 % | 15.765 |
| SKEPTISCH\|DSR0.5 | WERTLOS | mit futility | 14,3 % | 2,6 % | 1,3 % | 0,7 % | 13.915 |
| SKEPTISCH\|DSR0.5 | BRAUCHBAR | ohne futility | 53,8 % | 35,3 % | 23,5 % | 9,5 % | 28.241 |
| SKEPTISCH\|DSR0.5 | BRAUCHBAR | mit futility | 53,8 % | 17,0 % | 11,3 % | 6,9 % | 20.302 |
| LITERATUR\|DSR0.95 | SCHAEDLICH | ohne futility | 0,0 % | 0,0 % | 0,0 % | 0,0 % | 12.791 |
| LITERATUR\|DSR0.95 | SCHAEDLICH | mit futility | 0,0 % | 0,0 % | 0,0 % | 0,0 % | 12.791 |
| LITERATUR\|DSR0.95 | WERTLOS | ohne futility | 0,1 % | 0,1 % | 0,0 % | 0,0 % | 12.811 |
| LITERATUR\|DSR0.95 | WERTLOS | mit futility | 0,1 % | 0,1 % | 0,0 % | 0,0 % | 12.811 |
| LITERATUR\|DSR0.95 | BRAUCHBAR | ohne futility | 2,2 % | 1,4 % | 0,9 % | 0,9 % | 13.416 |
| LITERATUR\|DSR0.95 | BRAUCHBAR | mit futility | 2,2 % | 1,4 % | 0,9 % | 0,9 % | 13.416 |
| LITERATUR\|DSR0.8 | SCHAEDLICH | ohne futility | 0,2 % | 0,1 % | 0,0 % | 0,0 % | 12.812 |
| LITERATUR\|DSR0.8 | SCHAEDLICH | mit futility | 0,2 % | 0,1 % | 0,0 % | 0,0 % | 12.812 |
| LITERATUR\|DSR0.8 | WERTLOS | ohne futility | 1,6 % | 0,7 % | 0,3 % | 0,3 % | 13.095 |
| LITERATUR\|DSR0.8 | WERTLOS | mit futility | 1,6 % | 0,7 % | 0,3 % | 0,3 % | 13.095 |
| LITERATUR\|DSR0.8 | BRAUCHBAR | ohne futility | 13,4 % | 8,9 % | 6,1 % | 6,1 % | 16.700 |
| LITERATUR\|DSR0.8 | BRAUCHBAR | mit futility | 13,4 % | 8,9 % | 6,1 % | 6,1 % | 16.700 |
| LITERATUR\|DSR0.5 | SCHAEDLICH | ohne futility | 3,6 % | 1,4 % | 0,8 % | 0,8 % | 13.408 |
| LITERATUR\|DSR0.5 | SCHAEDLICH | mit futility | 3,6 % | 1,4 % | 0,8 % | 0,8 % | 13.408 |
| LITERATUR\|DSR0.5 | WERTLOS | ohne futility | 14,3 % | 6,9 % | 3,6 % | 3,6 % | 15.765 |
| LITERATUR\|DSR0.5 | WERTLOS | mit futility | 14,3 % | 6,9 % | 3,6 % | 3,6 % | 15.765 |
| LITERATUR\|DSR0.5 | BRAUCHBAR | ohne futility | 53,8 % | 35,3 % | 23,5 % | 23,5 % | 28.241 |
| LITERATUR\|DSR0.5 | BRAUCHBAR | mit futility | 53,8 % | 35,3 % | 23,5 % | 23,5 % | 28.241 |
<!-- GEN:END tab.oc -->

Befund: In der registrierten Konfiguration ist das Tor G3 so streng, dass die Futility-Regel nichts mehr zusätzlich stoppt; wertlose Strategien bestehen G3 in <!--v:oc:registered/WERTLOS/ohne_futility/rates/passed_G3|pct2-->0,12 %<!--/v--> der Fälle (Vergleich: <!--v:oc:v2_reference|raw-->v2.0: Strategie ohne Edge bestand E1 und E2 zu etwa 89 % (EV-05)<!--/v-->). Der Preis ist geringe Teststärke: Eine brauchbare Strategie besteht G3 nur in <!--v:oc:registered/BRAUCHBAR/ohne_futility/rates/passed_G3|pct1-->2,2 %<!--/v--> der Fälle. Erst bei gelockerter DSR-Schwelle (Sensitivität SKEPTISCH mit DSR <!--v:param:P-OC-DSR-SENS/1|d1-->0,5<!--/v-->) wirkt die Regel, und zwar vor allem auf brauchbare Strategien: Deren Anteil am Endtor sinkt von <!--v:ocs:SKEPTISCH/DSR0.5/BRAUCHBAR/ohne_futility/rates/accepted_final|pct1-->9,5 %<!--/v--> auf <!--v:ocs:SKEPTISCH/DSR0.5/BRAUCHBAR/mit_futility/rates/accepted_final|pct1-->6,9 %<!--/v-->, und die mittleren Kosten je brauchbarer Strategie sinken um <!--v:ocs:SKEPTISCH/DSR0.5/BRAUCHBAR/saved_cost_eur_per_strategy|eur-->7.939 EUR<!--/v--> – eine Ersparnis, die mit verlorenen brauchbaren Strategien bezahlt wird. Der Anteil wertloser Strategien im Systembau sinkt dabei nur von <!--v:ocs:SKEPTISCH/DSR0.5/WERTLOS/ohne_futility/rates/reached_G5_build|pct1-->6,9 %<!--/v--> auf <!--v:ocs:SKEPTISCH/DSR0.5/WERTLOS/mit_futility/rates/reached_G5_build|pct1-->2,6 %<!--/v-->. EV-05 ist damit durch die strenge DSR-Schwelle gelöst, nicht durch die Futility-Regel; sie bleibt als zweite Sicherung, falls die Schwelle gelockert wird. Die Kosten bis einschließlich G3 betragen <!--v:oc:cumulative_cost_eur/BS-03|eur-->12.791 EUR<!--/v-->.

## §7 Hebel, Risiko und Kapital (Kernkapitel)

> **Betreiberfassung.** Hebel ist hier ein Ergebnis und kein Ziel: Jede Positionsgröße folgt aus dem Risikobudget und aus einer Lückenregel, die deine Tagesgrenze von <!--v:param:P-OP-DAILY-LOSS-CAP|pct0-->9 %<!--/v--> schon vor der Order einhält. Die Regel verlangt, dass die gleichzeitige ungünstige Kurslücke aller Positionen plus des bereits aufgelaufenen Tagesverlusts höchstens <!--v:calc:gap_budget|pct0-->8 %<!--/v--> beträgt, wobei Lücken über Wochenenden mit dem Faktor <!--v:param:P-RISK-WEEKEND-FACTOR|d1-->1,5<!--/v--> zählen; damit ist Brutto-Hebel über <!--v:param:P-LEV-BAND-LOW|x0-->5×<!--/v--> nur mit viel Risiko in kurzfristigen Zinsfutures erreichbar, und genau diese Kontrakte sind bei kurzer Haltedauer am teuersten. Für H10 bräuchte die Referenzstufe <!--v:calc:rate_share_H10|pct0-->50 %<!--/v--> des Risikos in Zinsen und käme im Konstruktionsstress eines Handelstags auf <!--v:calc:gap_H10|pct0-->14 %<!--/v--> Verlust, für H20 auf <!--v:calc:gap_H20|pct0-->23 %<!--/v-->; H10, H15 und H20 sind deshalb in keiner Stufe zulässig, und H5 scheitert, wo überhaupt Instrumente zugelassen sind, an der Mindestdiversifikation von <!--v:param:P-LEV-H5-MINDIV|int-->8<!--/v--> Instrumenten. Selbst mit der Lückenregel bleibt ein Restrisiko, die Grenze an einem Tag zu überschreiten (<!--v:kelly:results/H5/SYSTEM/p_day_loss_over_cap_per_year|pct1-->0,7 %<!--/v--> je Jahr in der Simulation mit Ereignissen jenseits der Konstruktion), deshalb brauchst du eine Auslegung von „niemals“ (X-OP-DLC-MODE). Für Go/No-Go heißt das: Kein Profil ist heute signierbar, ein Pilot würde nur in H5 mit halber Größe beginnen. Nächster Schritt ist die Liquidationsregel des Brokers (X-BRK-LIQ) und deine Entscheidung zu DEC-CF-02.

Details: `risk/leverage_risk_model.md`, `risk/limits.md`, `risk/margin_liquidity.md`; Rechner `risk/leverage_calculator.py`, `risk/kelly_ruin_simulator.py`, `risk/stress_test_engine.py`.

### 7.1 Definitionen (verbindlich, im Glossar)

| Größe | Definition im Paket |
|---|---|
| Konto-Brutto-Hebel L_g | Σ_i \|q_i · M_i · P_i · FX_i\| / NAV; Nominal = Multiplikator × Preis (DEC-DS-09), bei Zinsfutures der Kontraktwert laut Börse |
| Netto-Hebel L_n | \|Σ_i q_i · M_i · P_i · FX_i\| / NAV, zusätzlich je Anlageklasse und je Risikofaktor |
| Kontrakt-Hebel | Nominal / Initial Margin eines Kontrakts; nur informativ (`risk/leverage_results.json`, Feld `contract_leverage_informative`) |
| Margin-Auslastung M/E | Initial Margin / NAV, zusätzlich Maintenance Margin / NAV; Margin-Level = Guthaben beim Broker / Initial Margin (beim Broker liegt der Anteil <!--v:param:P-ECO-CASH-AT-BROKER|pct0-->25 %<!--/v--> des NAV) |
| Portfolio-Volatilität σ_p | ex ante √(wᵀΣw); Kovarianz aus EWMA und aus Schockregimen (MOD-COV) |
| VaR / ES | Konfidenz <!--v:param:P-RISK-VAR-CONF|pct0-->99 %<!--/v--> bzw. <!--v:param:P-RISK-ES-CONF|pct1-->97,5 %<!--/v-->, Horizont ein und zehn Handelstage, historisch und parametrisch mit fetten Rändern |
| Stressverlust | Verlust in % NAV je Szenario aus §7.9 (`risk/stress_scenarios.json`) |
| Lückenstress | Σ_i \|w_i\| · max(Klassenlücke_i, k · σ_Tag,i) mit k = P-GAP-K-HYP-HIGH, alle Positionen gleichzeitig ungünstig (P-LEV-CLUSTER-MODE); über Wochenenden und Feiertage × P-RISK-WEEKEND-FACTOR |

### 7.2 Zusammenhang von Hebel und Risiko

Mit dem Diversifikationsmultiplikator D und dem risikogewichteten harmonischen Mittel der Instrumentvolatilitäten σ_h gilt **L_g = D · σ_p / σ_h**. Der Rechner rechnet das Beispiel des Auftrags nach: Ohne Zinsfutures (D = <!--v:lev:masterprompt_example_check/inputs/D|d0-->2<!--/v-->, σ_h = <!--v:lev:masterprompt_example_check/inputs/sigma_h|pct0-->15 %<!--/v-->) verlangt L_g = <!--v:lev:masterprompt_example_check/inputs/Lg_low|x0-->5×<!--/v--> ein σ_p von <!--v:lev:masterprompt_example_check/D2_no_stir_sigma_h_15/sigma_p_for_Lg5|pct1-->37,5 %<!--/v--> und L_g = <!--v:lev:masterprompt_example_check/inputs/Lg_high|x0-->20×<!--/v--> eines von <!--v:lev:masterprompt_example_check/D2_no_stir_sigma_h_15/sigma_p_for_Lg20|pct0-->150 %<!--/v-->; mit einem Risikoanteil von <!--v:lev:masterprompt_example_check/inputs/stir_share|pct0-->40 %<!--/v--> in kurzfristigen Zinsfutures (σ = <!--v:lev:masterprompt_example_check/inputs/stir_sigma|pct1-->0,7 %<!--/v-->) ergibt σ_p = <!--v:lev:masterprompt_example_check/inputs/sigma_p|pct0-->10 %<!--/v--> einen Hebel von <!--v:lev:masterprompt_example_check/D2_40pct_stir_rest_15_sigma_p_10/L_g|d1-->12,2<!--/v-->. Eine gleichgerichtete Lücke von <!--v:lev:masterprompt_example_check/inputs/gap|pct0-->5 %<!--/v--> bei <!--v:lev:masterprompt_example_check/inputs/Lg_high|x0-->20×<!--/v--> Hebel vernichtet <!--v:lev:masterprompt_example_check/gap_5pct_at_20x|pct0-->100 %<!--/v--> des Kapitals.

Mit den Planwerten des Instrumentregisters (Nominal aus Spezifikation und Planpreis; Volatilität und Margin sind Annahmen bis zur Messung in G2 bzw. zur Brokerangabe X-BRK-MARGIN; historische Klassenlücken aus R4) folgt der **Hebeldeckel je Anlageklasse**: Wie viel Nominal im Verhältnis zum Kapital eine Klasse allein tragen darf, ohne dass ihre Konstruktionslücke mit dem Wochenendfaktor das Lückenbudget von <!--v:calc:gap_budget|pct0-->8 %<!--/v--> übersteigt.

<!-- GEN:BEGIN tab.class_caps -->
| Risikoklasse | Konstruktionslücke (Median) | Hebeldeckel typisch | strengstes Instrument | Hebeldeckel streng |
|---|---|---|---|---|
| AGRAR | 13,86 % | 0,38× | ZW | 0,30× |
| ANLEIHE_KURZ | 1,01 % | 5,29× | ZT | 5,29× |
| ANLEIHE_LANG | 6,93 % | 0,77× | FGBX | 0,59× |
| ANLEIHE_MITTEL | 4,09 % | 1,30× | FBTP | 1,13× |
| EDELMETALL | 18,90 % | 0,28× | PA | 0,21× |
| ENERGIE | 25,00 % | 0,21× | QG | 0,14× |
| FX | 7,00 % | 0,76× | MSF | 0,27× |
| INDUSTRIEMETALL | 15,75 % | 0,34× | MHG | 0,34× |
| KRYPTO | 44,10 % | 0,12× | MET | 0,12× |
| RENDITE | 15,75 % | 0,34× | 2YY | 0,34× |
| SOFTS | 22,05 % | 0,24× | CC | 0,19× |
| STIR | 0,84 % | 6,35× | SR1 | 6,34× |
| VIEH | 11,34 % | 0,47× | HE | 0,34× |
<!-- GEN:END tab.class_caps -->

Nur kurzfristige Zinsfutures (<!--v:lev:class_caps/STIR/standalone_cap_typical|x1-->6,4×<!--/v-->) und kurze Anleihen (<!--v:lev:class_caps/ANLEIHE_KURZ/standalone_cap_typical|x1-->5,3×<!--/v-->) tragen überhaupt Hebel über dem unteren Bandende; Energie (<!--v:lev:class_caps/ENERGIE/standalone_cap_typical|x2-->0,21×<!--/v-->) und Edelmetalle (<!--v:lev:class_caps/EDELMETALL/standalone_cap_typical|x2-->0,28×<!--/v-->) liegen weit darunter.

Mit den forschungsfähigen Instrumenten (§6.2, Datenhistorie) erreicht in keiner Kapitalstufe irgendein Profil seine Hebelobergrenze (<!--v:calc:calib_research_feasible|int-->0<!--/v--> erreichbare Zellen), weil SOFR-, €STR- und Eurex-Kontrakte zu wenig Historie haben. Die folgende Kalibrierung ist deshalb **hypothetisch**: Sie nimmt alle handelbaren Zinskontrakte ohne Kosten- und Historienfilter (Universum U-HANDELBAR) und zeigt, was ein Hebel im Band kosten würde, wenn diese Kontrakte erforscht wären:

<!-- GEN:BEGIN tab.leverage_calibration -->
| Kapital (Mio. EUR) | Profil | Zins-Risikoanteil | L_g | Lückenstress | mittlere Kosten (Sharpe/Jahr) | Verlustbudget |
|---|---|---|---|---|---|---|
| 0,25 | H5 | 41 % | 5,1× | 7,3 % | 0,512 | über Budget |
| 0,25 | H10 | 53 % | 10,2× | 12,5 % | 0,646 | über Budget |
| 0,25 | H15 | 59 % | 15,1× | 17,4 % | 0,714 | über Budget |
| 0,25 | H20 | 63 % | 20,1× | 22,2 % | 0,758 | über Budget |
| 0,5 | H5 | 41 % | 5,1× | 7,3 % | 0,512 | über Budget |
| 0,5 | H10 | 53 % | 10,2× | 12,5 % | 0,646 | über Budget |
| 0,5 | H15 | 59 % | 15,1× | 17,4 % | 0,714 | über Budget |
| 0,5 | H20 | 63 % | 20,1× | 22,2 % | 0,758 | über Budget |
| 1 | H5 | 45 % | 5,1× | 7,3 % | 0,492 | über Budget |
| 1 | H10 | 58 % | 10,1× | 12,2 % | 0,618 | über Budget |
| 1 | H15 | 65 % | 15,0× | 16,9 % | 0,687 | über Budget |
| 1 | H20 | 71 % | 20,1× | 21,4 % | 0,745 | über Budget |
| 5 | H5 | 37 % | 5,0× | 8,6 % | 0,396 | über Budget |
| 5 | H10 | 50 % | 10,0× | 13,8 % | 0,527 | über Budget |
| 5 | H15 | 59 % | 15,2× | 18,7 % | 0,617 | über Budget |
| 5 | H20 | 65 % | 20,1× | 23,2 % | 0,677 | über Budget |
| 25 | H5 | 45 % | 5,1× | 7,3 % | 0,476 | über Budget |
| 25 | H10 | 58 % | 10,1× | 12,2 % | 0,606 | über Budget |
| 25 | H15 | 65 % | 15,0× | 16,9 % | 0,676 | über Budget |
| 25 | H20 | 71 % | 20,1× | 21,4 % | 0,736 | über Budget |
| 100 | H5 | – | – | – | – | kein Basis- oder Zinsuniversum |
| 100 | H10 | – | – | – | – | kein Basis- oder Zinsuniversum |
| 100 | H15 | – | – | – | – | kein Basis- oder Zinsuniversum |
| 100 | H20 | – | – | – | – | kein Basis- oder Zinsuniversum |
<!-- GEN:END tab.leverage_calibration -->

Befund: Schon H5 über Zinsen verlangt in der Referenzstufe <!--v:lev:leverage_calibration_via_rates/5000000/H5/rate_risk_share|pct0-->37 %<!--/v--> Zinsrisiko, liegt mit <!--v:lev:leverage_calibration_via_rates/5000000/H5/gap_loss_design|pct1-->8,6 %<!--/v--> Lückenstress an einem Handelstag und dem <!--v:param:P-RISK-WEEKEND-FACTOR|d1-->1,5<!--/v-->-Fachen über Wochenenden über dem Budget von <!--v:calc:gap_budget|pct0-->8 %<!--/v--> und kostet bei der geforderten Haltedauer <!--v:lev:leverage_calibration_via_rates/5000000/H5/mean_cost_sr|d2-->0,40<!--/v--> Sharpe-Einheiten im Jahr, H20 sogar <!--v:lev:leverage_calibration_via_rates/5000000/H20/mean_cost_sr|d2-->0,68<!--/v-->. Das ist ein Vielfaches jeder plausiblen Bruttokante (§6.3).

### 7.3 Hebelprofile

<!-- GEN:BEGIN tab.profiles -->
| Profil | Obergrenze L_g | σ-Ziel p. a. | M/E höchstens | ES-Limit (97,5 %, 1 Tag) | Mindestdiversifikation | zulässig in (Variante, Mio. EUR) |
|---|---|---|---|---|---|---|
| H5 | 5× | 6 % (Obergrenze; mindestens 3 %) | 25 % | 2 % | 8 | keine |
| H10 | 10× | 9 % | 35 % | 3 % | 8 | keine |
| H15 | 15× | 12 % | 45 % | 4 % | 10 | keine |
| H20 | 20× | 15 % | 50 % | 5 % | 10 | keine |
<!-- GEN:END tab.profiles -->

Die Profilgrenze ist eine Obergrenze. **Betriebsband:** Die natürlichen Allokationen bleiben in der Simulation die ganze Zeit unter <!--v:param:P-LEV-BAND-LOW|x0-->5×<!--/v-->, weil die Lückenregel das Risiko früher begrenzt als der Hebel:

<!-- GEN:BEGIN tab.band -->
| Variante | Profil | Zeitanteil L_g = 0 | unter dem Band | im Band | an der Profilgrenze |
|---|---|---|---|---|---|
| U-KOSTEN | H5 | 14,1 % | 100,0 % | 0,0 % | 0,0 % |
| U-KOSTEN | H20 | 15,8 % | 100,0 % | 0,0 % | 0,0 % |
| U-BREAKEVEN | H5 | 2,0 % | 100,0 % | 0,0 % | 0,0 % |
| U-BREAKEVEN | H20 | 2,7 % | 100,0 % | 0,0 % | 0,0 % |
| U-KOSTEN-TFD1-7T | H5 | 1,9 % | 100,0 % | 0,0 % | 0,0 % |
| U-KOSTEN-TFD1-7T | H20 | 1,9 % | 100,0 % | 0,0 % | 0,0 % |
| U-KOSTEN-TFD1 | H5 | 0,0 % | 100,0 % | 0,0 % | 0,0 % |
| U-KOSTEN-TFD1 | H20 | 0,0 % | 100,0 % | 0,0 % | 0,0 % |
<!-- GEN:END tab.band -->

**Kein Zwangshebel:** L_g darf bis auf null fallen (P-OP-LEV-MIN). Ein erzwungener Mindesthebel wird nur auf signierte Betreiberanweisung modelliert; seine Folgen zeigt die Allokation WUNSCHHEBEL in §7.4 und §7.9.

### 7.4 Pflichtrechnungen je Profil

1. **Kelly unter Parameterunsicherheit.** σ* = S, g(σ) ≈ σ·S − σ²/2, Nullwachstum bei σ = 2·S, gerechnet über die Prior-Verteilung von S. Für die registrierte Allokation in H5 liegt das volle Kelly-σ bei <!--v:kelly:results/H5/SYSTEM/kelly/sigma_star_full_kelly|pct1-->9,9 %<!--/v-->; H5 entspricht <!--v:kelly:results/H5/SYSTEM/kelly/kelly_fraction_of_profile|pct0-->45 %<!--/v--> davon, und die Wahrscheinlichkeit negativen Wachstums beträgt <!--v:kelly:results/H5/SYSTEM/kelly/p_growth_negative|pct0-->17 %<!--/v-->. Die Alternative TF-D1 läuft mit <!--v:kelly:results/H5/ALTERNATIVE_TFD1/kelly/kelly_fraction_of_profile|pct0-->5 %<!--/v--> des vollen Kelly-σ, weil die Lückenregel bindet. Für WUNSCHHEBEL ist die erwartete Netto-Sharpe-Ratio negativ (<!--v:kelly:results/H20/WUNSCHHEBEL/sr_prior/mean|d2-->-0,97<!--/v--> in H20); jedes σ > 0 senkt dort das Wachstum.
2. **Verteilungen** (fette Ränder t(<!--v:param:P-SIM-T-DF|d0-->4<!--/v-->), Volatilitätsregime, Sprünge, Ereignisse jenseits der Konstruktion; Ruin = Verlust ≥ <!--v:param:P-RISK-RUIN|pct0-->50 %<!--/v--> oder Zwangsliquidation):

<!-- GEN:BEGIN tab.kelly -->
| Profil | Allokation | σ_p | E[Netto-Sharpe] | Jahresrendite Median | max. Drawdown 5 J (95 %) | P(DD ≥ 20 %) | P(Ruin 5 J) | P(Tag > 9 %) je Jahr |
|---|---|---|---|---|---|---|---|---|
| H5 | SYSTEM | 4,5 % | 0,096 | 0,5 % | 17,5 % | 0,7 % | 0,00 % | 0,66 % |
| H5 | WUNSCHHEBEL | 6,0 % | -0,527 | -3,5 % | 23,9 % | 33,4 % | 0,00 % | 1,44 % |
| H5 | ALTERNATIVE_TFD1 | 2,5 % | 0,478 | 1,4 % | 9,8 % | 0,0 % | 0,00 % | 0,42 % |
| H5 | SYSTEM_OHNE_LEITER | 4,5 % | 0,096 | 0,7 % | 18,7 % | 3,3 % | 0,00 % | 0,66 % |
| H10 | SYSTEM | wie H5/SYSTEM |  |  |  |  |  |  |
| H10 | WUNSCHHEBEL | 9,0 % | -0,764 | -6,7 % | 30,0 % | 84,3 % | 0,00 % | 0,84 % |
| H10 | ALTERNATIVE_TFD1 | wie H5/ALTERNATIVE_TFD1 |  |  |  |  |  |  |
| H15 | SYSTEM | wie H5/SYSTEM |  |  |  |  |  |  |
| H15 | WUNSCHHEBEL | 12,0 % | -0,898 | -10,4 % | 30,4 % | 97,5 % | 0,00 % | 0,56 % |
| H15 | ALTERNATIVE_TFD1 | wie H5/ALTERNATIVE_TFD1 |  |  |  |  |  |  |
| H20 | SYSTEM | wie H5/SYSTEM |  |  |  |  |  |  |
| H20 | WUNSCHHEBEL | 15,0 % | -0,972 | -12,4 % | 30,8 % | 99,8 % | 0,00 % | 0,34 % |
| H20 | ALTERNATIVE_TFD1 | wie H5/ALTERNATIVE_TFD1 |  |  |  |  |  |  |
<!-- GEN:END tab.kelly -->

<!-- GEN:BEGIN tab.kelly_dd -->
| Profil | Allokation | max. DD 1 J (Median / 95 %) | 3 J | 5 J | P(DD ≥ 10 %) | P(DD ≥ 20 %) | P(DD ≥ 30 %) | P(DD ≥ 50 %) | Erholung Median (Handelstage) | P(Handelsstopp 5 J) | ES 97,5 % Jahresrendite |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H5 | SYSTEM | 4,2 / 9,4 % | 7,5 / 14,5 % | 9,9 / 17,5 % | 49,6 % | 0,7 % | 0,0 % | 0,0 % | 238 | 0,0 % | -9,8 % |
| H5 | WUNSCHHEBEL | 7,2 / 13,8 % | 14,2 / 21,3 % | 18,3 / 23,9 % | 95,4 % | 33,4 % | 0,1 % | 0,0 % | 283 | 0,1 % | -17,4 % |
| H5 | ALTERNATIVE_TFD1 | 1,9 / 4,4 % | 3,3 / 7,8 % | 3,9 / 9,8 % | 4,6 % | 0,0 % | 0,0 % | 0,0 % | 195 | 0,0 % | -6,0 % |
| H5 | SYSTEM_OHNE_LEITER | 4,0 / 9,2 % | 7,3 / 15,1 % | 9,4 / 18,7 % | 46,2 % | 3,3 % | 0,0 % | 0,0 % | 222 | 0,0 % | -11,1 % |
| H10 | WUNSCHHEBEL | 11,0 / 18,2 % | 20,1 / 25,6 % | 23,4 / 30,0 % | 99,9 % | 84,3 % | 5,2 % | 0,0 % | 312 | 5,2 % | -23,3 % |
| H15 | WUNSCHHEBEL | 14,9 / 22,2 % | 23,2 / 29,6 % | 27,5 / 30,4 % | 100,0 % | 97,5 % | 25,9 % | 0,0 % | 206 | 25,9 % | -28,6 % |
| H20 | WUNSCHHEBEL | 17,2 / 23,4 % | 25,6 / 30,2 % | 30,0 / 30,8 % | 100,0 % | 99,8 % | 58,1 % | 0,0 % | 485 | 58,1 % | -28,7 % |
<!-- GEN:END tab.kelly_dd -->

3. **Kurslücken und 4. Margin-Pfade** in der Referenzstufe (<!--v:param:P-RISK-STRESS-REF-STAGE|mio-->5 Mio. EUR<!--/v-->):

<!-- GEN:BEGIN tab.gaps -->
| Variante | Profil | σ_p erreicht | L_g | Lücke historisch | Lücke 5 σ | Lücke 10 σ | Konstruktionslücke | M/E Basis / +50 % / +100 % | zulässig |
|---|---|---|---|---|---|---|---|---|---|
| U-KOSTEN | H5 | 5,7 % | 0,33× | 5,0 % | 2,5 % | 5,0 % | 5,3 % | 2,5 / 3,7 / 4,9 % | nein |
| U-KOSTEN | H10 | 5,7 % | 0,33× | 5,0 % | 2,5 % | 5,0 % | 5,3 % | 2,5 / 3,7 / 4,9 % | nein |
| U-KOSTEN | H15 | 5,7 % | 0,33× | 5,0 % | 2,5 % | 5,0 % | 5,3 % | 2,5 / 3,7 / 4,9 % | nein |
| U-KOSTEN | H20 | 5,7 % | 0,33× | 5,0 % | 2,5 % | 5,0 % | 5,3 % | 2,5 / 3,7 / 4,9 % | nein |
| U-BREAKEVEN | H5 | 4,5 % | 0,30× | 5,1 % | 2,4 % | 4,9 % | 5,3 % | 2,3 / 3,4 / 4,5 % | nein |
| U-BREAKEVEN | H10 | 4,5 % | 0,30× | 5,1 % | 2,4 % | 4,9 % | 5,3 % | 2,3 / 3,4 / 4,5 % | nein |
| U-BREAKEVEN | H15 | 4,5 % | 0,30× | 5,1 % | 2,4 % | 4,9 % | 5,3 % | 2,3 / 3,4 / 4,5 % | nein |
| U-BREAKEVEN | H20 | 4,5 % | 0,30× | 5,1 % | 2,4 % | 4,9 % | 5,3 % | 2,3 / 3,4 / 4,5 % | nein |
| U-KOSTEN-TFD1-7T | H5 | 4,5 % | 0,30× | 5,1 % | 2,4 % | 4,9 % | 5,3 % | 2,3 / 3,4 / 4,5 % | nein |
| U-KOSTEN-TFD1-7T | H10 | 4,5 % | 0,30× | 5,1 % | 2,4 % | 4,9 % | 5,3 % | 2,3 / 3,4 / 4,5 % | nein |
| U-KOSTEN-TFD1-7T | H15 | 4,5 % | 0,30× | 5,1 % | 2,4 % | 4,9 % | 5,3 % | 2,3 / 3,4 / 4,5 % | nein |
| U-KOSTEN-TFD1-7T | H20 | 4,5 % | 0,30× | 5,1 % | 2,4 % | 4,9 % | 5,3 % | 2,3 / 3,4 / 4,5 % | nein |
| U-KOSTEN-TFD1 | H5 | 2,5 % | 0,43× | 4,2 % | 2,2 % | 4,3 % | 5,3 % | 1,8 / 2,8 / 3,7 % | nein |
| U-KOSTEN-TFD1 | H10 | 2,5 % | 0,43× | 4,2 % | 2,2 % | 4,3 % | 5,3 % | 1,8 / 2,8 / 3,7 % | nein |
| U-KOSTEN-TFD1 | H15 | 2,5 % | 0,43× | 4,2 % | 2,2 % | 4,3 % | 5,3 % | 1,8 / 2,8 / 3,7 % | nein |
| U-KOSTEN-TFD1 | H20 | 2,5 % | 0,43× | 4,2 % | 2,2 % | 4,3 % | 5,3 % | 1,8 / 2,8 / 3,7 % | nein |
<!-- GEN:END tab.gaps -->

5. **Zulässigkeit.** Ein Profil ist nur zulässig, wenn es sein σ-Ziel unter der Lückenregel zu mindestens <!--v:param:P-LEV-SIGMA-TOLERANCE|pct0-->90 %<!--/v--> erreicht (H5: mindestens <!--v:param:P-LEV-H5-SIGMA-MIN|pct0-->3 %<!--/v--> σ), die Mindestdiversifikation erfüllt und M/E auch nach einer Margin-Erhöhung um <!--v:param:P-MRG-STRESS-2|pct0-->100 %<!--/v--> unter der Profilgrenze bleibt. Die vollständige Zellentabelle (Variante × Stufe × Profil) steht in `risk/leverage_risk_model.md`.

### 7.5 Limits-Hierarchie

Ebenen Konto → Strategie → Anlageklasse → Instrument → Korrelationscluster. Als harte Grenzen im Register stehen Tagesverlust (Leiter), Wochenverlust, Drawdown (Leiter), Lückenstress, Brutto-Hebel, Margin-Auslastung und Margin-Level, Expected Shortfall, Risikobudget je Strategie, Hebeldeckel je Klasse, Liquidität (Order ≤ <!--v:param:P-RISK-MAX-ADV-SHARE|pct0-->1 %<!--/v--> des Tagesvolumens, Position ≤ <!--v:param:P-RISK-MAX-OI-SHARE|pct1-->0,5 %<!--/v--> des Open Interest), Haltedauer, Verfall, Ereignissperren, Preiskorridor, Höchstmenge und Nachrichtenrate. Netto-Hebel, VaR und σ_p werden gemessen und berichtet, aber nicht als eigene Grenze geführt, weil Lückenregel, Expected Shortfall und Brutto-Hebel früher binden; einen Monatsverlust deckt die Drawdown-Leiter ab; die Clustergrenze ist nur informativ (P-LEV-CLUSTER-MODE), weil die Lückenregel ohnehin Korrelation eins annimmt. **Tagesverlust-Leiter** (vom Tagesbeginn um <!--v:param:P-RISK-DAY-START|raw-->00:00 Europe/Berlin<!--/v-->, P-RISK-DAY-START): bei <!--v:param:P-RISK-DL-L1|pct0-->3 %<!--/v--> Risikoziel halbieren, bei <!--v:param:P-RISK-DL-L2|pct0-->5 %<!--/v--> Einstiegssperre, bei <!--v:param:P-RISK-DL-L3|pct1-->6,5 %<!--/v--> geordneter Abbau. **Drawdown-Leiter** vom Höchststand: <!--v:param:P-RISK-DD-L1|pct0-->10 %<!--/v--> Risikoziel um ein Viertel senken; <!--v:param:P-RISK-DD-L2|pct0-->15 %<!--/v--> Risikoziel halbieren und Profilabstieg; <!--v:param:P-RISK-DD-L3|pct0-->20 %<!--/v--> Einstiegssperre und Betreiberprüfung; <!--v:param:P-RISK-DD-KILL|pct0-->30 %<!--/v--> Abbau und Stopp. Kill-Switch storniert alle offenen Orders in höchstens <!--v:param:P-RISK-KILL-CANCEL-S|d0-->5<!--/v--> Sekunden und stellt optional geordnet glatt. Pre-Trade- und Post-Trade-Kontrollen: `execution/pretrade_controls.md`. Alle Limits mit Wertverweis: `registers/limits.json`, Beschreibung `risk/limits.md`.

### 7.6 Intraday-Risiko

P&L, Margin und Limits laufen während der Handelszeiten in Echtzeit im Risikomotor und unabhängig im Prüfmodul. Ob die Tagesverlust-Leiter vor einer Brokerliquidation greift, hängt vom Guthaben beim Broker ab (§7.7). Über Wochenenden und Feiertage wird der Lückenstress mit dem Faktor <!--v:param:P-RISK-WEEKEND-FACTOR|d1-->1,5<!--/v--> bewertet; weil alle Strategien außer S-IM über Wochenenden halten, rechnet die Planung die Größenregel dauerhaft mit diesem Faktor (konservativ; ein Abbau vor Wochenenden mit größeren Positionen unter der Woche ist nicht modelliert); vor registrierten Ereignissen (Notenbanktermine, Verfall, wichtige Berichte) gibt es <!--v:param:P-RISK-EVENT-BLACKOUT-MIN|d0-->30<!--/v--> Minuten lang keine neuen Einstiege. Handelsaussetzungen und Preislimits sind Zustände des Datenautomaten (SM-DATAFEED: HALTED, LIMIT_LOCKED; Trace TR-DATA-004), negative Preise lässt der Dezimaltyp aller Verträge zu, und der Fall SC-H-2020WTI ist gerechnet; Energie-Frontmonate werden <!--v:param:P-UNI-ENERGY-EXPIRY-DAYS|d0-->7<!--/v--> Geschäftstage vor dem letzten Handelstag nicht gehalten.

### 7.7 Margin- und Liquiditätsmanagement (EV-09)

Die Liquidationsregel des Primärbrokers für Futures ist nicht belegt (X-BRK-LIQ); geplant wird mit einem Stop-out bei <!--v:param:P-MRG-BROKER-STOPOUT|pct0-->50 %<!--/v--> der Initial-Margin (ANNAHME in Anlehnung an die CFD-Regel, SRC-REG-ESMA-CFD). Für Privatkunden mit Sitz in Deutschland muss die Nachschusspflicht bei Futures vertraglich ausgeschlossen sein (SRC-REG-BAFIN-FUT); gilt das für dein Konto (Kundeneinstufung beim Broker, X-BRK-NACHSCHUSS), stellt der Broker glatt, bevor ein negativer Saldo entsteht. Die eigene De-Risking-Schwelle liegt bei einem Margin-Level von <!--v:param:P-MRG-DERISK-TRIGGER|pct0-->150 %<!--/v-->; die Größenrechnung nutzt immer die Übernacht-Margin, nie die Intraday-Margin des Brokers (P-MRG-USE-INTRADAY). Nachschüsse dauern <!--v:param:P-MRG-TOPUP-DAYS|d0-->2<!--/v--> Geschäftstage; das Szenario „Nachschuss unmöglich“ ist in der Tabelle der Margin-Pfade enthalten.

<!-- GEN:BEGIN tab.margin -->
| Allokation | Profil | M/E (Anteil NAV) | M/E +100 % | Margin-Level am Broker ohne Verlust | Margin-Level nach schlimmstem Szenario | Verlust bis De-Risking-Schwelle (Margin +100 %) | Verlust bis Stop-out (Margin +100 %) | nötiger Anteil beim Broker | Anteil beim Broker reicht | Szenarien mit Liquidation |
|---|---|---|---|---|---|---|---|---|---|---|
| MON-HARM (MH-R1) | schädlich, wahre Sharpe -0,2 | über 120 Monate | 0,0 % (Pilot) | 0,0 % (24 M) | 2,7 % (60 M) |
| MON-HARM (MH-R1) | stark schädlich (Harm-Screen), wahre Sharpe -1,0 | 68 Monate | 0,0 % (Pilot) | 0,6 % (24 M) | 41,0 % (60 M) |
| MON-HARM (MH-R1) | wertlos, wahre Sharpe 0,0 | über 120 Monate | 0,0 % (Pilot) | 0,0 % (24 M) | 1,1 % (60 M) |
| MON-HARM (MH-R1) | brauchbar, wahre Sharpe 0,3 | über 120 Monate | 0,0 % (Pilot) | 0,0 % (24 M) | 0,0 % (60 M) |
| MON-DRIFT (MD-R3) | Volatilität ×1,0 | über 252 Handelstage | 2,0 % (20 T) | 2,6 % (63 T) | 6,6 % (252 T) |
| MON-DRIFT (MD-R3) | Volatilität ×1,5 | 104 Handelstage | 3,9 % (20 T) | 19,0 % (63 T) | 93,2 % (252 T) |
| MON-DRIFT (MD-R3) | Volatilität ×2,0 | 47 Handelstage | 13,0 % (20 T) | 76,8 % (63 T) | 100,0 % (252 T) |
<!-- GEN:END tab.margin -->

Befund: Maßgeblich ist das Guthaben beim Broker (<!--v:param:P-ECO-CASH-AT-BROKER|pct0-->25 %<!--/v--> des NAV), denn Verluste werden dort abgerechnet und das Kapital außerhalb hilft erst nach einer Überweisung. Für die registrierte Allokation SYSTEM reicht dieser Anteil in <!--v:calc:stress_margin/SYSTEM/insufficient|int-->4<!--/v--> von <!--v:calc:stress_margin/SYSTEM/profiles|int-->4<!--/v--> Profilen nicht ganz: Nötig wären bis zu <!--v:calc:stress_margin/SYSTEM/required_max|pct1-->25,5 %<!--/v-->, getrieben vom Nickel-Szenario, in dem eine Handelsaussetzung den Abbau verhindert. Für die Zins-kalibrierte Allokation mit Wunschhebel reicht er in <!--v:calc:stress_margin/WUNSCHHEBEL/insufficient|int-->3<!--/v--> von <!--v:calc:stress_margin/WUNSCHHEBEL/profiles|int-->4<!--/v--> Profilen nicht (nötig bis <!--v:calc:stress_margin/WUNSCHHEBEL/required_max|pct0-->48 %<!--/v-->), und in <!--v:calc:stress_margin/WUNSCHHEBEL/with_liquidation|int-->1<!--/v--> von <!--v:calc:stress_margin/WUNSCHHEBEL/profiles|int-->4<!--/v--> Profilen käme es in einzelnen Szenarien zur Brokerliquidation. Regel: Vor jedem Grant liegt beim Broker mindestens der für das Profil nötige Anteil (Spalte „nötiger Anteil beim Broker“); ein Nachschuss wird nötig, wenn das Level unter die Schwelle fällt und der Abbau ausgesetzt ist. Liquiditätssteuerung: Beim Broker liegen <!--v:param:P-ECO-CASH-AT-BROKER|pct0-->25 %<!--/v--> des Kapitals, der Rest in Geldmarkt oder kurzlaufenden Staatsanleihen; Währungssalden werden täglich in EUR zurückgeführt (`risk/margin_liquidity.md`).

### 7.8 Hebel-Stufenleiter

Der Pilot beginnt immer in H5 mit <!--v:param:P-LEV-PILOT-SIZE|pct0-->50 %<!--/v--> des Risikoziels (DEC-DS-02). Ein Aufstieg um genau eine Stufe verlangt mindestens <!--v:param:P-LEV-STEP-MIN-DAYS|d0-->90<!--/v--> Handelstage in der Stufe, keine Limitverletzung, gemessene Kosten höchstens <!--v:param:P-LEV-STEP-COST-BAND|pct0-->25 %<!--/v--> über dem Modell, realisierte Volatilität höchstens <!--v:param:P-LEV-STEP-VOL-BAND|pct0-->30 %<!--/v--> neben dem Ziel und keine schweren Incidents, dazu die doppelte Freigabe durch Betreiber und unabhängige Risikofunktion (X-ORG-RISK, DEC-CF-06). Die Bedingungen stehen als Wächter im Automaten SM-LEVERAGE; bei einer harten Limitverletzung erfolgt der Abstieg automatisch (Trace TR-LEV-003). Weil H10 bis H20 unzulässig sind, endet die Leiter im heutigen Stand bei H5.

### 7.9 Stresstests

`risk/stress_test_engine.py` rechnet <!--v:calc:stress_scenarios_total|int-->21<!--/v--> Szenarien aus `risk/stress_scenarios.json` (alle historischen und hypothetischen Pflichtszenarien des Auftrags einschließlich Zinsschock) für drei Allokationen: SYSTEM (registrierte Familie mit der großzügigen Kostenregel), ALTERNATIVE TF-D1 und WUNSCHHEBEL (Hebel über Zinsen auf die Profilgrenze kalibriert). Werte in % NAV nach Tages- und Drawdown-Leiter im Tagesraster: Die Stufen L1, L2 und DD-L1 bis DD-L3 wirken am Folgetag mit den Faktoren aus P-RISK-LADDER-FACTORS (dieselbe Regel wie in der Kelly/Ruin-Simulation, `lib/calc.py`), L3 und die Kill-Stufe bauen sofort ab; Tagesbewegungen gelten als Lücken und werden nicht gekappt. Fehlende Klassenbewegungen ersetzt der Motor durch <!--v:param:P-RISK-STRESS-SUBST-SHARE|pct0-->50 %<!--/v--> der ungünstigsten Tageslücke der Klasse, fehlende Mehrtagesbewegungen durch die Tagesbewegung × √<!--v:param:P-RISK-STRESS-MULTI-DAYS|d0-->3<!--/v--> (Status ERSATZWERT). ⚠ markiert eine Verletzung der <!--v:param:P-OP-DAILY-LOSS-CAP|pct0-->9 %<!--/v-->-Grenze.

<!-- GEN:BEGIN tab.stress -->
| ID | Szenario | SYSTEM H5 | ALTERNATIVE TF-D1 H5 | WUNSCHHEBEL H5 | WUNSCHHEBEL H10 | WUNSCHHEBEL H15 | WUNSCHHEBEL H20 |
|---|---|---|---|---|---|---|---|
| SC-H-1987 | Aktiencrash 19.10.1987 | 4,4 % | 2,9 % | 8,1 % | 7,4 % | 10,2 % ⚠ | 12,8 % ⚠ |
| SC-H-1994 | Anleihecrash 1994 | 4,4 % | 3,7 % | 5,6 % | 8,3 % | 7,9 % | 9,7 % ⚠ |
| SC-H-1998 | LTCM/Russland 1998 | 4,4 % | 5,3 % | 6,2 % | 7,5 % | 10,3 % ⚠ | 12,9 % ⚠ |
| SC-H-2008 | Finanzkrise Herbst 2008 | 3,4 % | 3,7 % | 7,1 % | 11,9 % ⚠ | 16,4 % ⚠ | 20,7 % ⚠ |
| SC-H-2010 | Flash Crash 06.05.2010 | 3,8 % | 3,4 % | 3,2 % | 4,4 % | 5,1 % | 5,9 % |
| SC-H-2015 | SNB-Mindestkursaufgabe 15.01.2015 | 2,9 % | 4,6 % | 6,3 % | 6,7 % | 9,0 % ⚠ | 11,2 % ⚠ |
| SC-H-2018 | Volatilitätsschock Februar 2018 | 4,4 % | 3,6 % | 4,4 % | 5,6 % | 6,6 % | 7,4 % |
| SC-H-2020 | März 2020 | 5,1 % | 3,9 % | 7,8 % | 11,5 % | 7,7 % | 9,0 % ⚠ |
| SC-H-2020WTI | Negativer WTI-Preis 20.04.2020 | 4,4 % | 3,7 % | 6,8 % | 6,7 % | 9,0 % ⚠ | 11,2 % ⚠ |
| SC-H-2022NI | LME-Nickel März 2022 | 20,4 % ⚠ | 3,7 % | 6,8 % | 6,7 % | 9,0 % ⚠ | 11,2 % ⚠ |
| SC-H-2022GILT | UK-Gilts Herbst 2022 | 4,4 % | 3,4 % | 6,8 % | 6,7 % | 9,0 % ⚠ | 11,2 % ⚠ |
| SC-H-2023 | Bankenstress März 2023 | 4,4 % | 3,6 % | 7,2 % | 7,1 % | 9,6 % ⚠ | 12,0 % ⚠ |
| SC-H-2025 | Zollschock April 2025 | 3,6 % | 2,8 % | 3,7 % | 4,9 % | 5,9 % | 6,8 % |
| SC-X-CORR1 | Korrelationen → 1 | 1,5 % | 1,3 % | 2,0 % | 3,0 % | 3,9 % | 4,8 % |
| SC-X-LIQ | Liquiditätsausfall | 1,0 % | 0,9 % | 1,5 % | 2,3 % | 3,0 % | 3,7 % |
| SC-X-BROKER | Ausfall von Broker oder FCM | 2,2 % | 1,9 % | 3,0 % | 4,5 % | 5,9 % | 7,1 % |
| SC-X-EXCH | Ausfall einer Börse | 1,2 % | 0,8 % | 0,5 % | 1,0 % | 1,5 % | 2,1 % |
| SC-X-DATA | Datenausfall | 0,5 % | 0,4 % | 0,7 % | 1,0 % | 1,3 % | 1,6 % |
| SC-X-GAP5 | Kurslücke 5 σ | 2,4 % | 2,2 % | 3,4 % | 5,1 % | 6,6 % | 7,9 % |
| SC-X-GAP10 | Kurslücke 10 σ | 4,9 % | 4,3 % | 6,7 % | 10,1 % ⚠ | 13,1 % ⚠ | 15,9 % ⚠ |
| SC-X-RATESHOCK | Zinsschock (Zinswende) auf die Zinsfutures-Allokation | 0,0 % | 0,5 % | 5,7 % | 10,5 % | 8,9 % | 11,9 % ⚠ |
<!-- GEN:END tab.stress -->

<!-- GEN:BEGIN tab.stress_summary -->
| Allokation | Profil | L_g | M/E | schlimmstes Szenario | Verlust mit Leiter | Szenarien > 9 % am Tag | Liquidationen |
|---|---|---|---|---|---|---|---|
| ALTERNATIVE_TFD1 | H10 | 0,4× | 1,8 % | SC-H-1998 | 5,3 % | 0 | 0 |
| ALTERNATIVE_TFD1 | H15 | 0,4× | 1,8 % | SC-H-1998 | 5,3 % | 0 | 0 |
| ALTERNATIVE_TFD1 | H20 | 0,4× | 1,8 % | SC-H-1998 | 5,3 % | 0 | 0 |
| ALTERNATIVE_TFD1 | H5 | 0,4× | 1,8 % | SC-H-1998 | 5,3 % | 0 | 0 |
| SYSTEM | H10 | 0,3× | 2,3 % | SC-H-2022NI | 20,4 % | 1 | 0 |
| SYSTEM | H15 | 0,3× | 2,3 % | SC-H-2022NI | 20,4 % | 1 | 0 |
| SYSTEM | H20 | 0,3× | 2,3 % | SC-H-2022NI | 20,4 % | 1 | 0 |
| SYSTEM | H5 | 0,3× | 2,3 % | SC-H-2022NI | 20,4 % | 1 | 0 |
| WUNSCHHEBEL | H10 | 10,0× | 6,4 % | SC-H-2008 | 11,9 % | 2 | 0 |
| WUNSCHHEBEL | H15 | 15,2× | 8,6 % | SC-H-2008 | 16,4 % | 9 | 0 |
| WUNSCHHEBEL | H20 | 20,1× | 10,7 % | SC-H-2008 | 20,7 % | 12 | 2 |
| WUNSCHHEBEL | H5 | 5,0× | 4,0 % | SC-H-1987 | 8,1 % | 0 | 0 |
<!-- GEN:END tab.stress_summary -->

Befund: Die registrierte Allokation verletzt die Grenze im Nickel-Szenario (<!--v:stress:results/SYSTEM/H5/worst_scenario|raw-->SC-H-2022NI<!--/v-->: <!--v:stress:results/SYSTEM/H5/worst_loss_with_ladder|pct1-->20,4 %<!--/v-->), weil die Handelsaussetzung den Abbau durch die Leiter verhindert (Feld halt im Szenario; die Bewegung ist konservativ auf Industriemetalle übertragen). Die Alternative TF-D1 bleibt überall innerhalb (schlimmstes Szenario <!--v:stress:results/ALTERNATIVE_TFD1/H5/worst_loss_with_ladder|pct1-->5,3 %<!--/v-->). WUNSCHHEBEL H20 verletzt die Grenze in <!--v:calc:stress_breaches/WUNSCHHEBEL/H20|int-->12<!--/v--> Szenarien (schlimmstes <!--v:stress:results/WUNSCHHEBEL/H20/worst_loss_with_ladder|pct1-->20,7 %<!--/v-->). Brokerliquidationen treten in der registrierten Allokation in <!--v:calc:stress_margin/SYSTEM/with_liquidation|int-->0<!--/v--> und bei WUNSCHHEBEL in <!--v:calc:stress_margin/WUNSCHHEBEL/with_liquidation|int-->1<!--/v--> von <!--v:calc:stress_margin/WUNSCHHEBEL/profiles|int-->4<!--/v--> Profilen ein. Im Brokerausfall (SC-X-BROKER) ist zusätzlich das Guthaben beim Broker (<!--v:param:P-ECO-CASH-AT-BROKER|pct0-->25 %<!--/v--> des NAV) bis zur Klärung nicht verfügbar; es steht getrennt vom Marktverlust in den Ergebnissen.

### 7.10 Risikoakzeptanz des Betreibers

Vor jedem Grant signierst du ein Risikoprofil mit Klartextzahlen (X-OP-RISK-ACCEPT, Vorlage in `governance/grants_and_risk_acceptance.md`). Gefüllt mit den Rechenwerten der registrierten Allokation in H5 und der Referenzstufe würde es lauten: „Mit einer Wahrscheinlichkeit von fünf Prozent verlieren Sie innerhalb von drei Jahren in der Spitze mindestens <!--v:kelly:results/H5/SYSTEM/max_drawdown/3/p95|pct1-->14,5 %<!--/v--> (<!--v:calc:mdd_eur/H5/SYSTEM/3/p95|eur-->726.701 EUR<!--/v-->); im Szenario <!--v:stress:results/SYSTEM/H5/worst_scenario|raw-->SC-H-2022NI<!--/v--> beträgt der Verlust <!--v:stress:results/SYSTEM/H5/worst_loss_with_ladder|pct1-->20,4 %<!--/v--> (<!--v:calc:stress_eur/SYSTEM/H5|eur-->1.020.588 EUR<!--/v-->).“ Weil dieses Profil nicht zulässig ist, ist diese Signatur heute nicht vorgesehen; ohne Signatur gibt es keinen Grant.

### 7.11 Neue Risiken im Risikoregister

Kurslücken bei hohem Hebel (RK-01), Margin-Erhöhungen (RK-02), Zwangsliquidation (RK-03), Zusammenbruch von Korrelationen (RK-04), Konzentration in Zinsfutures und Zinswende (RK-05), Betreiberverhalten nach Verlusten (RK-06), Modellrisiko der Kovarianzschätzung (RK-07), dazu die Überschreitung der Tagesgrenze trotz Größenregel (RK-29) und Wochenendrisiko (RK-25). Das vollständige Register mit <!--v:calc:risks_total|int-->32<!--/v--> Risiken steht in `registers/risk_register.json`.

## §8 Ausführung und Handelsinfrastruktur

> **Betreiberfassung.** Orders laufen ausschließlich über MT5 zu einem Futures-Broker; als einziger Kandidat ist FXFlat per Primärquelle zugleich als MT5-Anbieter börsengehandelter Futures und als deutscher Broker belegt, AvaFutures ist Zweitkandidat. Die MT5-Python-Schnittstelle hat drei harte Eigenschaften, die das OMS auffangen muss: keine Ereignisse, keine eigene Client-Order-ID und unklare Zeitstempel; eine Wiederholung nach Zeitüberschreitung ohne Abgleich könnte deshalb eine Doppelorder erzeugen. Bevor irgendetwas gebaut wird, laufen im Demokonto und in einem kleinen Echtgeldkonto die Killer-Tests KT-01 bis KT-16; jeder hat ein Orakel und eine Rückfallvariante. Fällt der serverseitige Schutzstopp (KT-06) durch, ist Halten über Nacht und damit dein Haltehorizont nicht vertretbar. Für Go/No-Go heißt das: Ohne bestandene Killer-Tests kein Systembau. Nächster Schritt: Kontozugang und die Broker-Bestätigungen X-BRK-ACCOUNT bis X-BRK-DEMO.

Details: `execution/oms_ems.md`, `execution/broker_killer_tests.md`, `execution/tca_model.md`, `execution/pretrade_controls.md`.

### 8.1 OMS/EMS

Der Order-Lebenszyklus ist als Zustandsautomat mit Traces geführt (SM-ORDER, SM-POSITION, übernommen aus v2.0 und auf MT5 angepasst). Neu in v3.0:

- **Parent- und Child-Orders:** Eine Absicht des Portfoliomotors ist eine Parent-Order; ab <!--v:param:P-EXE-ALGO-THRESHOLD|d0-->10<!--/v--> Kontrakten wird sie in Child-Orders im Abstand von mindestens <!--v:param:P-EXE-ALGO-INTERVAL-S|d0-->60<!--/v--> Sekunden zerlegt (zeitgesteuert im Liquiditätsfenster).
- **Algo-Orders** laufen im eigenen EMS; MT5 bietet dafür nichts Eigenes.
- **Kalenderspreads** bietet MT5 nicht als eine Order; gerollt wird als Schließen plus Eröffnen (DEC-DS-12), und wegen der Höchsthaltedauer wird eine Position im Rollfenster in der Regel geschlossen statt gerollt.
- **Mehrere Strategien auf einem Konto:** Das Konto läuft im Hedging-Modus (laut Broker), das OMS nettet aber intern und hält je Instrument genau eine Brokerposition (DEC-DS-11); jede Strategie hat eine virtuelle Teilposition, und Fills werden nach Absicht zugeordnet.
- **Netting und Zuordnung:** Gegenläufige Absichten verschiedener Strategien werden intern gekreuzt; an den Markt geht nur die Differenz, die interne Kreuzung wird zum Mittelkurs verbucht.

### 8.2 Broker und FCM

Nach BQ-08 und BQ-08a nur MT5. Kandidaten mit Stand der Recherche (`registers/source_register.json`):

| Kandidat | Status | Belegt | Offen |
|---|---|---|---|
| FXFlat (FXFlat Bank GmbH, BaFin) | Primärkandidat (DEC-DS-16) | MT5 mit Eurex und CME (Kurse via CQG), Hedging, All-in-Kommission <!--v:costreg:COST-COMM-FXFLAT-LOW|eur2-->0,80 EUR<!--/v--> bis <!--v:costreg:COST-COMM-FXFLAT|eur2-->1,00 EUR<!--/v--> je Kontrakt und Seite, Intraday-Margin rund <!--v:param:P-MRG-INTRADAY-FXFLAT|pct0-->10 %<!--/v--> der Börsenmargin (SRC-BRK-FXFLAT) | Kontraktliste, Übernacht-Margins, Nachschussausschluss, Python/EA-Erlaubnis, Futures im Demo, Stop-out-Regel (X-BRK-*) |
| AvaFutures (AVA Trade EU Ltd) | Zweitkandidat | MT5 für Futures im Netting-Modus, CME/Eurex/Euronext (SRC-BRK-AVA) | Zusatzbedingungen für deutsche Privatkunden, Margins, Python-Erlaubnis |
| AMP Futures | nur technische Referenz | beste Dokumentation der MT5-Futures-Semantik (SRC-BRK-AMP) | Annahme deutscher Kunden, Nachschussregel; Rechtsprüfung vor jeder Nutzung |
| Just2Trade, StoneX, TradePro, ITG | nicht geeignet belegt | MT5-Futures vorhanden (SRC-BRK-J2T, SRC-BRK-STONEX, SRC-BRK-TRADEPRO, SRC-BRK-ITG) | Annahme deutscher Privatkunden |

Clearing-Broker oder FCM mit FIX, Drop-Copy und Give-up betreffen B3 und B4, die nach BQ-02 ausgeschlossen sind; die Adapterschnittstelle bleibt brokerneutral (`architecture/interfaces.md`). Due Diligence je Broker: Segregation der Kundengelder und Einlagensicherung, Insolvenzrisiko (Szenario SC-X-BROKER), Kosten, API-Erlaubnis, Kontenarten, Produktfreigaben und der vertragliche Ausschluss der Nachschusspflicht (SRC-REG-BAFIN-FUT). Der CFD-Rückfallpfad bleibt abgeschaltet, bis du ihn freigibst (X-OP-CFD, DEC-CF-05); die Kosten zeigt `financials/economic_model.md`.

### 8.3 Frühe Killer-Tests (EV-06)

In BS-01, direkt nach dem Kontozugang und vor jeder weiteren Entwicklung, laufen die Killer-Tests im Demokonto und – nur wo das Demo nichts beweist – mit Minimalgröße im Echtgeldkonto. Themen: Symbol- und Kontoeigenschaften, Zeitstempel, Ordersemantik und Wiederholung nach Zeitüberschreitung, serverseitiger Schutzstopp, Modify-Semantik, Preisbänder und Tageslimits (besonders Agrar), Teilausführungen, Stopps bei Limit-Moves, Rollen ohne Kalenderspread, Wiederverbindung und Korrekturen, Kommissionen, Orderfrequenz und die Unterscheidung von Demo und Echtgeld. Orakel, Rückfallvariante und Abbruchfolge je Test: `execution/broker_killer_tests.md`.

### 8.4 Ausführung und Transaktionskostenanalyse

Gemessen werden Implementation Shortfall gegenüber dem Entscheidungskurs und Slippage gegenüber dem Ankunftskurs, je Fill und je Parent-Order. Das Modell (MOD-SLIP) besteht aus halbem Spread, Schlupf in Ticks und Marktwirkung abhängig von Ordergröße gegenüber Tagesvolumen; das Handelsfenster ist das Liquiditätsfenster je Instrument aus dem Referenzdatendienst. Der laufende Vergleich von Messung und Modell speist die gepoolte Kostendrift-Überwachung (§14.2): Liegen die wahren Kosten genau auf der Auslöseschwelle (<!--v:drift:results/pooled/AN_SCHWELLE/true_ratio|d1-->1,3<!--/v-->-fach), löst sie im Median nach <!--v:drift:results/pooled/AN_SCHWELLE/median_months|d0-->5<!--/v--> Monaten aus, bei <!--v:drift:results/pooled/FAKTOR_1_5/true_ratio|d1-->1,5<!--/v-->-fachen Kosten nach <!--v:drift:results/pooled/FAKTOR_1_5/median_months|d0-->1<!--/v--> Monat; ohne Drift gibt es im Pilot in <!--v:drift:results/pooled/OHNE_DRIFT/p_trigger_within_pilot|pct1-->3,7 %<!--/v--> der Läufe einen Fehlalarm (`execution/tca_model.md`).

### 8.5 Pre-Trade-Kontrollen und Kill-Switch

Ausgerichtet an MiFID II Art. 17 und der Delegierten Verordnung (EU) 2017/589, auch wenn sie für das Eigenkonto nicht anwendbar sind: Preiskorridor (<!--v:param:P-PTC-COLLAR-SIGMA|d1-->0,5<!--/v--> σ_Tag um einen Kurs, der höchstens <!--v:param:P-EXE-QUOTE-MAX-AGE-S|d0-->5<!--/v--> Sekunden alt ist), Höchstmenge je Order (Zielabweichung aus dem Risikomotor und höchstens <!--v:param:P-RISK-MAX-ADV-SHARE|pct0-->1 %<!--/v--> des Tagesvolumens), Höchstnominal je Order (<!--v:param:P-PTC-NOTIONAL-SHARE-OF-CAP|pct0-->25 %<!--/v--> der Profilobergrenze), Nachrichtendrosselung (<!--v:param:P-PTC-MSG-PER-MIN|d0-->30<!--/v--> sendende Aufrufe je Minute), Duplikaterkennung (<!--v:param:P-PTC-DUP-WINDOW-S|d0-->60<!--/v--> Sekunden), Lückenregel, Haltedauer, Handelszeiten, Ereignissperre und Moduskontrolle Demo/Echtgeld. Der Kill-Switch storniert alle Orders in höchstens <!--v:param:P-RISK-KILL-CANCEL-S|d0-->5<!--/v--> Sekunden und stellt optional geordnet glatt; er wird in jedem Quartal im Demokonto geprobt (`operations/drills.md`). Kontrollen PTC-01 bis PTC-14: `execution/pretrade_controls.md`.

### 8.6 Rollen, Verfall, Lieferung

First Notice Day und Last Trading Day stehen versioniert im Referenzdatendienst. Keine neuen Einstiege <!--v:param:P-UNI-ROLL-DAYS|d0-->5<!--/v--> Geschäftstage vor FND bzw. LTD; Positionen im Rollfenster werden geschlossen (Aktion ROLL_AS_CLOSE), Liefervermeidung eskaliert an den Betreiber, bevor der Broker selbst glattstellt. Sonderfälle: negative Preise (Energie-Frontmonat <!--v:param:P-UNI-ENERGY-EXPIRY-DAYS|d0-->7<!--/v--> Geschäftstage vor LTD nicht halten), Tageslimits und Limit-Moves (Stopps können nicht ausführen; Lückenregel rechnet damit), Handelsaussetzungen und Stornierungen durch die Börse (Nickel 2022, SRC-STRESS-E2022-LME-NICKEL) sowie ein nicht laufendes MT5-Terminal im Lieferfenster (Heartbeat und Alarm, RK-18).

### 8.7 Aus v2.0 übernommen und erweitert

Persistenz vor Netzwerk (SQLite im WAL-Modus mit `synchronous=FULL`, SRC-SQLITE-WAL), UNKNOWN mit Negativnachweis, Deduplizierung (Deal-Tickets statt execId), Abgleich mit Snapshot-Höchstalter <!--v:param:P-EXE-SNAPSHOT-MAX-S|d0-->60<!--/v--> Sekunden, genau ein Writer mit Lease (<!--v:param:P-EXE-LEASE-S|d0-->15<!--/v--> Sekunden) und Fencing, Notfalljournal – jeweils übernommen aus v2.0 und auf MT5 und Mehrstrategiebetrieb erweitert. Weil MT5 keine Client-Order-ID kennt, trägt jede Order eine Strategie- und Absichtskennung in `magic` und eine gekürzte Command-ID in `comment`; ob der Broker `comment` verändert, prüft KT-05. Einstiege werden nie wiederholt; ein UNKNOWN wird über `history_orders_get` und `history_deals_get` geklärt (erste Abfragen nach <!--v:param:P-EXE-UNKNOWN-POLL-S/0|d0-->5<!--/v-->, <!--v:param:P-EXE-UNKNOWN-POLL-S/1|d0-->15<!--/v--> und <!--v:param:P-EXE-UNKNOWN-POLL-S/2|d0-->60<!--/v--> Sekunden).

## §9 Daten

> **Betreiberfassung.** Für Forschung und Kostenmessung braucht das System Intraday-Historie mit verfallenen Kontrakten; der günstigste belegte Weg ist ein einmaliger Kauf bei Kibot mit Abgleich gegen CQG Data Factory für ausgewählte Märkte (<!--v:cost:fixed_costs/historical_data_once_eur|eur-->3.477 EUR<!--/v--> einmalig). Die Lizenzen erlauben nur interne Nutzung und keine Weitergabe; Kursrohdaten gehen deshalb nie an den Sprachmodellanbieter, Hermes sieht nur abgeleitete Kennzahlen (DEC-CF-07). Offen und für die Wirtschaftlichkeit wichtig ist, ob der automatisierte Handel als Non-Display-Nutzung gilt; das würde die Marktdatenkosten auf <!--v:cost:fixed_costs/market_data_monthly_eur/NON_DISPLAY_MANAGED/monthly_eur|eur-->1.568 EUR<!--/v--> bis <!--v:cost:fixed_costs/market_data_monthly_eur/NON_DISPLAY_USER/monthly_eur|eur-->2.441 EUR<!--/v--> im Monat heben (X-DATA-ND). Für Go/No-Go heißt das: Daten sind kein Hindernis für Demo und Forschung, die Non-Display-Frage kann aber einen Echtgeldbetrieb weiter verschlechtern. Nächster Schritt ist die Lizenzprüfung vor dem Kauf (X-DATA-LIC).

Details: `data/data_plan.md`, `data/vendor_matrix.md`, `data/proxy_rules.md`, `data/reference_data_spec.md`.

### 9.1 Anbieter

Auswahlmatrix mit Datum und Status in `data/vendor_matrix.md`: Kibot (Intraday seit 2009 für die CME-Gruppe einschließlich verfallener Kontrakte, einmalig <!--v:costreg:COST-HIST-KIBOT|d0-->820<!--/v--> USD, nur interne Nutzung; SRC-HIST-KIBOT), CQG Data Factory (Tick- und Minutendaten je Markt und Monat; Lizenz nicht geprüft; SRC-HIST-CQG-DATA-FACTORY), Databento (nutzungsbasiert, Eurex und ICE ab 2018; AGB nicht geprüft; SRC-HIST-DATABENTO), FirstRate Data (erlaubt KI-Nutzung abgeleiteter Ergebnisse, nicht der Rohdaten; SRC-HIST-FIRSTRATE-DATA), Norgate (nur Tagesdaten, für Kostenanalyse ungeeignet; SRC-HIST-NORGATE-DATA) und Tick Data LLC (Preis auf Anfrage; SRC-HIST-TICK-DATA-LLC). Für Eurex liefert Kibot keine Historie; dafür ist der CQG-Abgleich für <!--v:costreg:COST-HIST-EUREX-MARKETS|d0-->7<!--/v--> Eurex-Märkte über <!--v:costreg:COST-HIST-CQG-MONTHS|d0-->24<!--/v--> Monate eingeplant. Live-Kurse kommen über das MT5-Terminal des Brokers (CQG-Anbindung bei FXFlat).

Lizenzregeln: Forschung und automatisierter Handel nur im Rahmen der geprüften Lizenz (X-DATA-LIC); Speicherung unveränderlich mit Hash; **keine Weitergabe an LLM-Anbieter** – Hermes erhält nur Kennzahlen, Metadaten und Berichte, die aus den Daten abgeleitet sind (Arbeitsregel bis zur rechtlichen Prüfung, SRC-HIST-KIBOT, SRC-HIST-FIRSTRATE-DATA).

### 9.2 Datenmodell

Punktgenaue Daten (point-in-time) mit Zeitstempel in UTC und Quelle; Kontrakt-Metadaten mit Gültigkeitsdatum. Rollkalender je Kontrakt aus FND und LTD; fortlaufende Reihen für Signale werden rückwärts per Differenz angepasst (P-DATA-CONT-ADJUST), weil Verhältnisanpassung bei Preisen nahe null verzerrt; P&L, Kosten und Stops rechnen immer auf Einzelkontrakten. Referenzdaten (Tick, Multiplikator, Gebühren, Margins, Handels- und Liquiditätszeiten) sind versioniert mit Gültigkeitsdatum; das Schema steht in `data/reference_data_spec.md`, die Werte mit Quelle und Abrufdatum in `registers/instruments.json`.

### 9.3 Qualität

Regeln und Service-Levels: Datenlücken im Liquiditätsfenster über <!--v:param:P-DATA-GAP-MAX-MIN|d0-->15<!--/v--> Minuten machen den Handelstag des Instruments ungültig; Live-Kurse gelten nach <!--v:param:P-DATA-STALE-S|d0-->10<!--/v--> Sekunden ohne Aktualisierung als veraltet (SM-DATAFEED). Revisionen des Anbieters werden <!--v:param:P-DATA-REVISION-DAYS|d0-->5<!--/v--> Geschäftstage lang übernommen, danach ist der Datensatz eingefroren. Der Abgleich zweier Quellen verlangt Übereinstimmung auf <!--v:param:P-DATA-XCHECK-TOL-TICKS|d0-->1<!--/v--> Tick in mindestens <!--v:param:P-DATA-XCHECK-SHARE-MIN|pct0-->99 %<!--/v--> der Balken. Ablage unveränderlich mit Hash; der Holdout (<!--v:param:P-RES-HOLDOUT-YEARS|d0-->2<!--/v--> Jahre) ist versiegelt und wird genau einmal geöffnet (übernommen aus v2.0).

### 9.4 Proxy-Regel

Siehe §6.5 und `data/proxy_rules.md`.

## §10 Softwarearchitektur und Engineering

> **Betreiberfassung.** Die Software besteht aus einem deterministischen Kern, der in Backtest, Paper und Echtgeld derselbe ist, einem Ereignisjournal, aus dem sich jeder Zustand nachrechnen lässt, und drei getrennten Vertrauensbereichen. Der Geldpfad läuft auf deinem Windows-VPS, weil die MT5-Python-Schnittstelle Windows verlangt; Forschung mit KI und das unabhängige Prüfmodul laufen auf eigenen kleinen Linux-Instanzen. Sprache ist Python, Datenhaltung SQLite im WAL-Modus; ein Message-Broker, Microservices oder eine eigene Hochfrequenz-Infrastruktur sind bei stündlichen Entscheidungen unnötig. Jeder Build ist reproduzierbar und signiert, jede Komponente hat Ziele für Wiederanlauf und Datenverlust. Für Go/No-Go heißt das: Die Architektur trägt Demo, Paper und einen Pilot; sie ist kein Engpass. Nächster Schritt ist die Entscheidung über die Aufteilung der Vertrauensbereiche (X-INF-ZONES, DEC-CF-04).

Details: `architecture/system_design.md`, `architecture/interfaces.md`, `architecture/state_machines.json`, `architecture/threat_model.md`.

### 10.1 Architektur

Verträge zwischen Komponenten sind JSON Schema 2020-12 (dasselbe Format wie alle Register dieses Pakets; menschenlesbar, mit der Paketprüfung prüfbar); Protobuf bringt bei lokaler Kopplung und stündlicher Frequenz keinen Vorteil. Backtest, Paper und Echtgeld nutzen denselben Kern mit austauschbaren Adaptern (Simulationsbroker, MT5-Demo, MT5-Echtgeld) und injizierter Uhr. Jede Entscheidung ist ein Ereignis im Journal (Event Sourcing); Zustände entstehen nur durch Anwenden von Ereignissen, und das Prüfmodul kann sie unabhängig nachrechnen.

### 10.2 Technologieentscheidung

| Bereich | Entscheidung | verworfen |
|---|---|---|
| Sprache Kern und Forschung | Python (Versionen 3.11 bis 3.13 in CI) | Rust oder C++ (unnötig bei stündlicher Frequenz, höhere Bau- und Prüfkosten); MQL5 als Kern (nicht in CI testbar, Bindung an eine Plattform) |
| Journal und Zustand | SQLite im WAL-Modus mit `synchronous=FULL` (SRC-SQLITE-WAL) | PostgreSQL (zusätzlicher Betrieb ohne Mehrwert für einen Writer) |
| Forschungsdaten | spaltenorientierte Dateien mit Hash in der Forschungszone | Datenbankserver |
| Messaging | Prozessintern; zwischen Zonen HTTPS mit gegenseitiger Authentifizierung über WireGuard | Kafka, RabbitMQ (Komplexität ohne Nutzen) |
| Deployment | Geldpfad als Windows-Dienst auf dem VPS, Forschung/KI und Prüfmodul als Linux-Dienste | Container auf dem Geldpfad (MT5-Terminal braucht Windows-Desktop-Umgebung) |
| Make-or-Buy | eigener schlanker Kern; Frameworks als Referenz und Testorakel (DEC-DS-22, `implementation/make_or_buy.md`) | NautilusTrader, LEAN, pysystemtrade als Laufzeitbasis (keine MT5-Anbindung) |

### 10.3 Umgebungen und Lieferkette

DEV (lokal), TEST (CI mit Simulationsbroker), UAT (Demokonto mit Wiedergabe), PAPER (Demokonto vorwärts, G7), PROD (Echtgeldkonto ab G8). Konfiguration ist Code und Teil des Releases; Releases sind signiert, Builds reproduzierbar (Lock-Datei mit Hashes), jedes Release hat eine Stückliste (SBOM) und Herkunftsnachweise nach dem Vorbild von SLSA; Abhängigkeiten werden vor jedem Release auf bekannte Schwachstellen geprüft. Kritische Sicherheitsupdates binnen <!--v:param:P-SEC-PATCH-CRIT-D|d0-->14<!--/v--> Tagen.

### 10.4 Qualitätssicherung

Unit-, Eigenschafts-, Simulations-, Integrations-, Broker-Zertifizierungs- (Killer-Tests), Last-, Dauer-, Chaos- und Fehlerinjektionstests; Mutationstests für den Geldpfad (mindestens <!--v:param:P-QA-MUTATION-MIN|pct0-->80 %<!--/v--> erkannte Mutanten, Zweigabdeckung mindestens <!--v:param:P-QA-COVERAGE-MIN|pct0-->90 %<!--/v-->); statische Analyse ohne Warnungen; CI über mehrere Python-Versionen mit Warnungen als Fehler (EV-12). Der Testkatalog `implementation/test_catalog.json` enthält <!--v:calc:tests_total|int-->151<!--/v--> Tests mit Prozedur, Orakel und Bestehenskriterium; <!--v:calc:tests_by_exec/IM_PAKET|int-->40<!--/v--> davon laufen schon heute in der Paketprüfung, die übrigen in der genannten Baustufe, beim Broker oder im Betrieb. Die <!--v:calc:requirements_total|int-->113<!--/v--> Anforderungen in `requirements.json` nennen je mindestens einen Test; ihr Status folgt aus dem Ausführungsort dieser Tests, nicht aus einer Selbstauskunft.

<!-- GEN:BEGIN tab.tests_summary -->
| Ausführung | Tests | Ebenen |
|---|---|---|
| im Paket ausgeführt | 40 | MUTATION 1, SIMULATION 3, STATIC 17, UNIT 19 |
| Killer-Tests beim Broker (BS-01) | 17 | BROKER_CERT 16, INTEGRATION 1 |
| Abnahme im Systembau | 79 | CHAOS 1, FAULT_INJECTION 5, INTEGRATION 24, LOAD 2, MUTATION 1, PROPERTY 5, SECURITY 17, SIMULATION 9, STATIC 4, UNIT 11 |
| Drills, Dauerläufe, Messungen im Betrieb | 15 | CHAOS 1, DRILL 10, INTEGRATION 1, SIMULATION 1, SOAK 2 |
<!-- GEN:END tab.tests_summary -->

<!-- GEN:BEGIN tab.requirements_summary -->
| Bereich | Anforderungen | im Paket nachgewiesen | teilweise | nur spezifiziert |
|---|---|---|---|---|
| Wirtschaft | 6 | 6 | 0 | 0 |
| Forschung | 10 | 6 | 4 | 0 |
| Risiko | 14 | 4 | 8 | 2 |
| Ausführung | 19 | 0 | 13 | 6 |
| Pre-Trade | 4 | 0 | 3 | 1 |
| Daten | 6 | 0 | 3 | 3 |
| Architektur | 11 | 2 | 2 | 7 |
| Sicherheit | 8 | 0 | 2 | 6 |
| KI-Schicht | 9 | 2 | 4 | 3 |
| ML-Komponenten | 2 | 0 | 2 | 0 |
| Governance | 7 | 3 | 3 | 1 |
| Betrieb | 8 | 4 | 0 | 4 |
| Recht und Steuern | 2 | 1 | 0 | 1 |
| Qualitätssicherung | 3 | 0 | 1 | 2 |
| Paket | 4 | 4 | 0 | 0 |
<!-- GEN:END tab.requirements_summary -->

### 10.5 Hochverfügbarkeit und Wiederherstellung

Aktiv-Passiv mit Fencing: Eine kalte Ersatzinstanz wird erst Writer, wenn die alte Anmeldung nachweislich abgewiesen wird (Wechsel des Hauptpassworts, KT-16). Ohne gültige Lease sendet der Kern nichts; offene Positionen schützen die Stopps beim Broker, der externe Monitor alarmiert (Befund aus v2.0). Ziele: Journal-Kopie mindestens alle <!--v:param:P-OPS-RPO-JOURNAL-MIN|d0-->5<!--/v--> Minuten, Wiederherstellung des Geldpfads in <!--v:param:P-OPS-RTO-CORE-H|d0-->4<!--/v--> Stunden, normaler Wiederanlauf in <!--v:param:P-OPS-RESTART-S|d0-->120<!--/v--> Sekunden; Restoreprobe alle <!--v:param:P-OPS-RESTORE-DRILL-D|d0-->30<!--/v--> Tage. Alle Daten liegen in der EU (X-INF-VPS).

### 10.6 Beobachtbarkeit

Metriken, strukturierte Logs und eine durchgehende Korrelationskennung von der Absicht über die Order bis zum Deal; SLOs in `operations/sla_slo.md` (Verfügbarkeit des Geldpfads in Handelszeiten <!--v:param:P-SLO-CORE-AVAIL|pct1-->99,5 %<!--/v-->). Zwei unabhängige Alarmwege über einen externen Monitor; der KI-Agent ist nie Alarmweg.

### 10.7 Bedienung

Das Cockpit zeigt Risiko, Hebel, Margin, Limits, Positionen, Orders und Incidents; Echtgeld und Paper sind in jeder Ansicht farblich, textlich und über getrennte Instanzen unterschieden. Freigaben mit Handels- oder Governancewirkung brauchen eine zweite, menschliche Freigabe (§13). Die mobile Notfallansicht kann nur pausieren, Orders stornieren und abbauen, nie Risiko erhöhen.

## §11 KI-Schicht

> **Betreiberfassung.** Hermes arbeitet als Assistent für Forschung, Code-Entwürfe, Datenprüfung, Incident-Sichtung und Berichte, aber nie im Geldpfad: Er hat keinen Brokerzugang, keine Freigaberechte und keinen Zugriff auf den versiegelten Holdout. Er läuft über dein Nous-Portal-Abo mit harter Monatsgrenze, und das System funktioniert ohne ihn vollständig (Stufe H0). Weil das Upstream-Projekt sehr schnell ändert – im Mittel ein Release alle <!--v:r5:hermes_upstream/release_frequency/mean_interval_days|d1-->5,6<!--/v--> Tage –, wird eine Version gepinnt und nur nach bestandener Evaluationssuite aktualisiert; die Pflege ist als Betreiberzeit eingerechnet. Bleibt der gemessene Nutzen <!--v:param:P-AI-ROLLBACK-QUARTERS|d0-->2<!--/v--> Quartale in Folge negativ, wird der Agent zurückgebaut. Für Go/No-Go heißt das: Die KI-Schicht ändert am Befund nichts; sie ist optional und begrenzt. Nächster Schritt ist die Klärung der Datenverarbeitung beim Anbieter (X-AI-DPA).

Details: `ai/ai_layer.md`, `ai/hermes_integration.md`, `ai/eval_suite_spec.md`, `ai/mrm_policy.md`.

### 11.1 Rollen der Agenten

Hermes (NousResearch/hermes-agent, MIT-Lizenz, SRC-HERMES-UPSTREAM) ist gepinnter Kandidat; neueste Version am 24.09.2026: <!--v:r5:hermes_upstream/latest_release_2026_09_24/version|raw-->v0.21.5<!--/v--> (Tag <!--v:r5:hermes_upstream/latest_release_2026_09_24/tag|raw-->v2026.9.24<!--/v-->). Bewertete Alternativen: kein Agent (H0), ein allgemeiner Coding-Agent nur für den Bau unter Review (COST-AI-CODING-AGENT) und Hermes. Aufgaben: Forschungsassistenz, Code-Entwürfe unter Review, Datenqualitätsprüfung und Anomalie-Erklärung, Incident-Triage, Berichte, Dokumentation und Wissensregister (`ai/ai_layer.md`).

### 11.2 Technische Grenzen (übernommen aus v2.0)

Kein Brokerzugang, keine Freigaberechte, kein Zugriff auf den Holdout; Zugang zum Modellanbieter nur über ein LLM-Gateway mit Kanarienprüfung; Forschungsjobs in einer Sandbox ohne Netz (höchstens <!--v:param:P-AI-JOB-MAX-H|d0-->4<!--/v--> Stunden, ein Job gleichzeitig); Egress nur über Allowlist; Konfiguration, Skills und Hooks schreibgeschützt. Die Grenzen wirken über Netz und Dateisystem, nicht über Einstellungen des Agenten (SRC-HERMES-SECURITY, SRC-HERMES-CONFIG, SRC-HERMES-EGRESS).

### 11.3 Upstream-Management (EV-10)

Belegt (Stand 24.09.2026): <!--v:r5:hermes_upstream/release_frequency/releases_in_window|int-->36<!--/v--> Releases in <!--v:r5:hermes_upstream/release_frequency/span_days_first_to_last|d0-->196<!--/v--> Tagen, davon <!--v:r5:hermes_upstream/release_frequency/releases_last_30_days|int-->7<!--/v--> in den letzten dreißig Tagen; Minor-Releases im Mittel alle <!--v:r5:hermes_upstream/release_frequency/minor_mean_interval_days|d1-->9,1<!--/v--> Tage; auch Patch-Releases umfassen teils Tausende Commits (SRC-HERMES-UPSTREAM). `hermes update` folgt dem Hauptzweig und hebt Pins auf (SRC-HERMES-UPDATE, SRC-HERMES-ISSUE-34514) und ist deshalb verboten. Update-Politik: höchstens ein reguläres Update je <!--v:param:P-AI-UPDATE-MIN-DAYS|d0-->30<!--/v--> Tage, Sicherheitskorrekturen binnen <!--v:param:P-SEC-PATCH-CRIT-D|d0-->14<!--/v--> Tagen, immer nur nach Evaluationssuite mit mindestens <!--v:param:P-AI-EVAL-PASS|pct0-->95 %<!--/v--> bestandenen Fällen und ohne Verschlechterung der Regeltreue. Pflegeaufwand <!--v:param:P-AI-UPDATE-EFFORT-H|d0-->3<!--/v--> Stunden je Update (Annahme), in der Betreiberzeit enthalten.

### 11.4 Nutzenmessung mit Rückbaukriterium

Quartalsweise: Nettozeitgewinn gegen eine Basislinie ohne Agent, Annahmequote der Vorschläge (mindestens <!--v:param:P-AI-ACCEPT-MIN|pct0-->50 %<!--/v-->), Fehlerquote und Kosten. Die Abo-Kosten stehen in der Wirtschaftsrechnung als eigene Zeile (<!--v:cost:fixed_costs/ai_subscription_monthly_eur/SUPER|eur2-->87,63 EUR<!--/v--> im Monat), mit harter Monatsgrenze <!--v:param:P-AI-MONTHLY-BUDGET-EUR|eur-->350 EUR<!--/v--> für KI und Coding-Agent. Negative Bilanz über <!--v:param:P-AI-ROLLBACK-QUARTERS|d0-->2<!--/v--> Quartale → Rückbau auf H0.

### 11.5 Maschinelles Lernen im Signal- oder Größenpfad

Nur deterministische, versionierte, validierte Modelle, nie Sprachmodelle; Modellrisikomanagement nach dem Vorbild von SR 11-7 (SRC-LIT-SR11-7): Inventar (`registers/model_inventory.json`), Dokumentation, unabhängige Validierung, Drift-Überwachung, Erklärbarkeit und Rückfall auf die Regel. Hürden: Vorregistrierung, DSR mindestens <!--v:param:P-AI-ML-DSR-MIN|d2-->0,95<!--/v-->, PBO höchstens <!--v:param:P-RES-PBO-MAX|pct0-->20 %<!--/v-->, Mehrwert nach Kosten mindestens <!--v:param:P-AI-ML-UPLIFT-MIN|d2-->0,10<!--/v--> Sharpe-Einheiten gegenüber der Regel. Ohne Bestehen wird verzichtet und der Verzicht begründet (`ai/mrm_policy.md`).

### 11.6 KI-Regulierung und Datenschutz

Die Anwendbarkeit der KI-Verordnung (EU) 2024/1689 und der DSGVO prüft nach BQ-03 die externe Person (SRC-REG-AIACT, SRC-REG-DSGVO, beide nicht geprüft). Technisch gilt unabhängig davon: keine personenbezogenen Daten, keine Secrets und keine lizenzierten Rohdaten an den Modellanbieter; Region, Speicherung und Training auf Kundendaten des Anbieters sind vor der ersten Nutzung mit nicht öffentlichen Daten zu klären (X-AI-DPA).

## §12 Sicherheit

> **Betreiberfassung.** Das wertvollste Schutzgut ist das Guthaben beim Broker; deshalb kann keine Systemkomponente Geld auszahlen, und nur ein Teil des Kapitals liegt überhaupt beim Broker. Betrachtet werden fünf Angreifer: externe Angreifer, Innentäter, ein kompromittierter KI-Agent, eine vergiftete Lieferkette und die Übernahme des Brokerkontos; jeder hat einen Angriffsbaum mit Gegenmaßnahmen und Tests. Freigaben brauchen einen Hardware-Schlüssel, Geldpfad, Forschung/KI und Prüfmodul sind getrennte Vertrauensbereiche, und vor dem ersten Echtgeld gibt es einen externen Penetrationstest. Ein einzelner Windows-VPS ohne Trennung wäre möglich, aber schwächer; die Folgen stehen in DEC-CF-04. Für Go/No-Go heißt das: Ohne bestandenen Penetrationstest und ohne Hardware-Schlüssel kein Pilot. Nächster Schritt ist die Beschaffung von zwei Hardware-Schlüsseln und die Klärung der Broker-Zugänge (X-BRK-API).

Details: `architecture/threat_model.md`, `security/security_architecture.md`, `security/key_management.md`.

- **Bedrohungsmodell:** Angreifer extern, Innentäter (einschließlich Bedienfehler), kompromittierter Agent, Lieferkette, Übernahme des Brokerkontos; Angriffsbäume, Gegenmaßnahmen und Tests T-SEC-* in `architecture/threat_model.md`.
- **Identitäten und Schlüssel:** Hardware-Schlüssel nach FIDO2 für Freigaben und Anmeldungen (<!--v:costreg:COST-INF-KEYS|eur-->120 EUR<!--/v--> für zwei Schlüssel), signierte Betreiberaktionen mit Gültigkeit <!--v:param:P-SEC-SIG-EXPIRY-MIN|d0-->15<!--/v--> Minuten, Rotation der Credentials alle <!--v:param:P-SEC-CRED-ROTATION-D|d0-->90<!--/v--> Tage und nach jedem Host-Wechsel, Break-glass-Zugang und Hinterlegung gegen das Schlüsselpersonenrisiko (`security/key_management.md`).
- **Broker:** Die vom System genutzte MT5-Anmeldung kann nicht auszahlen; Auszahlungen laufen nur über das Kundenportal des Brokers mit eigener Zwei-Faktor-Anmeldung des Betreibers. Getrennte Zugänge für Handel (Geldpfad), Lesen (Prüfmodul und Monitor, soweit der Broker einen Lesezugang bietet) und Betreiber; ob der Broker IP-Allowlists anbietet, ist offen (X-BRK-API).
- **Netz:** getrennte Vertrauensbereiche für Geldpfad, Forschung/KI und Prüfmodul; Zero Trust mit WireGuard und gegenseitiger TLS-Authentifizierung; kein öffentlich erreichbarer Fernzugang zum Geldpfad.
- **Betrieb:** Secrets-Scanning, zentrale Protokollauswertung mit Alarmregeln (SIEM im kleinen Maßstab), Penetrationstest vor Echtgeld (<!--v:costreg:COST-EXT-PENTEST|eur-->5.000 EUR<!--/v-->), Incident-Response-Plan (`operations/runbooks.md`).
- **Orientierung:** ISO/IEC 27001 und BSI IT-Grundschutz als Gliederung der Maßnahmen; DORA (SRC-REG-DORA) beträfe nur B3/B4, die nach BQ-02 ausgeschlossen sind.

## §13 Governance, Organisation und Freigaben

> **Betreiberfassung.** Du bist nach BQ-09 die einzige Person, die zwischen Demo und Echtgeld schalten darf, und das bleibt so. Der Auftrag verlangt zusätzlich ein menschliches Vier-Augen-Prinzip und eine unabhängige Risikofunktion; eine zweite KI-Instanz zählt dafür nicht. Das Paket löst den Konflikt (DEC-CF-06) mit einer externen Risikofunktion, die lesen und Profilaufstiege blockieren, aber nicht handeln kann, und mit einer Notfallvertretung, die nur abbauen darf. Ohne diese zweite Person ist der Pilot (G8) gesperrt, ohne die Risikofunktion der Standardbetrieb (G9). Für Go/No-Go heißt das: Echtgeld setzt mindestens zwei handlungsfähige Menschen voraus. Nächster Schritt ist deine Entscheidung zu X-ORG-RISK und X-ORG-DEPUTY.

Details: `governance/organisation_raci.md`, `governance/policies/`, `governance/grants_and_risk_acceptance.md`.

- **Rollen und RACI:** Betreiber (portfolioverantwortlich, einziger Befugter für den Moduswechsel), externe Risikofunktion (nicht portfolioverantwortlich; Lese- und Vetorecht bei Profilaufstiegen und Änderungen der Klassen C und D; ab G9), Notfallvertretung (nur Pausieren und Abbau; ab G8), externe Person für Recht und Steuern (BQ-03), externe Prüfer (Gegenprüfung, Penetrationstest, Audit). KI-Agenten haben keine Rolle mit Freigabewirkung (EV-11, EV-13).
- **Vier-Augen-Prinzip:** Änderungen mit Handels- oder Governancewirkung (Klassen C und D) brauchen eine zweite menschliche Freigabe und eine Karenzzeit von <!--v:param:P-OPS-CHANGE-COOLDOWN-H|d0-->24<!--/v--> Stunden zwischen Prüfbericht und Freigabe. Solange keine zweite Person benannt ist, lassen sich Änderungen der Klassen C und D nicht freigeben; das System läuft dann mit dem freigegebenen Stand weiter, Änderungen der Klassen A und B bleiben möglich (Restrisiko DEC-CF-06).
- **Rhythmus:** täglicher Risikobericht, wöchentliche Risikorunde, monatliche Performance-Attribution, quartalsweise Modellprüfung, jährliche Strategie- und Wirtschaftlichkeitsprüfung.
- **Richtlinien:** Risiko, Handel, Änderungen, Incidents, KI, Auslagerung, Informationssicherheit und Aufbewahrung (`governance/policies/`); Interessenkonflikte betreffen nur B3/B4 und entfallen nach BQ-02.
- **Grants je Profil:** Paper, Pilot und Standard mit signierter Risikoakzeptanz (§7.10), Laufzeit (höchstens <!--v:param:P-SEC-GRANT-DAYS/PAPER|d0-->90<!--/v-->, <!--v:param:P-SEC-GRANT-DAYS/PILOT|d0-->30<!--/v--> bzw. <!--v:param:P-SEC-GRANT-DAYS/STANDARD|d0-->90<!--/v--> Tage) und Widerruf.
- **Schlüsselpersonenrisiko:** Vertretung, Notfallhandbuch, Übergabeprozess; ohne bestätigte Erreichbarkeit des Betreibers länger als <!--v:param:P-OPS-PRESENCE-MAX-D|d0-->7<!--/v--> Tage werden neue Einstiege gesperrt (RK-16).

## §14 Betrieb

> **Betreiberfassung.** Im Betrieb rechnet das Paket mit rund <!--v:dmc:operator_hours_per_year|d0-->314<!--/v--> Stunden deiner Zeit im Jahr für Routinen, Incidents, Modellprüfung und die Pflege des KI-Agenten; diese Zeit ist bewertet und in der Wirtschaftsrechnung enthalten. Für jedes Stressszenario, jeden Killer-Test und jeden Ausfall gibt es ein Runbook, und die wichtigsten Abläufe werden regelmäßig im Demokonto geprobt und protokolliert. Die Kostendrift-Überwachung erkennt überhöhte Ausführungskosten schon während des Pilots, weil sie über alle Instrumente gepoolt schätzt; in v2.0 hätte die Prüfung je Instrument länger gedauert als der Pilot. Ein Einzelbetreiber kann kurze Quittungszeiten nicht zusichern, deshalb braucht der Pilot eine Notfallvertretung. Für Go/No-Go heißt das: Der Betrieb ist tragbar, aber nicht ohne zweite Person. Nächster Schritt ist die Messung deiner tatsächlichen Routinezeiten im Paper-Betrieb.

Details: `operations/operations_plan.md`, `operations/runbooks.md`, `operations/drills.md`, `operations/sla_slo.md`.

### 14.1 Routinen und Abläufe

Tägliche Routine <!--v:param:P-OPS-DAILY-MIN|d0-->20<!--/v--> Minuten, wöchentliche Risikorunde <!--v:param:P-OPS-WEEKLY-MIN|d0-->90<!--/v--> Minuten, monatliche Attribution und Abgleich <!--v:param:P-OPS-MONTHLY-MIN|d0-->240<!--/v--> Minuten, Incidents <!--v:param:P-OPS-INCIDENT-MIN|d0-->180<!--/v--> Minuten im Monat, quartalsweise Modellprüfung und Drills <!--v:param:P-OPS-QUARTERLY-MIN|d0-->480<!--/v--> Minuten (Annahmen, im Paper-Betrieb gemessen). Bereitschaft und Service-Levels in `operations/sla_slo.md`; <!--v:calc:runbooks_total|int-->35<!--/v--> Runbooks für alle Szenarien aus §7.9, §8.3 und §10.5; <!--v:calc:drills_total|int-->10<!--/v--> Drills mit Protokoll; Incident- und Problemmanagement mit Post-Mortems; täglicher NAV- und Buchhaltungsabgleich mit den Brokerauszügen.

### 14.2 Kostendrift-Überwachung mit Trennschärfe (EV-07)

Gepoolte Schätzung über alle Instrumente mit Schrumpfung der Einzelschätzungen (P-MON-COSTDRIFT-*). Die Auslösezeit ist simuliert (`operations/costdrift_monitor.py`): Bei <!--v:drift:results/pooled/FAKTOR_1_5/true_ratio|d1-->1,5<!--/v-->-fachen Kosten löst der Monitor im Pilot (<!--v:param:P-RES-PILOT-MONTHS|d0-->6<!--/v--> Monate) in <!--v:drift:results/pooled/FAKTOR_1_5/p_trigger_within_pilot|pct0-->98 %<!--/v--> der Läufe aus, bei doppelten Kosten in <!--v:drift:results/pooled/FAKTOR_2/p_trigger_within_pilot|pct0-->100 %<!--/v-->; die Prüfung je Instrument mit der Handelsfrequenz von TF-D1 wie in v2.0 bräuchte im Median <!--v:drift:results/v2_frequency_unpooled_min20/FAKTOR_2/median_months|d0-->15<!--/v--> Monate. Damit ist nachgewiesen, dass der Monitor innerhalb der Pilotdauer auslösen kann; die Fehlalarmquote ohne Drift beträgt <!--v:drift:results/pooled/OHNE_DRIFT/p_trigger_within_pilot|pct1-->3,7 %<!--/v-->.

## §15 Recht, Regulierung und Steuern (Umfang nach BQ-03)

> **Betreiberfassung.** Nach deiner Entscheidung BQ-03 prüft das Paket weder Recht noch Steuern; das erledigt eine externe Person. Das Paket liefert ihr eine vollständige Übergabeliste mit allen Rechtsakten, die der Auftrag nennt, mit der Frage, die zu beantworten ist, und mit der Sperre, die bis zur Antwort gilt. Unabhängig davon baut das System technische Grenzen ein, die in jedem Fall sinnvoll sind: keine Gelder Dritter, Kontrollen gegen manipulative Ordermuster, Positionsgrenzen und Aufbewahrung unveränderlicher Protokolle. Ohne schriftliche Bestätigung der externen Person gibt es keinen Pilot mit Echtgeld (X-LEGAL-01, X-TAX-01). Für Go/No-Go heißt das: Recht und Steuern sind eine externe Sperre vor G8, kein Teil der Systemleistung. Nächster Schritt ist die Übergabe von `legal/handover_external.md` an die externe Person.

Details: `legal/applicability_matrix.md`, `legal/tax_matrix.md`, `legal/handover_external.md`.

Die Matrix gilt nur für den gerechneten Fall (Eigenkonto, B1); B2 bis B4 sind nach BQ-02 nicht Systemaufgabe (DEC-CF-03). Jede Zeile nennt Rechtsakt, Quelle mit Status, Frage an die externe Person, technische Wirkung im System, Sperre und Verantwortliche. Ethische Ausschlüsse: Aktienindizes nur rüstungsfrei (BQ-06a, alle Kandidaten gesperrt); Agrar, Energie und Krypto sind nach BQ-06 nicht ausgeschlossen.

## §16 Evidenz-, Tor- und Freigabeprozess

> **Betreiberfassung.** Der Weg von der Idee zum Echtgeld führt über die Tore G0 bis G10, und jedes Tor ist eine feste Regeltabelle: Sie sagt vorab, bei welchen Werten das Ergebnis PASS, FAIL oder etwas dazwischen lautet, und nennt für jedes Ergebnis genau einen nächsten Schritt. Auswerten darf nur das unabhängige Prüfmodul; es signiert das Ergebnis mit Laufbeleg, weder du noch der KI-Agent können es nachträglich ändern. Die teuren Tore kommen spät, die billigen mit großer Abbruchwirkung zuerst: G0 kostet kein Geld und prüft, ob sich der Aufbau mit echten Gebühren überhaupt lohnt. Heute steht G0 auf BLOCKED_EXTERNAL, weil Gebühren, Stundensatz, Budget, Verzinsung und Vergleichsprodukte fehlen; selbst wenn sie so bestätigt würden, wie das Paket heute rechnet, scheitert die registrierte Familie an G0, weil eine Alternative sie dominiert. Für Go/No-Go heißt das: Es gibt heute keinen zulässigen Weg zu Echtgeld, und vor einem bestandenen G0 soll kein Geld ausgegeben werden. Nächster Schritt sind die fünf G0-Eingaben (X-BRK-FEES, X-OP-RATE, X-OP-BUDGET, X-BRK-INTEREST, X-V1-PRODUCTS).

Details: `research/evidence_gates.json` (führende Quelle der Torregeln), `validation/gate_engine.py` (Interpreter), `examples/valid/gate_cases/` (Torfälle), `research/operating_characteristics.py` (Betriebscharakteristik), `governance/grants_and_risk_acceptance.md` (Freigaben).

### 16.1 Stufenplan

<!-- GEN:BEGIN tab.gates -->
| ID | Tor | Stufe | E-Baustein | sperrende externe Eingaben | scheitert, wenn (FAIL-Regeln) | Folgeschritt bei PASS | Torfälle |
|---|---|---|---|---|---|---|---|
| GATE-G0 | G0 Betreibereingaben, Wirtschaftlichkeit mit echten Gebühren, Kauf-statt-Bau | BS-00 | E-1 | X-BRK-FEES, X-BRK-INTEREST, X-OP-BUDGET, X-OP-RATE, X-V1-PRODUCTS | G0-R3: finding_class ∈ {PROFILE_NOT_ADMISSIBLE, NON_POSITIVE_BASE, NOT_VIABLE_AT_CAPITAL} (Befundklasse nicht wirtschaftlich oder Profil unzulässig (§5.7; wird vor der Dominanz geprüft)); G0-R4: variant_decision = DOMINATED_BY_ALTERNATIVE (Alternative V0 oder V1 dominiert (EV-04)); G0-R5: p_npv_positive < P-ECO-MARGINAL-P (0,50 Anteil) (P(NPV > 0) unter der Schwelle MARGINAL) | BS-01 und BS-02 parallel starten. | 19 |
| GATE-G1 | G1 Kontozugang und frühe Killer-Tests | BS-01 | E-2 | X-BRK-ACCOUNT, X-BRK-API, X-BRK-CONTRACTS, X-BRK-DEMO, X-BRK-LIQ, X-BRK-MARGIN, X-BRK-NACHSCHUSS | G1-R3: (kt_04 = GESCHEITERT oder kt_05 = GESCHEITERT oder kt_06 = GESCHEITERT) (Order-Lebenszyklus, Wiederholungssicherheit oder serverseitiger Schutz ohne tragfähige Rückfallvariante) | Register mit gemessenen Werten aktualisieren; BS-05 nach G4 freigeben. | 21 |
| GATE-G2 | G2 Datenlizenz, Abgleich zweier Quellen, Leckagetests | BS-02 | E-3 | X-DATA-LIC, X-DATA-ND | G2-R4: xcheck_share_min < P-DATA-XCHECK-SHARE-MIN (0,99 Anteil) (Datenquellen weichen zu stark ab); G2-R5: n_admitted_with_history < P-LEV-H5-MINDIV (8 Anzahl) (zu wenige Instrumente mit Historie für die Mindestdiversifikation) | BS-03 (Forschung) registrieren. | 13 |
| GATE-G3 | G3 Forschung auf Entwicklungsdaten mit Futility-Regel | BS-03 | E-4 | X-DATA-HIST, X-DATA-LIQ, X-DATA-VOL | G3-R3: dsr < P-RES-DSR-MIN (0,95 Anteil) (Deflated Sharpe Ratio unter der Schwelle); G3-R4: pbo > P-RES-PBO-MAX (0,20 Anteil) (Überanpassung (PBO) zu hoch); G3-R5: spa_p > P-RES-ALPHA (0,05 Anteil) (Reality Check bzw. SPA nicht signifikant); G3-R6: turnover_dev > P-RES-TURNOVER-TOL (0,30 Anteil) (Umschlag widerlegt Kosten- und Kapazitätsrechnung); G3-R7: p_predictive_final < P-RES-FUTILITY (0,10 Anteil) (Futility: Aussicht auf das Endtor zu gering (DEC-DS-21)); G3-R8: (neighbors_same_sign = falsch oder subperiods_same_sign = falsch) (nicht robust (Nachbarschaft oder Teilperioden)) | Kandidat mit Hash einfrieren; G4 registrieren. | 20 |
| GATE-G4 | G4 Einmalige Holdout-Prüfung | BS-04 | E-4 | – | G4-R2: sr_holdout ≤ 0 (Netto-Sharpe im Holdout nicht positiv); G4-R3: p_predictive_final < P-RES-FUTILITY (0,10 Anteil) (Futility nach Holdout) | BS-05 (Systembau) beginnen, sofern G1 bestanden. | 7 |
| GATE-G5 | G5 System gebaut, Abnahmetests bestanden, Prüfmodul ohne Abweichung | BS-05 | E-5 | X-INF-VPS, X-INF-ZONES, X-OP-BUDGET | G5-R3: acceptance_failed > 0 (Abnahmetests nicht bestanden); G5-R4: evaluator_deviations > 0 (Prüfmodul weicht ab); G5-R5: mutation_score < P-QA-MUTATION-MIN (0,80 Anteil) (Mutationsziel verfehlt); G5-R6: branch_coverage < P-QA-COVERAGE-MIN (0,90 Anteil) (Abdeckungsziel verfehlt); G5-R7: pentest_critical_open > 0 (kritische Befunde des Penetrationstests offen); G5-R8: llm_isolation_passed = falsch (Sprachmodell nicht nachweislich außerhalb des Geldpfads) | BS-06 (Drills) beginnen. | 17 |
| GATE-G6 | G6 Drills | BS-06 | E-6 | – | G6-R2: mindestens eines von {dr_01 … dr_10} = GESCHEITERT (mindestens ein Drill gescheitert) | Paper-Grant signieren; G7 beginnt. | 7 |
| GATE-G7 | G7 Paper-Forward | BS-07 | E-7 | – | G7-R1: sr_paper_est < P-OC-HARM-SCREEN (-1 Sharpe p. a.) (Harm-Screen: klar schädlich); G7-R2: hard_limit_breaches > 0 (harte Grenze verletzt); G7-R3: costdrift_triggered = wahr (Kostendrift ausgelöst); G7-R4: critical_incidents_open > 0 (kritischer Incident offen) | Pilot-Grant nur nach Lösung aller externen Sperren (G8-Voraussetzungen); Moduswechsel nur durch den Betreiber. | 10 |
| GATE-G8 | G8 Pilot mit Echtgeld im Profil H5 (Endtor) | BS-08 | E-8 | X-DATA-ND, X-EXEC-TCA, X-LEGAL-01, X-OP-CAPITAL, X-OP-DLC-MODE, X-OP-RISK-ACCEPT, X-ORG-DEPUTY, X-TAX-01 | G8-R1: pilot_loss_share ≥ P-RES-PILOT-LOSS-BUDGET (0,15 Anteil) (Pilotverlustbudget erreicht); G8-R2: hard_limit_breaches > 0 (harte Grenze verletzt); G8-R3: sr_pilot_est < P-OC-HARM-SCREEN (-1 Sharpe p. a.) (Harm-Screen); G8-R4: costdrift_triggered = wahr (Kosten außerhalb des Modellbands); G8-R6: posterior_p_positive < P-RES-FINAL-P (0,80 Anteil) (Endtor verfehlt: Posterior unter der Schwelle) | Standard-Grant (H5) mit Risikofunktion möglich; Moduswechsel nur durch den Betreiber. | 21 |
| GATE-G9 | G9 Standardbetrieb mit Hebel-Stufenleiter | BS-09 | E-9 | X-OP-CAPITAL, X-OP-RISK-ACCEPT, X-ORG-RISK | G9-R1: hard_limit_breaches > 0 (harte Grenze verletzt); G9-R2: ladder_violations > 0 (Stufenleiter verletzt); G9-R3: severe_incidents > 0 (schwerer Incident); G9-R4: posterior_p_negative ≥ P-MON-HARM-SR (0,90 Anteil) (Harm-Monitor) | Externes Audit (G10) beauftragen. | 10 |
| GATE-G10 | G10 Externes Audit (Technik, Risiko, Prozesse) | BS-10 | E-9 | – | G10-R3: material_findings > 0 (wesentliche Feststellungen) | Jährliche Wiederholung; E-9 vollständig. | 5 |
<!-- GEN:END tab.gates -->

Der Plan folgt dem Vorschlag in §16 des Auftrags; Anpassungen mit Begründung:

- **G1 im Demokonto mit wenigen Echtgeldorders:** Das Demo beweist weder Ausführung noch Kommission noch Auszug. Deshalb laufen KT-04, KT-06 und KT-14 zusätzlich mit Minimalgröße im Echtgeldkonto; jede dieser Orders löst der Betreiber selbst aus, der Verlust ist auf <!--v:param:P-EXE-KT-LOSS-CAP-EUR|eur-->250 EUR<!--/v--> gedeckelt (P-EXE-KT-LOSS-CAP-EUR), und es gibt keinen Grant (`governance/grants_and_risk_acceptance.md` §4).
- **G2 mit Messbericht:** Die Rechnungen ab G3 brauchen gemessene Volatilitäten, Spreads, Tagesvolumen, Liquiditätsfenster und Historien (X-DATA-VOL, X-DATA-LIQ, X-DATA-HIST); G2 liefert sie, G3 sperrt ohne sie.
- **G3 und G4 mit Futility, Posterior-Schwelle erst in G8:** Ein Holdout von <!--v:param:P-RES-HOLDOUT-YEARS|d0-->2<!--/v--> Jahren (P-RES-HOLDOUT-YEARS) kann eine kleine Kante nicht allein belegen (§6.4). Deshalb prüft G4 nur das Vorzeichen und die Aussicht (Futility); die Schwelle P(Sharpe > 0) ≥ <!--v:param:P-RES-FINAL-P|pct0-->80 %<!--/v--> (P-RES-FINAL-P) gilt im Endtor nach dem Pilot (G8), wenn Entwicklung, Holdout, Paper und Pilot zusammen vorliegen.
- **G5 mit messbaren Qualitätszielen:** Mutations- und Abdeckungsziele (mindestens <!--v:param:P-QA-MUTATION-MIN|pct0-->80 %<!--/v--> erkannte Mutanten, <!--v:param:P-QA-COVERAGE-MIN|pct0-->90 %<!--/v--> Zweigabdeckung), Penetrationstest und der Nachweis, dass kein Sprachmodell im Geldpfad liegt, sind eigene FAIL-Regeln.
- **G6 mit Dauerlauf:** Zu den Drills kommt ein Dauerlauf von <!--v:param:P-QA-SOAK-H|d0-->72<!--/v--> Stunden (P-QA-SOAK-H) im Demokonto, weil Speicher-, Verbindungs- und Uhrfehler erst über Tage sichtbar werden.
- **G8 mit Pilotgröße:** Der Pilot läuft im Profil H5 mit <!--v:param:P-LEV-PILOT-SIZE|pct0-->50 %<!--/v--> der Zielgröße (P-LEV-PILOT-SIZE) und endet, wenn der Verlust <!--v:param:P-RES-PILOT-LOSS-BUDGET|pct0-->15 %<!--/v--> des Pilotkapitals erreicht (P-RES-PILOT-LOSS-BUDGET). Heute ist H5 nicht zulässig (§7.4); G8 ist damit gesperrt, unabhängig von den übrigen Voraussetzungen.

### 16.2 Regeln der Tore (Technik übernommen aus v2.0)

- **Auswertung:** Voraussetzungen in fester Reihenfolge; die erste nicht erfüllte liefert ihr Ergebnis (meist BLOCKED_EXTERNAL oder INVALID). Danach Berechnungen, dann die Ergebnisregeln in Reihenfolge: Die erste wahre Regel bestimmt das Ergebnis, die letzte ist immer wahr. Flags werden zusätzlich gesetzt und ändern das Ergebnis nicht. Schwellen sind Verweise auf `parameters.json`, nie Zahlen im Regeltext.
- **Ergebnisklassen:** PASS, FAIL, INCONCLUSIVE, INVALID, ERROR, BLOCKED_EXTERNAL; je Tor und Klasse genau ein Folgeschritt (`next_steps`).
- **Signierte Ergebnisse:** Nur der Evaluator im Prüfmodul erzeugt ein `gate_result` (Vertrag IF-06) mit Hash der Eingaben, Hash der Regeln, Regel-ID, Flags, Exitcode, Laufbeleg und Signatur; PASS, FAIL und INCONCLUSIVE setzen Exitcode 0 voraus. Der Geldpfad akzeptiert nur Ergebnisse mit gültiger Evaluator-Signatur (T-SEC-011); der KI-Agent kann Ergebnisse lesen, nie schreiben.
- **Kein Überschreiben:** Ein Ergebnis wird nie geändert. Will der Betreiber nach einem FAIL anders vorgehen, ist das eine neue, signierte Entscheidung im Entscheidungsregister; danach wird das Tor mit den neuen Eingaben erneut ausgewertet, und der Versuch zählt gegen das Versuchsbudget von <!--v:param:P-OC-TRIALS|d0-->20<!--/v--> Versuchen je Kampagne (P-OC-TRIALS).
- **Prüfung im Paket:** `validation/gate_engine.py` wertet <!--v:calc:gate_cases_total|int-->172<!--/v--> Torfälle aus und verlangt, dass jede der <!--v:calc:gate_rules_total|int-->140<!--/v--> Ergebnisregeln von mindestens einem Fall getroffen wird; zu jeder Schwelle gibt es Fälle auf beiden Seiten.

### 16.3 Betriebscharakteristik

Die Tore G3, G4, G7 und G8 sind in `research/operating_characteristics.py` als Kette simuliert (Klassen schädlich, wertlos und brauchbar; Tabelle in §6.6). Kernwerte der registrierten Konfiguration ohne Futility-Regel: Eine wertlose Strategie erreicht den Systembau in <!--v:oc:registered/WERTLOS/ohne_futility/rates/reached_G5_build|pct2-->0,05 %<!--/v--> der Fälle (<!--v:oc:v2_reference|raw-->v2.0: Strategie ohne Edge bestand E1 und E2 zu etwa 89 % (EV-05)<!--/v-->), eine brauchbare mit Netto-Sharpe <!--v:param:P-RES-SR-USEFUL|d1-->0,3<!--/v--> in <!--v:oc:registered/BRAUCHBAR/ohne_futility/rates/reached_G5_build|pct2-->1,40 %<!--/v--> und das Endtor in <!--v:oc:registered/BRAUCHBAR/ohne_futility/rates/accepted_final|pct2-->0,88 %<!--/v-->. Die Tore trennen damit scharf, halten aber auch brauchbare Strategien fast immer auf; das ist die Folge kurzer Daten (§6.4) und kein Einstellfehler. Bis einschließlich G3 kostet der Weg <!--v:oc:cumulative_cost_eur/BS-03|eur-->12.791 EUR<!--/v-->, bis zum Ende des Piloten <!--v:oc:cumulative_cost_eur/BS-08|eur-->58.147 EUR<!--/v-->.

### 16.4 Torlage heute

Die folgenden Fälle sind mit den heutigen Rechenwerten gebildet (Spalte „Werte aus“) und werden bei jeder Paketprüfung neu ausgewertet:

<!-- GEN:BEGIN tab.gate_today -->
| Fall | Tor | Lage | Ergebnis | Regel | Flags | Werte aus |
|---|---|---|---|---|---|---|
| GC-G0-101 | GATE-G0 | Stand 24.09.2026: Gebühren, Stundensatz, Budget, Verzinsung und V1-Produkte unbestätigt | BLOCKED_EXTERNAL | PRE-G0-1 | – | financials/decision_montecarlo_results.json#/table/U-KOSTEN/5000000/H5 |
| GC-G0-102 | GATE-G0 | Rechenwerte 24.09.2026, Eingaben hypothetisch bestätigt: registrierte Familie in H5 bei Referenzstufe | FAIL | G0-R3 | – | financials/decision_montecarlo_results.json#/variants_V0_V4/5000000 |
| GC-G0-103 | GATE-G0 | Rechenwerte 24.09.2026, Eingaben hypothetisch bestätigt: TF-D1 ohne Sieben-Tage-Grenze in H5 bei Referenzstufe | FAIL | G0-R3 | MARGINAL, OPERATOR_DECISION_REQUIRED | financials/decision_montecarlo_results.json#/table/U-KOSTEN-TFD1/5000000/H5 |
<!-- GEN:END tab.gate_today -->

Lesart: GC-G0-101 ist der Stand heute. GC-G0-102 zeigt, dass die registrierte Familie auch mit bestätigten Eingaben scheitert: Ergebnis <!--v:calc:gate_today/GC-G0-102/outcome|raw-->FAIL<!--/v--> nach Regel <!--v:calc:gate_today/GC-G0-102/rule|raw-->G0-R3<!--/v--> (G0-R3: Befundklasse, geprüft vor der Dominanz durch V0 oder V1 nach G0-R4). GC-G0-103 prüft dieselbe Lage für die Alternative TF-D1 ohne Sieben-Tage-Grenze: Sie verletzt deine Vorgabe BQ-04 (DEC-OP-04), ist deshalb nur Vergleichsbasis (DEC-DS-08) und erreicht mit den heutigen Rechenwerten das Ergebnis <!--v:calc:gate_today/GC-G0-103/outcome|raw-->FAIL<!--/v--> nach Regel <!--v:calc:gate_today/GC-G0-103/rule|raw-->G0-R3<!--/v-->.

### 16.5 Monitore im Betrieb

Ab dem Paper-Betrieb laufen Monitore mit denselben Regeltabellen; jede Auslösung führt zu genau einer Folge (Einstiegssperre, Abbau oder Rückbau):

<!-- GEN:BEGIN tab.monitors -->
| ID | Monitor | löst aus, wenn | Folge | Torfälle |
|---|---|---|---|---|
| MON-HARM | Harm- und Futility-Monitor | MH-R1: posterior_p_negative ≥ P-MON-HARM-SR (0,90 Anteil) (schädlich); MH-R2: p_predictive_final < P-RES-FUTILITY (0,10 Anteil) (Futility im Betrieb) | MONITOR_STOP → WIND_DOWN (SM-MODE); Ursachenbericht. | 4 |
| MON-COSTDRIFT | Kostendrift-Monitor (gepoolt, EV-07) | MC-R1: p_ratio_above ≥ P-MON-COSTDRIFT-PROB (0,90 Anteil) (Kostendrift) | RB-32: Einstiegssperre der Gruppe, Kostenmodell und Wirtschaftlichkeit neu rechnen. | 3 |
| MON-DRIFT | Aktivitäts- und Modell-Drift | MD-R1: holding_max_violations > 0 (Höchsthaltedauer verletzt (BQ-04)); MD-R2: turnover_dev > P-RES-TURNOVER-TOL (0,30 Anteil) (Umschlag außerhalb der Toleranz); MD-R3: vol_dev > P-MON-VOL-BAND (0,40 Anteil) (Volatilität außerhalb des Bands) | Einstiegssperre; Neukalibrierung und Neuvalidierung (MRM); kein Profilaufstieg. | 5 |
| MON-LIMITS | Limitverletzungen und Datenqualität | ML-R1: hard_limit_breaches > 0 (harte Grenze verletzt); ML-R2: xcheck_share_min < P-DATA-XCHECK-SHARE-MIN (0,99 Anteil) (Datenqualität unzureichend) | schwerer Incident (RK-29) bzw. Instrument sperren; Ursachenbericht. | 4 |
| MON-AI | Nutzen der KI-Schicht (EV-10) | MA-R1: negative_quarters ≥ P-AI-ROLLBACK-QUARTERS (2 Quartale) (Rückbaukriterium erfüllt); MA-R2: eval_pass_rate < P-AI-EVAL-PASS (0,95 Anteil) (Evaluationssuite nicht bestanden); MA-R3: (acceptance_rate < P-AI-ACCEPT-MIN (0,50 Anteil) oder net_benefit_hours < 0) (Quartal negativ (Annahmequote oder Nettonutzen nach Abo-Kosten und Korrekturen)) | Rückbau (SM-HERMES RETIRED) bzw. kein Update, voriges Image behalten. | 6 |
<!-- GEN:END tab.monitors -->

Die Auslösezeiten sind simuliert: Kostendrift in §14.2 (EV-07), Harm- und Volatilitätsmonitor in `operations/monitor_simulation.py` (<!--v:mon:runs|int-->1.000<!--/v--> Läufe je Lage; der Harm-Monitor stoppt ab einer Posterior-Wahrscheinlichkeit von <!--v:param:P-MON-HARM-SR|pct0-->90 %<!--/v--> für eine negative Netto-Sharpe, Prior wie in der Betriebscharakteristik; der Volatilitätsmonitor vergleicht <!--v:param:P-MON-VOL-WINDOW-D|d0-->126<!--/v--> Handelstage mit dem Ziel und löst ab <!--v:param:P-MON-VOL-BAND|pct0-->40 %<!--/v--> Abweichung aus):

<!-- GEN:BEGIN tab.monitor_triggers -->
| Monitor | Lage | Median bis Auslösung | P(Auslösung) kurz | P(Auslösung) mittel | P(Auslösung) lang |
|---|---|---|---|---|---|
| MON-HARM (MH-R1) | schädlich, wahre Sharpe -0,2 | über 120 Monate | 0,0 % (Pilot) | 0,0 % (24 M) | 2,7 % (60 M) |
| MON-HARM (MH-R1) | stark schädlich (Harm-Screen), wahre Sharpe -1,0 | 68 Monate | 0,0 % (Pilot) | 0,6 % (24 M) | 41,0 % (60 M) |
| MON-HARM (MH-R1) | wertlos, wahre Sharpe 0,0 | über 120 Monate | 0,0 % (Pilot) | 0,0 % (24 M) | 1,1 % (60 M) |
| MON-HARM (MH-R1) | brauchbar, wahre Sharpe 0,3 | über 120 Monate | 0,0 % (Pilot) | 0,0 % (24 M) | 0,0 % (60 M) |
| MON-DRIFT (MD-R3) | Volatilität ×1,0 | über 252 Handelstage | 2,0 % (20 T) | 2,6 % (63 T) | 6,6 % (252 T) |
| MON-DRIFT (MD-R3) | Volatilität ×1,5 | 104 Handelstage | 3,9 % (20 T) | 19,0 % (63 T) | 93,2 % (252 T) |
| MON-DRIFT (MD-R3) | Volatilität ×2,0 | 47 Handelstage | 13,0 % (20 T) | 76,8 % (63 T) | 100,0 % (252 T) |
<!-- GEN:END tab.monitor_triggers -->

Befund: Der Harm-Monitor ist für eine leicht schädliche Strategie praktisch blind – bei wahrer Sharpe <!--v:mon:harm/SCHAEDLICH/true_sharpe|d1-->-0,2<!--/v--> löst er binnen fünf Jahren nur in <!--v:mon:harm/SCHAEDLICH/p_trigger_within_60m|pct1-->2,7 %<!--/v--> der Läufe aus, und selbst bei <!--v:mon:harm/STARK_SCHAEDLICH/true_sharpe|d1-->-1,0<!--/v--> während des Piloten nur in <!--v:mon:harm/STARK_SCHAEDLICH/p_trigger_within_pilot|pct1-->0,0 %<!--/v-->. Das ist keine Schwäche der Regel, sondern der Statistik: Eine Sharpe-Ratio lässt sich in Monaten nicht von null unterscheiden (§6.4). Den Schutz im Betrieb tragen deshalb die Drawdown-Leiter und die Tagesgrenze, nicht der Harm-Monitor. Der Volatilitätsmonitor erkennt eine Verdopplung der Volatilität im Median nach <!--v:mon:vol_drift/FAKTOR_2/median_days|d0-->47<!--/v--> Handelstagen und löst ohne Drift in <!--v:mon:vol_drift/OHNE_DRIFT/p_trigger_within_252d|pct1-->6,6 %<!--/v--> der Jahre fälschlich aus; Fenster und Band sind danach gewählt. Nicht simuliert sind die Futility-Regel im Betrieb (MH-R2) und der Umschlag (MD-R2); die Höchsthaltedauer (MD-R1) löst sofort aus. Der KI-Monitor setzt das Rückbaukriterium aus §11.4 um (EV-10).

### 16.6 Freigaben und Evidenz-Score

Freigaben folgen den Toren: Paper-Grant nach G5 und G6, Pilot-Grant nach G7 und allen externen Sperren von G8, Standard-Grant nach G8; jeder Grant ist eine signierte Betreiberaktion mit Hardware-Schlüssel, und nur der Betreiber schaltet zwischen Demo und Echtgeld (BQ-09). Der Evidenz-Score E (§20.3) vergibt Punkte nur für signierte Torergebnisse mit Laufbeleg:

<!-- GEN:BEGIN tab.e_map -->
| E-Baustein | Tore | Nachweis durch |
|---|---|---|
| E-1 | GATE-G0 | G0 Betreibereingaben, Wirtschaftlichkeit mit echten Gebühren, Kauf-statt-Bau |
| E-2 | GATE-G1 | G1 Kontozugang und frühe Killer-Tests |
| E-3 | GATE-G2 | G2 Datenlizenz, Abgleich zweier Quellen, Leckagetests |
| E-4 | GATE-G3, GATE-G4 | G3 Forschung auf Entwicklungsdaten mit Futility-Regel; G4 Einmalige Holdout-Prüfung |
| E-5 | GATE-G5 | G5 System gebaut, Abnahmetests bestanden, Prüfmodul ohne Abweichung |
| E-6 | GATE-G6 | G6 Drills |
| E-7 | GATE-G7 | G7 Paper-Forward |
| E-8 | GATE-G8 | G8 Pilot mit Echtgeld im Profil H5 (Endtor) |
| E-9 | GATE-G9, GATE-G10 | G9 Standardbetrieb mit Hebel-Stufenleiter; G10 Externes Audit (Technik, Risiko, Prozesse) |
<!-- GEN:END tab.e_map -->

Heute liegt kein signiertes Torergebnis vor; E beträgt deshalb null (`audit/scorecard_E.json`). E misst nachgewiesene Betriebs- und Prozessqualität, nicht Gewinn.

## §17 Bauprogramm

> **Betreiberfassung.** Gebaut wird in elf Stufen, BS-00 bis BS-10, jede mit einem Tor am Ende; Mensch und Coding-Agent sind getrennt geschätzt: <!--v:calc:build_person_days_low|d0-->44<!--/v--> bis <!--v:calc:build_person_days_high|d0-->124<!--/v--> Personentage und <!--v:calc:build_agent_days_low|d0-->55<!--/v--> bis <!--v:calc:build_agent_days_high|d0-->118<!--/v--> Agententage, im Basisfall <!--v:calc:build_person_days_base|d0-->73<!--/v--> und <!--v:calc:build_agent_days_base|d0-->82<!--/v-->; das ist mehr als in v2.0, weil jede Komponente einzeln geschätzt und die menschliche Prüfung mitgerechnet ist. Bis zum abgenommenen System vergehen im Basisfall <!--v:calc:build_weeks_until/BS-05/base|d0-->28<!--/v--> Wochen, bis zum Ende des Piloten <!--v:calc:build_weeks_until/BS-08/base|d0-->82<!--/v--> Wochen und <!--v:dmc:build_cost_until_pilot_eur|eur-->58.147 EUR<!--/v-->. Die Reihenfolge folgt dem Informationswert: zuerst die kostenlose Wirtschaftlichkeitsprüfung mit echten Gebühren, dann die Killer-Tests beim Broker, dann Daten und Forschung, und erst danach der teure Systembau. Einen fertigen Handelskern kaufen wir nicht, weil keines der geprüften Frameworks MT5 anbindet. Für Go/No-Go heißt das: Heute ist nur BS-00 empfohlen. Nächster Schritt ist BS-00 mit den G0-Eingaben; bis dahin wird nur das Paket geprüft, ein Coding-Agent ist erst ab BS-01 nötig.

Details: `implementation/build_program.md`, `implementation/build_stages.json`, `implementation/test_catalog.json`, `implementation/CODING_AGENT_START.md`, `implementation/make_or_buy.md`.

### 17.1 Arbeitspakete, Aufwand und Kosten

<!-- GEN:BEGIN tab.build_program -->
| Stufe | Tor | Inhalt | Personentage (niedrig / Basis / hoch) | Agententage (niedrig / Basis / hoch) | Wochen (niedrig / Basis / hoch) | hängt ab von | externe Eingaben |
|---|---|---|---|---|---|---|---|
| BS-00 | GATE-G0 | Betreibereingaben, Wirtschaftlichkeit mit echten Gebühren, Kauf-statt-Bau-Entscheidung | 2,0 / 3,0 / 5,0 | 0,0 / 0,0 / 0,0 | 1 / 2 / 3 | – | X-BRK-FEES, X-BRK-INTEREST, X-OP-BUDGET, X-OP-RATE, X-V1-PRODUCTS |
| BS-01 | GATE-G1 | Kontozugang (Demo und kleines Echtgeldkonto), frühe Killer-Tests KT-01…KT-16 | 3,0 / 5,0 / 8,0 | 2,0 / 4,0 / 6,0 | 2 / 3 / 6 | BS-00 | X-BRK-ACCOUNT, X-BRK-API, X-BRK-CONTRACTS, X-BRK-DEMO, X-BRK-LIQ, X-BRK-MARGIN, X-BRK-NACHSCHUSS |
| BS-02 | GATE-G2 | Datenlizenz, Abgleich zweier Quellen, Leckagetests | 3,0 / 4,0 / 6,0 | 3,0 / 5,0 / 8,0 | 2 / 4 / 6 | BS-00 | X-DATA-LIC, X-DATA-ND |
| BS-03 | GATE-G3 | Forschung auf Entwicklungsdaten mit Futility-Regel | 5,0 / 8,0 / 12,0 | 6,0 / 10,0 / 15,0 | 3 / 5 / 8 | BS-02 | X-DATA-HIST, X-DATA-LIQ, X-DATA-VOL |
| BS-04 | GATE-G4 | Einmalige Holdout-Prüfung | 1,0 / 2,0 / 3,0 | 1,0 / 1,0 / 2,0 | 1 / 1 / 2 | BS-03 | – |
| BS-05 | GATE-G5 | Systembau, Abnahmetests, unabhängiges Prüfmodul ohne Abweichung | 16,4 / 30,0 / 55,8 | 42,0 / 60,0 / 84,0 | 10 / 16 / 26 | BS-04, BS-01 | X-INF-VPS, X-INF-ZONES, X-OP-BUDGET |
| BS-06 | GATE-G6 | Drills: Restore, Broker- und Datenausfall, Margin, Kill-Switch, Schlüsselverlust | 3,0 / 4,0 / 6,0 | 1,0 / 2,0 / 3,0 | 2 / 2 / 4 | BS-05 | – |
| BS-07 | GATE-G7 | Paper-Forward (Mindestdauer P-RES-PAPER-MONTHS (6 Monate)) | 4,0 / 6,0 / 10,0 | 0,0 / 0,0 / 0,0 | 26 / 26 / 39 | BS-06 | – |
| BS-08 | GATE-G8 | Pilot mit Echtgeld im Profil H5 (Pilotgröße P-LEV-PILOT-SIZE (0,50 Anteil), Pilotverlustbudget P-RES-PILOT-LOSS-BUDGET (0,15 Anteil)) | 4,0 / 6,0 / 10,0 | 0,0 / 0,0 / 0,0 | 26 / 26 / 39 | BS-07 | X-DATA-ND, X-EXEC-TCA, X-LEGAL-01, X-OP-CAPITAL, X-OP-DLC-MODE, X-OP-RISK-ACCEPT, X-ORG-DEPUTY, X-TAX-01 |
| BS-09 | GATE-G9 | Standardbetrieb mit Hebel-Stufenleiter | 0,0 / 0,0 / 0,0 | 0,0 / 0,0 / 0,0 | 52 / 52 / 52 | BS-08 | X-OP-CAPITAL, X-OP-RISK-ACCEPT, X-ORG-RISK |
| BS-10 | GATE-G10 | Externes Audit (Technik, Risiko, Prozesse) | 3,0 / 5,0 / 8,0 | 0,0 / 0,0 / 0,0 | 4 / 6 / 8 | BS-09 | – |
<!-- GEN:END tab.build_program -->

Schätzbasis: <!--v:calc:build_kloc_total|d1-->42,0<!--/v--> KLOC in <!--v:calc:build_components_total|int-->12<!--/v--> Komponenten, Produktivität und Prüfaufwand als Spanne (Annahmen mit Soll-Ist-Messung ab BS-05). Kritischer Pfad: <!--v:build:critical_path|chain-->BS-00 → BS-02 → BS-03 → BS-04 → BS-05 → BS-06 → BS-07 → BS-08 → BS-09 → BS-10<!--/v-->; <!--v:build:parallel/0|list-->BS-01, BS-02<!--/v--> laufen parallel. v2.0 nannte <!--v:v2map:comparisons/v2_agent_days/low|int-->45<!--/v--> bis <!--v:v2map:comparisons/v2_agent_days/high|int-->71<!--/v--> Agententage ohne Messbasis und ohne Personentage (EV-02). Kosten je Stufe mit Stundensatz, Agentenabo, einmaligen und laufenden Posten stehen in `implementation/build_program.md` §4; sie gehen als Aufbaukosten in die Entscheidungsrechnung ein (§5.4).

### 17.2 Abnahme je Stufe

Jede Stufe hat eine Definition of Done (`implementation/build_program.md` §6), die mit einem signierten PASS ihres Tors endet. Der Testkatalog enthält <!--v:calc:tests_total|int-->151<!--/v--> Tests mit Prozedur, Orakel und Bestehenskriterium, darunter <!--v:calc:killer_tests_total|int-->16<!--/v--> Killer-Tests, die zuerst laufen; <!--v:calc:tests_by_exec/IM_PAKET|int-->40<!--/v--> Tests laufen schon heute in der Paketprüfung. `implementation/CODING_AGENT_START.md` legt die ersten Schritte fest: vor G0 nur Paketprüfung und Übergabe der G0-Eingaben; nach dem signierten PASS von G0 Repository mit dem Paket als Vertrag, CI über drei Python-Versionen mit Warnungen als Fehler und Secret-Scan, bevor das erste Zugangsdatum existiert.

### 17.3 Make-or-Buy

Geprüft wurden NautilusTrader (LGPL-3.0), QuantConnect LEAN (Apache-2.0) und pysystemtrade (GPL-3.0) nach Lizenz, Reife, Brokeranbindung, Futures-Rollen, Prüfbarkeit und Eignung für den deterministischen Kern. Keines bindet MetaTrader 5 offiziell an; den MT5-Adapter, die Auftragsverwaltung, den Risikomotor und das Prüfmodul müssten wir in jedem Fall selbst bauen. Entscheidung (DEC-DS-22): eigener schlanker Kern; pysystemtrade dient als unabhängige Referenz für Rollkalender und angepasste Reihen (T-DAT-004), kein Framework-Code gelangt in den Geldpfad (T-REL-003). Kommerzielle Plattformen sind nach BQ-08 ausgeschieden und nicht geprüft; die Pflichten aus GPL-3.0 und LGPL-3.0 sind nicht belegt und gehen an die externe Person, ohne die Entscheidung zu berühren.

### 17.4 Reihenfolge nach Informationswert

1. Wirtschaftlichkeit mit echten Gebühren (G0, ohne Geldausgabe).
2. Kauf-statt-Bau-Vergleich gegen Geldmarkt und Fondslösung (G0).
3. Killer-Tests beim Broker (G1), zuerst die mit Projektabbruchwirkung.
4. Kostenmessung: Kommission gegen Auszug, Spreads und Liquidität aus den Daten, Schlupf im Demo- und Paper-Betrieb.

Bis einschließlich BS-02 kostet der Weg <!--v:oc:cumulative_cost_eur/BS-02|eur-->9.044 EUR<!--/v-->; der Systembau (<!--v:stagecost:BS-05/total_eur|eur-->18.871 EUR<!--/v-->) beginnt erst nach den Forschungstoren G3 und G4.

## §18 Paketstruktur

> **Betreiberfassung.** Das Paket ist so gebaut, dass jede Aussage auf eine Datei, einen Rechner oder ein Register zurückführt und maschinell geprüft wird. Es enthält <!--v:calc:schemas_total|int-->50<!--/v--> Schemas, <!--v:calc:contracts_total|int-->21<!--/v--> Datenverträge mit gültigen und ungültigen Beispielen, <!--v:calc:tests_total|int-->151<!--/v--> Tests und <!--v:calc:requirements_total|int-->113<!--/v--> Anforderungen. Das größte Risiko ist die Dichte: Wer nur das Masterkonzept liest, sieht die Belege nicht, deshalb nennt der Text zu jeder Aussage die Datei. Alle offenen externen Eingaben stehen gesammelt in `external_inputs.json`. Für Go/No-Go heißt das: Die Entscheidungsgrundlagen liegen vollständig im Paket; die Entscheidung für Echtgeld bleibt No-Go. Nächster Schritt: `README.md` lesen und die Paketprüfung selbst ausführen.

| Ordner oder Datei | Inhalt |
|---|---|
| `README.md`, `KURZFASSUNG_BETREIBER.md`, `STATUS.md` | Einstieg und Prüfbefehle; Kurzfassung mit Go/No-Go je Kapitalstufe und Profil; Stand der Erstellung |
| `Masterkonzept_v3.0.md` | dieses Dokument mit Betreiberfassung je Kapitel |
| `parameters.json`, `external_inputs.json`, `requirements.json` | Parameter mit Status und Quelle; externe Eingaben mit Sperrwirkung; Anforderungen mit Tests |
| `registers/` | Entscheidungen mit Siegel der Betreiberangaben, Risiken, Quellen, Auflösungsmatrix, Rückverfolgbarkeit, Modelle, Limits, Instrumente, Kosten |
| `financials/` | Kostenmodell, Steuer-Sensitivität, Baustufenkosten, Entscheidungs-Monte-Carlo, Kauf statt Bau |
| `research/` | Forschungsplan, Strategiefamilie mit Referenzstrategien, Prior, Statistik, Tore und Monitore (`research/evidence_gates.json`), Betriebscharakteristik, Rechercheprotokolle |
| `risk/` | Hebelmodell und Hebelrechner, Kelly/Ruin, Stresstests, Limits, Margin und Liquidität |
| `execution/`, `data/` | OMS/EMS, Killer-Tests, Ausführungsqualität, Pre-Trade-Kontrollen; Datenplan, Anbieter, Proxy-Regel, Referenzdaten |
| `architecture/`, `security/` | Systementwurf, Schnittstellen, Zustandsautomaten, Szenariokatalog, Bedrohungsmodell; Sicherheitsarchitektur, Schlüsselverwaltung |
| `ai/` | KI-Schicht, Hermes-Integration, Evaluationssuite, Modellrisikomanagement |
| `governance/`, `operations/`, `legal/` | Rollen, Grants, Richtlinien; Betriebsplan, Runbooks, Drills, SLOs, Monitore; Anwendbarkeit, Steuern, Übergabe an die externe Person |
| `implementation/` | Bauprogramm, Baustufen, Testkatalog, Startanleitung für Coding-Agenten, Make-or-Buy |
| `schemas/`, `examples/` | JSON Schema 2020-12 für Verträge und Register; gültige und ungültige Beispiele, Torfälle, Zustandstraces |
| `audit/` | Scorecards K und E, Konzeptprüfung, Prüfauftrag für die Gegenprüfung, Abbildung v2.0 → v3.0 |
| `validation/`, `lib/` | Paketprüfung, semantische Prüfungen, Mutationstests, Mehrversionslauf, Renderer, Tor- und Zustandsmotor, Referenztests, Laufbelege; gemeinsame Rechenbibliothek und Paketstand |
| `PACKAGE_MANIFEST.json`, `CHECKSUMS.sha256` | Manifest und Prüfsummen aller Dateien |

Zusätzlich zur Liste in §18 des Auftrags enthält das Paket `legal/handover_external.md` (Übergabe an die externe Person nach BQ-03), `lib/calc.py` und `lib/pkgstate.py` (gemeinsame Rechenregeln und Paketstand), `operations/monitor_simulation.py` (Auslösezeiten der Monitore), `ruff.toml` (Linter) und `validation/requirements-validation.txt` (gepinnte Abhängigkeiten der Prüfung mit Hashes). Alle verlangten Namen sind unverändert.

## §19 Paketprüfung

> **Betreiberfassung.** Die Paketprüfung stellt sicher, dass Zahlen, Register, Texte und Beispiele zusammenpassen, bevor jemand dem Paket vertraut. Sie umfasst vierzehn Phasen mit <!--v:calc:semantic_checks_total|int-->11<!--/v--> semantischen Querprüfungen und <!--v:calc:reference_tests_total|int-->22<!--/v--> Referenztests, und <!--v:calc:mutations_total|int-->60<!--/v--> absichtlich eingebaute Fehler müssen von ihr erkannt werden. Das größte Risiko sind Fehler, die keine Prüfung abdeckt; die <!--v:calc:known_limits_total|int-->13<!--/v--> bekannten Grenzen stehen unten, und eine interne Gegenlese hat weitere Lücken gefunden, die behoben sind (`audit/concept_review.md`). Offen ist die unabhängige Gegenprüfung (X-REVIEW). Für Go/No-Go heißt das: Ein grünes Prüfergebnis belegt Widerspruchsfreiheit, nicht Wirtschaftlichkeit. Nächster Schritt: `python validation/validate_package.py --root . --strict` selbst ausführen.

### 19.1 Phasen

| Phase | Prüft |
|---|---|
| P01 | Struktur: Pflichtdateien und -ordner, kein Bytecode, keine symbolischen Links |
| P02 | JSON-Syntax ohne doppelte Schlüssel |
| P03 | Schemas (JSON Schema 2020-12) für Register, Verträge, Beispiele und Scorecards |
| P04 | Registersemantik und Querverweise (Tickwert, Risikoscore, Belegstatus) |
| P05 | Verweise im Text: Kennungen, Dateien, Funktionen, JSON-Pointer |
| P06 | Bindungen: jede Zahl im Text ist an einen Rechner oder ein Register gebunden; Betreiberfassungen höchstens sechs Sätze |
| P07 | Referenzrechner: bytegleiche Neuberechnung (`validation/run_calculators.py --check`) |
| P08 | Beispiele, Torfälle und Zustandstraces (`validation/gate_engine.py`, `validation/state_engine.py`, `validation/example_rules.py`) |
| P09 | Semantische Querprüfungen (`validation/semantic_checks.py`) |
| P10 | Referenztests (`validation/test_reference_models.py`) |
| P11 | Hygiene: Platzhalter, Geheimnisse, personenbezogene Daten, lokale Pfade, Dateitypen |
| P12 | Selbstbewertung K und E gegen das Raster aus §20 |
| P13 | Statuswahrheit: Teststatus aus Ausführungsort und Laufbeleg, Anforderungsstatus aus den Tests, Nachweise der Befunde, Laufbelege mit Paketstand |
| P14 | Manifest und Prüfsummen (nur nach dem Packen) |

Die semantischen Querprüfungen rechnen nach: Kosten gegen Spreads und Gebühren (einschließlich der Regel, dass nur das Kostenmodell das Kostenregister liest), Hebel gegen Volatilität, Margin und Limits samt Wochenendfaktor, Stressergebnisse vollständig je Profil mit Margin-Level auf das Guthaben beim Broker, Steuerszenarien, Kapazität gegen Tagesvolumen, Proxy-Regel mit Notierung, Limits gegen Parameter und Leitern, Runbook-Abdeckung, Tore gegen Betriebscharakteristik und externe Eingaben, Betreiberangaben gegen Wortlaut und Siegel sowie die Scorecards.

### 19.2 Mutationstests und Mehrversionslauf

`validation/mutation_tests.py` baut jede Mutation aus `validation/mutation_catalog.json` in eine frische Kopie des Pakets ein und verlangt, dass die genannten Phasen mit dem erwarteten Fehler scheitern; vorher müssen dieselben Phasen auf der unveränderten Kopie bestehen. Darunter sind die <!--v:calc:mutations_required|int-->6<!--/v--> ausdrücklich verlangten Fälle (Spread ohne Kostenanpassung, Hebelprofil über einem Limit, entfernter Stresswert, erfundene Betreiberangabe, umgangene Futility-Regel, E-Punkt ohne Laufbeleg):

<!-- GEN:BEGIN tab.mutation_categories -->
| Kategorie | Mutationen | Beispiele |
|---|---|---|
| BEISPIEL | 4 | Erwartung eines Torfalls verfälscht; Zustandstrace verfälscht; Gültiges Beispiel verletzt eine semantische Regel (Aufrunden); Ungültiges Beispiel repariert (Erwartung nicht mehr erfüllt) |
| BINDUNG | 3 | Ungebundene Ergebniszahl im Fließtext; Gebundenen Wert im Text verfälschen; Betreiberfassung länger als sechs Sätze |
| HYGIENE | 4 | Platzhalter im Text; Personenbezogene E-Mail-Adresse; Privater Schlüssel im Paket; Absoluter lokaler Pfad |
| RECHNER | 3 | Parameter ändern ohne Rechner neu laufen zu lassen; Steuerfunktion kürzt auch Verluste; Leiterfaktor im Stressmotor verfälscht |
| REGISTER | 3 | Tickwert ≠ Multiplikator × Tick; Parameter BELEGT ohne Quelle; Risikoscore ≠ Wahrscheinlichkeit × Wirkung |
| SEMANTIK | 31 | Spread ändern ohne Kostenanpassung; Hebelprofil über ein Limit setzen (H20-Obergrenze über der Betreibergrenze); Stresswert entfernen; Betreiberangabe erfinden (Kapital als bestätigt ausgeben); Futility-Schwelle umgehen  |
| STATUS | 4 | Anforderung als im Paket nachgewiesen ausgegeben; Bautest als im Paket ausgeführt ausgegeben; Befund mit fehlendem Nachweis; Inhalt ändern ohne neuen Mehrversionslauf (Beleg eines alten Paketstands) |
| STRUKTUR | 5 | Pflichtdatei entfernen; JSON-Syntaxfehler; Doppelter JSON-Schlüssel; Schemaverstoß (Parameter ohne Einheit); Gepinnte Abhängigkeiten entfernen |
| VERWEIS | 3 | Verweis auf fehlende Datei; Verweis auf unbekanntes Risiko; Verweis auf unbekannten Parameter |
<!-- GEN:END tab.mutation_categories -->

`validation/run_multi_python.py` führt Rechner, Bindungen, Referenztests, semantische Prüfungen, die Paketprüfung und den Linter unter Python 3.11, 3.12 und 3.13 jeweils mit `-W error` aus, in Umgebungen mit den gepinnten Abhängigkeiten aus `validation/requirements-validation.txt` (Installation mit `--require-hashes`).

### 19.3 Belegzyklus und Laufbelege

Die Laufbelege entstehen nacheinander: Mehrversionslauf (`validation/execution_log.txt`), Mutationslauf (`validation/mutation_report.json`), Prüfung vor dem Packen (`validation/validation_report.json`), Manifest und Prüfsummen, ZIP und schließlich die strenge Prüfung nach frischem Entpacken, deren Bericht außerhalb des Archivs liegt. Jeder Beleg trägt den Paketstand, auf dem er entstand (`lib/pkgstate.py`); die Statuswahrheit (P13) vergleicht ihn mit dem geprüften Paket und erkennt so Belege einer älteren Fassung.

### 19.4 Bekannte Grenzen der Prüfung

<!-- GEN:BEGIN tab.check_limits -->
| ID | Bekannte Prüfgrenze |
|---|---|
| PG-01 | Aussagen in Worten ohne Zahl (etwa „in keiner Zelle“) prüft die Paketprüfung nicht gegen die Rechner; kritische Aussagen sind deshalb über Zählwerte gebunden (calc:dmc_class_count, calc:gate_today). |
| PG-02 | Die Suche nach ungebundenen Zahlen lässt Gliederungs-, Kennungs-, Datums-, Versions- und Rechtsaktnummern sowie die Konstanten 0 und 1 zu (Liste NUM_ALLOW in validation/validate_package.py); eine als Kennung getarnte Zahl würde nicht erkannt. |
| PG-03 | Werden Eingaben und Ergebnisse gemeinsam und konsistent geändert (Rechner neu gelaufen), ist das eine zulässige Änderung und keine Mutation; die Paketprüfung erkennt dann nur Widersprüche zu Registern, Siegel und Texten. |
| PG-04 | Zeitabhängige Tatsachen (Gebühren, Spezifikationen, Rechtslage) prüft die Paketprüfung nur über Status und Belege im Quellenregister, nicht gegen die Primärquelle; die Aktualität verantwortet der Abruf mit Datum. |
| PG-05 | Im Mutationslauf prüft P07 nur die Eingangs-Hashes (--calc-mode hash); Änderungen am Code eines Rechners erkennt dort erst P10 oder der vollständige Lauf von run_calculators --check. |
| PG-06 | Die Satzzählung der Betreiberfassungen ist eine Heuristik mit Abkürzungsliste; ungewöhnliche Abkürzungen können als Satzende zählen. |
| PG-07 | Personenbezogene Daten werden über Muster (E-Mail, Telefonnummer, IBAN) gesucht; Namen ohne Muster erkennt die Prüfung nicht. Der Name des Betreibers ist im Wortlaut der Betreiberantwort entfernt (R-13). |
| PG-08 | Die Referenztests der Strategien prüfen konstruierte Preisreihen; sie belegen die Regeln, nicht eine Kante (R-02). |
| PG-09 | Das Siegel der Betreiberangaben schützt vor unbemerkten Änderungen, nicht vor einer gemeinsamen Änderung von Angabe und Siegel; diese ist nur mit neuer, signierter Betreiberentscheidung zulässig und im Entscheidungsregister sichtbar. |
| PG-10 | Der Linter prüft research/reference_strategies/tf_d1_baseline.py nicht: Die Datei ist bytegleich aus v2.0 übernommen (Vergleichsbasis S-BASE); sie läuft aber in den Referenztests unter -W error. |
| PG-11 | Laufbelege entstehen nacheinander (Mehrversionslauf, Mutationslauf, Prüfung vor dem Packen). Belege, die im laufenden Zyklus erst entstehen, nennt --pending-evidence; vollständig mit Paketstand geprüft werden alle drei erst in der Prüfung nach frischem Entpacken. |
| PG-12 | Der Mehrversionslauf vergleicht die Versionen der installierten Pakete mit den Pins; die Hashes prüft pip bei der Installation (--require-hashes), nicht die Paketprüfung. |
| PG-13 | Im Mutationslauf meldet P13 bei jeder Inhaltsänderung zusätzlich den abweichenden Paketstand; als erkannt zählt eine Mutation trotzdem nur, wenn ihr eigenes Fehlermuster erscheint. |
<!-- GEN:END tab.check_limits -->

## §20 Bewertung

> **Betreiberfassung.** Die Selbstbewertung ergibt K = <!--v:calc:score_k_total|d2-->64,75<!--/v--> von <!--v:param:P-SCORE-MAX|d0-->100<!--/v--> Punkten und E = <!--v:calc:score_e_total|d0-->0<!--/v--> von <!--v:param:P-SCORE-MAX|d0-->100<!--/v--> Punkten (`audit/scorecard_K.json`, `audit/scorecard_E.json`). K misst Qualität und Entscheidungsreife des Pakets, E die in der realen Welt nachgewiesene Reife; keiner der beiden misst Gewinn. Das größte Risiko ist eine zu günstige Selbstbewertung wie in v2.0, deshalb ist jeder Abzug begründet und K ohne unabhängige Gegenprüfung auf höchstens <!--v:param:P-SCORE-K-CAP|d0-->99<!--/v--> begrenzt. Offen ist die Gegenprüfung durch eine andere Modellfamilie oder eine fachkundige Person (X-REVIEW, `audit/independent_review_request.md`). Für Go/No-Go heißt das: Auch ein höherer K-Wert rechtfertigt kein Echtgeld, solange E bei null steht. Nächster Schritt: die Gegenprüfung beauftragen.

### 20.1 Konzept-Score K (Selbstbewertung)

Grundlage ist eine interne Gegenlese in vier Blöcken gegen die Bedingungen „Vollpunkte nur, wenn …“ aus dem Raster; ihre Befunde sind entweder behoben oder als Abzug begründet (`audit/concept_review.md`). Die Gegenlese stammt von derselben Modellfamilie und ersetzt die unabhängige Prüfung nicht. Vollpunkte erhalten <!--v:calc:score_k_factor_count/1|int-->2<!--/v--> Unterkriterien, Faktor <!--v:param:P-SCORE-FACTORS/3|d2-->0,75<!--/v--> <!--v:calc:score_k_factor_count/0.75|int-->22<!--/v-->, Faktor <!--v:param:P-SCORE-FACTORS/2|d1-->0,5<!--/v--> <!--v:calc:score_k_factor_count/0.5|int-->8<!--/v-->, Faktor <!--v:param:P-SCORE-FACTORS/1|d2-->0,25<!--/v--> <!--v:calc:score_k_factor_count/0.25|int-->0<!--/v--> und null Punkte <!--v:calc:score_k_factor_count/0|int-->4<!--/v-->; insgesamt fehlen <!--v:calc:score_k_lost|d2-->35,25<!--/v--> Punkte.

<!-- GEN:BEGIN tab.score_k -->
| UK | Unterkriterium | Pkt. | Faktor | Punkte | Abzug begründet durch |
|---|---|---|---|---|---|
| A1 | Kostenmodell je Instrument | 5 | 0,75 | 3,75 | Währungsumrechnungskosten (USD-Margin und -Ergebnis auf dem EUR-Konto) fehlen als Kostenart; Börsen- und Clearinggebühren stecken nur in einer pauschalen, teilweise belegten All-in-Kommission und sind nicht je Kontrakt modelliert. |
| A2 | Steuern, Aufbau- und Betriebszeit | 4 | 0,50 | 2,00 | Steuerszenarien B1 und B2 fehlen (nach BQ-03 nur pauschale Sensitivität, DEC-CF-01); die Kosten der externen Rechts- und Steuerperson sind nicht eingerechnet. |
| A3 | Monte-Carlo-Entscheidungsrechnung | 5 | 0,75 | 3,75 | Die Dimension Betriebsmodell fehlt (nur Eigenkonto, BQ-02, DEC-CF-03); der Break-even ist nur operativ (Fixkosten / Mehrertragsrate) ohne Aufbaukosten definiert. |
| A4 | Kauf-statt-Bau und Varianten | 3 | 0,75 | 2,25 | V2 ist nur als Näherung ohne Monte-Carlo bewertet, V3 als V4 mit kleinerem Aufbau; ein eigenständiger Risikovergleich für V2 und V3 fehlt. |
| A5 | Geschäftsmodell je Betriebsmodell | 3 | 0,00 | 0,00 | B1 bis B4 sind nach der Betreiberentscheidung BQ-02 nicht bewertet (DEC-CF-03); Kosten der Institution, Mindest-AUM und Abbruchkriterien je Betriebsmodell fehlen vollständig. |
| B1 | Strategiefamilie | 4 | 0,75 | 3,00 | Kombination und Positionspuffer (P-STR-BUFFER) sind nur spezifiziert, weder implementiert noch getestet; die Tests prüfen Signal und Haltedauer, nicht die Skalierung. |
| B2 | Prior | 4 | 0,75 | 3,00 | Die Korrelationen und der maßgebliche Abschlag für die Trendfolge sind unbelegte Annahmen; der Referenztest prüft den Diversifikationsmultiplikator, nicht die Abschläge. |
| B3 | Universum und Zulassung | 4 | 0,50 | 2,00 | Das Zinsuniversum ist nicht vollständig (unter anderem Fed-Funds-Futures, dreijährige T-Note, kurze BTP-Futures fehlen); Volatilität, Spread, Tagesvolumen und Margin sind unbelegte Planwerte bis zur Messung in G2. |
| B4 | Kapazität und Robustheit | 3 | 0,75 | 2,25 | Die Grenze gegenüber dem Open Interest wird mangels Daten nicht gerechnet; der Plan für Regime und Teilperioden ist nur als Torbedingung formuliert, nicht operationalisiert. |
| C1 | Forschungsprotokoll | 3 | 0,75 | 2,25 | Purged Cross-Validation für ML ist nur benannt und mit einem Embargo parametrisiert, ohne Spezifikation des Purging, Referenzimplementierung oder Test. |
| C2 | Tore mit Futility | 4 | 0,75 | 3,00 | In der registrierten Konfiguration stoppt die Futility-Regel zusätzlich nichts (die DSR-Schwelle stoppt vorher); Einsparungen gibt es nur in Sensitivitäten und dort zum Teil durch verlorene brauchbare Strategien. |
| C3 | Holdout, Posterior, Monitore | 3 | 0,75 | 2,25 | Futility im Betrieb (MH-R2) und Umschlagsdrift (MD-R2) sind nicht simuliert; der Harm-Monitor erkennt leicht schädliche Strategien praktisch nie – der Schutz hängt an Drawdown-Leiter und Tagesgrenze. |
| D1 | Hebeldefinitionen und Profile | 3 | 0,75 | 2,25 | Die Kalibrierung ruht auf Annahmewerten für Volatilität und Margin; der Bandbericht fehlt für die kalibrierten Allokationen mit Wunschhebel. |
| D2 | Kelly, Ruin, Drawdown, ES | 3 | 0,75 | 2,25 | Der Korrelationsschock ist nur als Volatilitätsregime abgebildet; ES liegt nur jährlich und parametrisch für einen Tag vor (kein Zehn-Tage- und kein historisches ES); eine Zwangsliquidation wird in der Pfadsimulation nicht abgebildet. |
| D3 | Limits und Liquidität | 2 | 0,75 | 1,50 | Netto-Hebel, VaR und Monatsverlust sind keine eigenen harten Grenzen, und die Clustergrenze ist nur informativ. |
| D4 | Stress und Stufenleiter | 2 | 0,75 | 1,50 | Für die registrierte Allokation beruhen viele historische Szenarien auf Ersatzwerten, weil belegte Klassenbewegungen fehlen. |
| E1 | OMS/EMS-Zustände | 3 | 0,75 | 2,25 | Notfalljournal und Fail-Stop sind nur Sperrgründe, kein eigener Automat; die Wiederverwendung einer Befehlskennung mit anderem Inhalt steht nur als Invariante; die Traces decken nicht alle Übergänge des Orderautomaten ab. |
| E2 | Brokersemantik | 3 | 0,50 | 1,50 | Die Killer-Tests sind nicht je Börsengruppe (CME, CBOT, NYMEX, COMEX, Eurex) angelegt, sondern je Test einmal; die Reihenfolge nach Informationswert ist nicht belegt. |
| E3 | Pre-Trade und Kill-Switch | 2 | 0,50 | 1,00 | Die Ausrichtung an RTS 6 ist ohne Artikelzuordnung; Selbstbewertung (Art. 9) und Marktmissbrauchsüberwachung (Art. 13) fehlen; außer der Lückenregel ist keine Kontrolle im Paket ausgeführt. |
| E4 | TCA, Rollen, Sonderfälle | 2 | 0,75 | 1,50 | Die Preislimits je Kontrakt sind nicht belegt, und für Schlupf und Marktwirkung fehlt ein Schätzverfahren. |
| F1 | Architektur | 3 | 0,75 | 2,25 | Der tragende Zonenschnitt ist offen (X-INF-ZONES); die Ein-VPS-Variante ist nur als Restrisiko beschrieben, nicht ausgearbeitet. |
| F2 | Sicherheit | 3 | 0,75 | 2,25 | Der Pentest-Plan nennt weder Methode noch Nachtest; das SBOM-Format ist offen; die Projektschnittstelle in den Geldpfad-Host bleibt bis zur Entscheidung über das Pull-Modell ein Restrisiko. |
| F3 | KI-Schicht | 2 | 0,75 | 1,50 | Die Anwendbarkeit der KI-Verordnung ist nicht geprüft, sondern an die externe Person übergeben (BQ-03). |
| F4 | Modellrisikomanagement | 2 | 1,00 | 2,00 | – |
| G1 | Rollen und Kontrolle | 3 | 0,50 | 1,50 | Risikofunktion und Vertretung sind nicht besetzt; ohne zweite Person gibt es kein menschliches Vier-Augen-Prinzip (Klassen C und D sind gesperrt); Mindestbesetzung nur für das Eigenkonto. |
| G2 | Betriebsprozesse | 3 | 0,75 | 2,25 | Viele Runbooks sind knappe Skelette; das Quittungs-SLO für kritische Incidents ist ohne Vertretung nicht zusicherbar. |
| G3 | Kontinuität | 2 | 0,75 | 1,50 | Die Vertretung ist nicht benannt; die Auslagerungssteuerung hat keine Kritikalitätseinstufung, keine laufende Überwachung und keine Prüfrechte. |
| H1 | Anwendbarkeitsmatrix | 2 | 0,00 | 0,00 | Nach BQ-02 und BQ-03 ist keine Anwendbarkeitsprüfung für B1 bis B4 enthalten (DEC-CF-03, DEC-CF-01); die Matrix stellt Fragen an die externe Person statt Befunde. |
| H2 | Steuern | 2 | 0,00 | 0,00 | Weder ein Privat- noch ein Gesellschaftsszenario ist gerechnet; nach BQ-03 gibt es nur die pauschale Sensitivität (DEC-CF-01). |
| H3 | Verträge und Marktverhalten | 1 | 0,50 | 0,50 | Vertragsinhalte sind unbelegt; Marktmissbrauchskontrollen beschränken sich auf Vorhandelsprüfungen; Positionslimits und Meldeschwellen der Börsen fehlen. |
| I1 | Bauprogramm | 3 | 0,75 | 2,25 | Die Vertretung hat keine Kostenposition, und die Risikofunktion ist erst ab BS-09 bepreist, obwohl sie ab G8 empfohlen ist. |
| I2 | Tests und Referenzmodelle | 2 | 0,50 | 1,00 | Viele Orakel sind nur Stichworte; für PBO, SPA, Romano-Wolf und die Baustufenkosten fehlen unabhängige Referenzmodelle; die Datenbeschaffung BS-02 läuft parallel zu den Killer-Tests. |
| I3 | Paketprüfung | 2 | 1,00 | 2,00 | – |
| J1 | Lesbarkeit | 2 | 0,50 | 1,00 | Das Masterkonzept ist ohne Vorwissen kaum lesbar: sehr dicht, mit vielen Kennungen und Fachbegriffen; das Glossar mildert das nur. |
| J2 | Nachvollziehbarkeit | 2 | 0,75 | 1,50 | Die Statusprüfung ist strukturell: Sie erkannte nicht, dass drei Testeinträge mehr versprachen, als die Tests prüften, und dass ein Befund zu günstig eingestuft war (beides in der Gegenlese gefunden und korrigiert). |
| J3 | Unabhängige Prüfung | 1 | 0,00 | 0,00 | Keine unabhängige Gegenprüfung durchgeführt; die interne Gegenlese stammt von derselben Modellfamilie und zählt nicht (EV-11). |
<!-- GEN:END tab.score_k -->

Drei Unterkriterien (A5, H1, H2) sind ohne Punkte, weil die Betreiberentscheidungen BQ-02 und BQ-03 Betriebsmodelle, Recht und Steuern aus dem Systemumfang nehmen (DEC-CF-01, DEC-CF-03); das Raster wird dafür nicht umgedeutet (R-09). J3 bleibt null, bis eine unabhängige Gegenprüfung bestanden ist.

### 20.2 Punktregeln

Faktoren nur aus P-SCORE-FACTORS (<!--v:param:P-SCORE-FACTORS/0|d0-->0<!--/v-->, <!--v:param:P-SCORE-FACTORS/1|d2-->0,25<!--/v-->, <!--v:param:P-SCORE-FACTORS/2|d1-->0,5<!--/v-->, <!--v:param:P-SCORE-FACTORS/3|d2-->0,75<!--/v--> oder <!--v:param:P-SCORE-FACTORS/4|d0-->1<!--/v-->); keine Aufrundung; die Summe rechnet die Paketprüfung (P12, `validation/semantic_checks.py::check_scores`); jeder Abzug ist begründet; ohne Gegenprüfung ist K höchstens <!--v:param:P-SCORE-K-CAP|d0-->99<!--/v-->.

### 20.3 Evidenz-Score E

<!-- GEN:BEGIN tab.score_e -->
| Baustein | Pkt. | Nachweis nach §20.3 | Tore | Punkte | Stand |
|---|---|---|---|---|---|
| E-1 | 10 | Betreibereingaben bestätigt; Wirtschaftlichkeit mit echten Gebühren (G0) | GATE-G0 | 0 | G0 heute BLOCKED_EXTERNAL (GC-G0-101): Gebühren, Stundensatz, Budget, Verzinsung und V1-Produkte unbestätigt |
| E-2 | 10 | Kontozugang, Killer-Tests bestanden (G1) | GATE-G1 | 0 | kein signiertes Torergebnis; das Tor ist heute gesperrt oder noch nicht erreicht |
| E-3 | 10 | Lizenzierte Daten, Abgleich, Leckagetests (G2) | GATE-G2 | 0 | kein signiertes Torergebnis; das Tor ist heute gesperrt oder noch nicht erreicht |
| E-4 | 10 | Forschungstore G3 und G4 bestanden, einschließlich Futility | GATE-G3, GATE-G4 | 0 | kein signiertes Torergebnis; das Tor ist heute gesperrt oder noch nicht erreicht |
| E-5 | 15 | System gebaut, Abnahmetests bestanden, Prüfmodul ohne Abweichung (G5) | GATE-G5 | 0 | kein signiertes Torergebnis; das Tor ist heute gesperrt oder noch nicht erreicht |
| E-6 | 10 | Drills bestanden (G6) | GATE-G6 | 0 | kein signiertes Torergebnis; das Tor ist heute gesperrt oder noch nicht erreicht |
| E-7 | 10 | Paper-Forward bestanden (G7) | GATE-G7 | 0 | kein signiertes Torergebnis; das Tor ist heute gesperrt oder noch nicht erreicht |
| E-8 | 10 | Pilot H5 bestanden, Kosten im Modellband (G8) | GATE-G8 | 0 | kein signiertes Torergebnis; das Tor ist heute gesperrt oder noch nicht erreicht |
| E-9 | 15 | mindestens zwölf Monate Standardbetrieb ohne schwere Incidents, Stufenleiter regelkonform, externes Audit ohne wesentliche Feststellung (G9, G10) | GATE-G9, GATE-G10 | 0 | kein signiertes Torergebnis; das Tor ist heute gesperrt oder noch nicht erreicht |
<!-- GEN:END tab.score_e -->

E-Punkte gibt es nur mit einem signierten Torergebnis des Prüfmoduls und einem Laufbeleg im Paket; heute ist kein Tor bestanden, und G0 ist wegen unbestätigter Eingaben gesperrt (GC-G0-101).

### 20.4 Unabhängige Gegenprüfung

Der Prüfauftrag in `audit/independent_review_request.md` richtet sich an eine fachkundige Person oder ein Modell einer anderen Modellfamilie in frischer Sitzung: Es rechnet zentrale Zahlen mit eigenem Code nach, führt Paketprüfung und Mutationstests aus und vergibt K-Punkte je Unterkriterium. Weicht das Ergebnis um mehr als <!--v:param:P-SCORE-REVIEW-DEV|d0-->5<!--/v--> Punkte von dieser Selbstbewertung ab, werden die Befunde aufgelöst und erneut geprüft; das Ergebnis kommt ins Paket (EV-11). Beauftragen muss der Betreiber (X-REVIEW).

### 20.5 Vergleich v2.0 → v3.0

Das neue Raster ist auf das Raster der Ausgangsbewertung (§3.4) abgebildet; die Zuordnung der Kriterien des v2.0-Rasters zu den Unterkriterien steht in `audit/v2_to_v3_mapping.json#/criteria_mapping`. Der Vergleich stellt die unabhängige Bewertung von v2.0 neben die Selbstbewertung von v3.0; aussagekräftig wird er erst mit der Gegenprüfung.

<!-- GEN:BEGIN tab.score_compare -->
| Bereich | Name | Pkt. | v2.0 unabhängig (§3.4) | v3.0 Selbstbewertung | Hauptmangel v2.0 | größter Abzug v3.0 |
|---|---|---|---|---|---|---|
| A | Wirtschaftlichkeit und Business Case | 20 | 7,0 | 11,75 | Kostenwiderspruch; Steuern und Aufbauaufwand fehlen; kein Kauf-statt-Bau-Vergleich | A5: B1 bis B4 sind nach der Betreiberentscheidung BQ-02 nicht bewertet (DEC-CF-03); Kosten der Institution, Mindest-AUM und Abbruchkriterien je Betriebsmodell fehlen vollständig. |
| B | Strategie und Edge | 15 | 6,0 | 10,25 | Einzelregel auf 16 Micro-Kontrakten; kein eigener Beleg | B3: Das Zinsuniversum ist nicht vollständig (unter anderem Fed-Funds-Futures, dreijährige T-Note, kurze BTP-Futures fehlen); Volatilität, Spread, Tagesvolumen und Margin sind unbelegte Planwerte bis zur Messung in G2. |
| C | Statistik, Tore, Forschungsdesign | 10 | 8,0 | 7,50 | Keine frühe Futility-Regel | C2: In der registrierten Konfiguration stoppt die Futility-Regel zusätzlich nichts (die DSR-Schwelle stoppt vorher); Einsparungen gibt es nur in Sensitivitäten und dort zum Teil durch verlorene brauchbare Strategien. |
| D | Risiko, Kapital und Hebel | 10 | 8,0 | 7,50 | Margin- und Liquidationsmechanik des Brokers | D2: Der Korrelationsschock ist nur als Volatilitätsregime abgebildet; ES liegt nur jährlich und parametrisch für einen Tag vor (kein Zehn-Tage- und kein historisches ES); eine Zwangsliquidation wird in der Pfadsimulation nicht abgebildet. |
| E | Geldpfad und Ausführung | 10 | 7,0 | 6,25 | Kernmechanik beim Broker unbelegt und spät getestet | E2: Die Killer-Tests sind nicht je Börsengruppe (CME, CBOT, NYMEX, COMEX, Eurex) angelegt, sondern je Test einmal; die Reihenfolge nach Informationswert ist nicht belegt. |
| F | Architektur, Sicherheit, KI | 10 | 6,0 | 8,00 | Nutzen der KI unbelegt; für den Maßstab überdimensioniert | F2: Der Pentest-Plan nennt weder Methode noch Nachtest; das SBOM-Format ist offen; die Projektschnittstelle in den Geldpfad-Host bleibt bis zur Entscheidung über das Pull-Modell ein Restrisiko. |
| G | Betrieb und Organisation | 8 | 4,0 | 5,25 | Einzelbetreiber; kein menschliches Vier-Augen-Prinzip | G1: Risikofunktion und Vertretung sind nicht besetzt; ohne zweite Person gibt es kein menschliches Vier-Augen-Prinzip (Klassen C und D sind gesperrt); Mindestbesetzung nur für das Eigenkonto. |
| H | Recht, Steuern, Compliance | 5 | 3,0 | 0,50 | Steuern nicht modelliert | H2: Weder ein Privat- noch ein Gesellschaftsszenario ist gerechnet; nach BQ-03 gibt es nur die pauschale Sensitivität (DEC-CF-01). |
| I | Umsetzungsprogramm und Verifikation im Paket | 7 | 2,0 | 5,25 | Kein Produktionscode; 132 von 149 Tests nur geplant | I2: Viele Orakel sind nur Stichworte; für PBO, SPA, Romano-Wolf und die Baustufenkosten fehlen unabhängige Referenzmodelle; die Datenbeschaffung BS-02 läuft parallel zu den Killer-Tests. |
| J | Dokumentation und Integrität | 5 | 4,5 | 2,50 | Sehr dicht; Konzeptprüfung durch dasselbe Modell | J3: Keine unabhängige Gegenprüfung durchgeführt; die interne Gegenlese stammt von derselben Modellfamilie und zählt nicht (EV-11). |
|  | Summe | 100 | 55,5 | 64,75 |  |  |
<!-- GEN:END tab.score_compare -->

## §21 Befunde und ihre Auflösung

> **Betreiberfassung.** Jeder Befund aus der unabhängigen Bewertung von v2.0 (EV-01 bis EV-13) und aus der Konzeptprüfung CR-5 hat einen Eintrag mit Status, Behandlung, Nachweis und Restrisiko (`registers/resolution_matrix.json`). Im Paket nachgewiesen aufgelöst sind <!--v:calc:findings_by_status/AUFGELOEST|int-->12<!--/v-->, im Konzept gelöst mit Wirkung erst in Bau oder Betrieb <!--v:calc:findings_by_status/AUFGELOEST_IM_KONZEPT|int-->4<!--/v-->, teilweise <!--v:calc:findings_by_status/TEILWEISE|int-->3<!--/v-->, und <!--v:calc:findings_by_status/OFFEN_EXTERN|int-->1<!--/v--> hängen an einer externen Eingabe. Das größte Restrisiko sind die institutionellen Lücken (EV-13): Vier-Augen-Prinzip und unabhängige Risikofunktion lassen sich nur mit benannten Personen schließen. Offen ist vor allem die unabhängige Gegenprüfung (EV-11, X-REVIEW). Für Go/No-Go heißt das: Kein offener Befund sperrt Demo und Forschung; Echtgeld bleibt aus wirtschaftlichen Gründen No-Go. Nächster Schritt: Vertretung und Risikofunktion benennen und die Gegenprüfung beauftragen.

<!-- GEN:BEGIN tab.resolution -->
| ID | Befund | Status | Behandlung | Nachweis | Restrisiko |
|---|---|---|---|---|---|
| EV-01 | Kostenwiderspruch: Spreadannahmen plus Kommission lagen über den Kostensätzen des Wirtschaftsmodells. | AUFGELOEST | Kosten je Instrument nur noch aus registers/costs.json und financials/cost_model.py; jede Kostenzahl im Text ist gebunden; semantische Prüfung COST; Mutation 'Spread ohne Kostenanpassung'. | registers/costs.json, financials/cost_model.py, financials/cost_model_results.json, T-CALC-COST-001, T-SEM-COST-001, validation/mutation_tests.py | Gebühren und Spreads bis zur Bestätigung (X-BRK-FEES) und Messung (X-DATA-VOL) Annahmen. |
| EV-02 | Steuern und Aufbauaufwand fehlten; Betreiberzeit im Aufbau unbewertet. | TEILWEISE | Aufbauaufwand je Stufe (Mensch und Agent) mit Kosten; Betreiberroutinen in Paper, Pilot und Standardbetrieb und Pflege des Agenten bewertet. Steuern nach BQ-03 nur als pauschale Sensitivität (DEC-CF-01): Szenarien privat und Gesellschaft fehlen, die Kosten der externen Rechts- und Steuerperson sind nicht eingerechnet. | financials/tax_scenarios.py, implementation/build_stages.json, financials/stage_costs.py, financials/decision_montecarlo_results.json, T-CALC-TAX-001 | Steuerszenarien und Beratungskosten durch die externe Person (X-TAX-01). |
| EV-03 | Schlechtes Verhältnis von Ertrag zu Risiko; LLM-Budget entsprach dem Überschuss. | AUFGELOEST | Wert je Risikoeinheit, P(NPV > 0), Break-even und Sensitivitäten in allen Entscheidungstabellen; KI-Kosten und Pflegezeit enthalten. | financials/decision_montecarlo.py, financials/decision_montecarlo_results.json, T-CALC-DMC-001 | Befund bleibt negativ: Echtgeld No-Go in allen Stufen und Profilen. |
| EV-04 | Kein Kauf-statt-Bau-Vergleich. | AUFGELOEST | Varianten V0 bis V4 mit Entscheidungsregel in der Prüfreihenfolge von §5.7 (Befundklasse vor Dominanz) und Befundklasse DOMINATED_BY_ALTERNATIVE; V4 ist die registrierte Familie, das Sensitivitätsuniversum steht daneben; V2 nur als Näherung; G0 scheitert bei unzulässigem Profil (G0-R3) oder Dominanz (G0-R4). | financials/buy_vs_build.md, financials/decision_montecarlo_results.json, research/evidence_gates.json, T-CALC-DMC-002 | Konkrete Fondsprodukte für V1 offen (X-V1-PRODUCTS). |
| EV-05 | Tore stoppen zu spät: eine Strategie ohne Edge bestand die Tore E1 und E2 zu etwa 89 %. | AUFGELOEST | Deflationiertes G3, einmaliger Holdout, Futility-Regel nach G3 und G4; Betriebscharakteristik je 4.000 Strategien mit und ohne Regel simuliert. In der registrierten Konfiguration stoppt schon die DSR-Schwelle in G3 fast alle Strategien ohne Kante; die Futility-Regel stoppt dort zusätzlich nichts und wirkt erst bei gelockerter Schwelle, dann auch auf brauchbare Strategien. | research/operating_characteristics.py, research/operating_characteristics_results.json, research/evidence_gates.json, T-CALC-OC-001, T-SEM-GATE-001 | Geringe Teststärke: brauchbare Strategien bestehen G3 selten (Tausch gegen Fehlalarme dokumentiert). |
| EV-06 | Brokermechanik unbelegt und spät getestet. | AUFGELOEST_IM_KONZEPT | Sechzehn Killer-Tests mit Orakel und Rückfallvariante als erstes Tor G1 vor jedem Systembau; MT5-Semantik aus der Anbieterdokumentation belegt. | implementation/test_catalog.json, execution/broker_killer_tests.md, research/evidence_gates.json, SRC-MT5-API | Tests erst nach Kontoeröffnung durch den Betreiber ausführbar (X-BRK-ACCOUNT). |
| EV-07 | Kostendrift-Monitor wirkungslos im Pilot. | AUFGELOEST | Gepoolte, geschrumpfte Schätzung über alle Instrumente; Auslösezeit simuliert. | operations/costdrift_monitor.py, operations/costdrift_results.json, T-CALC-DRIFT-001, research/evidence_gates.json | Streuung je Fill (P-MON-FILL-NOISE (1,50 Faktor)) erst ab G1 kalibriert. |
| EV-08 | Datenhistorie der Micro-Kontrakte zu kurz; keine Proxy-Regel; MTN ≠ ZN. | AUFGELOEST | Historie als Zulassungskriterium (DEC-DS-24); Proxy-Regeln PX-1 bis PX-6 nur auf denselben Basiswert; MTN ausdrücklich kein Proxy für ZN. | data/proxy_rules.md, registers/instruments.json, research/prior_results.json, T-CALC-PRIOR-002, T-SEM-PROXY-001 | Listungsdaten und Historie beim Anbieter bestätigen (X-DATA-HIST). |
| EV-09 | Margin: Echtzeit-Liquidation des Brokers gegenüber manuellem Nachschuss. | AUFGELOEST_IM_KONZEPT | Größen immer mit Übernacht-Margin; Margin-Level auf das Guthaben beim Broker bezogen (P-ECO-CASH-AT-BROKER (0,25 Anteil)); De-Risking ab P-MRG-DERISK-TRIGGER (1,50 Anteil der Initial-Margin) vor dem Stop-out; je Allokation und Profil der nötige Anteil beim Broker gerechnet, auch nach Margin-Verdopplung und bei Handelsaussetzung (risk/stress_results.json); Runbook und Drill. | risk/margin_liquidity.md, operations/runbook_register.json, operations/drill_register.json, T-RISK-MRG-001, architecture/state_machines.json | Liquidationsregel des Brokers unbelegt (X-BRK-LIQ, KT-13); der Planwert beim Broker reicht für die registrierte Allokation knapp und für hohe Hebel deutlich nicht – vor jedem Grant ist der nötige Anteil umzuschichten. |
| EV-10 | 'KI-Trading' nur als Etikett; Nutzen von Hermes unbelegt; hohe Änderungsrate upstream. | AUFGELOEST_IM_KONZEPT | KI außerhalb des Geldpfads; Nutzenbilanz je Quartal (MON-AI) mit Rückbaukriterium; Update nur als Release mit Evaluationssuite; Upstream-Kennzahlen belegt. | ai/ai_layer.md, ai/hermes_integration.md, research/evidence_gates.json, architecture/state_machines.json, SRC-HERMES-UPSTREAM | Nutzen erst im Betrieb messbar. |
| EV-11 | Selbstprüfung durch dasselbe Modell; Selbstbewertung weit über der unabhängigen Bewertung. | OFFEN_EXTERN | K höchstens 99 bis zur Gegenprüfung; Prüfauftrag mit eigenem Nachrechnen und Paketprüfung für eine andere Modellfamilie oder eine fachkundige Person. | audit/independent_review_request.md, audit/scorecard_K.json, X-REVIEW | Gegenprüfung durch den Betreiber zu beauftragen (X-REVIEW). |
| EV-12 | Kleinmängel: Escape-Sequenz, unbenutzte Variable, Dateiname der .sha256, kein Mehrversionslauf. | AUFGELOEST | Linter und Läufe unter Python 3.11 bis 3.13 mit -W error; Prüfsummendatei mit identischem Namen; Prüfung nach frischem Entpacken. | validation/execution_log.txt, validation/validate_package.py, T-PKG-MULTI-001 | – |
| EV-13 | Institutionelle Lücken: Einzelbetreiber, kein menschliches Vier-Augen-Prinzip, keine unabhängige Risikofunktion, kein Lizenzpfad, kleines Universum. | TEILWEISE | Notfallvertretung und externe Risikofunktion mit Sperrwirkung (G8, G9); Vier-Augen-Prinzip für Klassen C und D; Rechtsmatrix als Übergabe; Kandidatenuniversum mit mehr als 60 Futures. Offen bleibt, was nur Personen lösen können: Ohne benannte zweite Person gibt es kein menschliches Vier-Augen-Prinzip (Klassen C und D sind bis dahin gesperrt, DEC-CF-06), und die unabhängige Risikofunktion ist erst ab G9 Pflicht; Lizenzpfad und Betriebsmodelle B2 bis B4 sind nach BQ-02 nicht bewertet. | governance/organisation_raci.md, legal/applicability_matrix.md, registers/instruments.json, research/evidence_gates.json | Personen nicht benannt (X-ORG-DEPUTY, X-ORG-RISK); Rechtsfragen extern (X-LEGAL-01). |
| CR5-01 | Prior nur erzählend hergeleitet (v2.0 CR-5). | AUFGELOEST | Rechnerische Herleitung aus der Literaturtabelle mit Abschlägen, Unsicherheit und Korrelationen. | research/prior_derivation.py, research/prior_results.json, T-CALC-PRIOR-001 | Literatur überwiegend zu langsameren Horizonten. |
| CR5-02 | Tore trennen schwach (v2.0 CR-5). | AUFGELOEST | wie EV-05 | research/operating_characteristics_results.json, research/evidence_gates.json | wie EV-05 |
| CR5-03 | Ausstiegsverbund beim Broker unbelegt (v2.0 CR-5). | AUFGELOEST_IM_KONZEPT | MT5 kennt keinen Ausstiegsverbund; Schutz als SL der Position beim Broker, Schließen mit position=Ticket; KT-06 und KT-07 prüfen das Verhalten. | execution/oms_ems.md, implementation/test_catalog.json, architecture/state_machines.json | KT-06 ausstehend. |
| CR5-04 | Liquiditätszeiten je Instrument fehlen (v2.0 CR-5). | TEILWEISE | Planwerte je Instrument im Register; Messung in G2 (X-DATA-LIQ) ist Voraussetzung von G3. | registers/instruments.json, research/evidence_gates.json | Messung ausstehend. |
| CR5-05 | Verpasste Wochenanmeldung im Lieferfenster (v2.0 CR-5). | AUFGELOEST | Keine Position im Rollfenster P-UNI-ROLL-DAYS (5 Geschäftstage) vor FND/LTD; Schließen im Rollfenster unabhängig vom Signal; Runbook RB-18. | architecture/state_machines.json, operations/runbook_register.json, T-EXE-010 | Kalender des Brokers mit KT-11 abgleichen. |
| CR5-06 | Keine Schutzaktion ohne gültige Lease (v2.0 CR-5). | AUFGELOEST | Schutz hängt nicht an der Lease: SL liegt beim Broker (DEC-DS-20); ohne Lease sendet der Kern keine Einstiege; externer Monitor und Brokerdirektkontrolle (RB-15). | registers/decision_register.json, architecture/state_machines.json, operations/runbook_register.json | KT-06 ausstehend. |
| CR5-07 | Prüfgrenzen des Pakets (v2.0 CR-5). | AUFGELOEST | Bekannte Prüfgrenzen im Prüfbericht und im README dokumentiert; Mutationstests belegen die Erkennung. | validation/validation_report.json, validation/mutation_tests.py, README.md | Prüfgrenzen bleiben (z. B. Wahrheit externer Quellen). |
<!-- GEN:END tab.resolution -->

Statuswerte: AUFGELOEST – im Paket nachgewiesen; AUFGELOEST_IM_KONZEPT – spezifiziert und geprüft, Wirksamkeit erst im Bau oder Betrieb messbar; TEILWEISE – ein Teil ist offen; OFFEN_EXTERN – hängt an einer externen Eingabe. Die Paketprüfung (P13) prüft, dass jeder genannte Nachweis existiert.

## Rollenabnahmen

Jede Rolle aus §1 des Auftrags hat ihre Kapitel geprüft und hält fest, was mit Laufbeleg geprüft ist, was offen bleibt und welche Restrisiken sie sieht. Alle Rollen wurden von derselben KI eingenommen; diese Abnahmen ersetzen keine unabhängige Prüfung (§20.4, EV-11).

| Rolle | Geprüfte Kapitel | Prüfungen mit Laufbeleg | Offene Punkte | Restrisiken | Empfehlung |
|---|---|---|---|---|---|
| Head of Quant Research | §6, `research/` | T-CALC-PRIOR-001, T-CALC-STAT-001, T-CALC-OC-001, T-STR-TF-001 bis T-STR-CA-001 (P10) | Purged CV für ML nur benannt; Zinsuniversum unvollständig; Kombination und Puffer ohne Implementierung | RK-08, RK-22; Korrelationen und Abschläge im Prior unbelegt | Forschung nur als gedeckelte Ausgabe; kein Echtgeld |
| Chief Risk Officer | §7, `risk/`, Risikoregister | T-CALC-LEV-001, T-CALC-KELLY-001, T-CALC-STRESS-001, T-RISK-MRG-001, T-SEM-LEV-001, T-SEM-STRESS-001 (P09, P10) | Liquidationsregel des Brokers (X-BRK-LIQ); nötiger Anteil beim Broker vor jedem Grant; Ersatzwerte in historischen Szenarien | RK-01, RK-03, RK-19, RK-29 | Kein Profil zulässig; Echtgeld No-Go |
| Head of Trading Technology | §8, §10, `execution/`, `architecture/` | T-SM-001, T-GATE-001, T-CON-001 (P08) | Killer-Tests erst nach Kontoeröffnung (X-BRK-ACCOUNT); Zonenschnitt (X-INF-ZONES); Notfalljournal als Automat | RK-10, RK-18, RK-28 | BS-01 erst nach G0; Killer-Tests vor jedem Systembau |
| Head of Data | §9, `data/` | T-SEM-PROXY-001, T-SEM-CAP-001, TR-DATA-004 (P08, P09) | Historie und Listungsdaten beim Anbieter bestätigen (X-DATA-HIST); Messung von Spread und Volumen (X-DATA-VOL) | RK-11, RK-13 | Daten erst nach G0 lizenzieren |
| Head of AI | §11, `ai/` | T-CON-001, TR-ML-001, TR-ML-004 (P08) | KI-Verordnung und Datenverarbeitung durch die externe Person (X-AI-DPA) | RK-14, RK-15, RK-23, RK-32 | Hermes nur außerhalb des Geldpfads; Rückbau nach Kriterium |
| CISO | §12, `security/`, Bedrohungsmodell | T-SEC-*-Tests sind Bautests; im Paket geprüft: T-CON-001 und die Hygiene (P11) | Penetrationstest (T-SEC-014) mit Methode und Nachtest; SBOM-Format; Pull-Modell der Projektschnittstelle | RK-17, RK-31, RK-32 | Kein Pilot ohne Penetrationstest und getrennte Hinterlegung |
| COO / SRE | §14, `operations/` | T-SEM-RB-001, T-CALC-DRIFT-001, T-CALC-MON-001 (P09, P10) | Vertretung benennen (X-ORG-DEPUTY); Runbooks ausarbeiten; Drills erst im Bau | RK-16, RK-18 | Betrieb nur mit benannter Vertretung (G8) |
| General Counsel, Compliance, Steuern | §15, `legal/` | keine Anwendbarkeitsprüfung im Paket (BQ-03) | Übergabeliste an die externe Person (X-LEGAL-01, X-TAX-01) | RK-24 | Vor G8 extern prüfen lassen |
| CFO / Controlling | §5, `financials/` | T-CALC-COST-001, T-CALC-DMC-001, T-CALC-DMC-002, T-CALC-TAX-001, T-SEM-COST-001 (P09, P10) | echte Gebühren und Stundensatz (X-BRK-FEES, X-OP-RATE); V1-Produkte (X-V1-PRODUCTS) | RK-09, RK-30 | Echtgeld No-Go in allen Stufen und Profilen |
| Head of Model Risk (unabhängige Validierung) | §16, §19, §20 | alle Phasen P01 bis P13 (`validation/validation_report.json`), Mutationstests (T-PKG-MUT-001), Mehrversionslauf (T-PKG-MULTI-001) | unabhängige Gegenprüfung (X-REVIEW); Validierung der Modelle im Inventar | RK-22, RK-23 | Selbstbewertung nur mit Gegenprüfung verwenden |
| Product Owner Betreiber | Kurzfassung, Betreiberfassungen, Betreiberfragen | P06 (Betreiberfassungen), P13 (Kurzfassung mit Go/No-Go) | Entscheidungen zu DEC-CF-02 und Haltedauer; Benennung der Personen | RK-06, RK-16, RK-21 | Demo und Forschung mit Ausgabendeckel; Echtgeld No-Go |

## Glossar

| Begriff | Bedeutung |
|---|---|
| Betreiberfassung | Kurzer Absatz am Kapitelanfang mit Entscheidung, Kennzahl, Risiko, offener Eingabe, Folge für Go/No-Go und nächstem Schritt (höchstens sechs Sätze). |
| Brutto-Hebel L_g | Summe der Beträge aller Positionen (Menge × Multiplikator × Preis × Währungsumrechnung) geteilt durch den NAV. |
| Netto-Hebel L_n | Betrag der Summe aller Positionen mit Vorzeichen geteilt durch den NAV, zusätzlich je Anlageklasse und Risikofaktor. |
| Kontrakt-Hebel | Nominal eines Kontrakts geteilt durch seine Initial Margin; nur informativ. |
| Margin-Auslastung M/E | Initial Margin (zusätzlich Maintenance Margin) geteilt durch den NAV. |
| Margin-Level | Guthaben beim Broker geteilt durch die Initial Margin; unter der eigenen De-Risking-Schwelle wird abgebaut, am Stop-out liquidiert der Broker. |
| Portfolio-Volatilität σ_p | Ex-ante-Schwankung des Portfolios aus Gewichten und Kovarianz (EWMA und Schockregime). |
| VaR und Expected Shortfall (ES) | Verlust, der mit der Konfidenz <!--v:param:P-RISK-VAR-CONF|pct0-->99 %<!--/v--> nicht überschritten wird, bzw. mittlerer Verlust jenseits der Konfidenz <!--v:param:P-RISK-ES-CONF|pct1-->97,5 %<!--/v-->. |
| Stressverlust | Verlust in % des NAV je Szenario aus §7.9 nach Tages- und Drawdown-Leiter. |
| Lückenregel | Größenregel: gleichzeitige ungünstige Lücke aller Positionen mal Wochenendfaktor plus bereits erlittener Tagesverlust bleibt unter der Tagesgrenze abzüglich Reserve. |
| Tagesverlust- und Drawdown-Leiter | Stufen, an denen das System das Risikoziel senkt, Einstiege sperrt oder abbaut (L1 bis L3, DD-L1 bis Kill-Stufe). |
| Diversifikationsmultiplikator D | Summe der Einzelrisiken geteilt durch das Portfoliorisiko. |
| Sharpe-Ratio, Netto-Sharpe | Mittlere Überrendite geteilt durch ihre Schwankung, jährlich; netto heißt nach allen Kosten. |
| Deflated Sharpe Ratio (DSR) | Wahrscheinlichkeit, dass die wahre Sharpe-Ratio positiv ist, bereinigt um die Zahl der Versuche und die Verteilungsform. |
| PBO / CSCV | Wahrscheinlichkeit der Überanpassung, geschätzt durch kombinatorisch symmetrische Kreuzvalidierung. |
| SPA / Romano-Wolf | Tests, ob die beste von vielen Strategien besser ist als der Zufall, mit Korrektur für Mehrfachtests. |
| Purged Cross-Validation | Kreuzvalidierung, bei der überlappende Beobachtungen zwischen Training und Test entfernt und durch ein Embargo getrennt werden. |
| Prior und Posterior | Verteilung der Netto-Sharpe vor den eigenen Daten (aus der Literatur) und danach (fortgeschrieben mit Daten). |
| Holdout | Versiegelter Datenabschnitt, der genau einmal geöffnet wird (G4). |
| Futility-Regel | Abbruch, wenn die Wahrscheinlichkeit, das Endtor zu bestehen, unter die registrierte Schwelle fällt. |
| Betriebscharakteristik | Simulierte Durchlaufquoten der Tore für schädliche, wertlose und brauchbare Strategien. |
| Tor, Torfall, Torergebnis | Feste Regeltabelle vor einer Ausgabe oder Freigabe; Beispiel mit erwartetem Ergebnis; signiertes Ergebnis des Prüfmoduls. |
| Monitor | Laufende Regel im Betrieb, die bei Auslösung genau eine Folge hat (Sperre, Abbau oder Rückbau). |
| Killer-Test | Früher Test beim Broker, der prüft, ob MT5 so arbeitet, wie das Konzept es braucht; mit Orakel und Rückfallvariante. |
| Grant, Lease, Fencing | Befristete Handelserlaubnis; zeitlich begrenzte Schreibberechtigung des aktiven Kerns; Nachweis, dass ein alter Kern nicht mehr senden kann. |
| UNKNOWN | Orderzustand nach Zeitüberschreitung ohne Klärung; das System sendet nie erneut, bevor der Negativnachweis vorliegt. |
| Kill-Switch | Storniert alle offenen Orders und stellt optional geordnet glatt. |
| Implementation Shortfall | Ausführungspreis gegenüber dem Kurs zur Entscheidung, einschließlich Kommission und nicht ausgeführter Menge. |
| Round-Turn | Einstieg und Ausstieg einer Position; Kosten je Round-Turn in EUR oder Basispunkten. |
| Proxy | Standardkontrakt auf denselben Basiswert, dessen Historie für einen jüngeren Micro- oder Mini-Kontrakt genutzt wird. |
| NPV und P(NPV > 0) | Barwert aller Zahlungen über den Horizont und Wahrscheinlichkeit, dass er positiv ist. |
| Wert je Risikoeinheit | Erwarteter Jahreswert geteilt durch die Schwankung des Jahresergebnisses. |
| Befundklasse | Ergebnis der Entscheidungsrechnung je Zelle: VIABLE, MARGINAL, NOT_VIABLE_AT_CAPITAL, NON_POSITIVE_BASE, DOMINATED_BY_ALTERNATIVE, PROFILE_NOT_ADMISSIBLE. |
| Paper und Pilot | Vorwärtstest ohne Echtgeld (G7) und kleiner Echtgeld-Test im Profil H5 (G8). |
| K-Score und E-Score | Qualität des Pakets und nachgewiesene Reife in der realen Welt (§20); keiner misst Gewinn. |
| Paketstand | Hash über alle Inhaltsdateien; Laufbelege tragen den Stand, auf dem sie entstanden. |
