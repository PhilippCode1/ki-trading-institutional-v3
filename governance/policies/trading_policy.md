# Handelsrichtlinie

1. **Nur Registriertes:** Gehandelt werden nur vorregistrierte Strategien (`research/strategy_family.md`) mit bestandenen Toren und nur zugelassene Instrumente (§6.2); Aktienindizes nur nach Nachweis der Rüstungsfreiheit (BQ-06a).
2. **Kein Handel durch Sprachmodelle:** Orders entstehen nur im deterministischen Kern (D3-05).
3. **Keine manuellen Trades durch das System-Konto:** Eingriffe des Betreibers nur über den eigenen Zugang und angekündigt (RB-23).
4. **Marktverhalten:** Jede Order ist mit Ausführungsabsicht gesendet. Stornieren und Ändern nur für Schutz, Abbau, Ablauf und Child-Order-Steuerung; Nachrichtendrosselung (PTC-05) und Duplikaterkennung (PTC-06) verhindern auffällige Muster. Die Anwendbarkeit von MAR und Börsenregeln wie CME Rule 575 prüft die externe Person (SRC-REG-MAR, SRC-REG-CME-575, nicht geprüft); die technischen Kontrollen gelten unabhängig davon.
5. **Positionsgrenzen:** höchstens <!--v:param:P-RISK-MAX-OI-SHARE|pct1-->0,5 %<!--/v--> des Open Interest je Kontrakt; Melde- und Positionsgrenzen der Börsen prüft die externe Person.
6. **Rollen und Lieferung:** keine Positionen im Liefer- oder Verfallsfenster (RB-18); Energie-Frontmonate nach P-UNI-ENERGY-EXPIRY-DAYS.
7. **Demo und Echtgeld:** Den Modus schaltet nur der Betreiber (BQ-09); jede Order prüft den Kontotyp (PTC-10).
