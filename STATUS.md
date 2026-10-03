# STATUS – Erstellung Konzeptpaket v3.0

Dieses Dokument hält den Stand der Erstellung nach jeder Etappe fest (§22.1). Es ist kein Prüfergebnis; maßgeblich sind `validation/validation_report.json` und der Bericht nach frischem Entpacken außerhalb des Archivs.

| Etappe | Inhalt | Stand |
|---|---|---|
| E0 | Eingangsprüfung: Hash, sicheres Entpacken, v2-Paketprüfung, Inventar | erledigt |
| E1 | Betreiberfragen BQ-01 … BQ-10 gestellt und beantwortet | erledigt |
| E2 | Paketgerüst, Register, Schemas, Validator-Grundlage | erledigt |
| E3 | Rechner: Kosten, Wirtschaft, Steuer-Sensitivität, Prior, Hebel, Kelly/Ruin, Stress, Statistik, Betriebscharakteristik, Entscheidungs-Monte-Carlo | erledigt |
| E4 | Kapitel §4–§9 | erledigt |
| E5 | Kapitel §10–§15 | erledigt |
| E6 | Tore, Zustandsautomaten, Szenarien, Testkatalog, Bauprogramm | erledigt |
| E7 | Paketprüfung, semantische Phasen, Mutationstests, Mehrversionslauf | erledigt |
| E8 | Selbstbewertung K und E, Prüf-Prompt für die Gegenprüfung | erledigt |
| E9 | Packen, frisch entpacken, Endprüfung, Übergabe | Belegzyklus auf diesem Stand; Abschluss mit dem Bericht nach frischem Entpacken |

## Letzte Etappe

Inhalt eingefroren am 24.09.2026 (E9). Auf diesem Paketstand sind danach entstanden: Mehrversionslauf unter Python 3.11, 3.12 und 3.13 (`validation/execution_log.txt`), Mutationslauf (`validation/mutation_report.json`), strenge Prüfung vor dem Packen (`validation/validation_report.json`), Manifest und Prüfsummen (`PACKAGE_MANIFEST.json`, `CHECKSUMS.sha256`) und das ZIP. Die strenge Prüfung nach frischem Entpacken (Stufe full) liegt als Bericht außerhalb des Archivs und schließt E9 ab. Echtgeld bleibt in allen Kapitalstufen und Profilen No-Go; die Selbstbewertung steht in `audit/scorecard_K.json` und `audit/scorecard_E.json`.

## Nächste Aktion

Für den Betreiber: `KURZFASSUNG_BETREIBER.md` lesen; die fünf Eingaben für G0 beschaffen (X-BRK-FEES, X-BRK-INTEREST, X-OP-RATE, X-OP-BUDGET, X-V1-PRODUCTS); über DEC-CF-02 und die Höchsthaltedauer entscheiden; die unabhängige Gegenprüfung mit `audit/independent_review_request.md` beauftragen (X-REVIEW).

## Dateien mit Hash (SHA-256, Auszug)

| Datei | SHA-256 |
|---|---|
| `parameters.json` | `5da0fc1b4b6ec8ad…` |
| `external_inputs.json` | `f63933b1a99e7534…` |
| `registers/source_register.json` | `d9ee1c49413a2470…` |
| `registers/instruments.json` | `e80fc6ee62413472…` |
| `registers/costs.json` | `34636f2620200568…` |
| `registers/decision_register.json` | `e2d2b6161b82b1c4…` |
| `registers/risk_register.json` | `4ff824bd145e7beb…` |
| `registers/model_inventory.json` | `33493b0d651ea1dc…` |
| `registers/limits.json` | `3b532265639709ec…` |
| `validation/validate_package.py` | `0576d52c463032ce…` |
| `lib/calc.py` | `5c6acb923b94edbe…` |
| `financials/cost_model_results.json` | `6dcbd5e98bb754c6…` |
| `research/prior_results.json` | `4a070e7d67bea4fb…` |
| `risk/leverage_results.json` | `38ee223f6cfcb212…` |
| `risk/kelly_ruin_results.json` | `54aa2663f3817f2c…` |
| `risk/stress_results.json` | `eda9177501a66b4b…` |
| `research/operating_characteristics_results.json` | `2fee1e58d47e2d09…` |
| `financials/decision_montecarlo_results.json` | `0e0b78e65caf2ae7…` |
| `Masterkonzept_v3.0.md` | `2c2f78f60cda2233…` |
| `KURZFASSUNG_BETREIBER.md` | `182ce7cbf349ce1c…` |
| `audit/scorecard_K.json` | `ca013f3e7265ed7a…` |
| `audit/scorecard_E.json` | `c1855ba53eb933ec…` |
