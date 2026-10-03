# Anwendbarkeitsmatrix Recht und Regulierung (§15, Umfang nach BQ-03)

> **Betreiberfassung.** Diese Matrix prüft nichts, sie übergibt: Nach deiner Entscheidung BQ-03 beantwortet eine externe Person alle Rechtsfragen, und das System handelt nur. Jede Zeile nennt den Rechtsakt, die Frage, die zu klären ist, was das System technisch ohnehin tut und welche Stufe bis zur Antwort gesperrt bleibt. Die Quellen sind im Quellenregister mit Status „nicht geprüft“ geführt; keine Zeile ist eine Rechtsauskunft. Gerechnet ist nur dein Eigenkonto (B1); B2 bis B4 sind nicht Systemaufgabe. Für Go/No-Go heißt das: Ohne schriftliche Antwort der externen Person (X-LEGAL-01) kein Pilot. Nächster Schritt ist die Übergabe nach `legal/handover_external.md`.

Stand: 24.09.2026. Status aller Zeilen: NICHT_GEPRUEFT (BQ-03, DEC-CF-01). Verantwortlich für die Antwort ist jeweils die externe Person; verantwortlich für die Beauftragung der Betreiber.

| Thema | Rechtsakt (Quelle) | Frage an die externe Person (B1 Eigenkonto) | Wirkung im System unabhängig von der Antwort | Sperre bis zur Antwort |
|---|---|---|---|---|
| Erlaubnispflicht | KWG (SRC-REG-KWG), WpIG (SRC-REG-WPIG), KAGB (SRC-REG-KAGB); Merkblatt der BaFin zu Eigenhandel und Eigengeschäft (SRC-BAFIN-EIGENGESCHAEFT) | Ist der Handel für eigene Rechnung mit eigenem Kapital ohne Dienstleistung für andere erlaubnisfrei? | keine Gelder Dritter, keine Signale oder Software für Dritte (X-SCOPE-THIRD) | G8 |
| Algorithmischer Handel | MiFID II Art. 17 (SRC-REG-MIFID2), Delegierte Verordnung (EU) 2017/589 (SRC-REG-RTS6) | Gelten Pflichten für algorithmischen Handel für das Eigenkonto über einen Broker? | Pre-Trade-Kontrollen, Kill-Switch, Tests und Protokolle nach dem Vorbild der Verordnung (`execution/pretrade_controls.md`) | G8 |
| Marktverhalten | Marktmissbrauchsverordnung (EU) Nr. 596/2014 (SRC-REG-MAR); CME Rule 575 (SRC-REG-CME-575) | Welche Pflichten und Verbote gelten (etwa zu Stornierungsmustern)? | Orders nur mit Ausführungsabsicht, Nachrichtendrosselung, Duplikaterkennung (`governance/policies/trading_policy.md`) | G8 |
| Positionslimits und Meldeschwellen | Börsenregeln, Aufsichtsrecht | Welche Grenzen und Meldungen gelten für die gehandelten Kontrakte? | Positionsgrenze je Kontrakt (P-RISK-MAX-OI-SHARE) | G8 |
| Futures an Privatkunden | Allgemeinverfügung der BaFin zu Futures (SRC-REG-BAFIN-FUT, belegt) | Ist der Nachschussausschluss im Brokervertrag wirksam vereinbart? | Liquidationsregel des Brokers als Planungsgrundlage (X-BRK-NACHSCHUSS) | G1 |
| CFD-Rückfall | Allgemeinverfügung CFD und ESMA-Maßnahme (SRC-BAFIN-AV-CFD, SRC-REG-ESMA-CFD) | nur falls der CFD-Pfad freigegeben wird (X-OP-CFD) | Hebelgrenzen als harte Limits | CFD-Pfad |
| EMIR | Verordnung (EU) Nr. 648/2012 (SRC-REG-EMIR) | Betrifft EMIR eine natürliche Person? | keine | – |
| DORA | Verordnung (EU) 2022/2554 (SRC-REG-DORA) | nur für Finanzunternehmen (B3/B4 ausgeschlossen) | Sicherheitsmaßnahmen nach `security/security_architecture.md` | – |
| Geldwäsche | GwG (SRC-REG-GWG) | Pflichten liegen beim Broker; eigene Pflichten? | keine Zahlungsflüsse durch das System | G8 |
| Datenschutz | DSGVO (SRC-REG-DSGVO) | Pflichten bei Verarbeitung eigener Daten und Daten der Vertretung und Risikofunktion? | Datensparsamkeit, keine personenbezogenen Daten an Modellanbieter | vor Nutzung nicht öffentlicher Daten mit KI (X-AI-DPA) |
| KI-Verordnung | Verordnung (EU) 2024/1689 (SRC-REG-AIACT) | Fällt der Einsatz von Hermes und ML-Komponenten im Eigengebrauch unter die Verordnung? | KI außerhalb des Geldpfads; ML nur nach `ai/mrm_policy.md` | vor ML im Größenpfad |
| Verträge | Brokervertrag, Börsen- und Marktdatenbedingungen, Datenlizenzen | API-Nutzung erlaubt? Einstufung Profi/Nicht-Profi und Non-Display? Lizenzumfang? | Klärung über X-BRK-API, X-DATA-ND, X-DATA-LIC | G1, G2 |
| Softwarelizenzen | Lizenztexte Apache-2.0 (SRC-LIC-APACHE2, belegt), GPL-3.0 und LGPL-3.0 (SRC-LIC-GPL-LGPL, nicht geprüft) | Lösen pysystemtrade (GPL-3.0) oder NautilusTrader (LGPL-3.0) als Referenz und Testorakel in Forschung und CI, ohne Übernahme von Code in den Kern und ohne Weitergabe, Pflichten aus? | kein Framework-Code im Geldpfad; Werkzeuge nur in Forschungszone und CI; SBOM weist die Lizenz jeder Abhängigkeit aus (`implementation/make_or_buy.md`) | Übernahme von Framework-Code und jede Weitergabe |
| Steuern | siehe `legal/tax_matrix.md` | Behandlung, Übergabeformat (X-TAX-01) | pauschale Sensitivität in der Wirtschaftsrechnung | G8 |
| Ethische Ausschlüsse | Betreiberentscheidung BQ-06/BQ-06a | – | Aktienindizes nur rüstungsfrei (alle Kandidaten gesperrt); keine weiteren Ausschlüsse | Universum |

**B2 bis B4:** nach BQ-02 nicht Systemaufgabe; keine Zeilen. Eine spätere Entscheidung für B2 bis B4 verlangt eine neue Matrix.
