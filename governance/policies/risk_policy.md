# Risikorichtlinie

1. **Grundsatz:** Hebel ist ein Ergebnis, Risiko die Steuergröße (R-06). Kein erzwungener Mindesthebel (P-OP-LEV-MIN).
2. **Tagesgrenze:** Der Tagesverlust darf <!--v:param:P-OP-DAILY-LOSS-CAP|pct0-->9 %<!--/v--> des Kapitals zu Tagesbeginn nicht erreichen (BQ-04). Durchsetzung durch die Lückenregel vor jeder Order (PTC-13) und die Tagesverlust-Leiter (<!--v:param:P-RISK-DL-L1|pct0-->3 %<!--/v-->, <!--v:param:P-RISK-DL-L2|pct0-->5 %<!--/v-->, <!--v:param:P-RISK-DL-L3|pct1-->6,5 %<!--/v-->); Auslegung der Restwahrscheinlichkeit nach X-OP-DLC-MODE.
3. **Profile:** Nur zulässige Profile (§7.4) dürfen in einem Grant stehen; der Pilot beginnt in H5 mit <!--v:param:P-LEV-PILOT-SIZE|pct0-->50 %<!--/v--> Größe; Aufstieg nur nach §7.8 mit zweiter Freigabe, Abstieg automatisch.
4. **Limits:** Alle Grenzen stehen in `registers/limits.json`; Verletzungen sind Incidents. Grenzen werden nie im laufenden Betrieb erhöht, sondern nur per Release der Klasse D.
5. **Risikoakzeptanz:** Kein Grant ohne signierte Risikoakzeptanz mit Rechenwerten (X-OP-RISK-ACCEPT, `governance/grants_and_risk_acceptance.md`).
6. **Unabhängigkeit:** Das Prüfmodul rechnet Limits und Entscheidungen unabhängig nach; Abweichungen sperren Einstiege (RB-21).
7. **Berichte:** täglicher Risikobericht, wöchentliche Risikorunde mit der externen Risikofunktion ab G9.
