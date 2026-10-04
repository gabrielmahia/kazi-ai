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
