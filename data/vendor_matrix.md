# Auswahlmatrix Datenanbieter (§9.1)

> **Betreiberfassung.** Für die Forschung braucht das System Intraday-Historie mit verfallenen Kontrakten, für den Betrieb Live-Kurse, für die Kostenmessung Geld- und Briefkurse. Der günstigste belegte Weg für die CME-Gruppe ist ein einmaliger Kauf bei Kibot; Eurex-Historie kommt im Plan von Databento (ab 2018) mit einem Abgleich über CQG. Keine geprüfte Lizenz erlaubt ausdrücklich, Rohdaten an einen Sprachmodellanbieter zu geben; Hermes bekommt deshalb nur abgeleitete Kennzahlen. Bei Live-Daten ist offen, ob dein automatisierter Handel als Non-Display-Nutzung gilt, was die Kosten deutlich erhöhen würde. Für Go/No-Go heißt das: Daten sind kaufbar, aber Lizenz und Einstufung müssen vor dem Kauf geklärt sein. Nächster Schritt: Lizenzbedingungen schriftlich beschaffen (X-DATA-LIC) und die Einstufung mit Broker und Börsen klären (X-DATA-ND).

Stand aller Angaben: Recherche vom 24.09.2026 (`research/sources/R5_data_index_hermes.json`, `research/sources/R5_notes.md`). Status nach Quellenregister; „nicht belegt“ heißt, dass die Angabe in der Quelle nicht gefunden wurde, nicht dass sie fehlt.

## 1 Historische Futuresdaten

<!-- GEN:BEGIN tab.vendors_hist -->
| Anbieter | Abdeckung | Auflösung | verfallene Kontrakte | Preis (laut Anbieter) | Lizenz | Status | Quelle |
|---|---|---|---|---|---|---|---|
| Databento | CME Globex MDP 3.0 seit 2010; Eurex, ICE, EEX seit 2018; alle gelisteten Verfallsmonate | trades (tick), OHLCV-1s/1m/1h/1d, MBP-1, MBP-10, MBO (L3) | ja | usage_based: $/GB (unkomprimierte Binärgröße); konkreter GB-Preis im Seitentext nicht sichtbar; standard_usd_per_month: 199; plus_usd_license_fees_per_month: 1750; unlimited_usd_license_fees_per_month: 4500 | redistribution_third_parties_incl_llm: Laut Databento-Blog ist für historische Daten keine Börsenlizenz nötig, außer bei Weitergabe; AGB (Terms) nur per JavaScript abrufbar, nicht geprüft. | TEILWEISE | SRC-HIST-DATABENTO |
| CQG Data Factory (CQG Inc.) | über 20 Jahre Historie, über 10 Jahre Intraday | Tick (Time & Sales), 1-Minuten-Bars, Tagesdaten | nicht belegt | futures_tick_usd_per_commodity_per_calendar_month: 16.0; futures_1min_usd_per_commodity_per_calendar_month: 14.0; eigene_rechnung_beispiel: 10 Jahre Tick für 1 Markt = 120 Monate × 16 USD = 1.920 USD (ob 'commodity' alle Kontraktmonate umfasst, nicht belegt) | – | TEILWEISE | SRC-HIST-CQG-DATA-FACTORY |
| Kibot | CME, CBOT, NYMEX, COMEX, CFE; seit 2009; 9.600+ Kontrakte inkl. delisteter | 1 Minute (plus 5/15/30 Min.), Tick, 30min + bid/ask | ja | all_futures_continuous_and_individual_1min_usd_one_time: 820.0; all_futures_continuous_and_individual_tick_usd_one_time: 2200.0; premium_subscription_usd_per_month: 139.0 | internal_use: nur eigene interne Nutzung; redistribution_third_parties_incl_llm: Weiterverkauf/Weitergabe untersagt; Übermittlung von Rohdaten an externe LLM-Anbieter damit mindestens fraglich (Auslegung) | BELEGT | SRC-HIST-KIBOT |
| FirstRate Data | Bundle 'Futures - Most Active' (130 Futures), u. a. CME, NYMEX, ICE, CBOT, EUREX; Einzelkontrakte und Continuous | 1-Minute, 5-Minute, 30-Minute, 1-Hour, 1-Day | ja | updates_usd_per_month: 59.95 | internal_use: private Nutzung des Subscribers; mehrere Nutzer nur innerhalb einer Organisation; automated_trading_allowed: Einbindung in interne Modelle erlaubt; Live-Trading nicht ausdrücklich geregelt; redistribution_third_parties_incl_llm: Rohdaten-Weitergabe untersagt; FAQ erlaubt ausdrücklich KI-Training und Veröffentlichung der Outputs. Übermittlung von Rohdaten an externe LLM-Anbieter nicht ausdrücklich geregelt (Auslegung). | TEILWEISE | SRC-HIST-FIRSTRATE-DATA |
| Norgate Data | rund 100 Futures-Märkte von 11 Börsen; Einzelkontrakte plus Continuous (unadjusted/back-adjusted); Historie bis ca. 1980 | nur Tagesdaten (End-of-Day) | nicht belegt | futures_package_usd_6_months: 148.5; futures_package_usd_12_months: 270 | internal_use: persönlicher Zweck, zwei Computer; automated_trading_allowed: persönlicher Zweck 'investment or trading' erlaubt; redistribution_third_parties_incl_llm: Weitergabe nur mit ausdrücklicher Erlaubnis | BELEGT | SRC-HIST-NORGATE-DATA |
| Tick Data, LLC (tickdata.com) | 150+ globale Futures (u. a. CME, ICE, Eurex); Historie bis Dezember 1974 laut Anbieter | Tick-by-tick Trades, Level-I-Quotes, selbst gebaute Bars (TickWrite) | nicht belegt | note: nur 'Contact Sales' | – | TEILWEISE | SRC-HIST-TICK-DATA-LLC |
| CME Group (Börsenlizenz, Kontext Weitergabe) | – | – | nicht belegt | historical_distribution_licensee_group_usd_per_year_2026: 35220 | redistribution_third_parties_incl_llm: Die Weitergabe (Distribution) historischer CME-Daten ist lizenz- und gebührenpflichtig (jährliche Distributionslizenz). Ob die Übermittlung an einen LLM-Anbieter als 'Distribution' gilt, ist nicht belegt (rechtliche Prüfung). | TEILWEISE | SRC-HIST-CME-HISTORICAL-DISTRIBUTION-LICENSE |
<!-- GEN:END tab.vendors_hist -->

## 2 Echtzeit-Marktdaten und Non-Display-Einstufung

<!-- GEN:BEGIN tab.md_fees -->
| Börse | Dokument | gültig ab | Gebühren (Auszug, Originalwährung je Monat) | Status | Quelle |
|---|---|---|---|---|---|
| CME Group (CME, CBOT, NYMEX, COMEX) | CME Group Fee List – CME, CBOT, NYMEX and COMEX Information | 2026-06-01 | non_professional_depth_of_market_per_exchange: 12.1; non_professional_depth_of_market_bundle_all_exchanges: 36.5; non_professional_top_of_book_per_exchange: 1.55; non_professional_top_of_book_bundle_all_exchanges: 4.65; professional_real_time_display_device_per_exchange: 134.5 | BELEGT | SRC-MDF-CME-FEELIST-2026-06-01 |
| CME Group (CME, CBOT, NYMEX, COMEX) | CME Group Fee List (angekündigt) | 2027-01-01 | non_professional_depth_of_market_per_exchange: 12.5; non_professional_depth_of_market_bundle_all_exchanges: 37.75; non_professional_top_of_book_per_exchange: 1.6; non_professional_top_of_book_bundle_all_exchanges: 4.8; professional_real_time_display_device_per_exchange: 139.2 | BELEGT | SRC-MDF-CME-FEELIST-2027-01-01 |
| CME Group | Non-Display Use Guidelines/FAQ (Stand laut Dokument: Januar 2025) und Schedule 5 zum ILA (Version 5.04, Datei Januar 2026) | – | – | BELEGT | SRC-MDF-CME-POLICY-NON-DISPLAY-NON-PRO |
| CME Group | Derived Data License Fees | 2026-01-01 | beispiel_indices_series_I_category_1_per_instrument_jaehrlich: 34260 | TEILWEISE | SRC-MDF-CME-DERIVED-DATA-2026 |
| Eurex (Deutsche Börse Market Data + Services) | Price List to the Market Data Dissemination Agreement, Version 16_1 | 2026-08-01 | non_professional_eurex_core_level_2_per_access_id: 10.9; non_professional_eurex_core_level_1_per_access_id: 4.9; non_professional_eurex_retail_europe_per_access_id: 1.0; professional_eurex_core_access_id: 62.67; professional_eurex_core_physical_user_id: 68.94 | BELEGT | SRC-MDF-EUREX-DISPLAY-2026-08-01 |
| Eurex (Deutsche Börse Market Data + Services) | Non-Display Agreement – Price List, Version 11_1 | 2026-08-01 | tier_3_trading_as_principal_or_brokerage_entry_1_2_device_accesses: eurex_ultra: 786.0; eurex_order_by_order_futures: 1454.0; eurex_order_by_order_futures_plus_options: 1817.0; eurex_ultra_tier_3_medium_3_10: 1010.0; eurex_enterprise_license: 10243.0 | TEILWEISE | SRC-MDF-EUREX-NON-DISPLAY-2026-08-01 |
| ICE Futures Europe (IFEU) | ICE Futures Technology & Market Data Fees 2026 v1; ICE Futures Europe Market Data Policy Version 4 (January 2026) | 2026-01 (Dokumentstand; exaktes Inkrafttreten nicht zitiert) | terminal_subscriber_ifeu_commodities: 144; terminal_subscriber_ifeu_financials: 123; terminal_subscriber_ifeu_equity_minis: 5; datafeed_non_display_ifeu_commodities: 865; datafeed_non_display_ifeu_financials: 740 | BELEGT | SRC-MDF-ICE-FUTURES-EUROPE-2026 |
| ICE Futures U.S. (IFUS) | ICE Futures Technology & Market Data Fees 2026 v1; January 1st, 2026 Exchange and Market Data Access Fees | 2026-01-01 | terminal_subscriber_ifus: 132; terminal_subscriber_ifus_canadian_grains: 41; datafeed_non_display_ifus: 795; datafeed_non_display_ifus_canadian_grains: 245 | TEILWEISE | SRC-MDF-ICE-FUTURES-US-2026 |
<!-- GEN:END tab.md_fees -->

Beträge in der Originalwährung und nach der Periodik der Quelle; die Umrechnung und die Zuordnung zu Szenarien erfolgt nur in `financials/cost_model.py` (Marktdaten-Szenarien ANZEIGE, NON_DISPLAY_MANAGED, NON_DISPLAY_USER).

## 3 Bewertung

| Kriterium | Kibot | CQG Data Factory | Databento | FirstRate Data | Norgate | Tick Data LLC |
|---|---|---|---|---|---|---|
| Forschung (Intraday, verfallene Kontrakte) | ja, CME-Gruppe | ja, Lizenz ungeprüft | ja, Eurex und ICE erst ab 2018 | eingeschränkt (aktivste Kontrakte) | nein (nur Tagesdaten) | ja, Preis unbekannt |
| Kostenmessung (Geld/Brief) | teilweise | ja | ja | nein | nein | ja |
| automatisierter Handel | nicht nötig (Live-Daten vom Broker) | – | – | – | – | – |
| Speicherung | intern erlaubt | ungeprüft | ungeprüft | intern erlaubt | persönlich | ungeprüft |
| Weitergabe an LLM-Anbieter | untersagt (Weitergabe) | ungeprüft | ungeprüft | Rohdaten untersagt, abgeleitete Ergebnisse erlaubt | nur mit Erlaubnis | ungeprüft |
| Rolle im Plan | Primärquelle CME-Gruppe | Abgleich Eurex, Option Vollhistorie | Zweitquelle und Eurex-Historie | – | – | – |

**Entscheidung (DEC-DS-17, Entwurf):** Kibot für die CME-Gruppe (<!--v:costreg:COST-HIST-KIBOT|d0-->820<!--/v--> USD einmalig), Databento Standard während der Forschungsphase (<!--v:costreg:COST-HIST-UPDATE|d0-->199<!--/v--> USD im Monat über <!--v:costreg:COST-HIST-UPDATE-MONTHS|d0-->4<!--/v--> Monate) als Zweitquelle und für Eurex ab 2018, CQG-Minutendaten für <!--v:costreg:COST-HIST-EUREX-MARKETS|d0-->7<!--/v--> Eurex-Märkte über <!--v:costreg:COST-HIST-CQG-MONTHS|d0-->24<!--/v--> Monate als Abgleich. Live-Kurse kommen vom Broker über das MT5-Terminal. Einmalige Datenkosten zusammen <!--v:cost:fixed_costs/historical_data_once_eur|eur-->3.477 EUR<!--/v-->.

**Offene Punkte:** AGB von Databento, CQG Data Factory und Tick Data; ob die Übermittlung abgeleiteter Kennzahlen an einen LLM-Anbieter als Weitergabe gilt; Non-Display-Einstufung und Pro/Non-Pro-Status beim Broker (X-DATA-LIC, X-DATA-ND, X-AI-DPA).
