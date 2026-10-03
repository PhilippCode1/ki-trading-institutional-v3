# R3 – Literatur-Prior: Notizen

Stand und Abruf: 2026-09-24. Die Datentabelle liegt in `R3_literature_prior.json` (35 Einträge). Jede Zahl dort ist mit URL und wörtlichem Zitat (höchstens 30 Wörter) belegt. Diese Notiz führt nur Zahlen aus der Tabelle. Eigene Rechnungen daraus sind als **eigene Rechnung** markiert.

## 1. Vorgehen und Konventionen

- **Zulässige Quellen:** Verlag (ScienceDirect, AFA-Seite des Journal of Finance, OUP), NBER, SSRN, Zentralbanken (Federal Reserve Board, FRB St. Louis) und Autorenseiten.
  - Als Autorenseite gelten auch Hochschul-Repositorien der Autoren (NYU Stern, Duke, Notre Dame, City, QUB, Bangor) und die Arbeitgeberseiten der Autoren (AQR, Man Group).
  - Pedersens eigene Forschungsseite verlinkt die AQR-PDFs.
  - Nicht verwendet wurden Archive, Caches, Konferenzkopien, Foren-Uploads und Drittseiten. Deshalb fallen mehrere v2.0-Belege weg (siehe Abschnitt 5).
- **Status:**
  - `VERIFIZIERT`: Alle Zahlen des Eintrags sind belegt.
  - `TEILWEISE`: Belegte Zahlen oder Aussagen liegen vor, die Sharpe-Ratio oder ein anderes Feld aber nicht.
  - `NICHT_GEPRUEFT`: Nichts ist belegt.
- **`sharpe = null`** trägt im Feld `sharpe_note` einen Vermerk:
  - `NICHT_GEPRUEFT`: nicht auffindbar;
  - `NICHT_BERICHTET`: Die Studie berichtet keinen Gesamtwert;
  - `NICHT_ANWENDBAR`: Die Studie misst keine Sharpe-Ratio;
  - `UNTERGRENZE`: Es gibt nur eine Schranke.
- **`other_key_numbers`:** Jede Kennzahl verweist mit `source` (Index) auf das stützende Zitat.
- **Zitate aus Tabellen:** Text in eckigen Klammern am Anfang eines Zitats ist ein Fundstellen-Hinweis und gehört nicht zum Wortlaut.
  - Tabellenwerte wurden nur übernommen, wenn die Tabelle als Text maschinenlesbar war (eigene Ja/Nein-Prüfung). Sie mussten außerdem über mehrere Abrufe gleich bleiben.
  - **Warnbeispiel:** Die Kostentabelle bei Hurst/Ooi/Pedersen 2017 (Exhibit B1) liegt nur als Bild vor. Zwei Abrufe lieferten dazu *verschiedene erfundene* Zahlen. Die Tabelle wurde verworfen.
  - Ebenso verworfen wurden die Carry-Sharpe-Werte je Anlageklasse (Koijen u. a.), weil drei Abrufe drei verschiedene Wertesätze ergaben.
- **Sharpe-Werte:** Alle Angaben sind annualisiert. „brutto“ heißt vor Transaktionskosten und Gebühren, sofern nicht anders vermerkt.

## 2. Was für kurze Horizonte belegt ist

Das Zielsystem hält Positionen 4 Stunden bis 4 Tage. **Keine gefundene Studie misst genau diesen Horizont für ein diversifiziertes Futures-Portfolio nach Kosten.** Die Evidenz umgibt den Zielhorizont von beiden Seiten:

| Horizont | Befund (brutto, falls nicht anders vermerkt) | Einträge |
|---|---|---|
| Trend, 1-Monats-Lookback, monatlich | 1985–2012, 58 Märkte: Sharpe 1,26 (3 M: 1,43; 12 M: 1,52; Kombination: 1,79). Alpha-t bei Lookback 1 M / Haltedauer 1 M: 4,34, bei 12 M / 1 M: 6,61. | TF-HOP-2013, TF-MOP-2012 |
| dasselbe, jüngere Periode | 1990–2022, 43 Futures ohne Währungen: 1 M 0,36; 12 M 0,64; Mittel 1/3/12 0,59; Umschlag 1135 % gegenüber 229 % p.a. | TF-GGHM-2023 |
| 1 M in teureren „alternativen“ Märkten | Alpha-t 8,17 (1 M) gegenüber 6,78 (12 M). In traditionellen Märkten 4,12 gegenüber 5,72. Die Autoren halten die Kosten alternativer Märkte für höher. | TF-BABU-2020-JOIM |
| 1-Monats-Querschnittsmomentum | Alle Anlageklassen: Sharpe 1,08, Rohstoffe 1,14 (Momentum, nicht Umkehr). Devisen MOM(1,1): 0,95. | MOM-ZLK-2019, FX-MSSS-2012 |
| 1–4 Wochen, Devisen | Momentum statt Umkehr, bis 8 % p.a. In der jüngeren Teilperiode kleiner. Keine Sharpe belegt. | FX-RMV-2014 |
| 1 Woche, 24 US-Futures | Umkehr: 0,31 % pro Woche (16,12 % p.a.), Stichprobe 1983–2000. Keine Sharpe belegt. | REV-WY-2004 |
| Umkehr, Rohstoffe | In 189 Formations-/Haltefenstern kein signifikanter Umkehrgewinn. | REV-UZ-2020 |
| Intraday, SPY | Sharpe 1,08 (6,67 % p.a., Volatilität 6,19 %), 1993–2013. | INTRA-GHLZ-2018 |
| Intraday, über 60 Futures | Sharpe je Klasse 0,87 (Devisen) bis 1,73 (Aktienindex), 1974–2020, ohne Kosten. Die Vorhersagekraft kehrt über die Folgetage um. | INTRA-BDLM-2021 |
| Intraday, 16 Märkte | In 13 Märkten signifikant positiv, in 12 Märkten Sharpe über Buy-and-hold. Zahlenwerte ungeprüft. | INTRA-LSU-2022 |
| Kurzfrist-CTA-Index | SG Short-Term Traders Index: definiert über Haltedauer unter 10 Tagen. **Keine Kennzahlen aus der Primärquelle.** | IDX-SG-STTI |
| Carry | Diversifiziert über alle Klassen 1,1, Durchschnitt über Klassen 0,74. Werte je Futures-Klasse ungeprüft. Belegt sind Querschnitts- und Zeitreihenstrategien auf das Carry-Signal; als Filter für 4 h–4 T nur indirekt. | CARRY-KMPV-2018 |

**Lesart:**

- **Kurze Trend-Lookbacks tragen, aber schwächer als lange.** Das gilt für die Sharpe-Ratio und die t-Statistiken. Das Verhältnis 1 M zu 12 M beträgt 0,83 (1985–2012) und 0,56 (1990–2022) (**eigene Rechnung**; unterschiedliche Universen, 1990–2022 ohne Währungen).
- **Die Richtung zwischen Momentum und Umkehr hängt vom Horizont ab.** Unterhalb eines Monats ist sie nicht robust belegt:
  - Umkehr auf Wochenbasis in US-Futures bis 2000;
  - Momentum auf 1–4 Wochen in Devisen;
  - Momentum auf einen Monat über Anlageklassen;
  - Intraday-Momentum, das über die Folgetage wieder umkehrt.
- **Folge für ein Signal mit 4 h–4 T Haltedauer:** Ein Intraday-Momentum-Signal kann über die Haltedauer teilweise gegen die Position laufen. Das ist nicht beziffert.

## 3. Wie stark Kosten die Kurzfrist-Evidenz verändern

| Befund | Zahl | Eintrag |
|---|---|---|
| Myopische Strategie, die alle Signale einschließlich des 5-Tage-Signals voll handelt | Sharpe brutto 0,83, netto **−9,84** (bei hohen Kosten −10,11) | COST-GP-2013 |
| Dieselben Signale mit kostenoptimalem, trägem Handel | brutto 0,62, netto 0,58 (hohe Kosten: 0,53). Langsame Signale erhalten mehr Gewicht. | COST-GP-2013 |
| Devisen-Momentum 1 M / 1 M | Rendite mit vollem Spread von knapp 10 % auf etwa 4 % p.a.; Umschlag über 70 % pro Monat | FX-MSSS-2012 |
| Devisen 1–4 Wochen | Break-even-Kosten **2 bp** (sehr kurzfristig) gegenüber 97 bp (monatlich) | FX-RMV-2014 |
| Umkehr in US-Futures, 1 Woche | Break-even 0,16 % einseitig | REV-WY-2004 |
| Trend 1 M gegenüber 12 M | Umschlag 1135 % gegenüber 229 % p.a.; dynamische Mischung bis 29 bp mittlere Kosten besser | TF-GGHM-2023 |
| Intraday-Momentum über 60 Futures | ohne Kosten; laut Autoren nach Kosten für viele nicht ausbeutbar; S&P-500-Future bei 1 Tick Kosten mit positiver Netto-Sharpe (Wert nicht genannt) | INTRA-BDLM-2021 |
| Trend über drei Geschwindigkeiten | brutto 1,79, nach Gebühren (2/20) und Kosten „near 1“; Kosten 1–4 % p.a. | TF-HOP-2013 |
| Umschlag-Schwelle (Aktien) | unter 50 % einseitig pro Monat meist netto signifikant, darüber selten | COST-NMV-2016 |
| Geschwindigkeit (Industrie) | Kosten treffen schnellere Geschwindigkeiten überproportional | TF-MAN-SPEED |

**Eigene Rechnungen aus belegten Zahlen** (Annahme 252 Handelstage):

- Behaltene Nettorendite je Befund:
  - Devisen-Momentum mit vollem Spread: etwa 0,4 (4 % / 10 %);
  - kostenoptimierter dynamischer Handel: 0,94 (0,58 / 0,62);
  - Trend nach Gebühren und Kosten: etwa 0,56 (1 / 1,79).
- Bruttoertrag je Handelstag bei Intraday-Momentum:
  - Aktienindexfutures etwa 2,7 bp (6,86 % / 252);
  - Anleihen etwa 0,9 bp;
  - Rohstoffe etwa 1,7 bp;
  - Währungen etwa 0,3 bp;
  - SPY etwa 2,6 bp.
- Jeder Handelstag umfasst Ein- und Ausstieg. Der Vorteil pro Runde liegt damit im Bereich weniger Basispunkte oder darunter.

**Schluss:**

- Je kürzer der Horizont, desto größer der Anteil der Kosten an der Bruttorendite.
- Brutto-Sharpe-Werte kurzer Signale (Intraday 0,87–1,73; 1-M-Trend 1,26) taugen ohne ausdrückliches Kostenmodell nicht als Prior.
- Die belegte Netto-Evidenz für Horizonte unter einem Monat ist dünn und liegt nahe der Gewinnschwelle, mit einer Ausnahme: Kostenoptimierter, träger Handel erhält den größten Teil der Brutto-Sharpe, indem er schnelle Signale abschwächt.

## 4. Zerfall nach Veröffentlichung, Mehrfachtests, Umsetzungsrealität

| Befund | Zahl | Eintrag |
|---|---|---|
| Aktienprädiktoren | Rendite −26 % außerhalb der Stichprobe, −58 % nach Veröffentlichung | DECAY-MP-2016 |
| Mehrfachtests | Hürde t > 3,0; Beispiel Sharpe 0,75 → 0,32 (T = 240, N = 200) | DECAY-HLZ-2016, DECAY-HL-2015 |
| Anomalien nach Kosten und Zerfall (Aktien) | im Mittel 8 bp pro Monat | DECAY-CV-2020 |
| SG Trend Index (realisiert) | 0,28 (2000–2018), 0,05 (2010–2018) | IDX-SGTREND-BABU-2020 |
| CTAs 1994–2007 | netto 0,85 % p.a. über T-Bills (nicht signifikant), brutto 5,4 % | CTA-BGR-2014 |
| Managed-Futures-Indizes bis 6/2012 | BTOP50 0,50; DJCS 0,27 (Gebührenbasis im Tabellentext nicht genannt) | TF-HOP-2013 |
| Devisen, technische Regeln | 388 Portfolios: 0,62 → 0,06 out-of-sample; Nettoüberrendite 5,74 % → 1,91 % p.a.; Gewinne von über 3 % auf etwa null | FX-HUTCH-2022, FX-NWU-2009, FX-OLSON-2004 |
| Gegenevidenz zu TSMOM | Einzelanlagen zeigen wenig TSMOM; Ergebnis stark durch Volatilitätsskalierung getrieben | SKEPT-HLWZ-2020, SKEPT-KTW-2016 |

**Eigene Rechnung** (behaltener Anteil):

- nach Veröffentlichung 0,42;
- SG Trend 2010–2018 gegenüber 2000–2018: 0,18;
- Devisenregeln out-of-sample: etwa 0,10;
- Mehrfachtest-Beispiel: etwa 0,43;
- Gebührenanteil bei CTAs: etwa 84 % der Bruttorendite.

## 5. Lücken und offene Punkte

1. **Hurst/Ooi/Pedersen 2017:**
   - Die Sharpe-Werte (gesamt, netto, Dekaden, 1/3/12 M) und die Kostentabelle liegen nur als Bild vor.
   - SSRN antwortete mit HTTP 429, die JPM-Seite ist robots-gesperrt.
   - Der v2.0-Wert 0,76 netto stammte von einer unzulässigen Drittseite und bleibt ungeprüft.
2. **Carry:** Die Sharpe je Futures-Klasse ist ungeprüft (widersprüchliche Transkription). Belegt sind nur der Gesamtwert 1,1 und der Durchschnitt 0,74 (Arbeitspapierfassung; die Zeitschriftenfassung kann abweichen).
3. **Baltas/Kosowski 2013 (Sharpe je Rebalancing-Frequenz), Levine/Pedersen 2016, Li/Sakkas/Urquhart 2022:** Die Volltexte waren nicht abrufbar. Belegt sind nur die Aussagen der Zusammenfassungen.
4. **SG Short-Term Traders Index:** Die Primärquelle liefert keine Rendite, Volatilität oder Sharpe. Die Daten gibt es nur über die SG-Plattform.
5. **Suhonen/Lennkh/Perez 2017:** nicht geprüft. Die v2.0-Werte (1,20 → 0,31) dürfen nicht verwendet werden.
6. **Kein Beleg für den Zielhorizont:** Es fehlt eine diversifizierte Futures-Strategie mit 4 h–4 T Haltedauer und Netto-Sharpe. Intraday-Belege sind brutto oder beziehen sich auf einen einzelnen Markt. Umkehr-Belege sind alt (bis 2000) oder negativ.
7. **Korrelationen zwischen Trend, Carry und Umkehr** wurden in R3 nicht erhoben. Der Rechner (§ 6.3) braucht sie für das Portfolio.
8. **Kosten je Transaktion in Futures:** In R3 gibt es dafür keine geprüften Werte (die AQR-Tabelle ist verworfen). Die Kostenannahmen müssen aus dem eigenen Kostenmodell (§ 5.1) kommen.
9. **Veröffentlichungsangaben:**
   - Neely/Weller/Ulrich: nur die Arbeitspapierfassung ist geprüft, nicht die JFQA-Fassung.
   - Bhardwaj/Gorton/Rouwenhorst: Die Zahlen stammen aus der NBER-Fassung 1994–2007; der Zeitraum der RFS-Fassung ist nicht geprüft.
   - Breaking Bad Trends: Jahrgang und Heft laut DOI 2023 online, Heft nicht geprüft.
10. **Suchbudget:** Das Websuche-Kontingent der Sitzung (200 Aufrufe) war während R3 erschöpft. Weitere Kandidaten wurden nicht mehr gesucht, zum Beispiel akademische Studien zu Kurzfrist-CTAs oder Arbeiten zu Handelskosten von Trendfolge und Kapazität über Baltas/Kosowski hinaus.

## 6. Hinweise für `prior_derivation.py`

- **Anker verwenden:** nur Einträge mit `sharpe` ungleich null und Status `VERIFIZIERT` oder `TEILWEISE`, jeweils mit Periode und Basis aus `sharpe_note`. Die übrigen Einträge dienen als Nebenbedingungen (Abschläge, Break-even, Umschlag).
- **Trend mehrerer Geschwindigkeiten, brutto:**
  - TF-HOP-2013 (1,79 kombiniert; 1 M 1,26);
  - TF-BABU-2020-JOIM (1,17, 12 M, traditionelle Märkte);
  - TF-GGHM-2023 (0,59, Mittel 1/3/12, 1990–2022, ohne Währungen).
  - Die Spanne zwischen älteren und jüngeren Stichproben ist groß. Sie gehört in die Unsicherheitsverteilung und darf nicht zu einem Punktwert gemittelt werden.
- **Umsetzungsrealität:** SG Trend 0,28 bzw. 0,05 und CTAs nach Gebühren (CTA-BGR-2014) dienen als Obergrenzen-Plausibilität für netto erreichbare Werte.
- **Kostenabzug über Umschlag rechnen**, nicht pauschal. Kostenabzug in Sharpe-Einheiten = Umschlag p.a. × Kosten je Umschlag / Zielvolatilität.
  - Den Umschlag kurzer Signale liefert TF-GGHM-2023.
  - Die Break-even-Werte (2 bp, 16 bp, 29 bp) dienen als Plausibilitätsprüfung.
- **Abschläge:**
  - Veröffentlichung (DECAY-MP-2016) und Mehrfachtests (DECAY-HL-2015, DECAY-HLZ-2016) getrennt anwenden.
  - Beide Studien beziehen sich auf Aktien; die Übertragung auf Futures ist eine Annahme und muss als solche gekennzeichnet werden.
- **Kurzfrist-Umkehr und Intraday-Momentum:**
  - Nach § 6.4 behandeln: kein belastbarer Netto-Prior, also Hürde t > 3 (DECAY-HLZ-2016).
  - Den Prior bis zu eigener Evidenz bei null oder nahe null ansetzen. Das ist eine Empfehlung, kein Literaturwert.
