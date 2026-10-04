# ⚖️ KaziAI — Kenya HR Compliance AI

> AI-powered HR compliance for Kenya SMEs and NGOs. Employment Act 2007, NSSF, SHIF, the Housing Levy, KRA PAYE calculations, contract generation, and payroll tax — in plain language.

[![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live-red)](https://kaziniai.streamlit.app)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)

## What it does

Every SME in Kenya faces the same compliance minefield: Employment Act requirements, NSSF contributions, SHIF deductions, KRA PAYE calculations, and statutory leave entitlements. KaziAI makes this navigable.

| Tool | What it does |
|------|-------------|
| 📄 **Contract generator** | Employment contracts aligned with Employment Act 2007 |
| 💰 **Payroll calculator** | NSSF + SHIF + Housing Levy + PAYE (rates as of Feb 2026 from secondary sources; verify before use) |
| ❓ **HR Q&A** | Plain-language answers to Kenya employment law questions |
| 🗓️ **Leave tracker** | Annual, sick, maternity, paternity, compassionate leave |
| ⚠️ **Compliance checker** | Audit your HR practices against Employment Act requirements |

## Payroll calculation (KES)

```python
from kazi_ai import PayrollCalculator

calc = PayrollCalculator()
result = calc.calculate(gross_salary=85000, period="2026-04")

print(result)
# Payroll: 2026-04
#   Gross salary:      KES     85,000
#   NSSF (employee):   KES      5,100
#   SHIF:              KES      2,338
#   Housing levy:      KES      1,275
#   PAYE:              KES     15,270
#   ──────────────────────────────
#   Net pay:           KES     61,018
#   Employer NSSF:     KES      5,100
#   Employer housing:  KES      1,275
#   Total employer cost: KES   91,375
```

## Contract generation

Contract generation is part of the Streamlit app (the Contract tab, which uses an LLM); it is not a Python API in this package. The package exports `PayrollCalculator` and `PayrollResult`.

## Live app

🌐 [kazi-ai.streamlit.app](https://kaziniai.streamlit.app) — calculate payroll, check compliance, generate contracts.

## Disclaimer

**KaziAI is a decision-support tool, not a law firm.** Statutory rates were last updated on 2026-10-04 from secondary sources (see `kazi_ai/payroll.py` for what was and was not re-checked) and are not updated automatically. Always verify with a qualified HR practitioner or lawyer for specific employment disputes.

## Related

- [TumaPesa](https://kaziniai.streamlit.app) — Diaspora remittance tool
- [mpesa-mcp](https://github.com/gabrielmahia/mpesa-mcp) — M-Pesa MCP server
- [gabrielmahia.github.io](https://gabrielmahia.github.io) — Full portfolio

## IP & Collaboration

© 2026 Gabriel Mahia · [contact@aikungfu.dev](mailto:contact@aikungfu.dev)
License: CC BY-NC-ND 4.0
Not affiliated with KRA, NSSF, SHA, or the Government of Kenya.
