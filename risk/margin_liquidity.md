# Margin- und Liquiditätsmanagement (§7.7, EV-09)

> **Betreiberfassung.** Das System soll nie in eine Zwangsliquidation durch den Broker laufen und nie einen Nachschuss brauchen. Die Liquidationsregel des Brokers für Futures ist noch nicht belegt; geplant wird vorsichtig mit einem Stop-out bei <!--v:param:P-MRG-BROKER-STOPOUT|pct0-->50 %<!--/v--> der Initial-Margin, und die eigene De-Risking-Schwelle liegt weit davor. Maßgeblich ist das Guthaben beim Broker: Dort liegt nur ein Teil des Kapitals (<!--v:param:P-ECO-CASH-AT-BROKER|pct0-->25 %<!--/v-->), und nur dieser Teil deckt Margin und Verluste, bis eine Überweisung ankommt. Für die registrierte Allokation reicht dieser Anteil knapp nicht, weil im Nickel-Szenario eine Handelsaussetzung den Abbau verhindert; für hohe Hebel reicht er deutlich nicht. Für Go/No-Go heißt das: Vor jedem Grant muss beim Broker mindestens der für das Profil gerechnete Anteil liegen; der Engpass bleibt trotzdem die Tagesgrenze. Nächster Schritt: Liquidationsregel, Übernacht-Margins und Nachschussausschluss schriftlich vom Broker (X-BRK-LIQ, X-BRK-MARGIN, X-BRK-NACHSCHUSS).

## 1 Liquidationsrichtlinie des Brokers

| Frage | Stand | Quelle / externe Eingabe |
|---|---|---|
| Stop-out-Level und Vorgehen bei Futures | nicht belegt; Planwert <!--v:param:P-MRG-BROKER-STOPOUT|pct0-->50 %<!--/v--> der Initial-Margin (ANNAHME) | X-BRK-LIQ |
| Nachschusspflicht | für Privatkunden mit Sitz in Deutschland vertraglich auszuschließen; ob das für das Konto gilt, hängt von der Kundeneinstufung ab | SRC-REG-BAFIN-FUT, X-BRK-NACHSCHUSS |
| Intraday-Margin | rund <!--v:param:P-MRG-INTRADAY-FXFLAT|pct0-->10 %<!--/v--> der Börsenmargin laut Broker (Seite undatiert) | SRC-BRK-FXFLAT |
| Übernacht-Margin je Kontrakt | nicht belegt; Planwerte je Risikoklasse im Instrumentregister | X-BRK-MARGIN |
| Zeitpunkt der Umstellung Intraday → Übernacht | nicht belegt | X-BRK-MARGIN, Killer-Test KT-13 |

Weil Positionen über Nacht gehalten werden (<!--v:param:P-OP-HOLD-STD-MIN-H|d0-->4<!--/v--> h bis <!--v:calc:hold_std_max_days|d0-->4<!--/v--> Tage), rechnet die Größenbestimmung immer mit der Übernacht-Margin; die niedrige Intraday-Margin wird nie für die Größe genutzt (P-MRG-USE-INTRADAY). So kann der Wechsel in die Übernacht-Margin keine Liquidation auslösen.

## 2 Puffer und De-Risking vor der Brokerliquidation

Margin-Level = Guthaben beim Broker / Initial Margin. Beim Broker liegt der Anteil <!--v:param:P-ECO-CASH-AT-BROKER|pct0-->25 %<!--/v--> des NAV (P-ECO-CASH-AT-BROKER); Verluste werden dort abgerechnet, das Kapital außerhalb hilft erst nach einer Überweisung (<!--v:param:P-MRG-TOPUP-DAYS|d0-->2<!--/v--> Geschäftstage). Eigene Schwellen: De-Risking ab einem Margin-Level von <!--v:param:P-MRG-DERISK-TRIGGER|pct0-->150 %<!--/v--> (Positionsabbau, bis das Level wieder darüber liegt), Einstiegssperre bei Margin-Defizit (Sperrgrund MARGIN_DEFICIT). Der Broker liquidiert erst beim Stop-out. Die Rechnung zeigt, wie viel Verlust bis zu diesen Schwellen nötig wäre, auch nach einer Margin-Erhöhung um <!--v:param:P-MRG-STRESS-1|pct0-->50 %<!--/v--> bzw. <!--v:param:P-MRG-STRESS-2|pct0-->100 %<!--/v--> (belegt sind durchschnittliche Erhöhungen je Schritt und Spitzen im März 2020, SRC-MARGIN-*):

<!-- GEN:BEGIN tab.margin -->
| Allokation | Profil | M/E (Anteil NAV) | M/E +100 % | Margin-Level am Broker ohne Verlust | Margin-Level nach schlimmstem Szenario | Verlust bis De-Risking-Schwelle (Margin +100 %) | Verlust bis Stop-out (Margin +100 %) | nötiger Anteil beim Broker | Anteil beim Broker reicht | Szenarien mit Liquidation |
|---|---|---|---|---|---|---|---|---|---|---|
| MON-HARM (MH-R1) | schädlich, wahre Sharpe -0,2 | über 120 Monate | 0,0 % (Pilot) | 0,0 % (24 M) | 2,7 % (60 M) |
| MON-HARM (MH-R1) | stark schädlich (Harm-Screen), wahre Sharpe -1,0 | 68 Monate | 0,0 % (Pilot) | 0,6 % (24 M) | 41,0 % (60 M) |
| MON-HARM (MH-R1) | wertlos, wahre Sharpe 0,0 | über 120 Monate | 0,0 % (Pilot) | 0,0 % (24 M) | 1,1 % (60 M) |
| MON-HARM (MH-R1) | brauchbar, wahre Sharpe 0,3 | über 120 Monate | 0,0 % (Pilot) | 0,0 % (24 M) | 0,0 % (60 M) |
| MON-DRIFT (MD-R3) | Volatilität ×1,0 | über 252 Handelstage | 2,0 % (20 T) | 2,6 % (63 T) | 6,6 % (252 T) |
| MON-DRIFT (MD-R3) | Volatilität ×1,5 | 104 Handelstage | 3,9 % (20 T) | 19,0 % (63 T) | 93,2 % (252 T) |
| MON-DRIFT (MD-R3) | Volatilität ×2,0 | 47 Handelstage | 13,0 % (20 T) | 76,8 % (63 T) | 100,0 % (252 T) |
<!-- GEN:END tab.margin -->

Befund: Die Spalte „nötiger Anteil beim Broker“ nennt je Allokation und Profil das Guthaben, bei dem das Margin-Level auch nach dem schlimmsten Szenario und verdoppelter Margin nicht unter die De-Risking-Schwelle fällt. Für SYSTEM reicht der Planwert in <!--v:calc:stress_margin/SYSTEM/insufficient|int-->4<!--/v--> von <!--v:calc:stress_margin/SYSTEM/profiles|int-->4<!--/v--> Profilen knapp nicht (nötig bis <!--v:calc:stress_margin/SYSTEM/required_max|pct1-->25,5 %<!--/v-->); Ursache ist das Nickel-Szenario, in dem die Tagesverlust-Leiter (<!--v:param:P-RISK-DL-L1|pct0-->3 %<!--/v-->, <!--v:param:P-RISK-DL-L2|pct0-->5 %<!--/v-->, <!--v:param:P-RISK-DL-L3|pct1-->6,5 %<!--/v-->) ausgesetzte Positionen nicht abbauen kann. Für WUNSCHHEBEL reicht er in <!--v:calc:stress_margin/WUNSCHHEBEL/insufficient|int-->3<!--/v--> von <!--v:calc:stress_margin/WUNSCHHEBEL/profiles|int-->4<!--/v--> Profilen nicht (nötig bis <!--v:calc:stress_margin/WUNSCHHEBEL/required_max|pct0-->48 %<!--/v-->); in <!--v:calc:stress_margin/WUNSCHHEBEL/with_liquidation|int-->1<!--/v--> von <!--v:calc:stress_margin/WUNSCHHEBEL/profiles|int-->4<!--/v--> Profilen käme es zur Brokerliquidation. Regel: Vor jedem Grant wird der Anteil beim Broker mindestens auf den nötigen Wert gesetzt; die Wirtschaftsrechnung rechnet mit dem Planwert, weil heute keine Allokation zulässig ist.

## 3 Überschussliquidität, Sicherheiten und Währungen

- **Aufteilung:** Beim Broker liegen <!--v:param:P-ECO-CASH-AT-BROKER|pct0-->25 %<!--/v--> des Kapitals (Margin plus Puffer); der Rest liegt in Geldmarktanlagen oder kurzlaufenden Staatsanleihen beim Betreiber. Das begrenzt den Schaden bei einem Brokerausfall (Szenario SC-X-BROKER) und die Zinslücke (§5.2).
- **Umschichtung:** Sinkt das Margin-Level unter die De-Risking-Schwelle und ist Abbau nicht möglich (Handelsaussetzung, Limit-Move), meldet das System einen Nachschussbedarf; eine Überweisung dauert <!--v:param:P-MRG-TOPUP-DAYS|d0-->2<!--/v--> Geschäftstage und wird nur vom Betreiber ausgelöst.
- **Nachschuss unmöglich:** In diesem Szenario bleibt nur Abbau; die Tabelle zeigt, in welchen Allokationen der Abstand dafür nicht reicht (Spalte „Anteil beim Broker reicht“).
- **Währungen:** CME-Kontrakte führen USD-Margin und USD-P&L. Das System hält USD-Salden nur in Höhe der Margin plus Puffer und führt realisierte P&L täglich in EUR zurück; das Währungsrisiko auf offene P&L ist Teil der Risikorechnung.

## 4 Ereignisse, die Margin kurzfristig erhöhen

Börsen erhöhen Margins in Stressphasen oft mehrfach in kurzer Folge (SRC-MARGIN-MH01 bis SRC-MARGIN-MH10). Das System beobachtet Margin-Mitteilungen über den Referenzdatendienst und rechnet M/E bei jeder Änderung neu; eine angekündigte Erhöhung löst vorab eine Neuberechnung der Größen aus.
