# Modellrisikomanagement (§11.5, nach dem Vorbild von SR 11-7)

> **Betreiberfassung.** Jedes Modell, das Zahlen für Entscheidungen liefert – vom Kostenmodell über die Hebelrechnung bis zu optionalen ML-Komponenten –, steht im Modellinventar mit Zweck, Annahmen, Grenzen, Validierung und Rückfall. ML darf nur Größen steuern oder Regime erkennen, nie Orders erzeugen, und muss vorab registrierte Hürden gegen die Regel bestehen. Sprachmodelle sind im Signal- und Größenpfad ausgeschlossen. Besteht ein ML-Modell nicht, wird darauf verzichtet und der Verzicht begründet. Für Go/No-Go heißt das: ML ist optional und ändert den Befund nicht. Nächster Schritt ist die Validierung der Kernmodelle mit gemessenen Daten in G2 und G3.

## 1 Grundsätze (SRC-LIT-SR11-7)

- **Inventar:** `registers/model_inventory.json` mit <!--v:calc:models_total|int-->20<!--/v--> Modellen (Rechner, Strategien, Kovarianz, Schlupf, optionale ML-Komponenten).
- **Dokumentation:** Zweck, Eingaben, Annahmen (mit Status), Grenzen, Rechner, Tests.
- **Unabhängige Validierung:** durch eine andere Person oder Instanz ohne Autorenrolle; für Kernmodelle zusätzlich das Prüfmodul, das Entscheidungen aus Brokerdaten nachrechnet.
- **Laufende Überwachung:** Drift von Eingangsdaten und Ergebnissen, Kostenverhältnis, realisierte gegen erwartete Volatilität; Auslöser führen zu Neuvalidierung.
- **Erklärbarkeit:** jede Entscheidung mit DecisionRecord (Eingaben, Regel, Ergebnis).
- **Rückfall:** jede ML-Komponente hat einen regelbasierten Rückfall, der ohne Umbau aktiv wird.

## 2 Hürden für ML im Signal- oder Größenpfad

| Hürde | Wert |
|---|---|
| Vorregistrierung | Experiment-Manifest vor jeder Ergebnisansicht |
| Deflated Sharpe Ratio | mindestens <!--v:param:P-AI-ML-DSR-MIN|d2-->0,95<!--/v--> |
| PBO (CSCV) | höchstens <!--v:param:P-RES-PBO-MAX|pct0-->20 %<!--/v--> |
| Mehrwert gegenüber der Regel nach Kosten | mindestens <!--v:param:P-AI-ML-UPLIFT-MIN|d2-->0,10<!--/v--> Sharpe-Einheiten |
| Validierung | bereinigte Kreuzvalidierung mit Embargo (<!--v:param:P-RES-EMBARGO-H|d0-->168<!--/v--> Stunden), versiegelter Holdout |
| Modellart | deterministisch, versioniert, reproduzierbar; keine Sprachmodelle |

Kandidaten: Meta-Labeling für die Größe von S-TF (MOD-ML-META) und Regimeerkennung für Volatilitätsregime (MOD-ML-REGIME). Weil schon die Regelbasis kaum Kante hat (§6.3), ist ein Bestehen unwahrscheinlich; der Verzicht ist der erwartete Fall und wird mit den Testergebnissen begründet.

## 3 Lebenszyklus

Entwicklung (Forschungszone) → Validierung (Prüfmodul) → Freigabe (Klasse C, zweite menschliche Freigabe) → Betrieb mit Überwachung → quartalsweise Modellprüfung → Stilllegung. Änderungen an Annahmen oder Daten mit Evidenzwirkung lösen eine Neuvalidierung aus.
