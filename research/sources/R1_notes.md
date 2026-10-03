# R1 – Notizen: MT5-Broker mit Börsenfutures, MT5-Python-Semantik, ESMA/BaFin-CFD-Regeln

Abrufdatum aller Quellen: 2026-09-24. Belege mit Zitaten stehen in `R1_mt5_brokers.json`. Hier nur Bewertung, Lücken, Widersprüche und Empfehlung.

## 1. Kernergebnis

1. **Nur FXFlat (FXFlat Bank GmbH, Ratingen, BaFin) ist per Primärquelle zugleich als MT5-Anbieter börsengehandelter Futures und als deutscher Privatkunden-Broker belegt.** Belegt sind Eurex und CME (Kurse via CQG), Hedging im selben Kontrakt, All-inclusive ab 0,80 € bzw. 1,00 € je Kontrakt und Seite, Kursgebühren 20 €/33 € pro Monat und Intraday-Margin rund 10 % der Eurex-Margin. Die Seiten sind undatiert; die MetaQuotes-Pressemitteilung vom 21.05.2019 ist nur ein Indiz für den heutigen Stand.
2. **AvaFutures (AVA Trade EU Ltd, Irland, Central Bank of Ireland C53877, MiFID)** bietet MT5 für Futures an (Netting, CME/Eurex/Euronext, 1,75 $/€ bzw. 0,75 $/€ je Seite, CME Level 2 kostenlos). Die EU-AGB verweisen auf „Additional Terms for German Retail Clients“, das spricht dafür, dass deutsche Privatkunden bedient werden. Der Anhang war aber nicht lesbar (Teilbeleg).
3. **AMP Futures (AMP Global Clearing LLC, USA, CFTC/NFA)** ist technisch am besten dokumentiert: Netting-only, Symbolliste mit MT5-Symbolen, All-in-Kommission, Day- und Übernacht-Margins, SL/TP als MIT. Ob AMP deutsche Privatkunden annimmt, ist **nicht belegt** (Sperrliste nur als Bild). Die EU-Einheit AMP Global (Europe) (CySEC 360/18) hat FX/CFD Ende 2023 eingestellt; ihre Lizenz wurde 2024 zurückgegeben (Sekundärquelle). Die Risikoaufklärung von AMP sieht eine Haftung für Fehlbeträge vor – das ist regulatorisch heikel (siehe 6).
4. **Just2Trade (J2T Services Ltd, CySEC 281/15)** führt in „MT5 Global“ börsengehandelte Futures (CME, ICE, CBOE; Symbole FUTES, FUTNQ usw.). Ob deutsche Kunden angenommen werden, wurde nicht geprüft.
5. **Weitere US-Anbieter mit MT5-Futures:** StoneX Financial Inc. (FCM), TradePro Futures (Seite von 2021), ITG Futures (FIB). Für keinen ist belegt, dass er deutsche Privatkunden annimmt.
6. **Optimus Futures** nennt MT5 auf der Startseite nicht (heute kein MT5-Kandidat). **Admirals**: NICHT_GEPRUEFT (Abruf gescheitert).

## 2. Empfehlung

- **Primärkandidat: FXFlat.** Vor einer Festlegung schriftlich vom Broker bestätigen lassen:
  1. aktuelle Kontraktliste Eurex/CME in MT5 mit Symbolen, Kontraktwerten und Rollterminen;
  2. Übernacht-Margins je Kontrakt und die Regel, wann die Intraday-Margin endet;
  3. vertraglicher Ausschluss der Nachschusspflicht für Futures bei Privatkunden (BaFin-Allgemeinverfügung Futures);
  4. Erlaubnis für EAs und die MT5-Python-Schnittstelle bei Futures, Grenzen für Order-Frequenz;
  5. Futures im Demokonto;
  6. Kontomodus (laut Seite Hedging) und Ausführungsmodus der Symbole (Erwartung: Exchange Execution);
  7. Liquidationsregel (Stop-out-Level, Zeitpunkt, Vorgehen).
- **Zweitkandidat: AvaFutures (EU-Einheit).** Anhang „Additional Terms for German Retail Clients“ beschaffen und prüfen. Außerdem klären: Kontraktliste in MT5, Margins, Mindesteinlage, ob Python/EAs erlaubt sind (die AGB verbieten Gateway- und Datafeed-Anbindungen ohne Genehmigung).
- **AMP nur nach Rechtsprüfung.** Zu klären sind Annahme von Kunden mit Wohnsitz in Deutschland, Umgang mit der Nachschusspflicht (die BaFin-Verfügung gilt für Wertpapierfirmen, auch grenzüberschreitend; ob sie eine US-FCM erfasst, ist eine Rechtsfrage) und die Einlagensicherung. AMP eignet sich als technische Referenz für die MT5-Futures-Semantik.
- **Rückfall CFDs** (nur falls Futures scheitern): Es gelten die ESMA/BaFin-Hebelgrenzen (Hauptindizes/Gold 20:1, andere Indizes/Rohstoffe 10:1), Glattstellung bei 50 % und Negativsaldoschutz. Übernachtfinanzierung als Beispiel: Pepperstone GmbH (BaFin, MT5), Index-CFD (Kurs × Volumen × (2,5 % ± ARR)) / 360.

## 3. Lücken

**FXFlat**
- Vollständige Kontraktliste; Übernacht-Margins.
- Futures im Demo; ausdrückliche Erlaubnis für EA/Python bei Futures.
- Nachschuss-Ausschluss speziell für Futures.
- Mindesteinlage für Futures (belegt sind nur „ab 200 €“ Kontoeröffnung Forex/CFD).
- Pro- und Non-Pro-Unterscheidung bei Kursgebühren.
- Ursache: mehrere fxflat.com-Seiten wegen robots.txt-Fehler nicht abrufbar.

**AMP**
- Ob Kommissionen je Seite gelten, ist nicht ausdrücklich belegt.
- Annahme deutscher Kunden; Sperrliste nur als Bild.
- Erlaubnis der Python-Schnittstelle.
- Aktualität der Symbolliste (enthält noch „Eurodollar (GE)“).

**AvaFutures**
- Mindesteinlage, Margins, vollständige Kontraktliste in MT5.
- Futures im Demo.
- Inhalt der Zusatzbedingungen für deutsche Privatkunden.

**Just2Trade, StoneX, TradePro, ITG**
- Annahme deutscher Privatkunden, Kontomodus, Margins; zum Teil Kommission je Seite.

**MT5-API**
- Maximale Länge von `comment` und ob der Broker den Kommentar verändert: nicht geprüft.
- Offset der Zeitstempel je Broker: nur empirisch klärbar.
- Ob SL/TP bei einem konkreten Broker als native Börsenorder liegen: nur für AMP belegt (serverseitige MIT-Orders).

**Regulatorik**
- Gilt die BaFin-Allgemeinverfügung Futures vom 30.09.2022 unverändert fort? Kein Aufhebungshinweis auf der Seite; eine gesonderte Änderungsrecherche war nicht möglich.

## 4. Widersprüche

1. FXFlat-Firmierung: Impressum und mehrere Seitentitel „FXFlat Bank GmbH“, einzelne Seitentitel in Suchergebnissen „FXFlat Bank AG“.
2. FXFlat-Kosten: aktuelle Seite CME-Kurse 33 €/Monat; Sekundärquelle brokerdeal.de (2021, aktualisiert 2023) 30 €. Preise: „ab 0,80 €“ und „1,00 € je Seite“ (Primärquelle) gegenüber „ab 1,90 Euro für Käufe und Verkäufe“ (Sekundärquelle).
3. AMP-Eurex-Daten: MT5-FAQ „EUREX Non-Pro (Level 1) – Included NO Fee“, die Gebührentabelle nennt dagegen „EUREX non-pro 24.00 EUR“ (Spalten CQG/Rithmic/TT).
4. AMP-Day-Trading-Margin: laut Margin-Seite nicht in den „last 15 minutes“ jeder Sitzung, laut FAQ nicht in den „last 5 minutes“. Zusätzlich „flatten … 5 minutes before the daily close“. Eurex-Margins sind auf der Seite mit „$“ dargestellt.
5. AMP-Plattformseite: „supports both … netting … and hedging“ (allgemein), für Futures dagegen „Exchange-Traded Futures is Netting Mode Only“. Die spezifische Aussage ist maßgeblich.
6. Zeitstempel: Die Python-Doku sagt, Tick- und Barzeiten seien UTC „without the shift“. Die MT5-Hilfe und MQL5 sagen dagegen Zeitzone des Broker-Servers bzw. Serverzeit (TimeCurrent). Bis zum Test gilt die Arbeitshypothese „Serverzeit als Epoch ohne Umrechnung“.
7. MQL5-Doku: RES_E_INTERNAL_FAIL_INIT und RES_E_INTERNAL_FAIL_CONNECT haben beide den Code -10003.
8. Pepperstone: englische EU-Seite zeigt den Nenner „3600“, deutsche Seite „360“ (vermutlich Tippfehler).
9. AMP Global (Europe): Blogdatum 01.10.2024, der Hinweis nennt aber den 15.12.2023 als Frist. Das Datum ist wohl ein Änderungsdatum.
10. Just2Trade listet MOEX-Futures; ihre Aktualität ist fraglich.

## 5. Regulatorik – Folgen für das Konzept

- **BaFin-Allgemeinverfügung Futures (30.09.2022, wirksam 01.01.2023):** Futures an Kleinanleger mit Sitz in Deutschland nur, wenn die Nachschusspflicht vertraglich ausgeschlossen ist (Ausnahmen: reine Absicherung, Altpositionen). Folge für das System: Der Broker stellt glatt, bevor ein negativer Saldo entsteht. Die De-Risking-Leiter muss vor der Broker-Liquidation greifen. Die Liquidationsregel des Brokers (Level, Zeitpunkt, Reihenfolge) ist ein Pflichtbeleg.
- **CFD-Rückfall (BaFin-Allgemeinverfügung 23.07.2019; ESMA-Maßnahme 2018/796 nicht mehr verlängert, PM 31.07.2019):**
  - Hebel: 30:1 Hauptwährungspaare; 20:1 andere Währungspaare, Gold, Hauptindizes; 10:1 andere Indizes und Rohstoffe außer Gold; 5:1 Einzelaktien und Sonstige; 2:1 Kryptowerte.
  - Glattstellung je Konto bei 50 % der Initial-Margin.
  - Negativsaldoschutz je Konto.

## 6. MT5-Semantik – was das OMS berücksichtigen muss

- **Betrieb:** nur Windows (das PyPI-Wheel 5.0.6180 gibt es nur für win_amd64). Das Terminal muss laufen (Kopplung per IPC; `initialize()` startet es bei Bedarf). Algo-Trading muss erlaubt sein (Fehler -8 `RES_E_AUTO_TRADING_DISABLED`; `account_info().trade_expert`, `terminal_info().trade_allowed`/`tradeapi_disabled`).
- **Keine Ereignisse im Python-API:** Zustand per Polling ermitteln (`orders_get`, `positions_get`, `history_orders_get`/`history_deals_get` mit `position=`).
- **Keine Client-Order-ID:** Korrelation über `magic`/`comment` und Historie. Ein Retry nach Timeout (retcode 10012 oder IPC -10005) nur nach Abgleich, sonst droht eine Doppelorder. Ein `order_send`-Erfolg bedeutet bei DEAL noch keine Ausführung; `deal` bzw. `order` können leer sein.
- **Exchange Execution:** Ausführung zu aktuellen Börsenangeboten. `type_filling` FOK/IOC laut Symboleinstellung, RETURN immer; Pending Orders mit RETURN. `price`/`deviation` sind bei Market/Exchange nicht nötig.
- **SL/TP bei Börseninstrumenten:** Auslösung nach Börsenregeln (meist Last), Ausführung zu Bid/Ask. Bei AMP als serverseitige MIT-Market-Order mit Slippage (TP ist keine ruhende Limit-Order). Trailing Stops und EAs laufen clientseitig. Für kritische Exits eigene Stop-Orders (BUY/SELL_STOP bzw. STOP_LIMIT) prüfen und das Verhalten beim Broker testen.
- **Netting (AMP, AvaFutures) gegenüber Hedging (FXFlat laut Seite):** Im Netting-Konto gibt es kein CLOSE_BY und keine getrennten Teilpositionen je Strategie; die Positionsbuchhaltung je Strategie muss das OMS selbst führen. Im Hedging-Konto ist beim Schließen `position=Ticket` Pflicht.
- **Kosten und P&L:** Bei AMP fehlen Kommissionen in MT5 (nur im Tagesauszug), und MT5 bildet VWAP-Positionen, während CQG Einzelfills führt. Der Abgleich muss gegen den Clearing-Auszug laufen.
- **Handelszeiten:** nicht über Python verfügbar (nur MQL5 `SymbolInfoSessionTrade`); aus Börsen- oder Broker-Angaben pflegen.

## 7. Killer-Tests vor Live-Betrieb (je Broker, Demo und kleines Live-Konto)

1. `symbol_info()` für jeden Zielkontrakt: `trade_exemode`, `filling_mode`, `trade_mode`, `trade_contract_size`, `trade_tick_size`/`trade_tick_value`, `volume_min`/`volume_step`, `margin_initial`/`margin_maintenance`, `expiration_time`.
2. `account_info().margin_mode`, `fifo_close`, `margin_so_call`/`margin_so_so`, `trade_expert`.
3. Zeitstempel-Offset: `symbol_info_tick().time` gegen NTP-UTC, auch über eine Sommerzeitumstellung.
4. Market-Order: `retcode`, `deal`/`order` gefüllt oder leer, Latenz. Danach `history_deals_get(position=…)` und Abgleich von `external_id` mit dem Auszug.
5. Simulierter Timeout (Netz trennen): kein Doppel-Fill beim Wiederholen; Korrelation über magic/comment. Prüfen, ob der Broker `comment` ändert oder kürzt.
6. SL/TP: Auslösepreis (Last oder Bid/Ask), Slippage, Verhalten bei geschlossenem Terminal und beim Neustart des VPS.
7. Margin-Stress: Verhalten nahe am Stop-out, Zeitpunkt der Liquidation, Übergang von Intraday- zu Übernacht-Margin.
8. Rollover: Verfall bzw. Umstellung der Symbole (z. B. „MESU22“-Schema), `SYMBOL_TRADE_MODE_CLOSEONLY` vor Verfall.

## 8. Methodik und Grenzen

- **Suchbudget:** Das WebSearch-Budget der Sitzung (200 Aufrufe) war während der Recherche erschöpft. Danach gab es nur noch gezielte WebFetch-Abrufe bekannter Anbieter-URLs. Weitere Kandidaten (z. B. Tickmill, Darwinex, weitere EU-Broker mit MT5-Börsenanbindung) konnten daher nicht systematisch gesucht werden.
- **Gescheiterte Abrufe:** fxflat.com-Unterseiten (robots.txt), admirals.com (robots.txt), admiralmarkets.com (404), cysec.gov.cy (SSL), darwinex.com (Weiterleitungsschleife), PyPI-JSON-API (robots). Gemäß Vorgabe wurden keine Archive, Caches, Spiegel, curl oder Python für Abrufe genutzt.
- **Zitate:** stammen aus einem Abruf-Tool (Markdown-Umwandlung). Tabellenzeilen können in der Formatierung normalisiert sein; die Inhalte wurden wörtlich übernommen.
- **Alte Quellen:** Pressemitteilungen (FXFlat 2019, AMP 2017, CME-Zertifizierung 2013, Just2Trade 2019) sind nur Indizien für den heutigen Stand und im JSON entsprechend datiert.
