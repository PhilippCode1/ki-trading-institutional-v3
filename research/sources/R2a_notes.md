# R2a – Notizen zu den Kontraktdaten für Zinsen, Anleihen und Devisen

Abruf: 2026-09-24. Die Daten liegen in `R2a_rates_fx_specs.json`: 34 Instrumente, 384 Quellenbelege aus 60 verschiedenen URLs.

## 1. Vorgehen

- Alle Seiten wurden am 2026-09-24 mit WebSearch und WebFetch abgerufen.
- Verwendet wurden nur offizielle Quellen der Börsen:
  - **CME/CBOT:** Rulebook-Kapitel (PDF), Special Executive Reports (SER), Clearing Advisory, FX Product Guide 2026, CME-Artikel und Übersichtsseiten.
  - **Eurex:** Produktseiten, Factsheets von 04/2026 und 06/2026, Rundschreiben, Seite zu den Volatility Interruptions.
  - **ICE:** Produktseiten.
- **Keine** Sekundärquellen, Archive, Caches oder Spiegel. Kein curl und kein Python für Abrufe.
- **Problem bei CME:** Die Seiten `*.contractSpecs.html` laden die eigentliche Tabelle per JavaScript nach. Statisch lesbar waren nur die „Contract Highlights“: Kontraktgröße, Notierung, Codes, teilweise die Handelszeit. Bei ZT, UB, allen FX-Futures sowie 2YY/10Y fehlte selbst das. Wie im Auftrag vorgesehen, habe ich stattdessen die **Rulebook-Kapitel** und andere offizielle CME-Seiten genutzt.
- **Zitate:** Das Werkzeug WebFetch liefert Seiteninhalte über ein Extraktionsmodell. Die Zitate (höchstens 25 Wörter) sind dessen wörtliche Ausgabe. Leerzeichen und Satzzeichen können vom Original leicht abweichen.
  - Tabellenzeilen sind mit „|“ wiedergegeben und in `source_type` als Tabellenzeile markiert.
  - Kernzahlen (Größe, Tick, Code, Abrechnung) habe ich wo möglich doppelt geprüft: Rulebook gegen FX Product Guide 2026 bzw. Produktseite gegen Factsheet.
- **Ableitungen** sind im Feldwert als „abgeleitet“ markiert. Das betrifft Spread-Tickwerte, den frühesten Intention Day bei Treasuries, 25 EUR je Basispunkt bei €STR und Euribor sowie alle Umrechnungen nach MEZ/MESZ.

## 2. Statuslogik

- **`field_status`** bewertet jedes Feld einzeln:
  - VERIFIZIERT: aktueller offizieller Beleg mit Zitat.
  - TEILWEISE: nur ein Teil belegt, nur eine ältere offizielle Quelle oder Schwellenwerte fehlen.
  - NICHT_GEPRUEFT: kein Beleg, der Wert ist `null`.
- **`status_core`** fasst die Kernfelder zusammen: symbol, contract_unit, price_quotation, tick_size, tick_value, trading_hours, settlement, last_trading_day_rule, first_notice_or_delivery_rule, listed_months.
- **`status`** (strenge Wertung) umfasst die Kernfelder plus `daily_price_limits`.
- `margin` ist laut Auftrag optional („nur wenn auffindbar“). Das Feld fließt in keinen Status ein; der Wert ist überall `null` bzw. NICHT_GEPRUEFT.
- Bei Barausgleich steht in `first_notice_or_delivery_rule` „entfällt (Barausgleich)“. Das ist über die Quelle zur Abrechnung belegt und deshalb VERIFIZIERT.

## 3. Ergebnis

| Ebene | VERIFIZIERT | TEILWEISE | NICHT_GEPRUEFT |
|---|---|---|---|
| Instrumente, streng (`status`) | 0 | 34 | 0 |
| Instrumente, nur Kernfelder (`status_core`) | 15 | 19 | 0 |
| Einzelfelder (34 × 12 = 408) | 320 | 46 | 42 (davon 34 × margin) |

Kein Instrument ist in der strengen Wertung vollständig belegt. Der Grund ist bei allen 34 gleich: Für die Preislimits fehlen die Schwellenwerte (CME, Eurex), oder es gibt gar keine Angabe (ICE).

| Börse | Symbol | status | status_core | Nicht vollständig belegte Felder |
|---|---|---|---|---|
| CME | SR3 | TEILWEISE | VERIFIZIERT | daily_price_limits=TEILWEISE, margin=NICHT_GEPRUEFT |
| CME | SR1 | TEILWEISE | VERIFIZIERT | daily_price_limits=TEILWEISE, margin=NICHT_GEPRUEFT |
| ICE Futures Europe | I (Euribor) | TEILWEISE | VERIFIZIERT | daily_price_limits=NICHT_GEPRUEFT, margin=NICHT_GEPRUEFT |
| ICE Futures Europe | SO3 (SONIA) | TEILWEISE | VERIFIZIERT | daily_price_limits=NICHT_GEPRUEFT, margin=NICHT_GEPRUEFT |
| Eurex | FST3 (€STR) | TEILWEISE | VERIFIZIERT | daily_price_limits=TEILWEISE, margin=NICHT_GEPRUEFT |
| CBOT | ZT | TEILWEISE | TEILWEISE | daily_price_limits=TEILWEISE, listed_months=TEILWEISE, margin=NICHT_GEPRUEFT |
| CBOT | ZF | TEILWEISE | TEILWEISE | daily_price_limits=TEILWEISE, listed_months=TEILWEISE, margin=NICHT_GEPRUEFT |
| CBOT | ZN | TEILWEISE | TEILWEISE | daily_price_limits=TEILWEISE, listed_months=TEILWEISE, margin=NICHT_GEPRUEFT |
| CBOT | TN | TEILWEISE | TEILWEISE | daily_price_limits=TEILWEISE, listed_months=TEILWEISE, margin=NICHT_GEPRUEFT |
| CBOT | ZB | TEILWEISE | TEILWEISE | daily_price_limits=TEILWEISE, listed_months=TEILWEISE, margin=NICHT_GEPRUEFT |
| CBOT | UB | TEILWEISE | TEILWEISE | daily_price_limits=TEILWEISE, listed_months=TEILWEISE, margin=NICHT_GEPRUEFT |
| CBOT | 2YY (2-Year Yield) | TEILWEISE | VERIFIZIERT | daily_price_limits=TEILWEISE, margin=NICHT_GEPRUEFT |
| CBOT | 10Y (10-Year Yield) | TEILWEISE | VERIFIZIERT | daily_price_limits=TEILWEISE, margin=NICHT_GEPRUEFT |
| Eurex | FGBS | TEILWEISE | VERIFIZIERT | daily_price_limits=TEILWEISE, margin=NICHT_GEPRUEFT |
| Eurex | FGBM | TEILWEISE | VERIFIZIERT | daily_price_limits=TEILWEISE, margin=NICHT_GEPRUEFT |
| Eurex | FGBL | TEILWEISE | VERIFIZIERT | daily_price_limits=TEILWEISE, margin=NICHT_GEPRUEFT |
| Eurex | FGBX | TEILWEISE | VERIFIZIERT | daily_price_limits=TEILWEISE, margin=NICHT_GEPRUEFT |
| Eurex | FBTP | TEILWEISE | VERIFIZIERT | daily_price_limits=TEILWEISE, margin=NICHT_GEPRUEFT |
| Eurex | FOAT | TEILWEISE | VERIFIZIERT | daily_price_limits=TEILWEISE, margin=NICHT_GEPRUEFT |
| ICE Futures Europe | R (Long Gilt) | TEILWEISE | VERIFIZIERT | daily_price_limits=NICHT_GEPRUEFT, margin=NICHT_GEPRUEFT |
| CME | 6E | TEILWEISE | TEILWEISE | daily_price_limits=TEILWEISE, listed_months=TEILWEISE, margin=NICHT_GEPRUEFT |
| CME | M6E | TEILWEISE | TEILWEISE | daily_price_limits=TEILWEISE, listed_months=NICHT_GEPRUEFT, margin=NICHT_GEPRUEFT |
| CME | 6B | TEILWEISE | TEILWEISE | daily_price_limits=TEILWEISE, listed_months=TEILWEISE, margin=NICHT_GEPRUEFT |
| CME | M6B | TEILWEISE | TEILWEISE | daily_price_limits=TEILWEISE, listed_months=NICHT_GEPRUEFT, margin=NICHT_GEPRUEFT |
| CME | 6J | TEILWEISE | TEILWEISE | daily_price_limits=TEILWEISE, listed_months=TEILWEISE, margin=NICHT_GEPRUEFT |
| CME | MJY | TEILWEISE | VERIFIZIERT | daily_price_limits=TEILWEISE, margin=NICHT_GEPRUEFT |
| CME | 6S | TEILWEISE | TEILWEISE | daily_price_limits=TEILWEISE, listed_months=TEILWEISE, margin=NICHT_GEPRUEFT |
| CME | MSF | TEILWEISE | TEILWEISE | daily_price_limits=TEILWEISE, listed_months=NICHT_GEPRUEFT, margin=NICHT_GEPRUEFT |
| CME | 6C | TEILWEISE | TEILWEISE | daily_price_limits=TEILWEISE, listed_months=TEILWEISE, margin=NICHT_GEPRUEFT |
| CME | MCD | TEILWEISE | TEILWEISE | trading_hours=TEILWEISE, daily_price_limits=TEILWEISE, listed_months=NICHT_GEPRUEFT, margin=NICHT_GEPRUEFT |
| CME | 6A | TEILWEISE | TEILWEISE | daily_price_limits=TEILWEISE, listed_months=TEILWEISE, margin=NICHT_GEPRUEFT |
| CME | M6A | TEILWEISE | TEILWEISE | daily_price_limits=TEILWEISE, listed_months=NICHT_GEPRUEFT, margin=NICHT_GEPRUEFT |
| CME | 6N | TEILWEISE | TEILWEISE | daily_price_limits=TEILWEISE, listed_months=TEILWEISE, margin=NICHT_GEPRUEFT |
| CME | 6M | TEILWEISE | TEILWEISE | daily_price_limits=TEILWEISE, listed_months=TEILWEISE, margin=NICHT_GEPRUEFT |

### 3.1 Kernfelder vollständig belegt (15)

SR3, SR1, ICE Euribor (I), ICE SONIA (SO3), Eurex €STR (FST3), 2YY, 10Y, FGBS, FGBM, FGBL, FGBX, FBTP, FOAT, ICE Long Gilt (R) und MJY.

### 3.2 Kernfelder nur teilweise belegt (19)

- **Treasuries (ZT, ZF, ZN, TN, ZB, UB):** Der Quartalszyklus ist aktuell belegt (CME-Übersicht, Stand 08/2024). Die Zahl der gleichzeitig gelisteten Kontrakte stammt nur aus einer CME-Kursseite von 2018: „three consecutively quarterly contract months“.
- **FX-Standardkontrakte (6E, 6B, 6J, 6C, 6A, 6S, 6N, 6M):** Der Zyklus ist belegt, laut CME-Seite zur FX-Lieferung (Stand 01/2026):
  - monatlich: EUR, JPY, GBP, CAD, AUD, MXN;
  - nur quartalsweise: CHF, NZD.

  Wie viele Kontrakte gleichzeitig gelistet sind, ist nicht belegt.
- **Micro-FX (M6E, M6B, MSF, MCD, M6A):** Der Listungsplan ist nicht belegt (`null`). Bei MCD ist zusätzlich die Handelszeit nur aus der allgemeinen CME-FX-Angabe übernommen.

### 3.3 Nicht geprüft

- **margin (alle 34):**
  - CME: Die Margin-Seiten laden dynamisch.
  - ICE: Die Seite `…/margin-rates` zeigt keine Werte.
  - Eurex: Es gibt nur Margin-Rechner und Dateien („Risk parameters and initial margins“), keine Werte auf der Seite.
- **daily_price_limits bei ICE (I, SO3, R):** Die Produktseiten enthalten keine Angabe. Eine ICE-Seite zu Circuit Breakers gab 404 zurück. Das Suchbudget war erschöpft, siehe Abschnitt 5.
- **listed_months:** M6E, M6B, MSF, MCD, M6A.

## 4. Auffälligkeiten

1. **ZN hat einen neuen lieferbaren Korb.** Rulebook-Kapitel 19 heißt jetzt „U.S. Treasury Note Futures (6½ to 8-Year)“. Lieferbar sind Restlaufzeiten von mindestens 6 Jahren 6 Monaten und unter 8 Jahren.
   - Laut SER-9520 (21.02.2025) sind ab dem Kontrakt März 2026 bei ZN und TN auch Aufstockungen (Reopenings) lieferbar.
   - Die CME-Kursseite von 2018 nennt noch „6½ bis 10 Jahre“. Diese Angabe ist veraltet und wurde nicht übernommen.
2. **SOFR-Laufzeiten haben sich geändert.** Aktuell (CME-Artikel 06/2026) gilt:
   - SR3: die nächsten 39 Quartalsmonate plus 6 Serienmonate;
   - SR1: die nächsten 25 Kalendermonate.

   Die CME-Spezifikations-PDF von 04/2018 nennt noch „Nearest 20 March Quarterly months“ bzw. „Nearest 7 calendar months“. Sie ist veraltet und wurde nicht verwendet.
3. **SR1-Tick hängt vom Kalender ab.** Im Liefermonat gilt 0,0025 Punkte (10,4175 USD). Beginnt der Monat an einem Di–Fr, gilt der kleine Tick schon ab dem letzten Sonntag des Vormonats (Rule 46102.C).
4. **„Micro 2-Year/10-Year Yield“ heißen heute „Yield futures“ (2YY, 10Y).** Beide sind weiter gelistet (Rulebook CBOT Kap. 80 und 82).
   - Basiswert ist die Rendite, der Kontrakt wird bar abgerechnet.
   - Es sind nur 2 Monatskontrakte gelistet (Stand 03/2024).
   - Nach Masterprompt §6.5 taugen sie ohne Nachweis nicht als Proxy für ZT bzw. ZN.
5. **Widerspruch bei MJY.** Die CME-Seite „Micro FX Futures“ nennt als Abrechnung „Financial“. Physische Lieferung nennen dagegen:
   - Rulebook Kap. 294 („PHYSICAL DELIVERY“),
   - SER-9326 („Deliverable“),
   - der FX Product Guide 2026 („Physical“).

   Übernommen wurde das Rulebook.

   Zur Geschichte: MJY wurde 2022 dauerhaft delistet (SER-8890) und am 26.02.2024 neu gelistet (SER-9326). Die alten Micro-Kontrakte auf USD-Basis (USD/JPY, USD/CAD, USD/CHF) sind laut SER-9270 delistet, letzter Kontraktmonat März 2024. Sie sind nicht mit MJY, MCD und MSF zu verwechseln.
6. **MCD fehlt in der Tabelle der Micro-FX-Seite.** Im FX Product Guide 2026 und im Rulebook (Kap. 293) steht der Kontrakt aber.
7. **CAD hat ein früheres Handelsende.** Bei 6C und MCD endet der Handel 1 Geschäftstag vor dem 3. Mittwoch, bei allen übrigen FX-Futures 2 Geschäftstage vorher.
8. **Handelsende 9:16 CT nur teilweise belegt.** Diese Uhrzeit ist nur für GBP (CME-Seite zur FX-Lieferung: VWAP 9:15:30–9:16:00 CT) und für MJY (SER-9326) belegt. Für die anderen FX-Kontrakte ist die Uhrzeit mit „nicht belegt“ markiert.
9. **CME-Preislimits.** Alle Produktkapitel verweisen auf Rule 589 (Special Price Fluctuation Limits).
   - Laut SER-8769 gilt ab Juli 2021 eine dynamische Variante (60-Minuten-Rollfenster, 2 Minuten Handelspause). Sie betrifft STIR-Futures (einschließlich SR1 und SR3) sowie die großen FX-Futures: EUR, CAD, GBP, JPY, AUD, NZD, CHF.
   - MXN und die Micro-Kontrakte nennt SER-8769 nicht.
   - Die konkreten Schwellen ließen sich nicht abrufen: Die CME-Seite zu Preislimits lädt dynamisch, und das PDF von Kapitel 5 wurde beim Abruf abgeschnitten.
   - Die statischen Werte aus SER-7259 (2014) sind veraltet und bewusst nicht übernommen.
10. **Eurex hat keine sichtbaren Tageslimits.** Stattdessen gibt es statische und dynamische Volatility Interruptions für alle Futures; die Schwellen veröffentlicht Eurex nicht.
11. **Eurex-Handelszeiten verschieben sich saisonal.** Bei den deutschen Anleihefutures (und laut Produktseite auch bei FOAT) beginnt der fortlaufende Handel um 01:10 MEZ im Winter bzw. 02:10 MESZ im Sommer und endet um 22:00. FBTP wird nur von 08:00 bis 19:00 gehandelt.
    - Die Produktseiten zeigen allgemeine Texte für alle Anleihefutures (Kontraktwert „EUR 100,000 or CHF 100,000“, Liste mehrerer Emittenten).
    - Die produktspezifischen Werte (Restlaufzeit, Kupon) stammen aus dem Eurex-Factsheet vom Juni 2026.
    - Für FOAT lieferte das Factsheet bei zwei Abrufen unterschiedliche Handelszeiten. Maßgeblich ist hier die Produktseite.
12. **Eurex €STR (FST3) ist gelistet.** Seit 09.06.2025 gelten 9 Serienmonate plus Quartalsmonate bis maximal 25 Quartale. Der Tick für Strategien beträgt 0,00125 (Rundschreiben vom 30.04.2025).
13. **Besonderheiten bei ICE:**
    - Euribor, SONIA und Long Gilt handeln 01:00–21:00 London, also 02:00–22:00 MEZ/MESZ.
    - Bei SONIA liegt der letzte Handelstag im nächsten Quartalsmonat nach dem benannten Kontraktmonat. Das ist bei Rollregeln zu beachten.
    - Beim Long Gilt liegt der First Notice Day vor dem Liefermonat (zwei Geschäftstage vor dessen Beginn). Das ist für den Rollzeitpunkt wichtig.
    - Die richtige Produkt-ID für den Long Gilt ist 37650336; die ID 37650330 liefert keinen Inhalt.
    - ICE listet außerdem „ICNL Three Month EURIBOR Futures“. Dieser Kontrakt ist nicht Teil des Auftrags und nicht erfasst.
14. **Zeitzonen:**
    - CME in CT: MEZ/MESZ = CT + 7 h. In den Umstellungswochen sind es nur + 6 h, und zwar vom 2. Sonntag im März bis zum letzten Sonntag im März sowie vom letzten Sonntag im Oktober bis zum 1. Sonntag im November.
    - CME in ET: + 6 h, in den Umstellungswochen + 5 h.
    - London: ganzjährig + 1 h.
    - Eurex nennt „CET“, meint damit aber die Frankfurter Ortszeit. Die Zeiten entsprechen direkt MEZ/MESZ.
    - Die Zeiten in ET (ZN-Seite) und CT (ZF/TN/ZB-Seiten) beschreiben dasselbe Fenster.
15. **Stand der Nebenquellen:**
    - CME-Treasury-Übersicht: 08/2024
    - Artikel zu Yield futures: 03/2024
    - SER-9326: 01/2024
    - Ältere Quellen, in `source_type` markiert: CME-Kurs zu Treasuries (2018) und CME-Artikel zu Preislimits (2020).

## 5. Einschränkungen

- Das WebSearch-Budget dieser Sitzung (200 Aufrufe) war gegen Ende erschöpft. Danach waren keine weiteren Suchen möglich, etwa nach den Interval Price Limits der ICE, dem PDF zur MXN-Advisory 26-249 oder den Listungszahlen der FX-Futures.
- Die Nummern einzelner Rulebook-Regeln im Feldtext sind teilweise aus dem Nummernschema des Kapitels abgeleitet (z. B. 29501.G). Der zitierte Wortlaut stammt jeweils aus dem angegebenen Kapitel.

## 6. Offene Punkte für die Nacharbeit

- **Margins:** CME-Margin-Dateien (CORE bzw. Clearing), Eurex Risk Parameter Files, ICE Margin Rates. Die Margins beim Broker sind getrennt zu erheben.
- **Preislimits:** CME-Tabelle „Special Price Fluctuation Limits“ aus Kapitel 5 (Anhang oder Excel-Datei), Interval Price Limits der ICE. Die Parameter der Eurex-Volatility-Interruptions sind nicht öffentlich.
- **Listungsschema:**
  - FX-Futures und Micro-FX: CME-Kalenderseiten oder Globex Product Reference Sheet (XLS);
  - 6M: Advisory 26-249, gültig ab 31.08.2026;
  - Treasuries: Zahl der gelisteten Quartalsmonate mit einer aktuellen Quelle bestätigen.
- **Uhrzeit des Handelsendes:** fehlt bei SR3 und den Treasuries; bei FX ist 9:16 CT nur für 6B und MJY belegt.
