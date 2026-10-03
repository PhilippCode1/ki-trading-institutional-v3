# Vorregistrierte Strategiefamilie (§6.1)

> **Betreiberfassung.** Hier ist festgelegt, welche Handelsregeln das System erforschen darf, bevor irgendein Ergebnis angesehen wird; eine Auswahl nach Ergebnis ist damit ausgeschlossen. Kern ist eine schnelle Trendfolge (S-TF), die auf deinen Haltehorizont von <!--v:param:P-OP-HOLD-STD-MIN-H|d0-->4<!--/v--> h bis <!--v:calc:hold_std_max_days|d0-->4<!--/v--> Tagen kalibriert ist, ergänzt um Intraday-Momentum (S-IM), Kurzfrist-Umkehr (S-REV) und einen Carry-Filter (S-CA). Jede Regel hat einen Mechanismus aus der Literatur, klare Widerlegungskriterien und eine ausführbare Referenzimplementierung. Die Kosten dieser Regeln sind bei kurzer Haltedauer hoch; deshalb bleiben nach der Zulassung nur wenige Kontrakte übrig (§6.2). Für Go/No-Go heißt das: Die Familie ist forschungsreif, aber nicht echtgeldreif. Nächster Schritt ist die Kampagne in G3 nach `research/research_plan.md`.

Alle Werte stehen in `parameters.json` (Gruppe STRATEGIE); die Referenzimplementierungen in `research/reference_strategies/` lesen nur diese Werte. Die Implementierungen arbeiten auf Stundenbalken mit Liquiditätsfenster; Einstiege nur im Fenster, Schutz- und Zeitausstiege jederzeit.

<!-- GEN:BEGIN tab.params:P-STR -->
| ID | Bedeutung | Wert | Einheit | Status |
|---|---|---|---|---|
| P-STR-FC-SCALE | Mittlerer Betrag der skalierten Prognose | 10 | Punkte | ENTWURF |
| P-STR-FC-CAP | Kappung der Prognose | 20 | Punkte | ENTWURF |
| P-STR-FDM-CAP | Obergrenze Prognose-Diversifikationsmultiplikator | 2 | Faktor | ENTWURF |
| P-STR-IDM-CAP | Obergrenze Instrument-Diversifikationsmultiplikator | 2,50 | Faktor | ENTWURF |
| P-STR-BUFFER | Positionspuffer (Anteil der Durchschnittsposition) | 0,10 | Anteil | ENTWURF |
| P-STR-TF-SPEEDS | S-TF: EWMA-Paare (schnell/langsam) in Handelsstunden | [[4; 16]; [8; 32]; [16; 64]; [32; 128]] | Stunden | ENTWURF |
| P-STR-TF-ENTRY | S-TF: Einstiegsschwelle der kombinierten Prognose | 8 | Punkte | ENTWURF |
| P-STR-TF-EXIT | S-TF: Ausstieg bei Prognose unter | 3 | Punkte | ENTWURF |
| P-STR-STOP-ATR | Schutzstopp beim Broker in Vielfachen der stündlichen ATR×√24 | 2,50 | Faktor | ENTWURF |
| P-STR-IM-SIGNAL-MIN | S-IM: Messfenster ab Sitzungsbeginn der Kernzeit | 120 | Minuten | ENTWURF |
| P-STR-IM-HOLD-H | S-IM: Haltedauer bis Kernzeitende | 4 | Stunden | ENTWURF |
| P-STR-REV-Z | S-REV: Schwelle der 3-Tage-Rendite in σ | 2 | σ | ENTWURF |
| P-STR-REV-HOLD-H | S-REV: höchste Haltedauer | 72 | Stunden | ENTWURF |
| P-STR-CA-TILT | S-CA: Größenfaktor für Trades mit (1 + x) bzw. gegen (1 − x) den Carry | 0,20 | Anteil | ENTWURF |
| P-STR-REENTRY-COOLDOWN-H | Sperrzeit nach Zeitstopp für denselben Kontrakt und dieselbe Richtung | 24 | Stunden | ENTWURF |
| P-STR-VOL-SPAN-D | Spanne der EWMA-Volatilität (Stundenrenditen) für Prognosen, Stopps und Größen | 20 | Handelstage | ENTWURF |
| P-STR-IM-MIN-MOVE-SD | S-IM: Mindestbewegung seit Beginn der Kernzeit bis zum Messpunkt | 0,25 | σ (Tag) | ENTWURF |
| P-STR-IM-STOP-FACTOR | S-IM: Schutzstopp als Anteil von P-STR-STOP-ATR | 0,50 | Faktor | ENTWURF |
| P-STR-REV-LOOKBACK-D | S-REV: Messfenster der Ausgangsbewegung | 3 | Handelstage | ENTWURF |
| P-STR-REV-STOP-FACTOR | S-REV: Schutzstopp als Vielfaches von P-STR-STOP-ATR | 1,50 | Faktor | ENTWURF |
| P-STR-BASE-ENTRY-N | TF-D1: Einstiegskanal | 55 | Handelstage | ENTWURF |
| P-STR-BASE-EXIT-N | TF-D1: Ausstiegskanal | 20 | Handelstage | ENTWURF |
| P-STR-BASE-ATR-N | TF-D1: Spanne der ATR | 20 | Handelstage | ENTWURF |
| P-STR-BASE-STOP-ATR | TF-D1: Schutzstopp in ATR | 2 | ATR | ENTWURF |
| P-STR-RISK-SHARES | Risikobudget je Strategie (S-TF, S-IM, S-REV) | S-TF: 0,60; S-IM: 0,20; S-REV: 0,20 | Anteile | ENTWURF |
<!-- GEN:END tab.params:P-STR -->

## S-TF – Trendfolge mehrerer Geschwindigkeiten (Kern)

- **Mechanismus:** Zeitreihen-Momentum; Preise reagieren verzögert auf Information und Absicherungsnachfrage, Trends setzen sich über Stunden bis Wochen fort (SRC-LIT-TF-MOP-2012, SRC-LIT-TF-HOP-2017, SRC-LIT-TF-BABU-2020-JOIM). Schnelle Varianten sind in Krisen oft wertvoller, aber teurer (SRC-LIT-TF-MAN-SPEED, SRC-LIT-TF-GGHM-2023).
- **Signal:** Je Geschwindigkeitspaar (P-STR-TF-SPEEDS, Spannen in Stunden) die Differenz zweier EWMA geteilt durch Preis mal Tagesvolatilität; Skalierung auf einen mittleren Betrag von <!--v:param:P-STR-FC-SCALE|d0-->10<!--/v-->, Kappung bei <!--v:param:P-STR-FC-CAP|d0-->20<!--/v-->, gleichgewichtete Kombination mit Prognose-Diversifikationsmultiplikator (gedeckelt bei <!--v:param:P-STR-FDM-CAP|d1-->2,0<!--/v-->). Einstieg, wenn der Betrag der kombinierten Prognose <!--v:param:P-STR-TF-ENTRY|d0-->8<!--/v--> erreicht; Ausstieg, wenn die Prognose in Positionsrichtung unter <!--v:param:P-STR-TF-EXIT|d0-->3<!--/v--> fällt (Hysterese als Positionspuffer).
- **Ausstiege:** serverseitiger Schutzstopp bei <!--v:param:P-STR-STOP-ATR|d1-->2,5<!--/v--> Tagesvolatilitäten, Zeitstopp bei <!--v:param:P-OP-HOLD-MAX-H|d0-->168<!--/v--> Stunden, danach Sperrfrist von <!--v:param:P-STR-REENTRY-COOLDOWN-H|d0-->24<!--/v--> Stunden in dieselbe Richtung.
- **Größe:** Anteil der Prognose an ihrer Kappung mal Risikobudget der Strategie; die Lückenregel (§7) begrenzt zusätzlich.
- **Umschlag und Haltedauer** (synthetisch gemessen, `research/turnover_results.json`): <!--v:turn:strategies/S-TF/round_turns_per_year|d0-->81<!--/v--> Round-Turns je Jahr und Instrument, Zeit im Markt <!--v:turn:strategies/S-TF/time_in_market|pct0-->62 %<!--/v-->, Median-Haltedauer <!--v:turn:strategies/S-TF/holding_hours_median|d0-->48<!--/v--> Stunden, Anteil im Standardfenster <!--v:turn:strategies/S-TF/share_within_4h_4d|pct0-->73 %<!--/v-->.
- **Widerlegung:** DSR nach Kosten unter <!--v:param:P-RES-DSR-MIN|d2-->0,95<!--/v--> in der Entwicklung, PBO über <!--v:param:P-RES-PBO-MAX|pct0-->20 %<!--/v-->, Holdout-Sharpe nicht positiv, gemessener Umschlag weicht um mehr als <!--v:param:P-RES-TURNOVER-TOL|pct0-->30 %<!--/v--> von der Simulation ab, oder die prädiktive Wahrscheinlichkeit für das Endtor fällt unter die Futility-Schwelle (§6.6).

## S-IM – Intraday-Momentum (Ergänzung)

- **Mechanismus:** Die Rendite vom Beginn der Kernhandelszeit bis zum Messpunkt sagt die Richtung des restlichen Tages voraus, getrieben durch Absicherungsflüsse zum Handelsende (SRC-LIT-INTRA-GHLZ-2018, SRC-LIT-INTRA-BDLM-2021, SRC-LIT-INTRA-LSU-2022).
- **Signal:** Messpunkt nach <!--v:param:P-STR-IM-SIGNAL-MIN|d0-->120<!--/v--> Minuten Kernzeit; Einstieg in Richtung der Bewegung, wenn sie mindestens <!--v:param:P-STR-IM-MIN-MOVE-SD|d2-->0,25<!--/v--> Tagesvolatilitäten beträgt; höchstens ein Trade je Tag und Instrument.
- **Ausstiege:** nach <!--v:param:P-STR-IM-HOLD-H|d0-->4<!--/v--> Stunden oder am Ende der Kernzeit, Schutzstopp bei <!--v:param:P-STR-IM-STOP-FACTOR|d1-->0,5<!--/v--> × P-STR-STOP-ATR.
- **Abweichung zur Literatur:** Die Literatur hält meist nur die letzte halbe Stunde; die Haltedauer hier folgt deiner Untergrenze von <!--v:param:P-OP-HOLD-STD-MIN-H|d0-->4<!--/v--> Stunden. Der Prior trägt dafür einen Übertragungsabschlag (P-PRI-H-IM).
- **Umschlag:** <!--v:turn:strategies/S-IM/round_turns_per_year|d0-->114<!--/v--> Round-Turns je Jahr und Instrument; die Kosten übersteigen selbst im günstigsten Kontrakt <!--v:calc:cheapest_im_cost|d3-->0,112<!--/v--> Sharpe-Einheiten im Jahr. S-IM ist damit nach heutigem Stand nirgends zulassungsfähig.
- **Widerlegung:** Vorzeichen des Zusammenhangs im Entwicklungszeitraum nicht positiv, oder Kosten nach gemessenen Spreads über dem Bruttoertrag.

## S-REV – Kurzfrist-Umkehr (Ergänzung, Prior bei null)

- **Mechanismus:** Nach außergewöhnlichen Bewegungen über wenige Tage kehren Preise teilweise um, wenn Liquiditätsgeber für Absicherungsdruck entschädigt werden (SRC-LIT-REV-WY-2004, SRC-LIT-REV-KRT-2020, SRC-LIT-REV-UZ-2020). Die Evidenz ist gemischt; der Prior ist um null zentriert (P-PRI-REV-SD).
- **Signal:** z-Wert der Bewegung über <!--v:param:P-STR-REV-LOOKBACK-D|d0-->3<!--/v--> Handelstage; Einstieg gegen die Bewegung ab |z| ≥ <!--v:param:P-STR-REV-Z|d1-->2,0<!--/v--> zu Beginn der Kernzeit.
- **Ausstiege:** z kreuzt null, nach <!--v:param:P-STR-REV-HOLD-H|d0-->72<!--/v--> Stunden oder am Schutzstopp (<!--v:param:P-STR-REV-STOP-FACTOR|d1-->1,5<!--/v--> × P-STR-STOP-ATR).
- **Widerlegung:** t-Statistik nach Mehrfachtest-Korrektur unter <!--v:param:P-RES-T-HURDLE|d1-->3,0<!--/v--> (Hürde für Faktoren ohne tragfähigen Literatur-Prior).

## S-CA – Carry als Filter

- **Mechanismus:** Die annualisierte Rollrendite zwischen Front- und Folgekontrakt misst die Prämie für das Halten (SRC-LIT-CARRY-KMPV-2018).
- **Regel:** S-TF-Trades in Carry-Richtung werden um <!--v:param:P-STR-CA-TILT|pct0-->20 %<!--/v--> vergrößert, gegen die Carry-Richtung um denselben Anteil verkleinert. Ein eigenständiger Carry-Handel scheitert an der Höchsthaltedauer, weil er jede Woche neu eröffnet werden müsste.
- **Widerlegung:** Der Filter verbessert die Netto-Sharpe-Ratio von S-TF in der Entwicklung nicht; dann entfällt er (Prior-Zuschlag P-PRI-CA-UPLIFT).

## S-BASE – TF-D1 und TF-D1-7T (Vergleichsbasis)

TF-D1 aus v2.0 (Kanalausbruch über P-STR-BASE-ENTRY-N Tage, Ausstieg über P-STR-BASE-EXIT-N Tage, Stopp P-STR-BASE-STOP-ATR ATR) bleibt unverändert als Vergleichsbasis (D3-04: kein Bestandsschutz). TF-D1 hält im Median <!--v:turn:strategies/S-BASE-TFD1/holding_hours_median|d0-->362<!--/v--> Stunden und verletzt damit deine Höchsthaltedauer; TF-D1-7T ergänzt den Zeitstopp und hält die Grenze ein, verliert dafür einen Teil der Kante (P-PRI-TFD1-7T).

## S-X und S-ML

Weitere Prämien (S-X) sind nicht registriert. ML-Komponenten (S-ML) sind auf Größensteuerung durch Meta-Labeling (MOD-ML-META) und Regimeerkennung (MOD-ML-REGIME) beschränkt und brauchen vor jedem Einsatz eine DSR von mindestens <!--v:param:P-AI-ML-DSR-MIN|d2-->0,95<!--/v--> und einen Mehrwert von mindestens <!--v:param:P-AI-ML-UPLIFT-MIN|d2-->0,10<!--/v--> Sharpe-Einheiten nach Kosten gegenüber der Regel (§11.5, `ai/mrm_policy.md`).

## Kombination und erwartete Korrelationen

Die Strategien teilen sich das Risikobudget in festen Anteilen (P-STR-RISK-SHARES). Die Instrumentdiversifikation ist bei <!--v:param:P-STR-IDM-CAP|d1-->2,5<!--/v--> gedeckelt, damit geschätzte Korrelationen den Hebel nicht aufblähen. Erwartete Korrelationen zwischen den Strategien und innerhalb der Anlageklassen stehen in P-PRI-RHO-STRAT, P-PRI-RHO-WITHIN und P-PRI-RHO-BETWEEN:

<!-- GEN:BEGIN tab.params:P-PRI -->
| ID | Bedeutung | Wert | Einheit | Status |
|---|---|---|---|---|
| P-PRI-ANCHORS | Ankerwerte aus der Literaturtabelle (Studie, Kennzahl) – Werte werden aus research/sources/R3_literature_prior.json gelesen | TF12_INSTR: [[TF-BABU-2020-JOIM; Median-Sharpe je Einzelanlage, traditionell]; [TF-HOP-2017; Mittlere Sharpe je Einzelmarkt]]; TF_RATIO_1M_12M: [[[TF-HOP-2013; Sharpe 1-Monats-TSMOM]; [TF-HOP-2013; Sharpe 12-Monats-TSMOM]]; [[TF-GGHM-2023; Sharpe 1-Monats-Trend]; [TF-GGHM-2023; Sharpe 12-Monats-Trend]]]; TF_RATIO_3M_12M: [[[TF-HOP-2013; Sharpe 3-Monats-TSMOM]; [TF-HOP-2013; Sharpe 12-Monats-TSMOM]]]; IM_CLASS_SR: ANLEIHE: [INTRA-BDLM-2021; Sharpe Anleihefutures]; ROHSTOFF: [INTRA-BDLM-2021; Sharpe Rohstofffutures]; FX: [INTRA-BDLM-2021; Sharpe Währungsfutures]; IM_CLASS_N: ANLEIHE: [INTRA-BDLM-2021; Anzahl Anleihefutures]; ROHSTOFF: [INTRA-BDLM-2021; Anzahl Rohstofffutures]; FX: [INTRA-BDLM-2021; Anzahl Währungsfutures]; DECAY_POST_PUB: [DECAY-MP-2016; Renditerückgang nach Veröffentlichung]; MT_EXAMPLE: [[DECAY-HL-2015; Beispiel Sharpe nach Abschlag]; [DECAY-HL-2015; Beispiel Sharpe vor Abschlag]]; PLAUS_NET: [[IDX-SGTREND-BABU-2020; Sharpe SG Trend Index 2000–2018]; [IDX-SGTREND-BABU-2020; Sharpe SG Trend Index 2010–2018]] | Verweise | BELEGT |
| P-PRI-H-TF | Übertragungsfaktor S-TF: 1-Monats-Lookback → Geschwindigkeiten 4–128 h (gleichverteilt) | [0,10; 0,90] | Faktor | ANNAHME |
| P-PRI-H-IM | Übertragungsfaktor S-IM: letzte 30 Minuten → Haltedauer bis Kernzeitende (≈ 4 h) | [0,20; 0,80] | Faktor | ANNAHME |
| P-PRI-DECAY | Behaltener Anteil nach Veröffentlichung (gleichverteilt; Untergrenze aus 1 − 58 %) | [0,42; 1] | Anteil | ANNAHME |
| P-PRI-MT-TF | Behaltener Anteil nach Mehrfachtests, S-TF (vorregistrierte, bekannte Familie) | [0,80; 1] | Anteil | ANNAHME |
| P-PRI-MT-IM | Behaltener Anteil nach Mehrfachtests, S-IM (Untergrenze aus Harvey/Liu-Beispiel 0,32/0,75) | [0,43; 1] | Anteil | ANNAHME |
| P-PRI-IMPL | Behaltener Anteil nach Umsetzung (Datenqualität, Ausführung, Plattform) | [0,80; 1] | Anteil | ANNAHME |
| P-PRI-REV-SD | S-REV: Streuung der Brutto-Sharpe je Instrument um null | 0,10 | Sharpe p. a. | ANNAHME |
| P-PRI-CA-UPLIFT | S-CA-Filter: Zuschlag auf die Brutto-Sharpe von S-TF je Instrument (gleichverteilt) | [0; 0,05] | Sharpe p. a. | ANNAHME |
| P-PRI-TFD1-7T | TF-D1-7T: behaltener Anteil der Trend-Brutto-Sharpe bei Zeitstopp 7 Tage (gleichverteilt) | [0,30; 0,70] | Anteil | ANNAHME |
| P-PRI-RHO-WITHIN | Korrelation der Strategierenditen innerhalb einer Risikoklasse | STIR: 0,60; ANLEIHE_KURZ: 0,60; ANLEIHE_MITTEL: 0,60; ANLEIHE_LANG: 0,60; RENDITE: 0,60; FX: 0,30; ENERGIE: 0,40; EDELMETALL: 0,40; INDUSTRIEMETALL: 0,30; AGRAR: 0,20; VIEH: 0,30; SOFTS: 0,10; KRYPTO: 0,70 | Korrelation | ANNAHME |
| P-PRI-RHO-ANLEIHE-GROUP | Korrelation zwischen Zins-Risikoklassen (STIR, kurze/mittlere/lange Anleihen, Rendite) | 0,50 | Korrelation | ANNAHME |
| P-PRI-RHO-BETWEEN | Korrelation der Strategierenditen zwischen Risikoklassen | 0,05 | Korrelation | ANNAHME |
| P-PRI-RHO-STRAT | Korrelation zwischen den Strategien | S-TF\|S-IM: 0,30; S-TF\|S-REV: -0,30; S-IM\|S-REV: -0,10 | Korrelation | ANNAHME |
| P-PRI-IM-RHO-CLASS | Korrelation innerhalb einer Klasse zur Umrechnung der Klassen-Sharpe (S-IM) auf ein Instrument | 0,30 | Korrelation | ANNAHME |
| P-PRI-DECISION-RULE | Strategien im Entscheidungsfall | NUR_P_NETTO_POSITIV_GROESSER_0_5 | Text | ENTWURF |
<!-- GEN:END tab.params:P-PRI -->

## Referenzimplementierung und Tests

| Strategie | Datei | geprüft durch |
|---|---|---|
| S-TF | `research/reference_strategies/s_tf.py` | Umschlagssimulation, Referenztests (`validation/test_reference_models.py`) |
| S-IM | `research/reference_strategies/s_im.py` | wie oben |
| S-REV | `research/reference_strategies/s_rev.py` | wie oben |
| S-CA | `research/reference_strategies/s_ca.py` | Einheitentests der Carry-Formel |
| S-BASE | `research/reference_strategies/s_base.py`, `research/reference_strategies/tf_d1_baseline.py` (unverändert aus v2.0) | Abgleich mit v2.0 |

Die Implementierungen sind deterministisch und nutzen nur die Standardbibliothek (DEC-DS-15). Sie belegen keine Kante (R-02); sie legen fest, was in G3 getestet wird.
