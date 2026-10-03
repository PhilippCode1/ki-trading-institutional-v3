# R2b – Kontraktdaten Energie, Metalle, Agrar, Krypto: Notizen

**Abrufdatum aller Quellen:** 2026-09-24. **Datendatei:** `R2b_commodity_crypto_specs.json` (44 Kontrakte, 416 Zitatbelege aus 81 offiziellen URLs).
**Zweck:** Instrumenttabelle für das Konzeptpaket (Haltedauer Stunden bis wenige Tage). Die Werte hier fassen die Datei zusammen. Die Einzelbelege mit URL und wörtlichem Zitat stehen je Feld in der JSON-Datei. Verweise `[Qn]` beziehen sich auf das Quellenverzeichnis in Abschnitt 6.

---

## 1. Methode und Grenzen

- **Nur Primärquellen:** CME Group (Rulebook, FAQ, Factcards, Education-Seiten, Notices), ICE-Produktseiten und die Euronext-Spezifikationsseiten. Sekundärquellen wurden nicht verwendet.
- **CME-Contract-Specs-Seiten waren nicht nutzbar.** `*.contractSpecs.html`, die Trading-Hours-Seite und die Margin-Seiten werden per JavaScript nachgeladen; der Abruf lieferte keine Spezifikationswerte [Q69][Q70]. Deshalb stützt sich die Datei auf:
  1. die CME-Rulebook-Kapitel (rechtlich maßgeblich; Kontraktgröße, Tick, Verfall, Lieferung, Verweis auf Rule 589);
  2. datierte CME-Factcards, FAQs und Education-Seiten (Handelszeiten, Codes, Monatszyklen). Bei jedem dieser Belege ist das Dokumentdatum oder die Referenznummer angegeben.
- **Nicht lesbare Dokumente:**
  - Die Tabelle der Special Price Fluctuation Limits liegt nur als xlsx vor [Q68].
  - Rulebook-Kapitel 5 (NYMEX) [Q72] und Kapitel 7 (CBOT) [Q71] wurden beim Abruf abgeschnitten.
  - Die Margin-Tabelle des CME-Advisory 26-315 (wirksam 18.09.2026) ist nur verlinkt und war nicht abrufbar [Q67].
  - Archive, Caches, Spiegel oder curl/Python wurden gemäß Vorgabe nicht verwendet.
- **Suchbudget erschöpft:** Das WebSearch-Kontingent der Sitzung (200/200) war während der Recherche aufgebraucht. Offene Punkte (Abschnitt 5) ließen sich danach nur noch über bekannte URLs prüfen, nicht mehr über eine Suche.
- **Statusregel:**
  - **VERIFIZIERT:** Alle Kernfelder sind mit Primärquelle und Zitat belegt. Kernfelder sind Symbol, Größe, Quotierung, Tick, Tickwert, Handelszeiten, Settlement, LTD, Liefer- bzw. FND-Regel bei physischer Lieferung, Preislimit-Regel und Monate. Der Tickwert darf als Größe × Tick abgeleitet sein. Ältere Dokumente sind zulässig, wenn ihr Datum angegeben ist und keine neuere Primärquelle widerspricht.
  - **TEILWEISE:** Mindestens ein Kernfeld ist `null`, widersprüchlich oder nur unbestimmt belegt.
  - **NICHT_GEPRUEFT:** Die Kernfelder sind überwiegend nicht belegbar.
  - **Margin** zählt nicht zum Status (der Auftrag lässt `null` zu).
- **Zeitumrechnung MEZ/MESZ (abgeleitet, nicht zitiert):**
  - Normalfall: CT + 7 h, ET + 6 h; London + 1 h ganzjährig.
  - Differenzwochen (Sommerzeit in USA und EU verschieden): 2026 vom 08.03. bis 28.03. und vom 25.10. bis 31.10., 2027 vom 14.03. bis 27.03. In diesen Wochen liegen CT- und ET-basierte Zeiten in MEZ/MESZ 1 h früher.

## 2. Ergebnisübersicht

**44 Kontrakte: 29 VERIFIZIERT, 15 TEILWEISE, 0 NICHT_GEPRUEFT.**

Klärung „Micro Silver (SIL bzw. SIC)“:
- **SIL** ist Micro Silver mit 1.000 oz und physischer Lieferung über ACE [Q26][Q63].
- **SIC** ist ein eigener Kontrakt, 100-Ounce Silver: bar abgerechnet und seit September 2026 im 24/7-Handel [Q11][Q27].
- Beide sind als getrennte Einträge erfasst. Alle optional genannten Kontrakte (BZ, MNG, 1OZ, ALI, MZC, MZS, MZW) sind gelistet und belegt.

| Klasse | Symbol | Börse | Größe | Tick → Tickwert | Settlement | Status | Grund für TEILWEISE |
|---|---|---|---|---|---|---|---|
| Energie | CL | NYMEX | 1.000 bbl | 0,01 USD → 10 USD | physisch | VERIFIZIERT | – |
| Energie | MCL | NYMEX | 100 bbl | 0,01 USD → 1 USD | bar | VERIFIZIERT | – |
| Energie | B | ICE Futures Europe | 1.000 bbl | 0,01 USD → 10 USD¹ | EFP, Option auf Barausgleich | TEILWEISE | Preislimit/IPL nicht belegt |
| Energie | BZ | NYMEX | 1.000 bbl | 0,001 USD (Rulebook) vs. 0,01 USD (Education) | bar | TEILWEISE | Tick widersprüchlich; Monate unbestimmt |
| Energie | NG | NYMEX | 10.000 MMBtu | 0,001 USD → 10 USD | physisch | VERIFIZIERT | – |
| Energie | QG | NYMEX | 2.500 MMBtu | 0,005 USD → 12,50 USD | bar | TEILWEISE | Handelszeiten nicht belegt; Monate unbestimmt |
| Energie | MNG | NYMEX | 1.000 MMBtu | 0,001 USD → 1 USD | bar | VERIFIZIERT | – |
| Energie | RB | NYMEX | 42.000 gal | 0,0001 USD → 4,20 USD | physisch | VERIFIZIERT | – |
| Energie | HO | NYMEX | 42.000 gal | 0,0001 USD → 4,20 USD | physisch | VERIFIZIERT | – |
| Energie | G | ICE Futures Europe | 100 t | 0,25 USD → 25 USD¹ | physisch | TEILWEISE | Preislimit nicht belegt |
| Energie | TFM | ICE Endex | 1 MW × Stunden | 0,005 EUR/MWh → ≈ 3,60 EUR je Lot¹ | physisch | TEILWEISE | Preislimit nicht belegt |
| Metalle | GC | COMEX | 100 oz | 0,10 USD → 10 USD¹ | physisch | VERIFIZIERT | – |
| Metalle | MGC | COMEX | 10 oz | 0,10 USD → 1 USD¹ | physisch (ACE) | VERIFIZIERT | – |
| Metalle | 1OZ | COMEX | 1 oz | 0,25 USD → 0,25 USD¹ | bar | VERIFIZIERT | – |
| Metalle | SI | COMEX | 5.000 oz | 0,005 USD → 25 USD¹ | physisch | VERIFIZIERT | – |
| Metalle | SIL | COMEX | 1.000 oz | 0,005 USD → 5 USD¹ | physisch (ACE) | VERIFIZIERT | – |
| Metalle | SIC | COMEX | 100 oz | 0,01 USD → 1 USD¹ | bar | VERIFIZIERT | – |
| Metalle | HG | COMEX | 25.000 lb | 0,0005 USD → 12,50 USD¹ | physisch | VERIFIZIERT | – |
| Metalle | MHG | COMEX | 2.500 lb | 0,0005 USD → 1,25 USD | bar | TEILWEISE | Listungstiefe 23 vs. 24 Monate |
| Metalle | PL | NYMEX | 50 oz | 0,10 USD → 5 USD¹ | physisch | VERIFIZIERT | – |
| Metalle | PA | NYMEX | 100 oz | 0,50 USD → 50 USD¹ | physisch | VERIFIZIERT | – |
| Metalle | ALI | COMEX | 25 t | 0,25 USD → 6,25 USD | physisch | VERIFIZIERT | – |
| Agrar | ZC | CBOT | 5.000 bu | ¼ ¢ → 12,50 USD | physisch | TEILWEISE | FND/First Position Day nicht belegt |
| Agrar | MZC | CBOT | 500 bu | ½ ¢ → 2,50 USD | bar | VERIFIZIERT | – |
| Agrar | ZS | CBOT | 5.000 bu | ¼ ¢ → 12,50 USD | physisch | TEILWEISE | FND nicht belegt |
| Agrar | MZS | CBOT | 500 bu | ½ ¢ → 2,50 USD | bar | VERIFIZIERT | – |
| Agrar | ZW | CBOT | 5.000 bu | ¼ ¢ → 12,50 USD | physisch | TEILWEISE | FND nicht belegt |
| Agrar | MZW | CBOT | 500 bu | ½ ¢ → 2,50 USD | bar | VERIFIZIERT | – |
| Agrar | KE | CBOT | 5.000 bu | ¼ ¢ → 12,50 USD | physisch | TEILWEISE | FND nicht belegt |
| Agrar | ZM | CBOT | 100 short tons | 0,10 USD → 10 USD | physisch | TEILWEISE | FND nicht belegt |
| Agrar | ZL | CBOT | 60.000 lb | 0,01 ¢ → 6 USD | physisch | TEILWEISE | FND nicht belegt |
| Agrar | LE | CME | 40.000 lb | 0,00025 USD → 10 USD | physisch | VERIFIZIERT | – |
| Agrar | HE | CME | 40.000 lb | 0,00025 USD → 10 USD | bar | TEILWEISE | LTD nicht belegt; Monate nur aus 2017 |
| Agrar | GF | CME | 50.000 lb | 0,00025 USD → 12,50 USD | bar | VERIFIZIERT | – |
| Agrar | SB | ICE Futures U.S. | 112.000 lb | 0,01 ¢ → 11,20 USD | physisch | VERIFIZIERT | – |
| Agrar | KC | ICE Futures U.S. | 37.500 lb | 0,05 ¢ → 18,75 USD | physisch | VERIFIZIERT | – |
| Agrar | CC | ICE Futures U.S. | 10 t | 1 USD → 10 USD | physisch | VERIFIZIERT | – |
| Agrar | CT | ICE Futures U.S. | 50.000 lb | 0,01 ¢ → 5 USD | physisch | VERIFIZIERT | – |
| Agrar | EBM | Euronext Paris | 50 t | 0,25 EUR → 12,50 EUR | physisch | TEILWEISE | Preislimit nicht belegt |
| Agrar | ECO | Euronext Paris | 50 t | 0,25 EUR → 12,50 EUR | physisch | TEILWEISE | Preislimit nicht belegt |
| Krypto | BTC | CME | 5 BTC | 5 USD → 25 USD | bar | VERIFIZIERT | – |
| Krypto | MBT | CME | 0,1 BTC | 5 USD → 0,50 USD | bar | VERIFIZIERT | – |
| Krypto | ETH | CME | 50 ETH | 0,50 USD → 25 USD | bar | VERIFIZIERT | – |
| Krypto | MET | CME | 0,1 ETH | 0,50 USD → 0,05 USD | bar | VERIFIZIERT | – |

¹ Tickwert abgeleitet (Kontraktgröße × Tick). Die Größe und der Tick selbst sind belegt.

## 3. Auffälligkeiten

### 3.1 24/7-Handel bei CME (neu 2026)

- **Krypto (BTC, MBT, ETH, MET):**
  - Rund um die Uhr seit Freitag, 29.05.2026 [Q6]. Das gilt für alle Krypto-Futures und -Optionen außer Spot-Quoted Futures [Q5].
  - Wartungsfenster: Mo–Fr 16:00–16:02 CT und Sa 02:00–04:00 CT [Q4][Q5]. In MEZ/MESZ (abgeleitet): Mo–Fr 23:00–23:02 und Sa 09:00–11:00.
  - Handel von Freitagabend bis Sonntagabend erhält das Trade Date des folgenden Geschäftstags. Clearing, Settlement und Meldewesen laufen ebenfalls erst dann [Q4][Q5].
- **1-Ounce Gold (1OZ):** 24/7 seit 24.07.2026, mit denselben Wartungsfenstern [Q9][Q10][Q7].
- **100-Ounce Silver (SIC):**
  - Die Pressemitteilung nennt den 11.09.2026 als Start, „pending regulatory review“ [Q8].
  - Die FAQ bestätigt: „now available to trade 24 hours a day, seven days a week“ [Q11].
- **10-Barrel WTI (TCL, 1/100 von CL):**
  - Neuer, bar abgerechneter Kontrakt, angekündigt für den 30.08.2026 (vorbehaltlich regulatorischer Prüfung) [Q7].
  - CME nennt ihn „the first Energy contract available for 24/7 trading“ [Q12]. Daraus folgt (Schlussfolgerung, nicht wörtlich belegt), dass CL und MCL im 23/5-Rhythmus bleiben. Für die Fünf-Tage-Nutzung nennt die Seite „existing Globex hours“: So–Fr 17:00–16:00 CT mit 60 Minuten Pause [Q12].
  - TCL ist nicht beauftragt und daher nicht in der JSON-Datei.
- **Folge fürs System:**
  - Bei 24/7-Kontrakten laufen Kursrisiko und Stop-Logik auch am Wochenende weiter.
  - Die Bewertung bezieht sich auf das Trade Date des folgenden Geschäftstags.
  - Die Wochenend-Trade-Date-Regel ist nur für Krypto ausdrücklich belegt, für 1OZ und SIC nicht (offener Punkt).

### 3.2 Preislimits

**CBOT-Getreide und Ölsaaten (variable Tageslimits):**
- Reset halbjährlich im Mai und November: 7 % des Durchschnitts-Settlements, gerundet, mit Mindestwerten. Nach einem Limit-Settlement werden die Limits am nächsten Geschäftstag um den Faktor 1,5 erweitert [Q35][Q36][Q37][Q38][Q39].
- Mindestlimits laut Rulebook: Corn 20 ¢, Soybeans 50 ¢, Wheat 30 ¢, Soybean Meal 20 USD je Ton, Soybean Oil 2 ¢ je Pfund [Q35][Q36][Q39][Q38][Q37].
- Die Micro-Kontrakte übernehmen die Limits des Standardkontrakts [Q40][Q43].
- Nächster Reset: November 2026 (zeitliche Angabe aus den Rulebook-Kapiteln, dort sinngemäß erfasst). Die Werte unten gelten bis dahin.

**CME-Vieh:**
- Live Cattle: jährlicher Reset, wirksam ab dem ersten Handelstag im Juni; 3,5 % des 45-Tage-Durchschnitts, mindestens 0,040 USD/lb [Q44].
- Lean Hogs: 4,5 %, mindestens 0,03 USD/lb. Im laufenden Monat gilt an den letzten zwei Handelstagen kein Limit [Q46].
- Feeder Cattle: 1,25 × das Live-Cattle-Limit [Q45].

**Aktuelle Limits, Stand Handelstag 24.09.2026 [Q1].** Die Spalten „USD je Kontrakt“ sind abgeleitet (Limit × Kontraktgröße):

| Kontrakt | Initial | ≙ USD je Kontrakt | Erweitert | ≙ USD je Kontrakt |
|---|---|---|---|---|
| ZC / MZC | 0,30 USD/bu | 1.500 / 150 | 0,45 | 2.250 / 225 |
| ZS / MZS | 0,85 USD/bu | 4.250 / 425 | 1,30 | 6.500 / 650 |
| ZW / MZW | 0,45 USD/bu | 2.250 / 225 | 0,70 | 3.500 / 350 |
| KE | 0,45 USD/bu | 2.250 | 0,70 | 3.500 |
| ZM | 20,00 USD/t | 2.000 | 30,00 | 3.000 |
| ZL | 0,045 USD/lb | 2.700 | 0,070 | 4.200 |
| LE | 0,0850 USD/lb | 3.400 | 0,1275 | 5.100 |
| GF | 0,1075 USD/lb | 5.375 | 0,1600 | 8.000 |
| HE | 0,0425 USD/lb | 1.700 | 0,0625 | 2.500 |

Für Kalenderspreads gelten jeweils die doppelten Werte, z. B. Corn 0,60 USD [Q1].

**ICE Futures U.S. (Softs):**
- Sugar No. 11, Coffee C und Cocoa: „Daily Price Limit: None“ [Q48][Q49][Q50].
- Cotton No. 2: Tageslimit variabel zwischen 3 und 7 ¢/lb [Q51]. Das entspricht 1.500 bis 3.500 USD je Kontrakt (abgeleitet). Die aktuelle Stufe ist nicht geprüft.

**CME Energie, Metalle und Krypto:**
- Die Rulebook-Kapitel verweisen auf Rule 589, die „Special Price Fluctuation Limits“. Beispiele: [Q16][Q17][Q18][Q19][Q20][Q21][Q22][Q23] für Energie, [Q25]–[Q29] und [Q34] für Metalle. Krypto hat zusätzlich „daily price limits“ [Q57][Q60][Q61].
- CME beschreibt Dynamic Circuit Breakers: ein rollierendes 60-Minuten-Fenster und eine produktspezifische Variante in Prozent des Vortages-Settlements [Q2][Q4]. Die Ausbildungsseite von 2020 nennt ±10 % und eine 2-Minuten-Pause als Beispiel [Q3]. Das ist kein belegter Produktparameter.
- **Die Prozentsätze je Produkt sind nicht geprüft**, weil die xlsx-Tabelle nicht lesbar war [Q68].

**ICE Futures Europe (B, G), ICE Endex (TFM) und Euronext (EBM, ECO):**
- Die Spezifikationsseiten enthalten keine Zeile zu Preislimits [Q52][Q53][Q54][Q55][Q56].
- Eine fehlende Zeile belegt nicht „keine Limits“. Deshalb ist das Feld `null` und der Status TEILWEISE.

**Folge fürs System:** Bei Agrar und Vieh kann ein Markt am Limit stehen („limit-locked“), dann ist ein Ausstieg unmöglich. Die Limitbewegung je Kontrakt (Tabelle oben) gehört ins Stressszenario und in die Positionsgrößenregel.

### 3.3 Liefer- und Verfallsrisiken

**Physische Lieferung:**
- Energie:
  - CL: Cushing, Oklahoma [Q16].
  - NG: Henry Hub, Erath, Louisiana [Q20].
  - RB und HO: New York Harbor [Q21][Q22].
  - Gasoil: ARA-Region, Lieferung vom 16. bis zum Monatsende [Q53].
  - TTF: Lieferung stündlich über den ganzen Liefermonat [Q54].
  - Brent: EFP mit Option auf Barausgleich [Q52].
- Metalle: GC, SI, HG, PL, PA, ALI, dazu **MGC und SIL** (siehe unten).
- Agrar:
  - CBOT-Getreide mit Shipping Certificates bzw. Warehouse Receipts [Q35]–[Q39].
  - Live Cattle [Q44].
  - ICE-Softs [Q48]–[Q51].
  - Euronext: Silos für EBM, FOB-Barge für ECO [Q55][Q56].

**FND vor dem LTD (dieses Datum bindet die Rollregel):**
- COMEX- und NYMEX-Metalle: First Notice Day ist der letzte Geschäftstag des Monats vor dem Liefermonat [Q14][Q15]. Der LTD liegt erst am drittletzten Geschäftstag des Liefermonats.
- Coffee: FND sieben Geschäftstage vor dem ersten Geschäftstag des Liefermonats [Q49].
- Cocoa: FND zehn Geschäftstage vor dem sechsten Geschäftstag des Liefermonats. Das ist der ICE-Wortlaut und erneut prüfenswert [Q50].
- Cotton: FND fünf Geschäftstage vor dem ersten Liefertag [Q51].
- Live Cattle: Andienung erst nach dem ersten Freitag des Kontraktmonats [Q44].
- **CBOT-Getreide: FND bzw. First Position Day nicht belegt**, weil Kapitel 7 beim Abruf abgeschnitten war [Q71]. Das ist ein offener Punkt.

**Micros mit physischer Lieferung:**
- Micro Gold (MGC) und Micro Silver (SIL) werden physisch über Accumulated Certificates of Exchange (ACE) beliefert [Q25][Q26].
- Anders als MCL, MNG, MHG, 1OZ, SIC und die Micro-Grains gilt dafür dieselbe Rollpflicht vor dem FND wie beim Standardkontrakt.

**Bar abgerechnete Kleinkontrakte verfallen früher als der Standardkontrakt:**
- MCL: einen Geschäftstag vor CL [Q17].
- QG: am Geschäftstag vor dem letzten Handelstag von NG [Q18].
- MNG: einen Geschäftstag vor dem Verfall von NG [Q19].
- Micro-Grains: am Freitag, der mindestens 2 Geschäftstage vor dem letzten Geschäftstag des Vormonats liegt [Q40][Q41][Q42].
- 1OZ, SIC und MHG: am drittletzten Geschäftstag des Vormonats [Q28][Q27][Q29].
- Folge: Der Rollkalender muss je Symbol geführt werden und darf nicht vom Standardkontrakt übernommen werden.

**Verfall im Vorvormonat:** Bei ICE Brent und CME BZ endet der Handel am letzten Geschäftstag des zweiten Monats vor dem Kontraktmonat [Q52][Q23].

**Euronext-Lieferlimits:** Euronext Clearing veröffentlicht sie 80 Tage vor dem LTD. Sie gelten ab 12 Tagen vor dem LTD [Q55].

### 3.4 Negative Preise

- CME Clearing hatte am 08.04.2020 (Advisory 20-152) einen getesteten Plan für einen möglicherweise negativen Basiswert bei bestimmten Energieoptionen veröffentlicht [Q13]. Negative Preise sind bei Energie-Futures also technisch vorgesehen.
- Das historische negative Settlement vom April 2020 ist hier **nicht** eigens belegt.
- Folgen fürs System (abgeleitet):
  - Preis- und Validierungslogik muss Werte ≤ 0 zulassen.
  - Log-Renditen und prozentuale Stops versagen bei Preisen nahe 0. P&L und Risiko sollten in Ticks bzw. in absoluten Preisdifferenzen gerechnet werden.
  - Das betrifft auch bar abgerechnete Ableitungen wie MCL, deren Floating Price sich auf CL bezieht [Q17].

### 3.5 Quellenkonflikte und veraltete Dokumente

| Thema | Konflikt | Auflösung |
|---|---|---|
| SIL-Tick | Die Micro-Metals-Seite zeigt 0,01 USD je oz bzw. 10 USD je Kontrakt [Q32]. | Das Rulebook nennt 0,005 USD [Q26]; Clearing Advisory 20-334 bestätigt die Reduktion ab 21.09.2020 [Q33]. Es gilt 0,005 USD. |
| ETH-Tick | Die Factcard von 2021 nennt 0,25 USD bzw. 12,50 USD [Q58]. | Rulebook [Q57] und Broschüre 03/2026 [Q59] nennen 0,50 USD bzw. 25 USD. Es gilt das Rulebook. |
| BZ-Tick | Das Rulebook nennt 0,001 USD [Q23], die Education-Seite von 2021 „$.01“ [Q24]. | Ungeklärt, Status TEILWEISE. |
| MHG-Listung | Die Factcard nennt 23 Monate [Q30], die FAQ 24 Monate [Q31]. | Ungeklärt, Status TEILWEISE. |
| Handelszeiten in Altdokumenten | Die WTI-Factcard von 2012 [Q65] und die Silver-Factcard von 2012 [Q66] nennen 18:00–17:15 ET mit 45 Minuten Pause und Parketthandel. Die Krypto-Broschüre 03/2026 [Q59] nennt noch So–Fr 17:00–16:00 CT. | Alle überholt; nicht verwendet bzw. durch 24/7 ersetzt [Q4]. |
| Krypto-Listung | Die Factcards von 2021 nennen „six consecutive months … two Dec“. | Die Broschüre 03/2026 nennt zusätzlich Quartalskontrakte für vier weitere Quartale [Q59]. Es gilt die Broschüre 2026. |

### 3.6 Besonderheiten bei Kontraktgröße und Tick (relevant für Kosten und Sizing)

- PA hat einen groben Outright-Tick von 0,50 USD, also 50 USD je Kontrakt [Q34].
- SI kostet 25 USD je Tick, SIL 5 USD und SIC 1 USD (Tickwerte abgeleitet) [Q26][Q27].
- TTF:
  - Die Mindesthandelsgröße ist 5 Lots, also 5 MW [Q54].
  - Der Tickwert hängt von der Stundenzahl der Lieferperiode ab (23, 24 oder 25 Stunden je Tag) [Q54]. Ein Monat mit 30 Tagen ergibt ≈ 3,60 EUR je Lot bzw. 18 EUR für die Mindestgröße (abgeleitet).
- MET hat einen Tickwert von 0,05 USD [Q61]. Gebühren je Kontrakt dürften die Kosten dominieren (Gebühren nicht geprüft).
- ALI hat geringe Liquidität: Das Rekord-Open-Interest lag laut CME bei 5.478 Kontrakten (09.07.2024) [Q73].

### 3.7 Handelszeiten und Gap-Risiko (Haltedauer Stunden bis Tage)

**Handelszeiten je Gruppe (MEZ/MESZ abgeleitet; in den Differenzwochen jeweils 1 h früher):**

| Gruppe | Börsenzeit | MEZ/MESZ | Quellen |
|---|---|---|---|
| CME Energie und Metalle (23/5) | So–Fr 17:00–16:00 CT | Mo 00:00 bis Fr 23:00, täglich Pause 23:00–00:00 | [Q12][Q64][Q63] |
| CBOT-Getreide | 19:00–07:45 und 08:30–13:20 CT | 02:00–14:45 und 15:30–20:20 | [Q43][Q74] |
| CME Vieh | Mo–Fr 08:30–13:05 CT | 15:30–20:05 | [Q47] |
| ICE Softs: Sugar | 03:30–13:00 ET | 09:30–19:00 | [Q48] |
| ICE Softs: Coffee | 04:15–13:30 ET | 10:15–19:30 | [Q49] |
| ICE Softs: Cocoa | 04:45–13:30 ET | 10:45–19:30 | [Q50] |
| ICE Softs: Cotton | 21:00–14:20 ET | 03:00–20:20 | [Q51] |
| ICE Brent und Gasoil | 01:00–23:00 London | 02:00–24:00 | [Q52][Q53] |
| TTF | 00:50–22:00 London | 01:50–23:00 | [Q54] |
| Euronext | 10:45–20:15 CET, die letzten drei Tage vor Verfall bis 18:30 | 10:45–20:15 | [Q55][Q56] |
| Krypto, 1OZ, SIC | 24/7 | 24/7 | [Q4][Q9][Q11] |

**Folgerung (abgeleitet):**
- Vieh, Softs und Euronext haben lange Schließzeiten. Das Übernacht- und Wochenend-Gap-Risiko ist dort deutlich höher als bei 23/5- und 24/7-Märkten.
- Stops wirken in der Schließzeit nicht. Das muss in die Risikoberechnung eingehen.

## 4. Hinweise für das Paket

- Das Schema `instrument_spec` verlangt `initial_margin`, `roll_rule` = `MIN(FND,LTD)-nBD` und `valid_until`.
- **Margin:** Das Feld bleibt aus dieser Recherche leer. Es ist in E0b über die Broker-API bzw. die Clearing-Advisories zu füllen [Q67].
- **Rollregel:**
  - Bei den TEILWEISE-Getreidekontrakten fehlt der FND.
  - Ersatzweise ist eine konservative Regel nötig, z. B. Rollen vor Monatsende des Vormonats. Das ist eine Annahme, keine belegte Regel.
- **Gültigkeit:**
  - Die Grain-Limits gelten bis zum Reset im November 2026 [Q35]–[Q39].
  - Handelszeiten aus Dokumenten von 2018 bis 2023 sollten vor dem Livegang gegen die Live-Contract-Specs geprüft werden.

## 5. Offene Punkte

1. **Margins (alle 44 `null`):**
   - CME-Advisory 26-315 (wirksam 18.09.2026) existiert, die Tabelle war aber nicht abrufbar [Q67].
   - ICE- und Euronext-Margins wurden nicht geprüft.
2. **DCB-Prozentsätze** für CME Energie, Metalle und Krypto: die xlsx-Tabelle war nicht lesbar [Q68], Kapitel 5 wurde abgeschnitten [Q72].
3. **Preislimits bzw. Interval Price Limits** bei ICE Futures Europe/Endex (B, G, TFM), die IPL der ICE-Softs und die Euronext-Mechanismen (EBM, ECO).
4. **CBOT FND/First Position Day** für ZC, ZS, ZW, KE, ZM und ZL (Kapitel 7 abgeschnitten [Q71]).
5. **HE:** Die Regel zum letzten Handelstag fehlt, weil Rulebook-Kapitel 152 keine enthält [Q46]. Der Monatszyklus ist nur aus der Factcard von 2017 belegt (PM264/0917, siehe [Q46]).
6. **QG:** Handelszeiten und konkreter Monatszyklus sind nicht belegt [Q18].
7. **BZ:** Welcher Tick auf Globex für Outright-Orders gilt (0,001 oder 0,01 USD) [Q23][Q24].
8. **MHG:** Listungstiefe 23 oder 24 Monate [Q30][Q31].
9. **HO:** Das Bezugsdatum der Abnahmeanzeige wurde im abgerufenen Zitat abgeschnitten (siehe JSON).
10. **Cotton:** Die aktuelle Limitstufe innerhalb von 3–7 ¢ ist nicht geprüft [Q51].
11. **Listungstiefe** bei CL, NG, RB und HO („von der Börse bestimmt“) [Q16][Q20][Q21][Q22].
12. **Wochenend-Trade-Date-Regel** für 1OZ und SIC ist nicht separat belegt (nur für Krypto [Q4]).
13. **Cocoa-FND** („sixth business day“): der ungewöhnliche Wortlaut sollte bestätigt werden [Q50].

## 6. Quellenverzeichnis (alle abgerufen am 2026-09-24)

**CME: Preislimits, 24/7, Notices**
- [Q1] CME Price Limits (As of Trade Date 09/24/2026): https://www.cmegroup.com/trading/price-limits.html
- [Q2] CME FAQ Dynamic Circuit Breakers: https://www.cmegroup.com/globex/trade-on-cme-globex/frequently-asked-questions-dynamic-circuit-breakers.html
- [Q3] CME Education „Understanding Price Limits and Circuit Breakers“ (23.03.2020): https://www.cmegroup.com/education/articles-and-reports/understanding-price-limits-and-circuit-breakers
- [Q4] CME FAQ Cryptocurrency Futures (Stand 22.09.2026): https://www.cmegroup.com/articles/faqs/frequently-asked-questions-cryptocurrency-futures.html
- [Q5] CME 24/7 Crypto Trading: https://www.cmegroup.com/markets/cryptocurrencies/24-7-crypto-trading.html
- [Q6] CME Pressemitteilung 01.06.2026 (24/7 Krypto seit 29.05.2026): https://www.cmegroup.com/media-room/press-releases/2026/6/01/cme_group_announceslaunchof247cryptocurrencyfuturesandoptionstra.html
- [Q7] CME Pressemitteilung 11.06.2026 (10-Barrel WTI, 1OZ 24/7): https://www.cmegroup.com/media-room/press-releases/2026/6/11/cme_group_to_expand247tradingforwticrudeoilandgold.html
- [Q8] CME Pressemitteilung 11.08.2026 (SIC 24/7): https://www.cmegroup.com/media-room/press-releases/2026/8/11/cme_group_to_expand247tradingto100-ouncesilverfuturesaftergoldss.html
- [Q9] CME FAQ 1-Ounce Gold: https://www.cmegroup.com/articles/faqs/faq-1-oz-gold-futures.html
- [Q10] CME Clearing Notice 26-220 (1OZ 24/7 ab 24.07.2026): https://www.cmegroup.com/notices/clearing/2026/06/26-220.html
- [Q11] CME FAQ 100-Ounce Silver: https://www.cmegroup.com/articles/faqs/frequently-asked-questions-100-ounce-silver-futures.html
- [Q12] CME 10-Barrel WTI: https://www.cmegroup.com/markets/energy/crude-oil/10-barrel-wti-crude-oil-futures.html
- [Q13] CME Clearing Advisory 20-152 (08.04.2020, negativer Basiswert): https://www.cmegroup.com/notices/clearing/2020/04/Chadv20-152.html

**CME-Rulebook, Metalle**
- [Q14] COMEX Rulebook Kapitel 7 (Rule 706.C(1)): https://www.cmegroup.com/rulebook/COMEX/1/7.pdf. Die Metall-Kapitel GC, SI, HG und ALI stehen in der JSON (COMEX/1a/113, 112, 111, 107).
- [Q15] NYMEX Rulebook Kapitel 7 (Rule 706.C): https://www.cmegroup.com/rulebook/NYMEX/1/7.pdf
- [Q25] COMEX Kapitel 120 (MGC): https://www.cmegroup.com/rulebook/COMEX/1a/120.pdf
- [Q26] COMEX Kapitel 121 (SIL): https://www.cmegroup.com/rulebook/COMEX/1a/121.pdf
- [Q27] COMEX Kapitel 130 (SIC): https://www.cmegroup.com/rulebook/COMEX/1a/130.pdf
- [Q28] COMEX Kapitel 131 (1OZ): https://www.cmegroup.com/rulebook/COMEX/1a/131.pdf
- [Q29] COMEX Kapitel 914 (MHG): https://www.cmegroup.com/rulebook/COMEX/9/914.pdf
- [Q34] NYMEX Kapitel 106 (PA): https://www.cmegroup.com/rulebook/NYMEX/1a/106.pdf. PL steht in Kapitel 105: https://www.cmegroup.com/rulebook/NYMEX/1a/105.pdf

**CME-Rulebook, Energie**
- [Q16] NYMEX Kapitel 200 (CL): https://www.cmegroup.com/rulebook/NYMEX/2/200.pdf
- [Q17] NYMEX Kapitel 309 (MCL): https://www.cmegroup.com/rulebook/NYMEX/3/309.pdf
- [Q18] NYMEX Kapitel 402 (QG): https://www.cmegroup.com/rulebook/NYMEX/4/402.pdf
- [Q19] NYMEX Kapitel 440 (MNG): https://www.cmegroup.com/rulebook/NYMEX/4/440.pdf
- [Q20] NYMEX Kapitel 220 (NG): https://www.cmegroup.com/rulebook/NYMEX/2/220.pdf
- [Q21] NYMEX Kapitel 191 (RB): https://www.cmegroup.com/rulebook/NYMEX/1a/191.pdf
- [Q22] NYMEX Kapitel 150 (HO): https://www.cmegroup.com/rulebook/NYMEX/1a/150.pdf
- [Q23] NYMEX Kapitel 698 (BZ): https://www.cmegroup.com/rulebook/NYMEX/6/698.pdf
- [Q24] CME Education Brent (08.01.2021): https://www.cmegroup.com/education/courses/introduction-to-energy/introduction-to-crude-oil/brent-crude-product-overview

**CME: Micro-Metalle und Advisory**
- [Q30] CME Micro Copper Factcard PM22_ME009/0422: https://www.cmegroup.com/education/files/micro-copper-futures-factcard.pdf
- [Q31] CME Micro Copper FAQ (02.05.2022): https://www.cmegroup.com/articles/faqs/micro-copper-futures-faq.html
- [Q32] CME Micro Metals: https://www.cmegroup.com/markets/microsuite/metals.html
- [Q33] CME Clearing Advisory 20-334 (SIL-Tick ab 21.09.2020): https://www.cmegroup.com/notices/clearing/2020/08/Chadv20-334.html

**CME-Rulebook, Agrar**
- [Q35] CBOT Kapitel 10 (ZC): https://www.cmegroup.com/rulebook/CBOT/II/10/10.pdf
- [Q36] CBOT Kapitel 11 (ZS): https://www.cmegroup.com/rulebook/CBOT/II/11/11.pdf
- [Q37] CBOT Kapitel 12 (ZL): https://www.cmegroup.com/rulebook/CBOT/II/12/12.pdf
- [Q38] CBOT Kapitel 13 (ZM): https://www.cmegroup.com/rulebook/CBOT/II/13/13.pdf
- [Q39] CBOT Kapitel 14 (ZW): https://www.cmegroup.com/rulebook/CBOT/II/14/14.pdf. KE steht in Kapitel 14H: https://www.cmegroup.com/rulebook/CBOT/II/14h.pdf
- [Q40] CBOT Kapitel 10O (MZC): https://www.cmegroup.com/rulebook/CBOT/I/10O.pdf
- [Q41] CBOT Kapitel 11O (MZS): https://www.cmegroup.com/rulebook/CBOT/II/11O.pdf
- [Q42] CBOT Kapitel 14O (MZW): https://www.cmegroup.com/rulebook/CBOT/II/14O.pdf
- [Q43] CME FAQ Micro Agricultural Futures (2025): https://www.cmegroup.com/articles/faqs/faq-micro-agriculture-futures.html
- [Q44] CME Kapitel 101 (LE): https://www.cmegroup.com/rulebook/CME/II/100/101/101.pdf
- [Q45] CME Kapitel 102 (GF): https://www.cmegroup.com/rulebook/CME/II/100/102/102.pdf
- [Q46] CME Kapitel 152 (HE): https://www.cmegroup.com/rulebook/CME/II/150/152/152.pdf. Dazu die Factcard PM264/0917: https://www.cmegroup.com/trading/agricultural/files/fact-card-lean-hog-futures-options.pdf und CME Education (12.06.2018): https://www.cmegroup.com/education/lessons/lean-hogs-product-overview
- [Q47] CME Cattle Factcard PM25_AGS007/0226: https://www.cmegroup.com/markets/agriculture/files/cattle-futures-and-options-fact-card.pdf

**ICE und Euronext**
- [Q48] ICE Sugar No. 11: https://www.ice.com/products/23/Sugar-No-11-Futures
- [Q49] ICE Coffee C: https://www.ice.com/products/15/Coffee-C-Futures
- [Q50] ICE Cocoa: https://www.ice.com/products/7/Cocoa-Futures
- [Q51] ICE Cotton No. 2: https://www.ice.com/products/254/Cotton-No-2-Futures
- [Q52] ICE Brent Crude: https://www.ice.com/products/219/Brent-Crude-Futures
- [Q53] ICE Low Sulphur Gasoil: https://www.ice.com/products/34361119/Low-Sulphur-Gasoil-Futures
- [Q54] ICE Endex Dutch TTF: https://www.ice.com/products/27996665/Dutch-TTF-Natural-Gas-Futures
- [Q55] Euronext Milling Wheat EBM (Stand 13.04.2026): https://live.euronext.com/en/product/commodities-futures/EBM-DPAR/contract-specification
- [Q56] Euronext Rapeseed ECO (Stand 13.04.2026): https://live.euronext.com/en/product/commodities-futures/ECO-DPAR/contract-specification

**CME: Krypto**
- [Q57] CME Kapitel 349 (ETH): https://www.cmegroup.com/rulebook/CME/III/300/349.pdf
- [Q58] CME Ether Factcard PM3051/0121 (veraltet): https://www.cmegroup.com/trading/files/ether-futures-fact-card-launch.pdf
- [Q59] CME Krypto-Broschüre PM25_CR004/0326: https://www.cmegroup.com/markets/cryptocurrencies/files/discover-cryptocurrency-futures-and-options-brochure.pdf
- [Q60] CME Kapitel 350 (BTC): https://www.cmegroup.com/rulebook/CME/IV/350/350.pdf
- [Q61] CME Kapitel 347 (MET): https://www.cmegroup.com/rulebook/CME/III/300/347.pdf. MBT steht in Kapitel 348: https://www.cmegroup.com/rulebook/CME/III/300/348.pdf
- Zusätzlich die Factcards von 2021, nur für den Listungsvergleich: https://www.cmegroup.com/markets/cryptocurrencies/files/micro-ether-futures-fact-card.pdf und https://www.cmegroup.com/trading/files/micro-bitcoin-futures-fact-card-retail-us.pdf

**CME: Guides, Factcards, Artikel und Education (datiert)**
- [Q62] CME Artikel „Refined for Retail“ (13.06.2024; Codes RB und HO): https://www.cmegroup.com/articles/2024/refined-for-retail.html
- [Q63] CME Metals Product Guide PM1985/0122: https://www.cmegroup.com/trading/metals/files/metals-prod-guide-2022.pdf
- [Q64] CME Gold Factcard PM22ME004E/1023: https://www.cmegroup.com/market-regulation/files/gold-futures-and-options-fact-card.pdf
- [Q65] CME WTI Factcard EN903/00/1112 (2012, veraltet): https://www.cmegroup.com/trading/files/WTI-Fact-Card.pdf
- [Q66] CME Silver Factcard MT901/00/1012 (2012, veraltet): https://www.cmegroup.com/trading/metals/files/fact-card-silver-futures-options.pdf
- [Q73] CME-Artikel Aluminum (27.02.2025): https://www.cmegroup.com/articles/2025/five-things-you-should-know-about-aluminum-futures.html. Dazu das Spezifikationsblatt von 2014 (nur Code und Tickwert): https://www.cmegroup.com/trading/metals/files/aluminum-futures-contract-specs.pdf
- [Q74] CME Grain Factcard PM254/0519: https://www.cmegroup.com/trading/agricultural/files/grain-and-oilseed-futures-options-fact-card.pdf
- Weitere datierte Education- und FAQ-Seiten, je Feld in der JSON:
  - CL, 08.01.2021: https://www.cmegroup.com/education/courses/introduction-to-energy/introduction-to-crude-oil/wti-overview
  - NG, 08.12.2020: https://www.cmegroup.com/education/courses/introduction-to-natural-gas/nat-gas-product-overview
  - RB, 16.12.2020: https://www.cmegroup.com/education/courses/introduction-to-energy/introduction-to-refined-products/rbob-product-overview.hideSubnav.educationIframe.html?hideHeader=y&hideFooter=y&hideRightRail=y&hideAddThisExt=y
  - HO, 18.12.2020: https://www.cmegroup.com/education/courses/introduction-to-energy/introduction-to-refined-products/heating-oil-product-overview
  - MCL, Factcard PM21_EN006/0621: https://www.cmegroup.com/trading/energy/files/micro-wti-crude-oil-futures-fact-card.pdf
  - MCL, FAQ 17.05.2021: https://www.cmegroup.com/education/articles-and-reports/micro-wti-crude-oil-futures-faq.html
  - MNG, FAQ 06.11.2023: https://www.cmegroup.com/articles/faqs/micro-henry-hub-natural-gas-futures-and-options-frequently-asked-questions.html
  - MNG, Factcard PM22_EN004/0923: https://www.cmegroup.com/markets/energy/files/micro-henry-hub-natural-gas-fact-card.pdf

**Nicht auswertbar (Abruf ohne Inhalt oder abgeschnitten)**
- [Q67] CME Performance-Bond-Advisory 26-315 (wirksam 18.09.2026; Tabelle nicht abrufbar): https://www.cmegroup.com/notices/clearing/2026/09/26-315.html
- [Q68] CME Special Price Fluctuation Limits (xlsx, nicht lesbar): https://www.cmegroup.com/rulebook/files/special-price-fluctuation-limits.xlsx
- [Q69] CME Contract Specs CL (per JavaScript geladen, ohne Inhalt): https://www.cmegroup.com/markets/energy/crude-oil/light-sweet-crude.contractSpecs.html
- [Q70] CME Trading Hours (per JavaScript geladen, ohne Inhalt): https://www.cmegroup.com/trading-hours.html
- [Q71] CBOT Rulebook Kapitel 7 (abgeschnitten): https://www.cmegroup.com/rulebook/CBOT/I/7.pdf
- [Q72] NYMEX Rulebook Kapitel 5 (abgeschnitten): https://www.cmegroup.com/rulebook/NYMEX/1/5.pdf
