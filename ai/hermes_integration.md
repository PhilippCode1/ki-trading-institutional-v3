# Hermes: Integration, Konfiguration und Upstream (§11.2, §11.3, EV-10)

> **Betreiberfassung.** Hermes wird in einer festen, geprüften Version betrieben und nie automatisch aktualisiert, weil das Projekt sehr schnell ändert und selbst kleine Versionssprünge Tausende Änderungen enthalten können. Er läuft ohne Root-Rechte in einem Container der KI-Zone, seine Konfiguration ist schreibgeschützt, und er erreicht das Internet nur über eine Allowlist und den Modellanbieter nur über ein Gateway. Updates kommen höchstens alle <!--v:param:P-AI-UPDATE-MIN-DAYS|d0-->30<!--/v--> Tage und nur nach bestandener Evaluationssuite; Sicherheitskorrekturen schneller. Der Pflegeaufwand ist als Betreiberzeit in der Wirtschaftsrechnung enthalten. Für Go/No-Go heißt das: Hermes ist beherrschbar, aber nur mit dieser Disziplin. Nächster Schritt: Pinning auf die beim Aufbau aktuelle, geprüfte Version in BS-05.

## 1 Upstream (belegt, Stand 24.09.2026)

| Kennzahl | Wert | Quelle |
|---|---|---|
| Lizenz | <!--v:r5:hermes_upstream/license/value|raw-->MIT<!--/v--> | SRC-HERMES-UPSTREAM |
| neueste Version | <!--v:r5:hermes_upstream/latest_release_2026_09_24/version|raw-->v0.21.5<!--/v--> (Tag <!--v:r5:hermes_upstream/latest_release_2026_09_24/tag|raw-->v2026.9.24<!--/v-->) | SRC-HERMES-UPSTREAM |
| Releases im Beobachtungsfenster | <!--v:r5:hermes_upstream/release_frequency/releases_in_window|int-->36<!--/v--> in <!--v:r5:hermes_upstream/release_frequency/span_days_first_to_last|d0-->196<!--/v--> Tagen | SRC-HERMES-UPSTREAM |
| mittlerer Abstand zwischen Releases | <!--v:r5:hermes_upstream/release_frequency/mean_interval_days|d1-->5,6<!--/v--> Tage (Median <!--v:r5:hermes_upstream/release_frequency/median_interval_days|d0-->5<!--/v-->) | SRC-HERMES-UPSTREAM |
| Minor-Releases | <!--v:r5:hermes_upstream/release_frequency/minor_releases_x_y_0|int-->20<!--/v-->, mittlerer Abstand <!--v:r5:hermes_upstream/release_frequency/minor_mean_interval_days|d1-->9,1<!--/v--> Tage | SRC-HERMES-UPSTREAM |
| Releases in den letzten neunzig bzw. dreißig Tagen | <!--v:r5:hermes_upstream/release_frequency/releases_last_90_days|int-->18<!--/v--> bzw. <!--v:r5:hermes_upstream/release_frequency/releases_last_30_days|int-->7<!--/v--> | SRC-HERMES-UPSTREAM |
| Änderungsvolumen | <!--v:r5:hermes_upstream/change_volume/summary|raw-->Minor-Releases umfassen laut Release-Notes ca. 800–5.800 Commits; Patch-Releases 28 bis 5.071 Non-Merge-Commits. Die Patch-Nummer ist kein Indikator für kleine Änderungen (v0.21.4 als Patch: 5.071 Commits, 5.169 Dateien).<!--/v--> | SRC-HERMES-UPSTREAM (teilweise belegt) |

Folgerung (EV-10): Jede Version ist ein neues Produkt; ein Update ohne Evaluation ist ausgeschlossen, auch bei Patch-Releases.

## 2 Update-Politik

- Gepinnte Version als Image mit selbst berechnetem Digest; `hermes update` ist verboten, weil es dem Hauptzweig folgt und Pins aufhebt (SRC-HERMES-UPDATE, SRC-HERMES-ISSUE-34514).
- Reguläre Updates höchstens alle <!--v:param:P-AI-UPDATE-MIN-DAYS|d0-->30<!--/v--> Tage, Sicherheitskorrekturen binnen <!--v:param:P-SEC-PATCH-CRIT-D|d0-->14<!--/v--> Tagen; jeweils als Release der Klasse B mit Evaluationssuite (`ai/eval_suite_spec.md`, Bestehensquote mindestens <!--v:param:P-AI-EVAL-PASS|pct0-->95 %<!--/v-->, keine Verschlechterung der Regeltreue).
- Pflegeaufwand <!--v:param:P-AI-UPDATE-EFFORT-H|d0-->3<!--/v--> Stunden je Update (Annahme); bei höchstens einem regulären Update je Intervall sind das <!--v:calc:ai_maintenance_hours_year|d0-->36<!--/v--> Stunden im Jahr, in der Betreiberzeit der Wirtschaftsrechnung enthalten.
- Rückweg: das vorige Image bleibt verfügbar; Rücknahme nach RB-20.

## 3 Betrieb und Konfiguration (übernommen aus v2.0, zu prüfen gegen die gepinnte Version)

Die Voreinstellungen des Upstreams sind für eine kontrollierte Governance zu offen (Skills werden frei geschrieben, Freigabe-Gates sind per Chat umschaltbar, Dateischutz gilt nur für die Datei-Werkzeuge, der Egress-Proxy ist optional; SRC-HERMES-CONFIG, SRC-HERMES-SECURITY, SRC-HERMES-EGRESS). Deshalb wirkt die Governance über Dateisystem und Netz:

- Container ohne Root und ohne Docker-Socket; Terminal-Backend nur im Container.
- Konfiguration, Persona, Hooks, Skills, Plugins und Agenten-Anweisungen schreibgeschützt eingebunden; gestagte Schreibvorgänge landen in einem Prüfordner; neue Skills nur als Release.
- Zielwerte (Schlüssel laut Dokumentation, gegen die gepinnte Version zu prüfen): Schreibfreigabe für Skills und Gedächtnis erzwingen, Projekterkennung von Skills aus, Hintergrund-Review aus, Cron und Delegation deaktiviert, Netzwerkwerkzeuge verweigert; MCP-Server nur die Projektschnittstelle mit Werkzeug-Allowlist; Modellendpunkt ist das LLM-Gateway.
- Gedächtnis enthält nur Verweise auf das Wissensregister (SRC-HERMES-MEMORY); bei Widerspruch gilt der autoritative Zustand.
- Geplante Arbeit startet ein externer Zeitgeber mit versioniertem Auftragstext, nicht die Cron-Funktion des Agenten.

## 4 LLM-Gateway, Ausfall und Kompromittierung

Das Gateway hält den Anbieter-Schlüssel (der Agent sieht ihn nie), prüft jede Anfrage auf Kanarienwerte und verbotene Muster, protokolliert Hash und Größe und leitet nur an den freigegebenen Anbieter weiter. Kontingent erschöpft oder Anbieter ausgefallen: Der Agent pausiert (RB-11), der Kern ist unberührt. Kompromittierungsverdacht: Isolation binnen <!--v:param:P-OPS-ISOLATE-MIN|d0-->15<!--/v--> Minuten und Rückkehr nur über eine saubere Neuinstallation (RB-12, DR-07).

## 5 Abo und Budget

Abrechnung über das Nous-Portal-Abo (BQ-07; Stufe P-AI-PORTAL-TIER, SRC-NOUS-PORTAL) mit harter Monatsgrenze <!--v:param:P-AI-MONTHLY-BUDGET-EUR|eur-->350 EUR<!--/v--> für KI-Abos und Coding-Agent (DEC-DS-14). Kursrohdaten gehen nie an den Anbieter (DEC-CF-07).
