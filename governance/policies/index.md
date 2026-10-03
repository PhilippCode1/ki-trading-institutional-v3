# Richtlinien (§13)

Die Richtlinien sind verbindlich für Betreiber, Vertretung, externe Risikofunktion, externe Prüfer und alle Systemkomponenten. Werte stehen nur in `parameters.json` und `registers/limits.json`; die Richtlinien verweisen darauf. Änderungen an einer Richtlinie sind Änderungen der Klasse D (`governance/policies/change_policy.md`).

| Richtlinie | Datei | Kern |
|---|---|---|
| Risiko | `risk_policy.md` | Lückenregel, Leitern, Profile, Grants, Risikoakzeptanz |
| Handel | `trading_policy.md` | nur registrierte Strategien, kein Handel durch Sprachmodelle, Marktverhalten |
| Änderungen | `change_policy.md` | Klassen A0 bis D, Vier-Augen-Prinzip, Karenzzeit, Releases |
| Incidents | `incident_policy.md` | Schweregrade, Reaktionszeiten, Post-Mortems |
| KI | `ai_policy.md` | Rollen, Grenzen, Evaluation, Nutzenbilanz, Rückbau |
| Auslagerung | `outsourcing_policy.md` | Broker, VPS, Daten, Modellanbieter, externe Rollen; Due Diligence und Ausstieg |
| Informationssicherheit | `infosec_policy.md` | Identitäten, Schlüssel, Netz, Härtung, Protokolle |
| Aufbewahrung | `retention_policy.md` | unveränderliche Protokolle, Fristen nach Vorgabe der externen Person |

Eine Richtlinie zu Interessenkonflikten betrifft nur die Betriebsmodelle B3 und B4 (Gelder Dritter, Software für Dritte), die nach BQ-02 ausgeschlossen sind (X-SCOPE-THIRD).
