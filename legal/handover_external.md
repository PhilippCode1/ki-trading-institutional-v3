# Übergabe an die externe Person für Recht und Steuern (BQ-03)

> **Betreiberfassung.** Dieses Blatt ist das, was du der externen Person gibst: worum es geht, was sie beantworten soll, bis wann welche Stufe gesperrt bleibt und welche Unterlagen sie bekommt. Es enthält keine Rechtsaussage des Pakets. Die Antworten werden als externe Eingaben X-LEGAL-01 und X-TAX-01 mit Datum und Unterschrift erfasst. Erst danach kann ein Pilot mit Echtgeld freigegeben werden. Für Go/No-Go heißt das: Diese Übergabe ist eine Voraussetzung für G8, nicht für Demo oder Forschung. Nächster Schritt: Termin mit der externen Person vereinbaren.

## 1 Sachverhalt

Ein Betreiber plant, mit eigenem Kapital über einen MT5-Broker börsengehandelte Futures vollautomatisch zu handeln (Haltedauer in der Regel <!--v:param:P-OP-HOLD-STD-MIN-H|d0-->4<!--/v--> h bis <!--v:calc:hold_std_max_days|d0-->4<!--/v--> Tage, höchstens <!--v:calc:hold_max_days|d0-->7<!--/v--> Tage). Es gibt keine Gelder Dritter, keine Signale oder Software für Dritte und keine Gesellschaft (BQ-02). KI-Komponenten laufen außerhalb des Handelspfads. Der Auftrag legt Deutschland und die EU als Rechtsrahmen zugrunde; Wohnsitz, Kundeneinstufung beim Broker und Datenrechte des Betreibers enthält das Paket nicht – sie stellt die externe Person fest.

## 2 Fragen

Rechtsfragen nach `legal/applicability_matrix.md`; Steuerfragen ST-1 bis ST-5 nach `legal/tax_matrix.md`.

## 3 Unterlagen

Masterkonzept (§4, §8, §11, §12, §15), Anwendbarkeitsmatrix, Steuerumfang mit Exportformat, Entscheidungsregister (Betreiberentscheidungen und Konflikte), Risikoregister (RK-24).

## 4 Erfassung der Antworten

| Eingabe | Inhalt | sperrt |
|---|---|---|
| X-LEGAL-01 | schriftliche Bestätigung der Anwendbarkeitsfragen mit Datum | GATE-G8 |
| X-TAX-01 | steuerliche Behandlung und Übergabeformat | GATE-G8 |
| X-AI-DPA | Datenverarbeitung beim Modellanbieter | Nutzung nicht öffentlicher Daten mit KI |
