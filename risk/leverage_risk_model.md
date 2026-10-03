# Hebel- und Risikomodell (§7)

> **Betreiberfassung.** Dieses Dokument beschreibt, wie das System aus einem Risikoziel Positionsgrößen macht und warum daraus fast nie ein hoher Hebel wird. Maßgeblich ist deine Tagesgrenze: Die gleichzeitige ungünstige Kurslücke aller Positionen plus des aufgelaufenen Tagesverlusts darf <!--v:calc:gap_budget|pct0-->8 %<!--/v--> nicht übersteigen, und diese Regel greift vor jeder Hebelgrenze. Mit den forschungsfähigen Instrumenten erreicht kein Profil seine Hebelobergrenze; hypothetisch über Zinsfutures wäre Hebel zwar herstellbar, verletzt aber das Verlustbudget und kostet ein Vielfaches der erwartbaren Kante. H5 ist die einzige Profilstufe, die überhaupt zulässig werden kann, und nur mit genügend Diversifikation. Für Go/No-Go heißt das: Kein Profil ist heute signierbar. Nächster Schritt: Liquidationsregel des Brokers (X-BRK-LIQ) und deine Auslegung der Tagesgrenze (X-OP-DLC-MODE).

## 1 Größenrechnung

1. **Risikoparität im Ziel:** Gewichte w_i = k · r_i / σ_i mit Risikoanteilen r_i und k = σ_p · D. Daraus folgt L_g = Σ|w_i| = D · σ_p / σ_h (Anhang A des Auftrags). D ist der Diversifikationsmultiplikator aus der Korrelationsmatrix (P-PRI-RHO-*; MOD-COV ersetzt sie in G3 durch Schätzungen aus EWMA und Schockregimen).
2. **Lückenregel (DEC-DS-10):** Lückenstress = Σ_i |w_i| · max(Klassenlücke_i, k · σ_Tag,i) mit k = <!--v:param:P-GAP-K-HYP-HIGH|d0-->10<!--/v-->, alle Positionen gleichzeitig ungünstig (P-LEV-CLUSTER-MODE). Vor jeder risikoerhöhenden Order gilt Lückenstress + Tagesverlust ≤ <!--v:param:P-OP-DAILY-LOSS-CAP|pct0-->9 %<!--/v--> − <!--v:param:P-RISK-GAP-RESERVE|pct0-->1 %<!--/v-->; über Wochenenden und Feiertage wird der Lückenstress mit <!--v:param:P-RISK-WEEKEND-FACTOR|d1-->1,5<!--/v--> bewertet. Weil alle Strategien außer S-IM über Wochenenden halten, rechnet die Planung dauerhaft mit diesem Faktor (konservativ; ein Abbau vor Wochenenden ist nicht modelliert).
3. **Skalierung:** Faktor s = min(Lückenbudget / (Wochenendfaktor × Lückenstress im Ziel); Profilgrenze / L_g im Ziel; 1). Erreichtes σ_p = s · σ-Ziel, erreichtes L_g = s · L_g im Ziel.
4. **Zulässigkeit je Profil:** σ-Ziel zu mindestens <!--v:param:P-LEV-SIGMA-TOLERANCE|pct0-->90 %<!--/v--> erreichbar (H5: σ_p mindestens <!--v:param:P-LEV-H5-SIGMA-MIN|pct0-->3 %<!--/v-->, das σ-Ziel von H5 ist Obergrenze), effektive Instrumentzahl mindestens gleich der Mindestdiversifikation, parametrischer ES (t-Verteilung mit <!--v:param:P-SIM-T-DF|d0-->4<!--/v--> Freiheitsgraden, <!--v:param:P-RISK-ES-CONF|pct1-->97,5 %<!--/v-->, ein Tag) unter dem ES-Limit, M/E unter der Profilgrenze und M/E nach einer Margin-Erhöhung um <!--v:param:P-MRG-STRESS-2|pct0-->100 %<!--/v--> unter der eigenen De-Risking-Schwelle.

## 2 Klassenlücken (historisch belegt, R4)

Die ungünstigsten Tageslücken je Klasse stammen aus der Stressrecherche (`research/sources/R4_stress_scenarios.json`, SRC-STRESS-*); bei Anleihen in Prozentpunkten Rendite (mal Duration), bei kurzfristigen Zinsfutures in Indexpunkten, sonst in Prozent des Preises.

<!-- GEN:BEGIN tab.params:P-GAP -->
| ID | Bedeutung | Wert | Einheit | Status |
|---|---|---|---|---|
| P-GAP-STIR | Ungünstigste Tageslücke STIR | 0,81 | Preispunkte | ENTWURF |
| P-GAP-ANLEIHE-KURZ | Ungünstigste Tageslücke ANLEIHE_KURZ | 0,50 | Prozentpunkte Rendite | ENTWURF |
| P-GAP-ANLEIHE-MITTEL | Ungünstigste Tageslücke ANLEIHE_MITTEL | 0,40 | Prozentpunkte Rendite | ENTWURF |
| P-GAP-ANLEIHE-LANG | Ungünstigste Tageslücke ANLEIHE_LANG | 0,45 | Prozentpunkte Rendite | ENTWURF |
| P-GAP-RENDITE | Ungünstigste Tageslücke RENDITE | 0,50 | Prozentpunkte Rendite | ENTWURF |
| P-GAP-FX | Ungünstigste Tageslücke FX | 7 | % Preis | ENTWURF |
| P-GAP-FX-CHF | Ungünstigste Tageslücke FX_CHF | 20 | % Preis | ENTWURF |
| P-GAP-ENERGIE | Ungünstigste Tageslücke ENERGIE | 25 | % Preis | ENTWURF |
| P-GAP-EDELMETALL | Ungünstigste Tageslücke EDELMETALL | 10 | % Preis | ENTWURF |
| P-GAP-INDUSTRIEMETALL | Ungünstigste Tageslücke INDUSTRIEMETALL | 15 | % Preis | ENTWURF |
| P-GAP-AGRAR | Ungünstigste Tageslücke AGRAR | 9 | % Preis | ENTWURF |
| P-GAP-VIEH | Ungünstigste Tageslücke VIEH | 6 | % Preis | ENTWURF |
| P-GAP-SOFTS | Ungünstigste Tageslücke SOFTS | 12 | % Preis | ANNAHME |
| P-GAP-KRYPTO | Ungünstigste Tageslücke KRYPTO | 25 | % Preis | ENTWURF |
| P-GAP-AKTIENINDEX | Ungünstigste Tageslücke AKTIENINDEX | 20 | % Preis | ENTWURF |
| P-GAP-K-HYP-LOW | Hypothetische Lücke k·σ (untere Stufe) | 5 | σ (Tag) | ENTWURF |
| P-GAP-K-HYP-HIGH | Hypothetische Lücke k·σ (obere Stufe) und Mindestlücke der Größenregel | 10 | σ (Tag) | ENTWURF |
<!-- GEN:END tab.params:P-GAP -->

Daraus folgen die Hebeldeckel je Klasse (eine Klasse allein darf das Lückenbudget auch mit dem Wochenendfaktor nicht überschreiten):

<!-- GEN:BEGIN tab.class_caps -->
| Risikoklasse | Konstruktionslücke (Median) | Hebeldeckel typisch | strengstes Instrument | Hebeldeckel streng |
|---|---|---|---|---|
| AGRAR | 13,86 % | 0,38× | ZW | 0,30× |
| ANLEIHE_KURZ | 1,01 % | 5,29× | ZT | 5,29× |
| ANLEIHE_LANG | 6,93 % | 0,77× | FGBX | 0,59× |
| ANLEIHE_MITTEL | 4,09 % | 1,30× | FBTP | 1,13× |
| EDELMETALL | 18,90 % | 0,28× | PA | 0,21× |
| ENERGIE | 25,00 % | 0,21× | QG | 0,14× |
| FX | 7,00 % | 0,76× | MSF | 0,27× |
| INDUSTRIEMETALL | 15,75 % | 0,34× | MHG | 0,34× |
| KRYPTO | 44,10 % | 0,12× | MET | 0,12× |
| RENDITE | 15,75 % | 0,34× | 2YY | 0,34× |
| SOFTS | 22,05 % | 0,24× | CC | 0,19× |
| STIR | 0,84 % | 6,35× | SR1 | 6,34× |
| VIEH | 11,34 % | 0,47× | HE | 0,34× |
<!-- GEN:END tab.class_caps -->

## 3 Profile

<!-- GEN:BEGIN tab.params:P-LEV -->
| ID | Bedeutung | Wert | Einheit | Status |
|---|---|---|---|---|
| P-LEV-H5-CAP | Profil H5: harte Obergrenze L_g | 5 | x | ENTWURF |
| P-LEV-H5-SIGMA | Profil H5: Ziel-Volatilität σ_p p. a. | 0,06 | Anteil | ENTWURF |
| P-LEV-H5-ME | Profil H5: Obergrenze Margin-Auslastung M/E | 0,25 | Anteil NAV | ENTWURF |
| P-LEV-H5-ES | Profil H5: ES-Limit (97,5 %, 1 Tag) | 0,02 | Anteil NAV | ENTWURF |
| P-LEV-H5-MINDIV | Profil H5: Mindestzahl effektiver Instrumente | 8 | Anzahl | ENTWURF |
| P-LEV-H10-CAP | Profil H10: harte Obergrenze L_g | 10 | x | ENTWURF |
| P-LEV-H10-SIGMA | Profil H10: Ziel-Volatilität σ_p p. a. | 0,09 | Anteil | ENTWURF |
| P-LEV-H10-ME | Profil H10: Obergrenze Margin-Auslastung M/E | 0,35 | Anteil NAV | ENTWURF |
| P-LEV-H10-ES | Profil H10: ES-Limit (97,5 %, 1 Tag) | 0,03 | Anteil NAV | ENTWURF |
| P-LEV-H10-MINDIV | Profil H10: Mindestzahl effektiver Instrumente | 8 | Anzahl | ENTWURF |
| P-LEV-H15-CAP | Profil H15: harte Obergrenze L_g | 15 | x | ENTWURF |
| P-LEV-H15-SIGMA | Profil H15: Ziel-Volatilität σ_p p. a. | 0,12 | Anteil | ENTWURF |
| P-LEV-H15-ME | Profil H15: Obergrenze Margin-Auslastung M/E | 0,45 | Anteil NAV | ENTWURF |
| P-LEV-H15-ES | Profil H15: ES-Limit (97,5 %, 1 Tag) | 0,04 | Anteil NAV | ENTWURF |
| P-LEV-H15-MINDIV | Profil H15: Mindestzahl effektiver Instrumente | 10 | Anzahl | ENTWURF |
| P-LEV-H20-CAP | Profil H20: harte Obergrenze L_g | 20 | x | BETREIBER |
| P-LEV-H20-SIGMA | Profil H20: Ziel-Volatilität σ_p p. a. | 0,15 | Anteil | ENTWURF |
| P-LEV-H20-ME | Profil H20: Obergrenze Margin-Auslastung M/E | 0,50 | Anteil NAV | ENTWURF |
| P-LEV-H20-ES | Profil H20: ES-Limit (97,5 %, 1 Tag) | 0,05 | Anteil NAV | ENTWURF |
| P-LEV-H20-MINDIV | Profil H20: Mindestzahl effektiver Instrumente | 10 | Anzahl | ENTWURF |
| P-LEV-SIGMA-TOLERANCE | Mindestanteil des σ-Ziels, der nach der Lückenregel erreichbar sein muss | 0,90 | Anteil | ENTWURF |
| P-LEV-H5-SIGMA-MIN | H5: kleinste sinnvolle Volatilität nach Lückenregel (Ziel-σ von H5 ist Obergrenze) | 0,03 | Anteil | ENTWURF |
| P-LEV-BAND-LOW | Unteres Ende des Betriebsbands L_g | 5 | x | ENTWURF |
| P-LEV-STEP-MIN-DAYS | Mindestdauer je Profilstufe vor Aufstieg | 90 | Handelstage | ENTWURF |
| P-LEV-STEP-COST-BAND | Zulässige Abweichung gemessener Kosten vom Modell für einen Aufstieg | 0,25 | Anteil | ENTWURF |
| P-LEV-STEP-VOL-BAND | Zulässige Abweichung realisierter von Ziel-Volatilität für einen Aufstieg | 0,30 | Anteil | ENTWURF |
| P-LEV-PILOT-SIZE | Pilotgröße als Anteil des Risikoziels von H5 | 0,50 | Anteil | ENTWURF |
| P-LEV-CLUSTER-MODE | Aggregation des Lückenstresses | ALLE_UNGUENSTIG | Text | ENTWURF |
<!-- GEN:END tab.params:P-LEV -->

<!-- GEN:BEGIN tab.profiles -->
| Profil | Obergrenze L_g | σ-Ziel p. a. | M/E höchstens | ES-Limit (97,5 %, 1 Tag) | Mindestdiversifikation | zulässig in (Variante, Mio. EUR) |
|---|---|---|---|---|---|---|
| H5 | 5× | 6 % (Obergrenze; mindestens 3 %) | 25 % | 2 % | 8 | keine |
| H10 | 10× | 9 % | 35 % | 3 % | 8 | keine |
| H15 | 15× | 12 % | 45 % | 4 % | 10 | keine |
| H20 | 20× | 15 % | 50 % | 5 % | 10 | keine |
<!-- GEN:END tab.profiles -->

## 4 Zulässigkeit je Variante, Kapitalstufe und Profil

Varianten: U-KOSTEN (registriert), U-BREAKEVEN (großzügige Kostenregel), U-ALLE (ohne Kostenfilter), U-KOSTEN-TFD1-7T (langsame Trendfolge mit Sieben-Tage-Grenze) und U-KOSTEN-TFD1 (Alternative ohne Sieben-Tage-Grenze).

<!-- GEN:BEGIN tab.leverage_cells -->
| Variante | Kapital (Mio. EUR) | Profil | Befund | σ_p erreicht | L_g | Lückenstress | Gründe |
|---|---|---|---|---|---|---|---|
| U-KOSTEN | 0,25 | H5 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-KOSTEN | 0,25 | H10 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-KOSTEN | 0,25 | H15 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-KOSTEN | 0,25 | H20 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-KOSTEN | 0,5 | H5 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-KOSTEN | 0,5 | H10 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-KOSTEN | 0,5 | H15 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-KOSTEN | 0,5 | H20 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-KOSTEN | 1 | H5 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-KOSTEN | 1 | H10 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-KOSTEN | 1 | H15 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-KOSTEN | 1 | H20 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-KOSTEN | 5 | H5 | unzulässig | 0,057 | 0,33 | 0,053 | Mindestdiversifikation: 2.0 < 8 effektive Instrumente |
| U-KOSTEN | 5 | H10 | unzulässig | 0,057 | 0,33 | 0,053 | Verlustbudget: Ziel-σ_p 9% nur zu 64% erreichbar (Lückenstress × Wochenendfaktor 12.5% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 2.0  |
| U-KOSTEN | 5 | H15 | unzulässig | 0,057 | 0,33 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 48% erreichbar (Lückenstress × Wochenendfaktor 16.7% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 2.0 |
| U-KOSTEN | 5 | H20 | unzulässig | 0,057 | 0,33 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 38% erreichbar (Lückenstress × Wochenendfaktor 20.9% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 2.0 |
| U-KOSTEN | 25 | H5 | unzulässig | 0,060 | 0,33 | 0,038 | Mindestdiversifikation: 1.0 < 8 effektive Instrumente |
| U-KOSTEN | 25 | H10 | unzulässig | 0,085 | 0,47 | 0,053 | Mindestdiversifikation: 1.0 < 8 effektive Instrumente |
| U-KOSTEN | 25 | H15 | unzulässig | 0,085 | 0,47 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 71% erreichbar (Lückenstress × Wochenendfaktor 11.3% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 1.0 |
| U-KOSTEN | 25 | H20 | unzulässig | 0,085 | 0,47 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 56% erreichbar (Lückenstress × Wochenendfaktor 14.2% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 1.0 |
| U-KOSTEN | 100 | H5 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-KOSTEN | 100 | H10 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-KOSTEN | 100 | H15 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-KOSTEN | 100 | H20 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-BREAKEVEN | 0,25 | H5 | unzulässig | 0,060 | 0,33 | 0,038 | Mindestdiversifikation: 1.0 < 8 effektive Instrumente |
| U-BREAKEVEN | 0,25 | H10 | unzulässig | 0,085 | 0,47 | 0,053 | Mindestdiversifikation: 1.0 < 8 effektive Instrumente |
| U-BREAKEVEN | 0,25 | H15 | unzulässig | 0,085 | 0,47 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 71% erreichbar (Lückenstress × Wochenendfaktor 11.3% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 1.0 |
| U-BREAKEVEN | 0,25 | H20 | unzulässig | 0,085 | 0,47 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 56% erreichbar (Lückenstress × Wochenendfaktor 14.2% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 1.0 |
| U-BREAKEVEN | 0,5 | H5 | unzulässig | 0,060 | 0,33 | 0,038 | Mindestdiversifikation: 1.0 < 8 effektive Instrumente |
| U-BREAKEVEN | 0,5 | H10 | unzulässig | 0,085 | 0,47 | 0,053 | Mindestdiversifikation: 1.0 < 8 effektive Instrumente |
| U-BREAKEVEN | 0,5 | H15 | unzulässig | 0,085 | 0,47 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 71% erreichbar (Lückenstress × Wochenendfaktor 11.3% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 1.0 |
| U-BREAKEVEN | 0,5 | H20 | unzulässig | 0,085 | 0,47 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 56% erreichbar (Lückenstress × Wochenendfaktor 14.2% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 1.0 |
| U-BREAKEVEN | 1 | H5 | unzulässig | 0,060 | 0,33 | 0,038 | Mindestdiversifikation: 1.0 < 8 effektive Instrumente |
| U-BREAKEVEN | 1 | H10 | unzulässig | 0,085 | 0,47 | 0,053 | Mindestdiversifikation: 1.0 < 8 effektive Instrumente |
| U-BREAKEVEN | 1 | H15 | unzulässig | 0,085 | 0,47 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 71% erreichbar (Lückenstress × Wochenendfaktor 11.3% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 1.0 |
| U-BREAKEVEN | 1 | H20 | unzulässig | 0,085 | 0,47 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 56% erreichbar (Lückenstress × Wochenendfaktor 14.2% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 1.0 |
| U-BREAKEVEN | 5 | H5 | unzulässig | 0,045 | 0,30 | 0,053 | Mindestdiversifikation: 4.0 < 8 effektive Instrumente |
| U-BREAKEVEN | 5 | H10 | unzulässig | 0,045 | 0,30 | 0,053 | Verlustbudget: Ziel-σ_p 9% nur zu 50% erreichbar (Lückenstress × Wochenendfaktor 16.2% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 4.0  |
| U-BREAKEVEN | 5 | H15 | unzulässig | 0,045 | 0,30 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 37% erreichbar (Lückenstress × Wochenendfaktor 21.5% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 4.0 |
| U-BREAKEVEN | 5 | H20 | unzulässig | 0,045 | 0,30 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 30% erreichbar (Lückenstress × Wochenendfaktor 26.9% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 4.0 |
| U-BREAKEVEN | 25 | H5 | unzulässig | 0,054 | 0,32 | 0,053 | Mindestdiversifikation: 3.0 < 8 effektive Instrumente |
| U-BREAKEVEN | 25 | H10 | unzulässig | 0,054 | 0,32 | 0,053 | Verlustbudget: Ziel-σ_p 9% nur zu 60% erreichbar (Lückenstress × Wochenendfaktor 13.3% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 3.0  |
| U-BREAKEVEN | 25 | H15 | unzulässig | 0,054 | 0,32 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 45% erreichbar (Lückenstress × Wochenendfaktor 17.8% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 3.0 |
| U-BREAKEVEN | 25 | H20 | unzulässig | 0,054 | 0,32 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 36% erreichbar (Lückenstress × Wochenendfaktor 22.2% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 3.0 |
| U-BREAKEVEN | 100 | H5 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-BREAKEVEN | 100 | H10 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-BREAKEVEN | 100 | H15 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-BREAKEVEN | 100 | H20 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-KOSTEN-TFD1-7T | 0,25 | H5 | unzulässig | 0,060 | 0,33 | 0,038 | Mindestdiversifikation: 1.0 < 8 effektive Instrumente |
| U-KOSTEN-TFD1-7T | 0,25 | H10 | unzulässig | 0,085 | 0,47 | 0,053 | Mindestdiversifikation: 1.0 < 8 effektive Instrumente |
| U-KOSTEN-TFD1-7T | 0,25 | H15 | unzulässig | 0,085 | 0,47 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 71% erreichbar (Lückenstress × Wochenendfaktor 11.3% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 1.0 |
| U-KOSTEN-TFD1-7T | 0,25 | H20 | unzulässig | 0,085 | 0,47 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 56% erreichbar (Lückenstress × Wochenendfaktor 14.2% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 1.0 |
| U-KOSTEN-TFD1-7T | 0,5 | H5 | unzulässig | 0,060 | 0,33 | 0,038 | Mindestdiversifikation: 1.0 < 8 effektive Instrumente |
| U-KOSTEN-TFD1-7T | 0,5 | H10 | unzulässig | 0,085 | 0,47 | 0,053 | Mindestdiversifikation: 1.0 < 8 effektive Instrumente |
| U-KOSTEN-TFD1-7T | 0,5 | H15 | unzulässig | 0,085 | 0,47 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 71% erreichbar (Lückenstress × Wochenendfaktor 11.3% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 1.0 |
| U-KOSTEN-TFD1-7T | 0,5 | H20 | unzulässig | 0,085 | 0,47 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 56% erreichbar (Lückenstress × Wochenendfaktor 14.2% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 1.0 |
| U-KOSTEN-TFD1-7T | 1 | H5 | unzulässig | 0,060 | 0,30 | 0,052 | Mindestdiversifikation: 2.0 < 8 effektive Instrumente |
| U-KOSTEN-TFD1-7T | 1 | H10 | unzulässig | 0,061 | 0,31 | 0,053 | Verlustbudget: Ziel-σ_p 9% nur zu 68% erreichbar (Lückenstress × Wochenendfaktor 11.7% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 2.0  |
| U-KOSTEN-TFD1-7T | 1 | H15 | unzulässig | 0,061 | 0,31 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 51% erreichbar (Lückenstress × Wochenendfaktor 15.6% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 2.0 |
| U-KOSTEN-TFD1-7T | 1 | H20 | unzulässig | 0,061 | 0,31 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 41% erreichbar (Lückenstress × Wochenendfaktor 19.6% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 2.0 |
| U-KOSTEN-TFD1-7T | 5 | H5 | unzulässig | 0,045 | 0,30 | 0,053 | Mindestdiversifikation: 4.0 < 8 effektive Instrumente |
| U-KOSTEN-TFD1-7T | 5 | H10 | unzulässig | 0,045 | 0,30 | 0,053 | Verlustbudget: Ziel-σ_p 9% nur zu 50% erreichbar (Lückenstress × Wochenendfaktor 16.2% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 4.0  |
| U-KOSTEN-TFD1-7T | 5 | H15 | unzulässig | 0,045 | 0,30 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 37% erreichbar (Lückenstress × Wochenendfaktor 21.5% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 4.0 |
| U-KOSTEN-TFD1-7T | 5 | H20 | unzulässig | 0,045 | 0,30 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 30% erreichbar (Lückenstress × Wochenendfaktor 26.9% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 4.0 |
| U-KOSTEN-TFD1-7T | 25 | H5 | unzulässig | 0,042 | 0,26 | 0,053 | Mindestdiversifikation: 7.0 < 8 effektive Instrumente |
| U-KOSTEN-TFD1-7T | 25 | H10 | unzulässig | 0,042 | 0,26 | 0,053 | Verlustbudget: Ziel-σ_p 9% nur zu 47% erreichbar (Lückenstress × Wochenendfaktor 17.1% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 7.0  |
| U-KOSTEN-TFD1-7T | 25 | H15 | unzulässig | 0,042 | 0,26 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 35% erreichbar (Lückenstress × Wochenendfaktor 22.8% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 7.0 |
| U-KOSTEN-TFD1-7T | 25 | H20 | unzulässig | 0,042 | 0,26 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 28% erreichbar (Lückenstress × Wochenendfaktor 28.4% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 7.0 |
| U-KOSTEN-TFD1-7T | 100 | H5 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-KOSTEN-TFD1-7T | 100 | H10 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-KOSTEN-TFD1-7T | 100 | H15 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-KOSTEN-TFD1-7T | 100 | H20 | unzulässig | – | – | – | Leeres Universum: kein Instrument erfüllt die Zulassung |
| U-KOSTEN-TFD1 | 0,25 | H5 | unzulässig | 0,055 | 0,48 | 0,053 | Mindestdiversifikation: 2.0 < 8 effektive Instrumente |
| U-KOSTEN-TFD1 | 0,25 | H10 | unzulässig | 0,055 | 0,48 | 0,053 | Verlustbudget: Ziel-σ_p 9% nur zu 61% erreichbar (Lückenstress × Wochenendfaktor 13.2% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 2.0  |
| U-KOSTEN-TFD1 | 0,25 | H15 | unzulässig | 0,055 | 0,48 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 46% erreichbar (Lückenstress × Wochenendfaktor 17.6% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 2.0 |
| U-KOSTEN-TFD1 | 0,25 | H20 | unzulässig | 0,055 | 0,48 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 36% erreichbar (Lückenstress × Wochenendfaktor 22.0% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 2.0 |
| U-KOSTEN-TFD1 | 0,5 | H5 | unzulässig | 0,038 | 0,65 | 0,053 | Mindestdiversifikation: 4.0 < 8 effektive Instrumente |
| U-KOSTEN-TFD1 | 0,5 | H10 | unzulässig | 0,038 | 0,65 | 0,053 | Verlustbudget: Ziel-σ_p 9% nur zu 42% erreichbar (Lückenstress × Wochenendfaktor 18.9% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 4.0  |
| U-KOSTEN-TFD1 | 0,5 | H15 | unzulässig | 0,038 | 0,65 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 32% erreichbar (Lückenstress × Wochenendfaktor 25.2% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 4.0 |
| U-KOSTEN-TFD1 | 0,5 | H20 | unzulässig | 0,038 | 0,65 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 25% erreichbar (Lückenstress × Wochenendfaktor 31.5% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 4.0 |
| U-KOSTEN-TFD1 | 1 | H5 | unzulässig | 0,038 | 0,56 | 0,053 | Mindestdiversifikation: 6.0 < 8 effektive Instrumente |
| U-KOSTEN-TFD1 | 1 | H10 | unzulässig | 0,038 | 0,56 | 0,053 | Verlustbudget: Ziel-σ_p 9% nur zu 42% erreichbar (Lückenstress × Wochenendfaktor 19.1% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 6.0  |
| U-KOSTEN-TFD1 | 1 | H15 | unzulässig | 0,038 | 0,56 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 31% erreichbar (Lückenstress × Wochenendfaktor 25.5% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 6.0 |
| U-KOSTEN-TFD1 | 1 | H20 | unzulässig | 0,038 | 0,56 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 25% erreichbar (Lückenstress × Wochenendfaktor 31.9% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 6.0 |
| U-KOSTEN-TFD1 | 5 | H5 | unzulässig | 0,025 | 0,43 | 0,053 | Verlustbudget: nach der Lückenregel nur σ_p 2.5% < Mindest-σ 3% |
| U-KOSTEN-TFD1 | 5 | H10 | unzulässig | 0,025 | 0,43 | 0,053 | Verlustbudget: Ziel-σ_p 9% nur zu 28% erreichbar (Lückenstress × Wochenendfaktor 28.3% > 8%); vom Grundprofil nicht unterscheidbar |
| U-KOSTEN-TFD1 | 5 | H15 | unzulässig | 0,025 | 0,43 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 21% erreichbar (Lückenstress × Wochenendfaktor 37.7% > 8%); vom Grundprofil nicht unterscheidbar |
| U-KOSTEN-TFD1 | 5 | H20 | unzulässig | 0,025 | 0,43 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 17% erreichbar (Lückenstress × Wochenendfaktor 47.1% > 8%); vom Grundprofil nicht unterscheidbar |
| U-KOSTEN-TFD1 | 25 | H5 | unzulässig | 0,025 | 0,70 | 0,053 | Verlustbudget: nach der Lückenregel nur σ_p 2.5% < Mindest-σ 3% |
| U-KOSTEN-TFD1 | 25 | H10 | unzulässig | 0,025 | 0,70 | 0,053 | Verlustbudget: Ziel-σ_p 9% nur zu 28% erreichbar (Lückenstress × Wochenendfaktor 28.6% > 8%); vom Grundprofil nicht unterscheidbar |
| U-KOSTEN-TFD1 | 25 | H15 | unzulässig | 0,025 | 0,70 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 21% erreichbar (Lückenstress × Wochenendfaktor 38.2% > 8%); vom Grundprofil nicht unterscheidbar |
| U-KOSTEN-TFD1 | 25 | H20 | unzulässig | 0,025 | 0,70 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 17% erreichbar (Lückenstress × Wochenendfaktor 47.7% > 8%); vom Grundprofil nicht unterscheidbar |
| U-KOSTEN-TFD1 | 100 | H5 | unzulässig | 0,026 | 0,57 | 0,053 | Verlustbudget: nach der Lückenregel nur σ_p 2.6% < Mindest-σ 3% |
| U-KOSTEN-TFD1 | 100 | H10 | unzulässig | 0,026 | 0,57 | 0,053 | Verlustbudget: Ziel-σ_p 9% nur zu 29% erreichbar (Lückenstress × Wochenendfaktor 27.6% > 8%); vom Grundprofil nicht unterscheidbar |
| U-KOSTEN-TFD1 | 100 | H15 | unzulässig | 0,026 | 0,57 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 22% erreichbar (Lückenstress × Wochenendfaktor 36.8% > 8%); vom Grundprofil nicht unterscheidbar |
| U-KOSTEN-TFD1 | 100 | H20 | unzulässig | 0,026 | 0,57 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 17% erreichbar (Lückenstress × Wochenendfaktor 46.0% > 8%); vom Grundprofil nicht unterscheidbar |
| U-ALLE | 0,25 | H5 | unzulässig | 0,037 | 0,55 | 0,053 | Mindestdiversifikation: 6.0 < 8 effektive Instrumente |
| U-ALLE | 0,25 | H10 | unzulässig | 0,037 | 0,55 | 0,053 | Verlustbudget: Ziel-σ_p 9% nur zu 41% erreichbar (Lückenstress × Wochenendfaktor 19.4% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 6.0  |
| U-ALLE | 0,25 | H15 | unzulässig | 0,037 | 0,55 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 31% erreichbar (Lückenstress × Wochenendfaktor 25.9% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 6.0 |
| U-ALLE | 0,25 | H20 | unzulässig | 0,037 | 0,55 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 25% erreichbar (Lückenstress × Wochenendfaktor 32.4% > 8%); vom Grundprofil nicht unterscheidbar; Mindestdiversifikation: 6.0 |
| U-ALLE | 0,5 | H5 | zulässig | 0,032 | 1,13 | 0,053 | – |
| U-ALLE | 0,5 | H10 | unzulässig | 0,032 | 1,13 | 0,053 | Verlustbudget: Ziel-σ_p 9% nur zu 36% erreichbar (Lückenstress × Wochenendfaktor 22.2% > 8%); vom Grundprofil nicht unterscheidbar |
| U-ALLE | 0,5 | H15 | unzulässig | 0,032 | 1,13 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 27% erreichbar (Lückenstress × Wochenendfaktor 29.5% > 8%); vom Grundprofil nicht unterscheidbar |
| U-ALLE | 0,5 | H20 | unzulässig | 0,032 | 1,13 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 22% erreichbar (Lückenstress × Wochenendfaktor 36.9% > 8%); vom Grundprofil nicht unterscheidbar |
| U-ALLE | 1 | H5 | zulässig | 0,031 | 1,01 | 0,053 | – |
| U-ALLE | 1 | H10 | unzulässig | 0,031 | 1,01 | 0,053 | Verlustbudget: Ziel-σ_p 9% nur zu 35% erreichbar (Lückenstress × Wochenendfaktor 23.1% > 8%); vom Grundprofil nicht unterscheidbar |
| U-ALLE | 1 | H15 | unzulässig | 0,031 | 1,01 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 26% erreichbar (Lückenstress × Wochenendfaktor 30.9% > 8%); vom Grundprofil nicht unterscheidbar |
| U-ALLE | 1 | H20 | unzulässig | 0,031 | 1,01 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 21% erreichbar (Lückenstress × Wochenendfaktor 38.6% > 8%); vom Grundprofil nicht unterscheidbar |
| U-ALLE | 5 | H5 | unzulässig | 0,026 | 0,77 | 0,053 | Verlustbudget: nach der Lückenregel nur σ_p 2.6% < Mindest-σ 3% |
| U-ALLE | 5 | H10 | unzulässig | 0,026 | 0,77 | 0,053 | Verlustbudget: Ziel-σ_p 9% nur zu 29% erreichbar (Lückenstress × Wochenendfaktor 27.2% > 8%); vom Grundprofil nicht unterscheidbar |
| U-ALLE | 5 | H15 | unzulässig | 0,026 | 0,77 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 22% erreichbar (Lückenstress × Wochenendfaktor 36.2% > 8%); vom Grundprofil nicht unterscheidbar |
| U-ALLE | 5 | H20 | unzulässig | 0,026 | 0,77 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 18% erreichbar (Lückenstress × Wochenendfaktor 45.3% > 8%); vom Grundprofil nicht unterscheidbar |
| U-ALLE | 25 | H5 | unzulässig | 0,025 | 0,67 | 0,053 | Verlustbudget: nach der Lückenregel nur σ_p 2.5% < Mindest-σ 3% |
| U-ALLE | 25 | H10 | unzulässig | 0,025 | 0,67 | 0,053 | Verlustbudget: Ziel-σ_p 9% nur zu 28% erreichbar (Lückenstress × Wochenendfaktor 28.6% > 8%); vom Grundprofil nicht unterscheidbar |
| U-ALLE | 25 | H15 | unzulässig | 0,025 | 0,67 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 21% erreichbar (Lückenstress × Wochenendfaktor 38.2% > 8%); vom Grundprofil nicht unterscheidbar |
| U-ALLE | 25 | H20 | unzulässig | 0,025 | 0,67 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 17% erreichbar (Lückenstress × Wochenendfaktor 47.7% > 8%); vom Grundprofil nicht unterscheidbar |
| U-ALLE | 100 | H5 | unzulässig | 0,025 | 0,67 | 0,053 | Verlustbudget: nach der Lückenregel nur σ_p 2.5% < Mindest-σ 3% |
| U-ALLE | 100 | H10 | unzulässig | 0,025 | 0,67 | 0,053 | Verlustbudget: Ziel-σ_p 9% nur zu 28% erreichbar (Lückenstress × Wochenendfaktor 28.6% > 8%); vom Grundprofil nicht unterscheidbar |
| U-ALLE | 100 | H15 | unzulässig | 0,025 | 0,67 | 0,053 | Verlustbudget: Ziel-σ_p 12% nur zu 21% erreichbar (Lückenstress × Wochenendfaktor 38.2% > 8%); vom Grundprofil nicht unterscheidbar |
| U-ALLE | 100 | H20 | unzulässig | 0,025 | 0,67 | 0,053 | Verlustbudget: Ziel-σ_p 15% nur zu 17% erreichbar (Lückenstress × Wochenendfaktor 47.7% > 8%); vom Grundprofil nicht unterscheidbar |
<!-- GEN:END tab.leverage_cells -->

## 5 Hebel über Zinsfutures (hypothetisch)

Mit forschungsfähigen Instrumenten erreicht keine Zelle ihre Hebelobergrenze (<!--v:calc:calib_research_feasible|int-->0<!--/v--> erreichbare Zellen). Die hypothetische Kalibrierung nimmt deshalb alle handelbaren Zinskontrakte ohne Kosten- und Historienfilter (U-HANDELBAR) und sucht den kleinsten Zins-Risikoanteil, mit dem das Profil seine Obergrenze bei seinem σ-Ziel erreicht:

<!-- GEN:BEGIN tab.leverage_calibration -->
| Kapital (Mio. EUR) | Profil | Zins-Risikoanteil | L_g | Lückenstress | mittlere Kosten (Sharpe/Jahr) | Verlustbudget |
|---|---|---|---|---|---|---|
| 0,25 | H5 | 41 % | 5,1× | 7,3 % | 0,512 | über Budget |
| 0,25 | H10 | 53 % | 10,2× | 12,5 % | 0,646 | über Budget |
| 0,25 | H15 | 59 % | 15,1× | 17,4 % | 0,714 | über Budget |
| 0,25 | H20 | 63 % | 20,1× | 22,2 % | 0,758 | über Budget |
| 0,5 | H5 | 41 % | 5,1× | 7,3 % | 0,512 | über Budget |
| 0,5 | H10 | 53 % | 10,2× | 12,5 % | 0,646 | über Budget |
| 0,5 | H15 | 59 % | 15,1× | 17,4 % | 0,714 | über Budget |
| 0,5 | H20 | 63 % | 20,1× | 22,2 % | 0,758 | über Budget |
| 1 | H5 | 45 % | 5,1× | 7,3 % | 0,492 | über Budget |
| 1 | H10 | 58 % | 10,1× | 12,2 % | 0,618 | über Budget |
| 1 | H15 | 65 % | 15,0× | 16,9 % | 0,687 | über Budget |
| 1 | H20 | 71 % | 20,1× | 21,4 % | 0,745 | über Budget |
| 5 | H5 | 37 % | 5,0× | 8,6 % | 0,396 | über Budget |
| 5 | H10 | 50 % | 10,0× | 13,8 % | 0,527 | über Budget |
| 5 | H15 | 59 % | 15,2× | 18,7 % | 0,617 | über Budget |
| 5 | H20 | 65 % | 20,1× | 23,2 % | 0,677 | über Budget |
| 25 | H5 | 45 % | 5,1× | 7,3 % | 0,476 | über Budget |
| 25 | H10 | 58 % | 10,1× | 12,2 % | 0,606 | über Budget |
| 25 | H15 | 65 % | 15,0× | 16,9 % | 0,676 | über Budget |
| 25 | H20 | 71 % | 20,1× | 21,4 % | 0,736 | über Budget |
| 100 | H5 | – | – | – | – | kein Basis- oder Zinsuniversum |
| 100 | H10 | – | – | – | – | kein Basis- oder Zinsuniversum |
| 100 | H15 | – | – | – | – | kein Basis- oder Zinsuniversum |
| 100 | H20 | – | – | – | – | kein Basis- oder Zinsuniversum |
<!-- GEN:END tab.leverage_calibration -->

Befund: In der Referenzstufe braucht H10 <!--v:calc:rate_share_H10|pct0-->50 %<!--/v--> und H20 <!--v:calc:rate_share_H20|pct0-->65 %<!--/v--> des Risikos in Zinsen; der Lückenstress liegt dann bei <!--v:calc:gap_H10|pct0-->14 %<!--/v--> bzw. <!--v:calc:gap_H20|pct0-->23 %<!--/v--> und damit über dem Budget. Die Kosten dieser Allokationen bei der geforderten Haltedauer übersteigen jede plausible Bruttokante. Diese Allokation heißt in Stress- und Kelly-Rechnung WUNSCHHEBEL; sie zeigt die Folgen eines erzwungenen Hebels (§7.3) und ist keine Option.

## 6 Kelly, Drawdowns und Ruin

`risk/kelly_ruin_simulator.py` simuliert <!--v:param:P-SIM-PATHS|int-->1.000<!--/v--> Pfade über <!--v:kelly:years|d0-->5<!--/v--> Jahre je Allokation und Profil: tägliche Renditen mit t(<!--v:param:P-SIM-T-DF|d0-->4<!--/v-->)-Innovationen, Volatilitätsregimen (P-SIM-REGIME), Sprüngen (P-SIM-JUMPS-PER-YEAR, P-SIM-JUMP-SIZE) und Ereignissen jenseits der Konstruktion (P-SIM-BEYOND-PER-YEAR, P-SIM-BEYOND-SIZE); die Drift ist um den Erwartungswert der Sprünge korrigiert, die Diffusionsvolatilität entsprechend verkleinert, höchstens bis auf <!--v:param:P-SIM-DIFF-VAR-FLOOR|pct0-->25 %<!--/v--> der Gesamtvarianz (P-SIM-DIFF-VAR-FLOOR). Die Netto-Sharpe-Ratio wird je Pfad aus dem Prior gezogen. Tagesverlust- und Drawdown-Leiter wirken im Pfad mit denselben Faktoren wie im Stressmotor (P-RISK-LADDER-FACTORS, am Folgetag); L3 baut innerhalb des Tages ab und kostet dabei zusätzlich <!--v:param:P-RISK-L3-SLIPPAGE|pct1-->0,5 %<!--/v--> (P-RISK-L3-SLIPPAGE), Lücken ab Konstruktionsgröße werden nicht gekappt; Ruin ist ein Verlust von <!--v:param:P-RISK-RUIN|pct0-->50 %<!--/v--> oder eine Zwangsliquidation.

<!-- GEN:BEGIN tab.params:P-SIM -->
| ID | Bedeutung | Wert | Einheit | Status |
|---|---|---|---|---|
| P-SIM-T-DF | Freiheitsgrade der t-Verteilung (fette Ränder) | 4 | Anzahl | ANNAHME |
| P-SIM-REGIME | Volatilitätsregime: Eintritt, Austritt (je Tag), Volatilitätsfaktor im Stress (Korrelationsschock) | enter: 0,01; exit: 0,05; vol_multiple: 2 | Wahrscheinlichkeit/Faktor | ANNAHME |
| P-SIM-JUMPS-PER-YEAR | Häufigkeit ungünstiger Kurslücken innerhalb der Konstruktionslücke | 1 | je Jahr | ANNAHME |
| P-SIM-JUMP-SIZE | Größe dieser Lücken als Anteil der Konstruktionslücke (gleichverteilt) | [0,05; 0,40] | Anteil | ANNAHME |
| P-SIM-BEYOND-PER-YEAR | Häufigkeit von Lücken jenseits der Konstruktionslücke | 0,02 | je Jahr | ANNAHME |
| P-SIM-BEYOND-SIZE | Größe dieser Lücken als Vielfaches der Konstruktionslücke (gleichverteilt) | [1; 2] | Faktor | ANNAHME |
| P-SIM-PATHS | Pfade je Variante | 1.000 | Anzahl | ENTWURF |
| P-SIM-DIFF-VAR-FLOOR | Untergrenze des Diffusionsanteils an der Gesamtvarianz, wenn Sprünge modelliert sind | 0,25 | Anteil | ENTWURF |
<!-- GEN:END tab.params:P-SIM -->

<!-- GEN:BEGIN tab.kelly -->
| Profil | Allokation | σ_p | E[Netto-Sharpe] | Jahresrendite Median | max. Drawdown 5 J (95 %) | P(DD ≥ 20 %) | P(Ruin 5 J) | P(Tag > 9 %) je Jahr |
|---|---|---|---|---|---|---|---|---|
| H5 | SYSTEM | 4,5 % | 0,096 | 0,5 % | 17,5 % | 0,7 % | 0,00 % | 0,66 % |
| H5 | WUNSCHHEBEL | 6,0 % | -0,527 | -3,5 % | 23,9 % | 33,4 % | 0,00 % | 1,44 % |
| H5 | ALTERNATIVE_TFD1 | 2,5 % | 0,478 | 1,4 % | 9,8 % | 0,0 % | 0,00 % | 0,42 % |
| H5 | SYSTEM_OHNE_LEITER | 4,5 % | 0,096 | 0,7 % | 18,7 % | 3,3 % | 0,00 % | 0,66 % |
| H10 | SYSTEM | wie H5/SYSTEM |  |  |  |  |  |  |
| H10 | WUNSCHHEBEL | 9,0 % | -0,764 | -6,7 % | 30,0 % | 84,3 % | 0,00 % | 0,84 % |
| H10 | ALTERNATIVE_TFD1 | wie H5/ALTERNATIVE_TFD1 |  |  |  |  |  |  |
| H15 | SYSTEM | wie H5/SYSTEM |  |  |  |  |  |  |
| H15 | WUNSCHHEBEL | 12,0 % | -0,898 | -10,4 % | 30,4 % | 97,5 % | 0,00 % | 0,56 % |
| H15 | ALTERNATIVE_TFD1 | wie H5/ALTERNATIVE_TFD1 |  |  |  |  |  |  |
| H20 | SYSTEM | wie H5/SYSTEM |  |  |  |  |  |  |
| H20 | WUNSCHHEBEL | 15,0 % | -0,972 | -12,4 % | 30,8 % | 99,8 % | 0,00 % | 0,34 % |
| H20 | ALTERNATIVE_TFD1 | wie H5/ALTERNATIVE_TFD1 |  |  |  |  |  |  |
<!-- GEN:END tab.kelly -->

<!-- GEN:BEGIN tab.kelly_dd -->
| Profil | Allokation | max. DD 1 J (Median / 95 %) | 3 J | 5 J | P(DD ≥ 10 %) | P(DD ≥ 20 %) | P(DD ≥ 30 %) | P(DD ≥ 50 %) | Erholung Median (Handelstage) | P(Handelsstopp 5 J) | ES 97,5 % Jahresrendite |
|---|---|---|---|---|---|---|---|---|---|---|---|
| H5 | SYSTEM | 4,2 / 9,4 % | 7,5 / 14,5 % | 9,9 / 17,5 % | 49,6 % | 0,7 % | 0,0 % | 0,0 % | 238 | 0,0 % | -9,8 % |
| H5 | WUNSCHHEBEL | 7,2 / 13,8 % | 14,2 / 21,3 % | 18,3 / 23,9 % | 95,4 % | 33,4 % | 0,1 % | 0,0 % | 283 | 0,1 % | -17,4 % |
| H5 | ALTERNATIVE_TFD1 | 1,9 / 4,4 % | 3,3 / 7,8 % | 3,9 / 9,8 % | 4,6 % | 0,0 % | 0,0 % | 0,0 % | 195 | 0,0 % | -6,0 % |
| H5 | SYSTEM_OHNE_LEITER | 4,0 / 9,2 % | 7,3 / 15,1 % | 9,4 / 18,7 % | 46,2 % | 3,3 % | 0,0 % | 0,0 % | 222 | 0,0 % | -11,1 % |
| H10 | WUNSCHHEBEL | 11,0 / 18,2 % | 20,1 / 25,6 % | 23,4 / 30,0 % | 99,9 % | 84,3 % | 5,2 % | 0,0 % | 312 | 5,2 % | -23,3 % |
| H15 | WUNSCHHEBEL | 14,9 / 22,2 % | 23,2 / 29,6 % | 27,5 / 30,4 % | 100,0 % | 97,5 % | 25,9 % | 0,0 % | 206 | 25,9 % | -28,6 % |
| H20 | WUNSCHHEBEL | 17,2 / 23,4 % | 25,6 / 30,2 % | 30,0 / 30,8 % | 100,0 % | 99,8 % | 58,1 % | 0,0 % | 485 | 58,1 % | -28,7 % |
<!-- GEN:END tab.kelly_dd -->

Die Zeile SYSTEM_OHNE_LEITER zeigt die Wirkung der Leitern: Ohne sie steigt die Wahrscheinlichkeit, in <!--v:kelly:years|d0-->5<!--/v--> Jahren zeitweise mindestens ein Fünftel des Kapitals zu verlieren, von <!--v:kelly:results/H5/SYSTEM/p_drawdown_ge/20|pct1-->0,7 %<!--/v--> auf <!--v:kelly:results/H5/SYSTEM_OHNE_LEITER/p_drawdown_ge/20|pct1-->3,3 %<!--/v-->. Die Restwahrscheinlichkeit, die Tagesgrenze an einem Tag zu überschreiten, liegt für die registrierte Allokation bei <!--v:kelly:results/H5/SYSTEM/p_day_loss_over_cap_per_year|pct1-->0,7 %<!--/v--> je Jahr; sie stammt aus Ereignissen jenseits der Konstruktion und ist der Grund für X-OP-DLC-MODE.

## 7 Kurslücken und Margin-Pfade in der Referenzstufe

<!-- GEN:BEGIN tab.gaps -->
| Variante | Profil | σ_p erreicht | L_g | Lücke historisch | Lücke 5 σ | Lücke 10 σ | Konstruktionslücke | M/E Basis / +50 % / +100 % | zulässig |
|---|---|---|---|---|---|---|---|---|---|
| U-KOSTEN | H5 | 5,7 % | 0,33× | 5,0 % | 2,5 % | 5,0 % | 5,3 % | 2,5 / 3,7 / 4,9 % | nein |
| U-KOSTEN | H10 | 5,7 % | 0,33× | 5,0 % | 2,5 % | 5,0 % | 5,3 % | 2,5 / 3,7 / 4,9 % | nein |
| U-KOSTEN | H15 | 5,7 % | 0,33× | 5,0 % | 2,5 % | 5,0 % | 5,3 % | 2,5 / 3,7 / 4,9 % | nein |
| U-KOSTEN | H20 | 5,7 % | 0,33× | 5,0 % | 2,5 % | 5,0 % | 5,3 % | 2,5 / 3,7 / 4,9 % | nein |
| U-BREAKEVEN | H5 | 4,5 % | 0,30× | 5,1 % | 2,4 % | 4,9 % | 5,3 % | 2,3 / 3,4 / 4,5 % | nein |
| U-BREAKEVEN | H10 | 4,5 % | 0,30× | 5,1 % | 2,4 % | 4,9 % | 5,3 % | 2,3 / 3,4 / 4,5 % | nein |
| U-BREAKEVEN | H15 | 4,5 % | 0,30× | 5,1 % | 2,4 % | 4,9 % | 5,3 % | 2,3 / 3,4 / 4,5 % | nein |
| U-BREAKEVEN | H20 | 4,5 % | 0,30× | 5,1 % | 2,4 % | 4,9 % | 5,3 % | 2,3 / 3,4 / 4,5 % | nein |
| U-KOSTEN-TFD1-7T | H5 | 4,5 % | 0,30× | 5,1 % | 2,4 % | 4,9 % | 5,3 % | 2,3 / 3,4 / 4,5 % | nein |
| U-KOSTEN-TFD1-7T | H10 | 4,5 % | 0,30× | 5,1 % | 2,4 % | 4,9 % | 5,3 % | 2,3 / 3,4 / 4,5 % | nein |
| U-KOSTEN-TFD1-7T | H15 | 4,5 % | 0,30× | 5,1 % | 2,4 % | 4,9 % | 5,3 % | 2,3 / 3,4 / 4,5 % | nein |
| U-KOSTEN-TFD1-7T | H20 | 4,5 % | 0,30× | 5,1 % | 2,4 % | 4,9 % | 5,3 % | 2,3 / 3,4 / 4,5 % | nein |
| U-KOSTEN-TFD1 | H5 | 2,5 % | 0,43× | 4,2 % | 2,2 % | 4,3 % | 5,3 % | 1,8 / 2,8 / 3,7 % | nein |
| U-KOSTEN-TFD1 | H10 | 2,5 % | 0,43× | 4,2 % | 2,2 % | 4,3 % | 5,3 % | 1,8 / 2,8 / 3,7 % | nein |
| U-KOSTEN-TFD1 | H15 | 2,5 % | 0,43× | 4,2 % | 2,2 % | 4,3 % | 5,3 % | 1,8 / 2,8 / 3,7 % | nein |
| U-KOSTEN-TFD1 | H20 | 2,5 % | 0,43× | 4,2 % | 2,2 % | 4,3 % | 5,3 % | 1,8 / 2,8 / 3,7 % | nein |
<!-- GEN:END tab.gaps -->

## 8 Modellrisiko

MOD-LEV, MOD-KELLY und MOD-STRESS sind im Modellinventar geführt (`registers/model_inventory.json`). Hauptschwächen: Korrelationen als Klassenannahmen (RK-07), Volatilitäten und Margins als Planungswerte, Lücken aus wenigen historischen Ereignissen, Sprünge und Regime als Annahmen (P-SIM-*). Jede dieser Größen wird in G2 gemessen oder in G3 geschätzt; die Profilzulässigkeit wird danach neu gerechnet.
