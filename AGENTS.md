# AGENTS.md — KaziAI

Kenya HR compliance AI.

## Files
- `kazi_ai/payroll.py` — PayrollCalculator (NSSF/SHIF/AHL/PAYE)
- `app.py` — Streamlit app (payroll, Q&A, contract generator)

## Rules
- Always cite Employment Act section
- Always add compliance disclaimer
- Rates: NSSF Year 4 (Feb 2026), SHIF 2.75%, AHL 1.5% each side, PAYE bands carried over (see payroll.py for sources and what was not re-checked)
- Not a law firm — always recommend professional advice

<!-- coverage-adaptive-reasoning:v2 -->

## Coverage-Adaptive Reasoning v2

For consequential research, recommendations, investigations, analogy searches, forecasting, opportunity discovery, and canon building:

- A correct ranking inside an incomplete universe is still a failed answer.
- Separate candidate generation from candidate ranking.
- Materiality-gate the search: use the minimum useful set of orthogonal retrieval routes that could change the answer.
- Before closure ask what correct answer the current search method would be structurally incapable of finding.
- Treat aliases, language/geography, era, source class, format, genealogy, taxonomy, legal identity vs operational control/economic benefit, intermediaries, schema categories, null/failure cases, and negative space as potential blind spots when material.
- Maintain leading + competing + null explanations.
- Distinguish answer confidence from coverage confidence.
- “Nothing found” is not evidence of absence when coverage is low.
- Stop when additional independent search routes no longer materially change the candidate universe, hypotheses, decision, or next test.
- When an important miss occurs, repair the retrieval architecture via MISS → SENSOR REDESIGN; do not merely append the missed example.

<!-- v2 section appended 2026-10-28 from https://github.com/gabrielmahia/nairobi-stack/blob/main/docs/COVERAGE_ADAPTIVE_REASONING.md; the rest of this file is unchanged. -->
