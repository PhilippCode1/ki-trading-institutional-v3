# Schlüssel- und Credential-Management (§12)

> **Betreiberfassung.** Jede geldwirksame Freigabe braucht deinen Hardware-Schlüssel; ein zweiter, getrennt verwahrter Schlüssel verhindert, dass ein Verlust das System lahmlegt. Alle Zugangsdaten haben einen festen Ort, eine Rotation und einen Widerrufsweg, und ein Break-glass-Verfahren erlaubt im Notfall nur Schutz und Abbau. Gegen das Schlüsselpersonenrisiko sind Ersatzschlüssel, PIN, Sicherungsschlüssel und Wiederherstellungscodes auf getrennte Orte verteilt, sodass kein einzelner Ort den Zugriff auf Konto und System erlaubt. Die Hardware-Schlüssel kosten zusammen <!--v:costreg:COST-INF-KEYS|eur-->120 EUR<!--/v-->. Für Go/No-Go heißt das: Ohne zwei Hardware-Schlüssel und geregelte Hinterlegung kein Pilot. Nächster Schritt ist die Benennung der Vertrauensperson für die Hinterlegung (X-ORG-DEPUTY).

## 1 Inventar

| Schlüssel oder Credential | Zweck | Ort | Rotation | Widerruf |
|---|---|---|---|---|
| Signaturschlüssel des Betreibers (primär) | signierte Aktionen, Grants, Freigaben | Hardware-Schlüssel (FIDO2), nie exportierbar | bei Verdacht; Gültigkeit je Aktion <!--v:param:P-SEC-SIG-EXPIRY-MIN|d0-->15<!--/v--> Minuten | Sperre im Grant-Register, Ersatzschlüssel aktivieren |
| Signaturschlüssel des Betreibers (Ersatz) | wie oben | zweiter Hardware-Schlüssel, getrennt verwahrt | wie oben | wie oben |
| Schlüssel der externen Risikofunktion | Veto und zweite Freigabe | eigener Hardware-Schlüssel der Person | bei Personenwechsel | Sperre im Grant-Register |
| Schlüssel der Notfallvertretung | Pause, Kill-Switch, Abbau | eigener Hardware-Schlüssel | bei Personenwechsel | Sperre im Grant-Register |
| Evaluator-Schlüssel | Signatur der Torergebnisse | nur im Prüfmodul | jährlich und bei Verdacht | Neuausstellung; alte Ergebnisse bleiben prüfbar |
| MT5-Hauptpasswort | Handel durch den Geldpfad | geschützter Speicher des Dienstkontos im Geldpfad | alle <!--v:param:P-SEC-CRED-ROTATION-D|d0-->90<!--/v--> Tage, nach Host-Wechsel, Restore, Verdacht (Fencing) | Änderung beim Broker |
| Lesezugang Broker | Prüfmodul und Monitor | jeweilige Instanz | wie oben | Änderung beim Broker |
| Kundenportal des Brokers | Ein- und Auszahlung, Kontoverwaltung | nur Betreiber; Zwei-Faktor-Anmeldung | nach Regel des Brokers | Broker |
| WireGuard-Schlüssel | Zugang zwischen Instanzen und Betreiber | je Instanz und Gerät | jährlich, bei Gerätewechsel | Peer entfernen |
| Anbieter-Schlüssel des Modellanbieters | Abo-Zugang | nur LLM-Gateway | nach Regel des Anbieters | Anbieter-Konto |
| Token der Projektschnittstelle | Agent → Geldpfad | KI-Zone (Container) | alle <!--v:param:P-SEC-CRED-ROTATION-D|d0-->90<!--/v--> Tage, bei Verdacht sofort | Sperre in `svc-projectops` |
| Sicherungsschlüssel | Verschlüsselung der Offsite-Kopien | Betreiber, Kopie in der Hinterlegung | jährlich | neue Sicherungen mit neuem Schlüssel |

## 2 Break-glass

Fällt der primäre Hardware-Schlüssel aus, aktiviert der Betreiber den Ersatzschlüssel; alle Grants werden neu signiert. Sind beide nicht verfügbar, darf die Notfallvertretung mit ihrem eigenen Schlüssel nur pausieren, stornieren und abbauen; neue Grants sind ausgeschlossen, bis ein Betreiberschlüssel wieder verfügbar ist (RB-19). Jede Break-glass-Nutzung ist ein Incident mit Post-Mortem; geprobt in DR-06.

## 3 Hinterlegung gegen das Schlüsselpersonenrisiko (übernommen aus v2.0, erweitert um Hardware-Schlüssel)

Die Hinterlegung ist auf getrennte Orte verteilt, damit kein einzelner Ort und keine einzelne Person die volle Kontrolle über Konto und System erhält:

| Ort | Inhalt | wer öffnen darf | Wirkung einer Kompromittierung |
|---|---|---|---|
| A Notfallvertretung | Notfallhandbuch (Kontakt des Brokers, Ablauf zu Sperre und Abbau), eigener Hardware-Schlüssel der Vertretung | Vertretung | nur Pause, Kill-Switch, Abbau; kein Geldabfluss |
| B Bankschließfach des Betreibers | Ersatz-Hardware-Schlüssel des Betreibers ohne PIN | Betreiber; sonst nur mit Vollmacht nach D | ohne PIN nicht nutzbar |
| C versiegelter Umschlag bei einer zweiten Vertrauensperson (nicht die Vertretung) | PIN des Ersatzschlüssels, Hälfte des Sicherungsschlüssels | nur gemeinsam mit D | allein nicht nutzbar |
| D Notar oder Bank nach Vollmacht | Wiederherstellungscodes des Kundenportals (Auszahlungen möglich), zweite Hälfte des Sicherungsschlüssels | nur mit Nachweis nach Vollmacht und Protokoll | Auszahlung erst nach Identitätsprüfung durch den Broker |

**Öffnungsverfahren.** B bis D werden nur geöffnet, wenn (1) der Betreiber seit P-OPS-PRESENCE-MAX-D Tagen nicht erreichbar ist (Sperrgrund OPERATOR_ABSENT, RB-35) und (2) zwei Personen anwesend sind, von denen keine allein Zugriff auf C und D zugleich hat. Wiederherstellungscodes und Ersatzschlüssel liegen nie am selben Ort. Jede Öffnung wird mit Zeit, Personen und entnommenen Teilen protokolliert und löst die Rotation aller entnommenen Zugänge aus (T-SEC-013, Drill DR-06). Die Vollmacht für D und die Benennung der Personen sind externe Eingaben (X-ORG-DEPUTY); bis dahin gilt die Hinterlegung als nicht eingerichtet und G8 bleibt gesperrt.

## 4 Regeln

- Kein Schlüssel und kein Passwort in Repository, Logs, Tickets, Chats oder Umgebungsvariablen von Agentenprozessen.
- Autor und Freigebender sind verschiedene Schlüssel (Vergleich der Schlüssel, nicht der Rollennamen; übernommen aus v2.0).
- Jeder Host-Wechsel oder Restore rotiert die Broker-Credentials; die neue Instanz wird erst Writer, wenn die alte Anmeldung abgewiesen wird (RB-17, DR-09).
