# KI-Richtlinie

1. KI-Agenten arbeiten außerhalb des Geldpfads, ohne Brokerzugang, ohne Freigaberechte und ohne Zugriff auf den Holdout (§11.2).
2. Sprachmodelle erzeugen keine Orders und keine Größen; ML-Modelle nur nach `ai/mrm_policy.md`.
3. Updates, Skills und Modellwechsel nur nach bestandener Evaluationssuite (`ai/eval_suite_spec.md`).
4. An Modellanbieter gehen keine personenbezogenen Daten, keine Secrets und keine lizenzierten Rohdaten; Prüfung am LLM-Gateway.
5. Quartalsweise Nutzenbilanz; Rückbau auf H0 nach <!--v:param:P-AI-ROLLBACK-QUARTERS|d0-->2<!--/v--> negativen Quartalen in Folge.
6. Harte Monatsgrenze für KI-Kosten: <!--v:param:P-AI-MONTHLY-BUDGET-EUR|eur-->350 EUR<!--/v--> (P-AI-MONTHLY-BUDGET-EUR).
7. Ausgaben des Agenten sind Vorschläge; Zahlen in Berichten tragen Registerverweise; Hypothesen werden als solche gekennzeichnet.
