# KI-Trading Institutional v3.0 – Konzeptpaket

Konzept für eine institutionell gebaute Plattform für den Eigenhandel mit börsengehandelten Futures über MetaTrader 5: Ein deterministischer Kern erzeugt alle Orders, Hermes und geprüfte ML-Komponenten beraten nur (kein Sprachmodell im Geldpfad). Das Paket ist ein Konzept und kein System: Es eröffnet keine Konten, schließt keine Verträge, bewegt kein Kapital, sendet keine Orders und gibt nichts für den Echtbetrieb frei. Es ist keine Anlage-, Rechts- oder Steuerberatung und enthält keine Handelsempfehlung.

## Einstieg

| Wofür | Datei |
|---|---|
| Entscheidung in Kürze | `KURZFASSUNG_BETREIBER.md` |
| Begründung, Kapitel mit Betreiberfassung | `Masterkonzept_v3.0.md` |
| Stand der Erstellung | `STATUS.md` |
| offene externe Eingaben | `external_inputs.json`; Übergabe an die externe Person: `legal/handover_external.md` |
| Bau (erst nach bestandenem G0) | `implementation/CODING_AGENT_START.md`, `implementation/build_program.md`, `implementation/test_catalog.json` |
| unabhängige Gegenprüfung | `audit/independent_review_request.md` |

## Stand

- Echtgeld: No-Go in <!--v:calc:gonogo_count/NO_GO|int-->24<!--/v--> von <!--v:calc:gonogo_cells|int-->24<!--/v--> Zellen aus Kapitalstufe und Hebelprofil; Demo und Paper sind mit Ausgabendeckel zulässig (`financials/decision_montecarlo_results.json`).
- Tor G0 heute: <!--v:calc:gate_today/GC-G0-101/outcome|raw-->BLOCKED_EXTERNAL<!--/v--> (`examples/valid/gate_cases/GC-G0-101.json`); die Tore G0 bis G10 stehen in `research/evidence_gates.json`.
- Selbstbewertung K = <!--v:calc:score_k_total|d2-->64,75<!--/v-->, E = <!--v:calc:score_e_total|d0-->0<!--/v--> (`audit/scorecard_K.json`, `audit/scorecard_E.json`); die unabhängige Gegenprüfung steht aus (X-REVIEW).
- Externe Eingaben: <!--v:calc:external_inputs_total|int-->34<!--/v-->, keine bestätigt. Parameter: <!--v:calc:parameters_total|int-->294<!--/v-->, jeder mit Status und Quelle (`parameters.json`).
- Befunde der Bewertung von v2.0 und der Konzeptprüfung: `registers/resolution_matrix.json`.

## Prüfbefehle

Voraussetzung ist Python 3.11 bis 3.13 in einer virtuellen Umgebung außerhalb des Paketordners mit den gepinnten Abhängigkeiten; die Rechner selbst brauchen nur die Standardbibliothek. Alle Befehle im Paketordner ausführen.

```
python3.12 -m venv ../venv312
../venv312/bin/pip install --require-hashes -r validation/requirements-validation.txt

# vollständige strenge Prüfung (nach frischem Entpacken, mit Manifest und Prüfsummen)
../venv312/bin/python validation/validate_package.py --root . --strict --stage full --report-out ../pruefbericht.json

# einzelne Bausteine
../venv312/bin/python validation/run_calculators.py --check
../venv312/bin/python validation/render_blocks.py --root . --check
../venv312/bin/python validation/test_reference_models.py
../venv312/bin/python validation/semantic_checks.py --root .
../venv312/bin/python validation/gate_engine.py --root .
../venv312/bin/python validation/state_engine.py --root .
../venv312/bin/python validation/mutation_tests.py --root .
../venv312/bin/python -m ruff check --no-cache .

# Mehrversionslauf (je Version eine Umgebung wie oben)
../venv312/bin/python validation/run_multi_python.py --root . --python ../venv311/bin/python --python ../venv312/bin/python --python ../venv313/bin/python --log ../execution_log_eigen.txt
```

Die Paketprüfung hat vierzehn Phasen (P01 bis P14, `Masterkonzept_v3.0.md` §19). Ohne `--stage full` entfallen Manifest und Prüfsummen (P14); das ist der Zustand vor dem Packen. Der Mehrversionslauf schreibt ohne `--log` in `validation/execution_log.txt` und überschreibt damit den mitgelieferten Beleg; mit `--log` bleibt das Paket unverändert.

## Laufbelege

Die mitgelieferten Belege sind in dieser Reihenfolge entstanden und tragen jeweils den Paketstand (SHA-256 über alle Inhaltsdateien, `lib/pkgstate.py`):

1. Mehrversionslauf unter Python 3.11, 3.12 und 3.13 mit `-W error`: `validation/execution_log.txt`
2. Mutationslauf mit <!--v:calc:mutations_total|int-->60<!--/v--> Mutationen: `validation/mutation_report.json`
3. strenge Prüfung vor dem Packen: `validation/validation_report.json`
4. Manifest und Prüfsummen: `PACKAGE_MANIFEST.json`, `CHECKSUMS.sha256`
5. ZIP mit einem Wurzelordner, Hash-Datei mit identischem Namen und Endung `.sha256` sowie der Bericht der strengen Prüfung nach frischem Entpacken, beide außerhalb des Archivs

Die Paketprüfung (P13) vergleicht den Paketstand jedes Belegs mit dem geprüften Paket; ein Beleg einer anderen Fassung ist ein Fehler.

## Grenzen der Prüfung

Ein grünes Ergebnis belegt, dass Zahlen, Register, Texte, Beispiele und Rechner zusammenpassen. Es belegt nicht, dass Annahmen stimmen, dass eine Strategie eine Kante hat oder dass der Broker so arbeitet wie beschrieben; das zeigen erst die Tore G0 bis G10. Bekannte Grenzen der Prüfung selbst:

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

## Dateinamen und Umfang

Alle in §18 des Auftrags verlangten Namen sind unverändert. Zusätzlich enthält das Paket `legal/handover_external.md`, `lib/calc.py`, `lib/pkgstate.py`, `operations/monitor_simulation.py`, `ruff.toml` und `validation/requirements-validation.txt` (Begründung in `Masterkonzept_v3.0.md` §18).

## Daten und Schutz

Das Paket enthält keine personenbezogenen Angaben, keine Zugangsdaten und keine Kontodaten; der Name des Betreibers ist im Wortlaut der Betreiberantworten entfernt. Recht und Steuern prüft nach deiner Entscheidung BQ-03 eine externe Person; das Paket liefert dafür nur Fragen und Übergabeformate.
