# Grants und Risikoakzeptanz (§7.10, §13)

> **Betreiberfassung.** Kein Handel außerhalb der Forschung ohne Grant: eine signierte Freigabe mit Art (Paper, Pilot, Standard), Konto, Instrumenten, Kapitaldeckel, Verlustbudget, Hebelprofil, Laufzeit und Widerrufsweg. Vor jedem Grant unterschreibst du eine Risikoakzeptanz in Klartextzahlen, die aus den Rechnern stammt, nicht aus Schätzungen. Ein Grant verfällt bei jedem Release-Wechsel und nach einem Restore; ohne gültigen Grant kann das System nur schützen und abbauen. Weil heute kein Profil zulässig ist, ist nur ein Paper-Grant möglich. Für Go/No-Go heißt das: Echtgeld-Grants sind gesperrt, bis ein Profil zulässig und alle Sperren gelöst sind. Nächster Schritt ist ein Paper-Grant nach G6.

## 1 Grant-Arten

| Art | Umgebung | Voraussetzungen (Tore) | Höchstlaufzeit | Profil |
|---|---|---|---|---|
| PAPER | Demokonto | G5, G6 | <!--v:param:P-SEC-GRANT-DAYS/PAPER|d0-->90<!--/v--> Tage | beliebig (ohne Geld) |
| PILOT | Echtgeldkonto | G7 bestanden; X-OP-CAPITAL, X-OP-RISK-ACCEPT, X-LEGAL-01, X-TAX-01, X-ORG-DEPUTY, X-BRK-* bestätigt | <!--v:param:P-SEC-GRANT-DAYS/PILOT|d0-->30<!--/v--> Tage | nur H5 mit <!--v:param:P-LEV-PILOT-SIZE|pct0-->50 %<!--/v--> Größe |
| STANDARD | Echtgeldkonto | G8 bestanden; X-ORG-RISK bestätigt | <!--v:param:P-SEC-GRANT-DAYS/STANDARD|d0-->90<!--/v--> Tage | nach Hebel-Stufenleiter (§7.8) |

Inhalt jedes Grants (Schema `live_grant`): Art, Schlüssel-Fingerabdruck, Broker, Kontoreferenz, Kontotyp laut Broker (Demo oder Echtgeld), Instrumente, Release-, Strategie- und Parameter-Hash, Kapitaldeckel, Verlustbudget, Profil, Laufzeit, zwei Alarmkanäle, Widerrufskennung, bestandene Tore, Signatur (übernommen aus v2.0, erweitert um Kontotyp und Profil). Ein Releasewechsel oder Restore invalidiert den Grant; ohne gültigen Grant gilt EXIT_ONLY.

## 2 Risikoakzeptanz (X-OP-RISK-ACCEPT)

Vorlage; die Werte füllt `risk/kelly_ruin_simulator.py` und `risk/stress_test_engine.py` für das beantragte Profil und Kapital, niemand von Hand:

> Ich habe verstanden: Mit einer Wahrscheinlichkeit von *q* verliere ich innerhalb von drei Jahren in der Spitze mindestens *Drawdown* (*Betrag* EUR). Im schlimmsten gerechneten Szenario *Szenario* beträgt der Verlust *Verlust* (*Betrag* EUR). Mit einer Wahrscheinlichkeit von *p* je Jahr überschreitet ein einzelner Tag die Tagesgrenze. Das Verlustbudget dieses Grants beträgt *Budget* EUR; wird es erreicht, endet der Grant.

Beispiel mit den heutigen Rechenwerten der registrierten Allokation in H5 und der Referenzstufe (nicht zulässig, nur zur Veranschaulichung): Drawdown über drei Jahre, der mit einer Wahrscheinlichkeit von fünf Prozent überschritten wird, <!--v:kelly:results/H5/SYSTEM/max_drawdown/3/p95|pct1-->14,5 %<!--/v--> (<!--v:calc:mdd_eur/H5/SYSTEM/3/p95|eur-->726.701 EUR<!--/v-->), schlimmstes Szenario <!--v:stress:results/SYSTEM/H5/worst_scenario|raw-->SC-H-2022NI<!--/v--> mit <!--v:stress:results/SYSTEM/H5/worst_loss_with_ladder|pct1-->20,4 %<!--/v--> (<!--v:calc:stress_eur/SYSTEM/H5|eur-->1.020.588 EUR<!--/v-->), Überschreitung der Tagesgrenze <!--v:kelly:results/H5/SYSTEM/p_day_loss_over_cap_per_year|pct1-->0,7 %<!--/v--> je Jahr.

Auslegung der Tagesgrenze (X-OP-DLC-MODE): STRENG (Standard) heißt, das System sperrt jedes Profil, dessen gerechnete Restwahrscheinlichkeit einer Überschreitung nicht null ist, sofern der Betreiber keine Restwahrscheinlichkeit signiert; im heutigen Stand ist diese Wahrscheinlichkeit wegen Ereignissen jenseits der Konstruktion nie null, deshalb verlangt jeder Echtgeld-Grant eine ausdrückliche Signatur der Restwahrscheinlichkeit (DEC-CF-02).

## 3 Widerruf und Ablauf

Widerruf jederzeit durch den Betreiber (signiert) oder automatisch bei: Ablauf, Releasewechsel, Restore, Erreichen des Verlustbudgets, Kill-Stufe der Drawdown-Leiter, Verletzung der Tagesgrenze, Wegfall einer Voraussetzung (etwa Vertretung nicht mehr verfügbar). Nach Widerruf gilt EXIT_ONLY; ein neuer Grant braucht bei Verlust- oder Grenzereignissen einen Ursachenbericht (RB-19).

## 4 Ausnahme ohne Grant: Echtgeld-Killer-Tests in BS-01

Drei Killer-Tests brauchen Minimalgrößen im Echtgeldkonto, weil das Demo Ausführung, Kommission und Auszug nicht beweist (KT-04, KT-06, KT-14). Das ist kein Handel des Systems und braucht keinen Grant, ist aber eng begrenzt:

- Jede einzelne Order löst der Betreiber aus; das Testskript sendet sie erst nach seiner signierten Bestätigung genau dieser Order (T-GOV-002). Kein Sprachmodell, keine Strategie, keine Wiederholung ohne neue Bestätigung.
- Kleinste handelbare Größe, jede Order mit Schutzstopp; Verlustdeckel über alle Echtgeldtests <!--v:param:P-EXE-KT-LOSS-CAP-EUR|eur-->250 EUR<!--/v--> (P-EXE-KT-LOSS-CAP-EUR). Ist er erreicht, enden die Echtgeldtests, und G1 wird mit den vorhandenen Ergebnissen ausgewertet.
- Die Systemanmeldung hat kein Auszahlungsrecht (T-SEC-007); Margin-Nähe und Stop-out werden nie im Echtgeldkonto herbeigeführt.
- Protokoll mit Rohantworten, Zeitstempeln und Auszugszeilen im Journal; die Ergebnisse gehen in GATE-G1 ein.

Die Kontoeröffnung selbst ist eine Entscheidung und Handlung des Betreibers (X-BRK-ACCOUNT); dieses Paket eröffnet kein Konto, schließt keinen Vertrag und sendet keine Order.
