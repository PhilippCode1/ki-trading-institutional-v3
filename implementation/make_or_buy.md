# Make-or-Buy (§17.3)

> **Betreiberfassung.** Für den Handelskern wurden drei verbreitete Open-Source-Frameworks geprüft, NautilusTrader, QuantConnect LEAN und pysystemtrade; keines bindet MetaTrader 5 offiziell an, und nach deiner Vorgabe BQ-08 kommt nur MT5 in Frage. Den MT5-Adapter, die Auftragsverwaltung, den Risikomotor und das Prüfmodul müssten wir also in jedem Fall selbst bauen; ein Framework würde nur Backtest- und Strategierahmen sparen, brächte aber ein fremdes Laufzeitmodell in den Geldpfad. Deshalb baut das Konzept einen eigenen, schlanken Kern und nutzt die Frameworks als Vergleich und Prüfwerkzeug. Kommerzielle Plattformen sind nach BQ-08 ausgeschieden und nicht untersucht. Für Go/No-Go heißt das: Make-or-Buy ändert den Befund nicht; die größere Kauf-Frage ist, ob überhaupt gebaut werden soll, und die beantwortet G0 mit dem Vergleich gegen Geldmarkt und Fondslösung (`financials/buy_vs_build.md`). Nächster Schritt: nach bestandenem G0 der Rollkalender-Vergleich gegen pysystemtrade in BS-02 (T-DAT-004).

Belege: `research/sources/R6_make_or_buy.json` und `research/sources/R6_notes.md` (Abruf 24.09.2026); Entscheidung DEC-DS-22 im Entscheidungsregister; Anforderung REQ-ARC-011.

## 1 Kriterien

Die Kriterien folgen §17.3 des Auftrags. Bewertet wird qualitativ (erfüllt, teilweise, nicht erfüllt, nicht geprüft), weil für eine Punktgewichtung keine belegte Grundlage besteht; ein einziges nicht erfülltes Muss-Kriterium schließt eine Variante als Laufzeitbasis aus.

| Kriterium | Muss | Bedeutung |
|---|---|---|
| Brokeranbindung MT5 | ja | offizielle, gepflegte Anbindung an MetaTrader 5 (BQ-08) |
| Lizenz | ja | Pflichten bekannt und mit dem Eigengebrauch vereinbar; unbelegte Pflichten gehen als Frage an die externe Person (BQ-03) |
| Eignung für den deterministischen Kern | ja | Kern als reine Funktion mit injizierter Uhr und Journal (Event Sourcing), unter Windows neben dem MT5-Terminal lauffähig |
| Prüfbarkeit | ja | CI mit Simulationsbroker, Mutationstests und unabhängiger Nachrechnung ohne Eingriff in fremden Code |
| Futures-Rollen | nein | Rollkalender, Verfall, rückwärts angepasste Reihen |
| Reife und Pflege | nein | Pflege, Gewährleistung, Support |

## 2 Bewertung

| Kriterium | eigener Kern (Python, MT5-Adapter) | NautilusTrader | QuantConnect LEAN | pysystemtrade | kommerzielle Plattformen | MQL5-Expert-Advisor als Kern |
|---|---|---|---|---|---|---|
| Brokeranbindung MT5 | erfüllt: MetaTrader5-Paket für Python, nur Windows (SRC-MT5-PYPI, SRC-MT5-API) | nicht erfüllt: MT5 nicht unter den offiziellen Integrationen (SRC-OSS-NAUTILUS) | nicht erfüllt: MT5 nicht unter den offiziellen Brokerages (SRC-OSS-LEAN) | nicht erfüllt: nur Interactive Brokers (SRC-OSS-PYSYSTEMTRADE) | ausgeschieden nach BQ-08; nicht geprüft | erfüllt (läuft im Terminal) |
| Lizenz | eigener Code; Nutzungsbedingungen von Broker und Plattform (X-BRK-API) | LGPL-3.0; Pflichten nicht belegt (SRC-LIC-GPL-LGPL) | Apache-2.0; Bedingungen knüpfen an Vervielfältigung und Weitergabe an (SRC-LIC-APACHE2) | GPL-3.0; Pflichten nicht belegt (SRC-LIC-GPL-LGPL) | nicht geprüft | Plattformbedingungen; nicht geprüft |
| Eignung für den deterministischen Kern | erfüllt: Kern als reine Funktion, Adapter austauschbar (§10.1) | teilweise: gleiche Strategie- und Ausführungslogik für Backtest und Live belegt; Rust-Kern mit Python-Steuerung, MT5-Adapter fehlt | teilweise: Codebasis in C# und Python; eine MT5-Anbindung wäre als eigene Brokerage-Erweiterung zu bauen | teilweise: Python, aber auf Interactive Brokers zugeschnitten | nicht geprüft | nicht erfüllt: Logik im Terminal, kein unabhängiges Journal außerhalb der Plattform |
| Prüfbarkeit | erfüllt: CI, Mutationstests, Prüfmodul (BS-05) | teilweise: eigene Tests des Projekts; Prüfung des Geldpfads umfasst fremden Kern | teilweise: wie links, zusätzlich zweite Sprache | teilweise: ohne Gewährleistung und Support | nicht geprüft | nicht erfüllt: nicht in CI testbar |
| Futures-Rollen | selbst zu bauen (C-DATA), gegen Referenz geprüft (T-DAT-004) | nicht geprüft | nicht geprüft | erfüllt: Rollkalender und Panama-Methode belegt | nicht geprüft | selbst zu bauen |
| Reife und Pflege | neu; Risiko liegt beim Bau (Bauprogramm, Tests) | offizielle Integrationen für mehrere Handelsplätze und Datenanbieter; Pflegezustand nicht geprüft | offizielle Brokerages für mehrere Broker und FIX; Pflegezustand nicht geprüft | ausdrücklich ohne Gewährleistung und ohne Support | nicht geprüft | Plattform des Brokers; eigener Code neu |
| Ergebnis | **gewählt** | als Laufzeitbasis verworfen | als Laufzeitbasis verworfen | als Laufzeitbasis verworfen; Referenz für Rollen | nicht untersucht (BQ-08) | verworfen |

Grenzen der Bewertung: Die Aussage „keine MT5-Anbindung“ bezieht sich auf die offiziellen Listen vom 24.09.2026; Community-Adapter sind nicht geprüft (NICHT_GEPRUEFT). Die Lizenztexte von GPL-3.0 und LGPL-3.0 waren am Abruftag nicht abrufbar; die Entscheidung hängt nicht an ihnen, weil kein Framework-Code in den Kern übernommen und nichts weitergegeben wird.

## 3 Entscheidung (DEC-DS-22)

Eigener schlanker Kern in Python mit MT5-Adapter; die Frameworks sind Referenz und Prüfwerkzeug, nicht Laufzeitbasis. Begründung:

1. Jede Variante braucht einen selbst gebauten MT5-Adapter mit Abfragen, Korrelation über `magic` und `comment`, UNKNOWN-Klärung und Negativnachweis (`execution/oms_ems.md`); genau dieser Teil trägt das größte Ausführungsrisiko und wird durch kein Framework abgedeckt.
2. Eingespart würden höchstens Backtest- und Strategierahmen (C-BT, C-STRAT in `implementation/build_program.md`); Adapter, Auftragsverwaltung, Risikomotor, Prüfmodul, Cockpit und Sicherheit machen den größeren Teil des Aufwands aus und blieben eigener Code.
3. Ein fremder Kern im Geldpfad vergrößert die Prüffläche: Mutationstests, Zweigabdeckung und unabhängige Nachrechnung (G5) müssten fremden Code einschließen, der sich unabhängig vom eigenen Releaseprozess ändert.
4. Unbelegte Lizenzpflichten (GPL-3.0, LGPL-3.0) sind für die gewählte Variante ohne Bedeutung, weil kein Framework-Code in das System übernommen wird (REQ-ARC-011, T-REL-003).

Verworfene Alternativen:

| Alternative | Grund der Verwerfung |
|---|---|
| NautilusTrader als Laufzeitbasis | keine offizielle MT5-Anbindung; Rust-Kern mit Python-Steuerebene, Prüfung und Fehlersuche im Geldpfad umfassen eine zweite Sprache; LGPL-Pflichten nicht belegt |
| QuantConnect LEAN als Laufzeitbasis | keine offizielle MT5-Anbindung; MT5-Anbindung wäre eine eigene Brokerage-Erweiterung einer C#- und Python-Codebasis, also zweite Sprache im Geldpfad |
| pysystemtrade als Laufzeitbasis | nur Interactive Brokers; ohne Gewährleistung und Support; GPL-Pflichten nicht belegt |
| kommerzielle Plattformen mit eigener Brokeranbindung | nach BQ-08 ausgeschieden (nur MT5); nicht geprüft |
| MQL5-Expert-Advisor als Kern | nicht in CI testbar, Bindung an eine Plattform, kein unabhängiges Journal (§10.2) |
| Community-Adapter für MT5 in einem Framework | nicht offiziell gelistet; Reife und Pflege nicht geprüft |

Die übergeordnete Frage „bauen oder ein fertiges Produkt kaufen“ (V0 Geldmarkt, V1 Trendfolge- oder Managed-Futures-Fonds) ist nicht Teil dieser Abwägung; sie entscheidet GATE-G0 mit der Variantenmatrix (`financials/buy_vs_build.md`, EV-04).

## 4 Nutzung als Referenz und Prüfwerkzeug

| Framework | Nutzung | Ort | Test |
|---|---|---|---|
| pysystemtrade | Rollkalender und rückwärts angepasste Reihen (Panama-Methode) als unabhängige Referenz für den eigenen Datendienst | Forschungszone | T-DAT-004 (REQ-DAT-006) |
| NautilusTrader oder LEAN | optional: unabhängiger Backtest derselben Referenzstrategie als Plausibilitätsvergleich; keine Torwirkung | Forschungszone | – (Plausibilität, kein Abnahmetest) |

Keines der Frameworks läuft auf dem Geldpfad-VPS oder im Prüfmodul; die SBOM jedes Geldpfad-Release weist die Lizenz jeder Abhängigkeit aus und darf keine dieser Bibliotheken enthalten (T-REL-003). Vor jeder Übernahme von Framework-Code oder einer Weitergabe klärt die externe Person die Lizenzfrage (`legal/applicability_matrix.md`, Zeile Softwarelizenzen).
