# R5 – Marktdatenkosten, Index-Futures ohne Rüstung, Hermes-Upstream

Abruf: **2026-09-24** · Maschinenlesbare Belege (URL, wörtliches Zitat ≤ 25 Wörter, Art der Quelle): `R5_data_index_hermes.json`
Statuswerte: `BELEGT` · `TEILWEISE` · `NICHT_GEPRUEFT` (nicht belegbare Werte = `null`).

---

## 0. Methode und Grenzen

- Recherche nur mit WebSearch/WebFetch; keine Archive, Caches, Spiegel oder curl.
- **Das Websuche-Budget der Sitzung (200 Suchen) war während Thema 2 erschöpft.** Danach nur noch direkte Abrufe offizieller, bereits verlinkter oder bekannter URLs. Einige Punkte bleiben deshalb `NICHT_GEPRUEFT` (ICE-MSCI-ESG-Futures, DAX-ESG-Futures, STOXX-Schwellenwerte).
- Das Abruf-Tool fasst Seiten mit einem kleinen Modell zusammen. Zitate wurden ausdrücklich wörtlich angefordert. Lange Dokumente werden aber gekürzt. **„Nicht gefunden“ ist deshalb nur ein schwacher Negativbefund.**
- **CME-Gebührenliste:** Der PDF-Text ordnet die Spalten „Annually“ und „Monthly“ nicht zu. Die Monatsbasis für Geräte- und Non-Display-Gebühren ist aus Schedule 5 zum ILA und aus der Non-Display-FAQ abgeleitet. Die Distributionslizenzen sind jährlich.
- **GitHub** lieferte teils veraltete Snapshots (Sternzahlen zwischen 213k und 249k). Die Releaseliste wurde deshalb über den aktuellen Snapshot (249k) der Seiten 1–4 und über 26 einzeln abgerufene Tag-Seiten abgeglichen.
- **STOXX-Methodik-PDFs** (www.stoxx.com) waren wegen eines TLS-Zertifikatsfehlers nicht abrufbar. Verfügbar waren nur die Index- und Factsheet-Seiten auf stoxx.com.

---

## 1a. Echtzeit-Marktdaten für automatisierten Handel

| Börse | Dokument / Datum | Non-Professional (Monat) | Professional (Monat) | Non-Display / automatisiert (Monat) | Status |
|---|---|---|---|---|---|
| CME Group (CME, CBOT, NYMEX, COMEX) | Fee List, **gültig ab 1.6.2026** (Beträge wie 1.1.2026) | Depth 12,10 USD je Börse / 36,50 Bundle; Top of Book 1,55 / 4,65 Bundle | Real-Time-Gerät 134,50 USD je Börse | A1 „Trading as Principal“: 609 (1 App) / 1.820 / 3.640 USD; **User Non-Display Kat. A (einzelne natürliche Person): 457 USD**; **Managed User Non-Display Kat. A: 208 USD**; Kat. C: 363 USD | BELEGT |
| CME Group | Fee List, **angekündigt ab 1.1.2027** | Depth 12,50 / 37,75; ToB 1,60 / 4,80 | 139,20 USD | A1: 630 / 1.833 / 3.767; User Non-Display 472; Managed 215; Kat. C 375 | BELEGT |
| CME Group | Derived Data License Fees, ab 1.1.2026 | – | – | **jährlich**; z. B. Indizes Series I Kat. 1: 34.260 USD je Instrument; gilt für abgeleitete Werke (Indizes, CFDs, ETP-Werte) | TEILWEISE |
| Eurex (Deutsche Börse MD+S) | MDDA-Preisliste v16.1, **gültig ab 1.8.2026** | Eurex Core L2 10,90 €; L1 4,90 €; **Eurex Retail Europe 1,00 €** (nur Level 1, ausgewählte Produkte) | Eurex Core 62,67 € (Access ID) / 68,94 € (Physical User ID); Ultra 68,37 / 75,21 € | Non-Display-Preisliste v11.1 (ab 1.8.2026), Tier 3 „Trading as Principal or Brokerage“, Entry (1–2 Device Accesses): **Eurex Ultra 786 €**, Order-by-Order Futures 1.454 €, Order-by-Order Futures + Options 1.817 €; keine Privatkunden-Ermäßigung gefunden | BELEGT / TEILWEISE |
| ICE Futures Europe | Fee Overview 2026 v1; Market Data Policy v4 (Jan. 2026) | **keine Non-Pro-Kategorie** („not relevant and not used“) | Terminal: Commodities 144, Financials 123, Equity Minis 5 USD | Datafeed/Non-display: 865 / 740 / 100 USD | BELEGT |
| ICE Futures U.S. | Fee Overview 2026 v1; Access Fees 1.1.2026 | nicht gefunden (`null`) | 132 USD je ID | Datafeed/Non-display 795 USD | TEILWEISE |

**Bedeutung für einen Privatkunden in Deutschland mit vollautomatischem Handel:**

1. **CME-Gebühren gelten je Börse.** Die Kopfzeile lautet „fees are assessed per exchange“. Nur die Bundle-Zeilen decken alle vier Börsen ab. Vollautomatischer Handel ohne Anzeige (z. B. auf einem VPS) ist Non-Display Kategorie A.
   - Eigene Rechnung für CME, CBOT, NYMEX und COMEX, ab 1.6.2026:
     - Managed User Non-Display: 4 × 208 = **832 USD/Monat**, falls der Datenanbieter einen von CME autorisierten Service anbietet.
     - User Non-Display (direkte Lizenz): 4 × 457 = **1.828 USD/Monat**.
     - Je nach Konstellation kommen Anzeige-Gebühren hinzu.
   - Ab 1.1.2027: 860 bzw. 1.888 USD/Monat.
   - Offen ist, ob der MT5-Broker oder Datenanbieter Managed User Non-Display anbietet.
2. **Halbautomatischer Handel** ist ein Werkzeug auf dem Anzeigegerät eines Einzelnutzers. Dafür fallen Gerätegebühren an. Non-Professionals lizenzieren über ihren Datenanbieter. Ob ein MT5-Expert-Advisor darunter fällt, muss mit Broker bzw. CME geklärt werden.
3. **Eurex:** Die Kategorie „Trading as Principal“ umfasst ausdrücklich algorithmische und automatisierte Ordergenerierung. Die Gebühr fällt je „Market Data Client“ an. Ob ein Privatkunde über seinen Broker selbst Vertragspartner werden muss, ist offen.
4. **ICE:** Es gibt keinen ermäßigten Privatkundentarif.

---

## 1b. Historische Intraday-Futuresdaten

| Anbieter | Abdeckung / Auflösung | Preis (belegt) | Lizenz: Nutzung | Weitergabe an Dritte / LLM | Status |
|---|---|---|---|---|---|
| **Databento** | CME seit 2010, Eurex/ICE/EEX seit 2018; Tick bis L3; alle Verfallsmonate | nutzungsbasiert $/GB (Satz nicht sichtbar); Standard 199 USD/Monat (16+ J. OHLCV, 1 J. L1, 1 Mon. L2/L3); Plus 1.750, Unlimited 4.500 USD/Monat Lizenzgebühren; Börsengebühren ohne Aufschlag durchgereicht | AGB nur per JavaScript, nicht geprüft | Blog: für historische Daten keine Börsenlizenz nötig, **außer bei Weitergabe** | TEILWEISE |
| **CQG Data Factory** | 20+ J. Historie, 10+ J. Intraday; Trades und Bid/Ask | Futures Tick **16 USD**, 1-Minute **14 USD** je Commodity und Kalendermonat (10 J. Tick ≈ 1.920 USD je Markt, eigene Rechnung) | nicht gefunden | nicht gefunden | TEILWEISE (Lizenz NICHT_GEPRUEFT) |
| **Kibot** | CME/CBOT/NYMEX/COMEX/CFE seit 2009, 9.600+ Kontrakte inkl. delisteter | alle Futures einmalig: 1-Minute **820 USD**, Tick **2.200 USD**; Abo 139 USD/Monat | „own internal use only“ | Weiterverkauf und Weitergabe untersagt | BELEGT |
| **FirstRate Data** | 130 aktivste Futures (u. a. CME, ICE, Eurex), Einzelkontrakte und Continuous, 1-Minute bis 1-Tag | Bundle-Preis nicht im Seitentext; Updates 59,95 USD/Monat | private Nutzung; interne Modelle erlaubt | Rohdaten-Weitergabe untersagt; **KI-Training und Veröffentlichung der Outputs ausdrücklich erlaubt** | TEILWEISE |
| **Norgate Data** | **nur Tagesdaten** („no intra-day or tick data“), rund 100 Märkte | 148,50 USD (6 Mon.) / 270 USD (12 Mon.) | persönlicher Zweck inkl. Trading | nur mit ausdrücklicher Erlaubnis | BELEGT (für Intraday ungeeignet) |
| **Tick Data LLC** | 150+ Futures (CME, ICE, Eurex …), Tick und Level-1-Quotes | „Contact Sales“ | nicht gefunden | nicht gefunden | TEILWEISE |
| CME (Börsenlizenz) | – | Distribution „Historical“: 35.220 USD/Jahr (2026) | – | Weitergabe historischer CME-Daten ist lizenzpflichtig | TEILWEISE |

**Folgerung für Hermes und LLM-Anbieter:** Kein Anbieter erlaubt ausdrücklich, Rohdaten an externe LLM-Anbieter zu übermitteln. Kibot und Norgate schließen Weitergabe aus bzw. verlangen eine Erlaubnis. FirstRate erlaubt KI-Nutzung der Outputs, aber nicht die Weitergabe der Rohdaten.
Arbeitsregel bis zur rechtlichen Prüfung: Dem LLM nur **abgeleitete Kennzahlen und Metadaten** geben, keine Kurs-Rohdaten. Das ist eine Auslegung und noch keine Rechtsauskunft.

---

## 2. Aktienindex-Futures ohne Rüstungsunternehmen

| Future (Börse, Code) | Ausschlussregel laut Methodik | Nur kontroverse Waffen? | Rüstungswerte enthalten (Beleg) | Liquidität (Tag) | Bedingung erfüllt? |
|---|---|---|---|---|---|
| E-mini S&P 500 ESG (CME, ESG) – S&P 500 Scored & Screened | Military Contracting **≥ 10 %** (integrale Waffen, waffenbezogen); kontroverse Waffen inkl. Nuklear > 0 %; Kleinwaffen > 0 % | nein | nicht prüfbar (nur Top-10 des ETF EFIV sichtbar) | 451 Kontrakte, OI 6.392 (21.9.2026); ES: ≈ 1,56 Mio., OI 1,90 Mio. (23.9.) | **nicht belegbar** (< 10 % und nicht waffenbezogene Militäraufträge bleiben zulässig) |
| E-mini Technology Select Sector (CME, XAK) | keine (GICS-Zuordnung aller S&P-500-Werte) | – | **Palantir 2,51 %** (XLK, 23.9.2026) | 435, OI 12.946 | **nein** |
| E-mini Industrial Select Sector (CME, XAI) | keine; GICS Industrials enthält Aerospace & Defense | – | **RTX 4,78 %** (XLI, 23.9.2026) | 945, OI 12.881 | **nein** |
| Übrige 9 Select Sectors (CME: XAZ, XAY, XAP, XAE, XAF, XAV, XAB, XAR, XAU) | keine; A&D per GICS ausgeschlossen, kein Umsatz-Screen | – | Beispielfirmen per GICS nicht enthalten; Holdings nicht vollständig geprüft | 213–2.214 Kontrakte, OI 6.338–60.932 | **nur formal (GICS)**, nicht nachweislich |
| E-mini / Micro Nasdaq-100 (CME, NQ/MNQ) | keine | – | Palantir, Honeywell, Axon (Nasdaq-Liste, Stand 19.05.2025) | ≈ 545.600, OI 276.244 (23.9.) | **nein** |
| EURO STOXX 50 ESG (Eurex, FSSX) | Screens u. a. **Military Contracting**, Controversial Weapons, Small Arms; Schwelle nicht abrufbar | nein | nicht prüfbar (Top-10 ohne Rüstungswerte) | nur Gruppe „STOXX ESG“: 1.649, OI 84.915 (23.9.); Gruppe „Blue Chip“ (EURO STOXX 50) 610.237 | **nicht belegbar** |
| STOXX Europe 600 ESG-X (Eurex, FSEG) | Norms-based, kontroverse Waffen, Tabak, Kraftwerkskohle | **ja** | nicht geprüft | Gruppe wie oben | **nein** (Regel) |
| STOXX USA 500 ESG-X (Eurex, FSUS) | vermutlich ESG-X-Standard (nicht separat geprüft) | vermutlich ja | nicht geprüft | nicht geprüft | nicht belegbar |
| STOXX Europe 600 SRI (Eurex, FSRI) | kontroverse Waffen plus Filter **„Weapons“**, Kernkraft, Tabak u. a.; Schwelle nicht abrufbar | nein | nicht prüfbar (Top-10 ohne Rüstungswerte) | nur Gruppe | **nicht belegbar – bester Kandidat** |
| STOXX Europe Climate Impact ex GC Controversial Weapons & Tobacco (Eurex, FSCI) | laut Name: kontroverse Waffen, Tabak | ja | nicht geprüft | nicht geprüft | nein / nicht belegbar |
| STOXX Europe ESG Leaders Select 30 (Eurex, FSLS) | nicht geprüft | – | – | – | NICHT_GEPRUEFT |
| MSCI-ESG-(Screened)-Futures (Eurex) | MSCI Screened (Feb. 2025): kontroverse Waffen, Nuklearwaffen, zivile Schusswaffen; **Militärlieferanten ausdrücklich nicht erfasst** | ja (plus Nuklear) | nicht geprüft | Gruppe „MSCI ESG“: 450, OI 26.491 (23.9.) | **nein** (Regel) |
| DAX-ESG-Futures (Eurex); MSCI-ESG-Futures (ICE US) | nicht gefunden bzw. nicht geprüft (Suchbudget erschöpft) | – | – | – | NICHT_GEPRUEFT |

Zu den CME-Liquiditätszahlen: Sie stammen aus den TOTAL-Zeilen des CME-Tagesbulletins. Die Spaltenköpfe waren im PDF-Text nicht eindeutig. Volumen ist hier die Summe der beiden Volumenspalten, dann folgen Open Interest und Veränderung. Der 21.9.2026 liegt direkt nach dem Septemberverfall, deshalb sinkt das Open Interest stark.

**Fazit:** Kein geprüfter Index-Future erfüllt die Bedingung „Index enthält nachweislich keine Rüstungsunternehmen“ belegbar.

- Am nächsten kommen:
  - **STOXX Europe 600 SRI (FSRI)**: Er hat einen „Weapons“-Filter, aber Schwelle und Komponenten sind nicht belegt.
  - **CME-Select-Sector-Futures außerhalb von Industrials und Technology**: Rüstung ist dort nur per GICS-Klassifikation ausgeschlossen, nicht über Umsatzanteile.
- **Alle ESG- und Sektor-Futures sind im Vergleich zu ES, NQ und FESX sehr illiquide.** Sie haben wenige hundert bis einige tausend Kontrakte pro Tag.
- **Empfehlung:** Aktienindex-Futures aus dem Universum ausschließen. Wiederaufnahme nur nach zwei Prüfungen: (a) STOXX-SRI-Methodik mit Umsatzschwelle für „Weapons“, (b) vollständige Komponentenliste. Das als Betreiberentscheidung BQ-06 dokumentieren.

---

## 3. Hermes Agent (NousResearch/hermes-agent)

- **Lizenz:** MIT („Copyright (c) 2025 Nous Research“) – BELEGT.
- **Neueste Version am 2026-09-24:** **v0.21.5** (Tag `v2026.9.24`), veröffentlicht 24.09.2026, 10:09, Badge „Latest“. Kuratierte Release-Notes folgen laut Text erst mit v0.22.0. Am selben Tag sind weitere Releases möglich.
- **Releases der letzten 12 Monate:** 36 Releases, alle zwischen **12.03.2026 (v0.2.0) und 24.09.2026**. Vor März 2026 steht keine GitHub-Release auf der Seite; v0.1.0 ist nur als Vorgänger erwähnt.

| Monat | Releases (Version – Datum) |
|---|---|
| 2026-03 | v0.2.0 – 12.3. · v0.3.0 – 17.3. · v0.4.0 – 23.3. · v0.5.0 – 28.3. · v0.6.0 – 30.3. |
| 2026-04 | v0.7.0 – 3.4. · v0.8.0 – 8.4. · v0.9.0 – 13.4. · v0.10.0 – 16.4. · v0.11.0 – 23.4. · v0.12.0 – 30.4. |
| 2026-05 | v0.13.0 – 7.5. · v0.14.0 – 16.5. · v0.15.0 – 28.5. · v0.15.1 – 29.5. · v0.15.2 – 29.5. |
| 2026-06 | v0.16.0 – 6.6. (Tag 6.5.) · v0.17.0 – 19.6. |
| 2026-07 | v0.18.0 – 1.7. · v0.18.1 – 8.7. · v0.18.2 – 8.7. · v0.19.0 – 20.7. · v0.19.1 – 30.7. |
| 2026-08 | v0.20.0 – 3.8. · v0.20.1 – 13.8. · v0.20.2 – 16.8. · v0.20.3 – 17.8. · v0.20.4 – 18.8. · v0.20.5 – 21.8. (Tag 19.8.) · v0.20.6 – 27.8. · v0.21.0 – 31.8. |
| 2026-09 | v0.21.1 – 7.9. · v0.21.2 – 11.9. · v0.21.3 – 14.9. · v0.21.4 – 21.9. · v0.21.5 – 24.9. |

- **Releasefrequenz** (eigene Berechnung):
  - Allgemein: im Mittel alle **5,6 Tage** ein Release (Median 5, Maximum 13 Tage). In den letzten 90 Tagen waren es 18 Releases, in den letzten 30 Tagen 7.
  - Minor-Releases: 20 Stück, im Mittel alle 9 Tage. Zuletzt wurden die Abstände länger (19, 14, 28 Tage). Dazwischen liegen mehrere „Roll-up“-Patches.
- **Änderungsvolumen:** Laut Release-Notes haben Minor-Releases etwa 800 bis 5.800 Commits.
  - v0.21.0: ≈ 5.800 Commits und 2.475 PRs seit v0.20.0.
  - Patch-Releases reichen von 28 Commits (v0.15.1) bis **5.071 Non-Merge-Commits und 1.812 PRs (v0.21.4)**.
  - **Die Patch-Nummer sagt nichts über den Umfang aus.**
  - Die Gesamtzahl der Commits im Repository ist nicht belastbar, weil die Repository-Seite nur als veralteter Snapshot kam.
- **Breaking Changes:** In den geprüften Notes gab es keinen Abschnitt „Breaking Changes“ (schwacher Negativbefund). Es gibt aber Verhaltensänderungen und Deprecations:
  - v0.11.0: `.env`-CWD-Variablen deprecated
  - v0.19.0: `max_async_children` deprecated, Session-Auto-Reset standardmäßig aus, kimi-k2.x entfernt
  - v0.20.3: MCP-2.x-SDK-Migration
  - v0.21.0: Kontext-Default geändert
- **Folgerung für EV-10:** Updates auf eine gepinnte Version sollten nur nach der Evaluationssuite erfolgen, auch bei Patch-Releases. Die sehr hohe Änderungsrate treibt die Pflegekosten.

---

## 4. Offene Punkte

1. **CME:** Beim MT5-Broker bzw. Datenanbieter klären:
   - Gibt es Managed User Non-Display, und fällt es je Börse an?
   - Gilt ein Expert Advisor auf dem Terminal als „Semi-Automated“ oder als Non-Display?
   - Ist der Kunde als Non-Professional eingestuft?
2. **Eurex:** Klären, ob ein Privatkunde für automatisierten Handel über den Broker eine eigene Non-Display-Vereinbarung braucht.
3. **ICE Futures U.S.:** Market-Data-Policy zu Non-Professionals nachrecherchieren.
4. **Datenlizenzen:** AGB von Databento, CQG Data Factory und Tick Data beschaffen. Rechtlich prüfen, ob die Übermittlung an LLM-Anbieter als „Weitergabe“ oder „Distribution“ gilt.
5. **Index-Screening:**
   - STOXX Index Guide (Schwellen für „Weapons“ und „Military Contracting“) beschaffen.
   - Vollständige Komponentenlisten von FSRI, FSSX und S&P 500 Scored & Screened prüfen.
   - Eurex-Einzelproduktvolumen beschaffen.
   - ICE- und DAX-ESG-Futures prüfen.
6. Für eine Nachrecherche muss das Websuche-Budget erhöht werden (`CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`).
