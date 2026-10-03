# Änderungsrichtlinie

| Klasse | Gegenstand | Freigabe |
|---|---|---|
| A0 | Dokumentation, Berichte, Wissenseinträge ohne ausgeführten Code | Betreiber |
| A1 | Code außerhalb des Kerns ohne Evidenzwirkung (Forschungsskripte, Agenten-Skills, Texte der Oberfläche) | Betreiber nach Tests |
| B | Infrastruktur, Abhängigkeiten, Agent-Updates, Kernänderungen mit belegter Entscheidungsgleichheit | Betreiber nach Tests und Äquivalenzprüfung auf dem Replay-Korpus |
| C | Handelswirkung: Strategie, Risiko- und Größenlogik, Kostenmodell, Daten mit Evidenzwirkung | Betreiber und zweite menschliche Freigabe nach Tests, Replay und Neubewertung der Tore |
| D | Governance: Grenzen, Rechte, Tore, Allowlists, Änderungsklassen, Autonomiestufe des Agenten | Betreiber und zweite menschliche Freigabe; Eintrag im Entscheidungsregister |

Regeln (übernommen aus v2.0, verschärft um die menschliche zweite Freigabe):

1. Die Klasse folgt aus der Wirkung, nicht aus der Angabe des Autors; jede Änderung im Importgraph des Kerns ist mindestens C, außer die Äquivalenzprüfung belegt gleiche Entscheidungen.
2. Autor und Freigebender sind verschiedene Schlüssel; eine zweite KI-Instanz zählt nicht als Freigabe.
3. Eigene Änderungen des Betreibers der Klassen C und D werden frühestens <!--v:param:P-OPS-CHANGE-COOLDOWN-H|d0-->24<!--/v--> Stunden nach dem Prüfbericht freigegeben.
4. Aktivierung ohne offene UNKNOWN und außerhalb des Einstiegsfensters; Klassen C und D nur bei flachem Konto.
5. Jedes Release nennt Rückweg oder Vorwärtsreparatur; ein Releasewechsel invalidiert Grants.
