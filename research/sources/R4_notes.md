# R4 – Stressereignisse: Notizen, Lücken, Sekundärquellen

Abruf aller Quellen: 2026-09-24. Zugehörige Daten: `R4_stress_scenarios.json` (13 Ereignisse, 10 Margin-Beispiele, 10 Limit-Beispiele).

## 1. Methode

- **Werkzeuge:** WebSearch und WebFetch. Gescheiterte Abrufe wurden **nicht** über Archive, Caches, Spiegel oder curl ersetzt (Liste in Abschnitt 6).
- **Suchbudget erschöpft:** Das WebSearch-Kontingent der Sitzung (200 Anfragen) war während der Recherche aufgebraucht. Danach wurden nur noch bekannte Primär-URLs direkt abgerufen. Mehrere Lücken in Abschnitt 4 gehen darauf zurück; mit neuem Suchbudget lassen sie sich wahrscheinlich schließen.
- **Zitate:** WebFetch gibt Seiteninhalte über ein Extraktionsmodell zurück. Angefordert wurde jeweils der genaue Wortlaut. Die tragenden Zitate wurden mit einem zweiten Abruf wortgleich bestätigt: BIS QR 03/2018 und 12/2008, FCA Final Notice LME, Fed FSR 05/2023, FSB Holistic Review, Fed Bulletin 03/1999, NY Fed FX-Berichte Q3 1998 und Q1 2020, CFTC WTI-Bericht und SEC/CFTC Flash-Crash-Bericht. Kleine Abweichungen im Wortlaut (Satzzeichen, Gedankenstriche) sind trotzdem nicht auszuschließen. Die Zahlen selbst waren in allen Wiederholungen gleich. Alle Zitate haben höchstens 30 Wörter; das wurde per Skript geprüft.
- **Tabellendaten:** US-Treasury „Daily Treasury Par Yield Curve Rates“ (TextView mit Monatsparameter, ab 1990), Fed H.15 Wochenarchiv (Sept. 2008 und Mai 2010), FRED VXOCLS (1987) und die Cboe-VIX-CSV (1994). Das Feld `quote` enthält hier die wörtlichen Zellwerte mit Datum und Spaltenname in verdichtetem Format; `quote_type` kennzeichnet das. Die 1994er-Werte vom April wurden zweimal abgerufen und stimmten überein. Die Werte vom 19.09.2008 decken sich zwischen H.15 und der Treasury-Kurve.
- **Berechnung (Status `BERECHNET_PRIMAER`):**
  - 1d = größte absolute Änderung zwischen zwei aufeinanderfolgenden Tabellentagen im Suchfenster.
  - 2–5d = größte absolute Änderung über 2 bis 5 Handelstage.
  - `note` nennt die Endpunkte, das Suchfenster und die größte Bewegung in Gegenrichtung.
  - Rechenskript und transkribierte Daten liegen im Scratchpad; sie sind nicht Teil der Ablieferung.
- **Status:**
  - `BELEGT_PRIMAER`: Zahl steht wörtlich in einer Primärquelle.
  - `BERECHNET_PRIMAER`: Zahl ist aus wörtlich zitierten Primärwerten gerechnet.
  - `BELEGT_SEKUNDAER`: Zahl ist nur sekundär belegt.
  - `NICHT_GEPRUEFT`: nicht belegbar, `move = null`.
- **kind:**
  - `PRIMAER`: Zentralbank, BIS, IWF, FSB, ESRB, BCBS/CPMI/IOSCO, Börse oder CCP (CME, NYSE, Cboe via FRED/CSV, Eurex), Aufsicht (FCA, FINMA, SEC, CFTC) sowie EIA und US Treasury.
  - `SEKUNDAER`: Wikipedia, Presse (CNN, ABC, City AM), Macroption und der Branchenverband FIA.
  - Die FXCM-Pressemitteilung ist als PRIMAER geführt, weil der Broker selbst über seine eigenen Salden berichtet. Sie ist aber keine Behördenquelle.
- **Konventionen:**
  - `move` trägt ein Vorzeichen: positiv = Anstieg von Preis, Rendite oder Index. Die Richtung beim FX-Paar steht in `instrument`.
  - `horizon_days` zählt Handelstage und ist bei Niveauangaben `null`. Werte über 5 sind Mehrwochenangaben der Quelle und in `note` markiert.
  - Mindestangaben der Quelle („more than“, „over“, „almost“) sind mit dem genannten Wert eingetragen und in `note` vermerkt.

## 2. Abdeckung je Ereignis und Anlageklasse

P = primär belegt mit Horizont bis 5 Tage · P* = primär nur mit längerem Horizont · S = nur sekundär · S* = nur sekundär mit längerem Horizont · – = keine belegte Zahl

| Ereignis | EQ | GOV | STIR | FX | OIL | NG | AU | MET | AGR | CRY | VOL |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E1987_BLACK_MONDAY | P | P | P | P* | – | – | – | – | – | – | P |
| E1994_BOND_CRASH | P* | P | P | – | – | – | – | – | – | – | P |
| E1998_LTCM_RUSSIA | P | P | P | P | – | – | – | – | – | – | – |
| E2008_GFC_AUTUMN | P | P | P | P* | P*/S | – | S | P* | – | – | S |
| E2010_FLASH_CRASH | P | P | P | – | – | – | P | – | – | – | P |
| E2015_SNB_FLOOR | P | P¹ | P | P | P* | – | – | P* | – | – | – |
| E2018_VOLMAGEDDON | P | P | P | – | – | – | – | – | – | S* | P |
| E2020_COVID_MARCH | P | P | P | P* | P*/S | P* | – | – | – | S | S |
| E2020_WTI_NEGATIVE | – | – | – | – | P | – | – | – | – | – | – |
| E2022_LME_NICKEL | – | – | – | – | – | – | – | P | – | – | – |
| E2022_UK_GILTS_LDI | – | P | – | S | – | – | – | – | – | – | – |
| E2023_BANK_STRESS | – | P | P | – | – | – | – | – | – | – | – |
| E2025_TARIFF_SHOCK | P | P | P | P* | P | P* | – | – | – | – | S |

¹ Nur US-Treasuries als Umfeld. Für Schweizer Renditen ist nur die Richtung belegt (lange Eidgenossen fielen unter null), kein Wert in bp.

Krypto vor 2014 gilt vorgabegemäß nicht und steht als `NICHT_GEPRUEFT` mit Hinweis. Bei WTI 2020 und LME 2022 wurden die übrigen Anlageklassen bewusst nicht erhoben.

## 3. Nur sekundär belegt

| Ereignis | Wert | Quelle |
|---|---|---|
| 1998 | S&P 500 −6,8 % am 31.08.1998 | CNN. Primär belegt ist nur Dow −11,6 % vom 26. bis 31.08. (NY Fed). |
| 2008 | WTI +16,37 USD/bbl am 22.09.2008 (Verfall-Squeeze) | Wikipedia |
| 2008 | Gold +70 USD (+8,97 %) am 17.09.2008 | ABC News |
| 2008 | S&P 500 +11,58 % am 13.10.2008 | Wikipedia |
| 2008 | VIX +16,54 Punkte (22.10.), Schlusshoch 80,86, Intraday-Hoch 89,53 | Macroption |
| 2018 | VIX exakt +20,01 Punkte | Macroption. Primär bei der BIS: „jumped 20 points“. |
| 2018 | Bitcoin −50 % in 16 Tagen | Wikipedia |
| 2020 | WTI −24,6 % und Brent −24,1 % am 09.03.2020 | Wikipedia. Primär nur −40 % über zwei Wochen (NY Fed). |
| 2020 | VIX +24,86 Punkte am 16.03.2020 | Macroption. Primär nur das Niveau 83 (FSB). |
| 2020 | Bitcoin −25 % in 24 Stunden | Wikipedia |
| 2020 | Auslösung der marktweiten Circuit Breaker am 9., 12. und 16.03. | Wikipedia. Die Schwellen sind primär belegt (NYSE). |
| 2020 | CME E-mini-IM 6.600 → 12.000 USD; Eurex FESX 2.300–2.700 → über 5.100 EUR | FIA |
| 2022 UK | GBP/USD −3 % am 23.09.; Rekordtief 1,0327 am 26.09. | Wikipedia |
| 2023 | USDC unter 1 USD; Coinbase stoppt Konvertierung | Wikipedia |
| 2025 | S&P 500 −4,84 % (03.04.), −5,97 % (04.04.), +9,52 % (09.04.) | Wikipedia. Primär: −12 % vom 2. bis 8.4. (BoE FSR). |
| 2025 | UST 30J +54 bp in drei Tagen (vermutlich intraday) | Wikipedia |
| 2025 | VIX +15,29 Punkte (04.04.), Schluss 52,33, Intraday 60,13 | Macroption |
| 2025 | Aussetzung des Nikkei-Futures-Handels (Trading Curb) | Wikipedia |

## 4. Lücken (NICHT_GEPRUEFT oder nur langer Horizont)

- **1987:** Öl, Gas, Gold, Metalle und Agrar ohne Werte. FX nur als Wert über die ganze FOMC-Intermeeting-Periode (USD −4,5 %). Anleihen: kein Ein-Tages-Wert in bp; belegt sind der Kurs +5,2 % über 2 Tage und ca. −100 bp über ca. 9 Tage. Die Margin-Erhöhung der CME ist ohne Prozentwert belegt.
- **1994:** FX, Rohstoffe und Aktien nur als Quartalswerte. Handelsaussetzungen und Margin-Änderungen sind nicht belegt.
- **1998:** VIX fehlt (die Cboe-CSV war im Abruf nur bis Mai 1994 lesbar). Öl, Gold, Metalle und Agrar fehlen. Die Größe der Fed-Senkung vom 15.10. ist in den abgerufenen Quellen nicht beziffert.
- **2008:**
  - Kein Ein-Tages-Wert für FX (USD/JPY −12,6 % über ca. 18 Tage) und für Rohstoffe breit.
  - Erdgas und Agrar fehlen.
  - Ereignisspezifische Margin-Erhöhungen der CME fehlen; vorhanden ist nur die allgemeine Statistik, eine Erhöhung beträgt im Schnitt 18,9 %.
- **2010:** EUR-Bewegung belegt, aber nicht beziffert. Öl, Gas und Metalle fehlen.
- **2015:** Renditen der Eidgenossen und VIX fehlen. Die Margin-Erhöhung der CME für CHF-Futures ist nicht belegt; belegt ist nur die CME-Gebühr von 100 bp auf CHF-Sicherheiten ab 22.01.2015.
- **2018:** FX und Rohstoffe fehlen. Margin-Änderungen für VIX-Futures (CFE) sind nicht belegt.
- **März 2020:** Gold fehlt. Metalle und Agrar fehlen; z. B. Lebendrind limit-down ist nicht als Ereignis belegt, belegt sind nur die Regeländerungen der CME von April/Mai 2020. Die zweite Fed-Senkung am 03.03. (−50 bp) wurde nicht separat abgerufen.
- **WTI 20.04.2020:** Margin-Änderungen der NYMEX für WTI im März und April 2020 sind im CFTC-Bericht nicht enthalten.
- **LME 2022:** Erhöhungen der Initial Margin durch LME Clear sind nicht beziffert. Belegt sind die Variation-Margin-Calls von 5,1 bzw. 19,7 Mrd. USD.
- **UK-Gilts 2022:**
  - Kein Ein-Tages-Wert (etwa 27. oder 28.09.) aus einer abrufbaren Primärquelle. Die BoE-PDFs (FSR, Cunliffe-Brief) sind per robots.txt gesperrt, die IADB-Abfrage lieferte keine Daten.
  - Belegt sind „mehr als 100 bp in wenigen Tagen“ und +270 bp für 30J vom 1.8. bis 14.10.
  - Die Größenordnung der LDI-Collateral-Calls fehlt.
- **März 2023:** Aktienindex (KBW), FX, Gold, VIX und der Tiefstwert von USDC sind nicht beziffert.
- **April 2025:** Gold, Kupfer, Bitcoin und Agrar fehlen. Der Ein-Tages-Wert für Öl fehlt; primär belegt sind Brent −14 % in 3 Tagen. FX nur mit langem Horizont. Margin-Erhöhungen von CME oder Eurex im April 2025 sind nicht belegt.
- **Margin-Beispiele:**
  - Kein einzelnes Eurex-Rundschreiben mit Prozentwert gefunden. Für Eurex vorhanden sind die Collateral-Summe (+83 %) und der FESX-Wert (FIA, sekundär).
  - Die CME-Advisories 26-035 und 26-041 (Silber und Gold, Januar 2026) wurden ausgelassen: Die Spaltenzuordnung der PDF-Tabellen war nicht eindeutig.
  - Die CME-Advisories von 2020 liegen nur als Excel vor und waren nicht auswertbar.
- **Limit-Moves:** Kein primär belegter historischer Limit-Move bei Agrarprodukten, etwa Weizen limit-up im Februar oder März 2022 (LM08, `NICHT_GEPRUEFT`). Belegt sind die aktuellen CBOT-Tageslimits, die Erweiterungsregel, die Livestock-Regeländerungen 2020 sowie für Energie die Circuit Breaker und TAS-Limits bei WTI am 20.04.2020. Hinzu kommt das 15-%-Limit der LME für Nickel.

## 5. Hinweise für die Kalibrierung

- **Aufwärtsbewegungen (Short-Risiko):**
  - S&P +11,58 % (13.10.2008) und +9,52 % (09.04.2025)
  - WTI +47,64 USD/bbl (21.04.2020)
  - 3M-T-Bill +76 bp (18. → 19.09.2008) und +125 bp in 3 Tagen
  - Nickel +238 % in 2 Tagen
  - UST 10J +61 bp in 4 Tagen (5. → 9.10.1998)
  - Die Gegenrichtung steht jeweils in `note`.
- **1994:** Die größte Ein-Tages-Änderung (31.03. → 04.04.1994: 10J +39 bp) umfasst Karfreitag, den 01.04., ohne Tabellenwert. Ohne diese Lücke liegt die größte Ein-Tages-Änderung bei +24 bp (06.05.1994).
- **NY Fed 1994:** Die Angabe „2J +280 bp bis Mitte Mai“ passt nicht zur Treasury-Par-Kurve. Dort ergeben sich vom 01.02. bis 09.05.1994 ca. +206 bp. Der Startpunkt der Quelle ist unklar.
- **Volatilität 1987:** Der VXO (+113,8 Punkte) beruht auf dem S&P 100 und alter Methodik und ist nicht direkt mit dem VIX vergleichbar.
- **WTI 2020:** Wegen des Vorzeichenwechsels sind die Bewegungen in USD/bbl angegeben. Prozentwerte (ca. −312 % ggü. Eröffnung) taugen für die Kalibrierung nicht. Der Stressrechner muss negative Preise, den Wegfall unterer Limits und über 30 DCB-Halts abbilden.
- **LME 2022:** Alle Trades ab 00:00 UK-Zeit am 08.03. wurden storniert (Nominalwert 13,373 Mrd. USD), danach war der Handel 8 Tage ausgesetzt. Für den Stresstest heißt das: Ausführungen und Gewinne können nachträglich entfallen, Positionen können eingefroren sein, und bei Wiederaufnahme gilt ein Tageslimit von 15 %.
- **Margin-Pfade:** Die Belege stützen die im Konzept vorgesehenen Margin-Pfade von +50 % und +100 %:
  - Durchschnittliche CME-Erhöhung 18,9 % je Schritt (FEDS 2014-86)
  - März 2020: ETD-Initial-Margin +62 % (BCBS/CPMI/IOSCO)
  - E-mini +82 % und FESX ca. +89 bis +122 % (FIA, sekundär)
  - Einzelne CCPs über +100 % (FSB)
  - Variation-Margin-Calls +460 % (von 25 auf 140 Mrd. USD pro Tag)
  - +100 % ist damit für Einzelkontrakte belegt und kein Extremwert jenseits der Historie.

## 6. Gescheiterte oder unbrauchbare Abrufe (nicht ersetzt)

- IWF eLibrary (403)
- CNBC (403)
- BAILII (Zugriff verweigert)
- caselaw.nationalarchives.gov.uk (404)
- BBC und Guardian (Website gesperrt)
- BoE: FSR-PDF Dezember 2022, Cunliffe-Brief vom Oktober 2022 und FPC Record April 2025 (robots.txt); IADB-Abfrage ohne Daten
- Fed H.15 Wochenarchiv März 2020 (404)
- NY Fed FX-Berichte Q4 1998, Q3 2022 und Q2 2025 (404 unter der angenommenen URL)
- Circle-Blog zu USDC (kein Inhalt)
- USDA AMS Cattle Report (404)
- Wikipedia-Artikel „2022–2023 food crises“ (nur Cache)
- BIS QR Juni 2025 (404)
- CME-Advisories 2020 (nur Excel)
- FRED-CSV (Binärdaten); die FRED-Datenseiten für DGS10 und VIXCLS sind abgeschnitten, 1998 und später sind nicht sichtbar
