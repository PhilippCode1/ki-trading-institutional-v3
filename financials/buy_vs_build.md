# Kauf statt Bau: Varianten V0 bis V4 (§5.5, EV-04)

> **Betreiberfassung.** Bevor ein eigenes System gebaut wird, vergleicht das Paket fünf Wege: Geld im Geldmarkt lassen (V0), ein Trendfolgeprodukt kaufen (V1), ein Signal-Skript mit manuellen Orders (V2), ein bestehendes Framework mit eigener Strategie (V3) und die volle Eigenentwicklung (V4). Innerhalb deiner Vorgaben ist V4 in keiner Kapitalstufe zulässig (kein zulassungsfähiges Universum oder unzulässiges Profil; wo V4 rechnet, wäre V1 bei gleichem Risiko zudem besser), und V2 und V3 erben dieses Problem, weil sie dieselben Kontrakte und Kosten haben. V1 braucht keinen Aufbau, aber konkrete Produkte mit Kosten und Liquidität sind noch nicht recherchiert (X-V1-PRODUCTS). Für Go/No-Go heißt das: Eigenbau mit Echtgeld No-Go, Demo und Forschung als gedeckelte Lernausgabe zulässig. Nächster Schritt ist deine Entscheidung, ob du V1-Produkte prüfen lassen willst. Dies ist keine Anlageempfehlung für ein bestimmtes Produkt.

## 1 Varianten

| ID | Inhalt | was sie mit deinen Vorgaben macht |
|---|---|---|
| V0 | Geldmarkt (<!--v:param:P-ECO-CASH-RATE|pct2-->2,44 %<!--/v-->, SRC-ECB-ESTR) | Vergleichsmaßstab; Überrendite null, nie „null Prozent“ |
| V1 | Trendfolge- oder Managed-Futures-Fonds bzw. -ETF | realisierte Netto-Sharpe-Ratio von Trendfolge-Indizes <!--v:param:P-ECO-V1-SR/0|d2-->0,05<!--/v--> bis <!--v:param:P-ECO-V1-SR/1|d2-->0,28<!--/v--> (SRC-SG-TREND-TTU-2025, SRC-LIT-IDX-SGTREND-BABU-2020) bei angenommener Produktvolatilität <!--v:param:P-ECO-V1-SIGMA|pct0-->10 %<!--/v-->; Haltedauer und Hebel bestimmt der Fonds, nicht du |
| V2 | Signal-Skript mit manuellen Orders und brokerseitigen Schutzstopps | behält <!--v:param:P-ECO-V2-EDGE-FACTOR|pct0-->80 %<!--/v--> der Bruttokante (verpasste Signale), kostet <!--v:param:P-ECO-V2-MIN-PER-ORDER|d0-->2<!--/v--> Minuten je Order, Aufbau <!--v:param:P-ECO-V2-BUILD-FACTOR|pct0-->25 %<!--/v--> des Systembaus |
| V3 | bestehende Plattform oder Open-Source-Framework plus eigene Strategie | Aufbau <!--v:param:P-ECO-V3-BUILD-FACTOR|pct0-->70 %<!--/v--> des Systembaus; kein geprüftes Framework mit MT5-Anbindung (`implementation/make_or_buy.md`) |
| V4 | volle Eigenentwicklung v3.0 | registrierte Strategiefamilie innerhalb deiner Vorgaben (Universum U-KOSTEN); das Sensitivitätsuniversum U-BREAKEVEN steht nur zur Information daneben |

## 2 Entscheidungsmatrix in der Referenzstufe (<!--v:param:P-RISK-STRESS-REF-STAGE|mio-->5 Mio. EUR<!--/v-->, Profil H5)

| Kriterium | V0 | V1 | V2 | V3 | V4 |
|---|---|---|---|---|---|
| Erwartungswert je Jahr nach Kosten, vor Steuern | <!--v:dmc:variants_V0_V4/5000000/V0/expected_annual_value_eur|eur-->0 EUR<!--/v--> | <!--v:dmc:variants_V0_V4/5000000/V1/expected_annual_value_eur_range/0|eur-->24.400 EUR<!--/v--> bis <!--v:dmc:variants_V0_V4/5000000/V1/expected_annual_value_eur_range/1|eur-->139.400 EUR<!--/v--> | etwa <!--v:dmc:variants_V0_V4/5000000/V2/expected_annual_value_eur_approx|eur-->-12.721 EUR<!--/v--> | <!--v:dmc:variants_V0_V4/5000000/V3/expected_annual_value_eur|eur-->-24.145 EUR<!--/v--> | <!--v:dmc:variants_V0_V4/5000000/V4/expected_annual_value_eur|eur-->-24.145 EUR<!--/v--> |
| Wert je Risikoeinheit | – | <!--v:dmc:variants_V0_V4/5000000/V1/value_per_risk_unit_range/0|d2-->0,05<!--/v--> bis <!--v:dmc:variants_V0_V4/5000000/V1/value_per_risk_unit_range/1|d2-->0,28<!--/v--> | etwa <!--v:dmc:variants_V0_V4/5000000/V2/value_per_risk_unit_approx|d3-->-0,044<!--/v--> (Näherung ohne Monte-Carlo) | <!--v:dmc:variants_V0_V4/5000000/V3/value_per_risk_unit|d3-->-0,084<!--/v--> | <!--v:dmc:variants_V0_V4/5000000/V4/value_per_risk_unit|d3-->-0,084<!--/v--> |
| NPV-Mittel über den Horizont | 0 | nicht gerechnet | nicht gerechnet | etwa <!--v:dmc:variants_V0_V4/5000000/V3/npv_mean_eur_approx|eur-->-149.526 EUR<!--/v--> (V4 plus eingesparter Aufbau) | <!--v:dmc:variants_V0_V4/5000000/V4/npv_mean_eur|eur-->-153.346 EUR<!--/v--> |
| Befundklasse | – | – | – | wie V4 | <!--v:dmc:variants_V0_V4/5000000/V4/class|raw-->PROFILE_NOT_ADMISSIBLE<!--/v--> |
| Aufwand Systembau (BS-05, Mensch und Agent) | – | <!--v:dmc:variants_V0_V4/5000000/V1/build_effort_bs05_eur|eur-->0 EUR<!--/v--> | <!--v:dmc:variants_V0_V4/5000000/V2/build_effort_bs05_eur|eur-->3.184 EUR<!--/v--> | <!--v:dmc:variants_V0_V4/5000000/V3/build_effort_bs05_eur|eur-->8.916 EUR<!--/v--> | <!--v:dmc:variants_V0_V4/5000000/V4/build_effort_bs05_eur|eur-->12.736 EUR<!--/v--> |
| Risiko | keines außer Zinsänderung | Produkt- und Emittentenrisiko, Trendfolge-Drawdowns | wie V4 plus Bedienfehler | wie V4 plus Framework-Abhängigkeit | Modell-, Ausführungs- und Betriebsrisiko (§7, §14) |
| Schlüsselpersonenrisiko | keines | gering | hoch (manuelle Orders) | hoch | hoch (Einzelbetreiber, RK-16) |
| Lernwert | keiner | gering | mittel | hoch | sehr hoch |
| Zeit bis Betrieb | sofort | Tage (nach Produktprüfung) | Wochen | Monate | Monate (BS-00 bis BS-08) |

Beträge nach Kosten einschließlich des entgangenen Geldmarktzinses auf das Brokerguthaben und der laufenden Fixkosten; Steuern nur als pauschale Sensitivität (§5.3). Der Wert je Risikoeinheit von V1 ist um die Betreiberzeit für Kauf und Überwachung bereinigt (<!--v:param:P-ECO-V1-OPS-MIN|d0-->60<!--/v--> Minuten im Monat).

## 3 Varianten über alle Kapitalstufen

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

## 4 Befund und Empfehlung zum Projektweg

1. **Innerhalb deiner Vorgaben** ist V4 in keiner Stufe zulässig. Die Prüfung folgt der Reihenfolge aus §5.7: Zuerst zählt die Befundklasse der Eigenentwicklung (in der Referenzstufe <!--v:dmc:variants_V0_V4/5000000/decision|raw-->PROFILE_NOT_ADMISSIBLE<!--/v-->), erst danach der Vergleich mit V1; in den Stufen, in denen V4 rechnet, läge die Untergrenze von V1 zusätzlich über V4. V2 und V3 ändern daran nichts, weil der Engpass Kosten je Risikoeinheit und Geldmarktzins sind, nicht der Bauaufwand.
2. **Lernwert ohne Echtgeld:** Demo- und Forschungsarbeit (BS-00 bis BS-04) kostet bis G4 <!--v:calc:spend_to_BS04|eur-->13.700 EUR<!--/v--> und liefert gemessene Kosten, Spreads und Killer-Test-Ergebnisse. Das ist der einzige Teil des Eigenbaus, den das Paket derzeit befürwortet.
3. **Alternative mit Betreiberentscheidung:** Die langsame Trendfolge ohne Sieben-Tage-Grenze (V4 Alternative TF-D1) erreicht in der Referenzstufe einen Wert je Risikoeinheit von <!--v:dmc:variants_V0_V4/5000000/V4_ALTERNATIVE_TFD1/value_per_risk_unit|d3-->0,063<!--/v--> (V1: <!--v:dmc:variants_V0_V4/5000000/V1/value_per_risk_unit_range/0|d3-->0,049<!--/v--> bis <!--v:dmc:variants_V0_V4/5000000/V1/value_per_risk_unit_range/1|d3-->0,279<!--/v-->). Sie bräuchte eine geänderte Haltedauer-Vorgabe und hat auch dann die Befundklasse <!--v:dmc:variants_V0_V4/5000000/V4_ALTERNATIVE_TFD1/class|raw-->PROFILE_NOT_ADMISSIBLE<!--/v--> (Größenregel mit Wochenendfaktor).
4. **V1** ist der natürliche Vergleichsmaßstab. Das Paket nennt keine Produkte, weil keine mit Datum, Kosten, Liquidität und Abbildungsqualität recherchiert sind (X-V1-PRODUCTS); eine Produktauswahl wäre eine Anlageentscheidung außerhalb des Systemumfangs.
