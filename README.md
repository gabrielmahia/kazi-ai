# ⚖️ KaziAI — Kenya HR Compliance AI

> AI-powered HR compliance for Kenya SMEs and NGOs. Employment Act 2007, NSSF, NHIF, KRA PAYE calculations, contract generation, and payroll tax — in plain language.

[![License: CC BY-NC-ND 4.0](https://img.shields.io/badge/License-CC%20BY--NC--ND%204.0-lightgrey.svg)](LICENSE)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live-red)](https://kazi-ai.streamlit.app)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)

## What it does

Every SME in Kenya faces the same compliance minefield: Employment Act requirements, NSSF contributions, NHIF deductions, KRA PAYE calculations, and statutory leave entitlements. KaziAI makes this navigable.

| Tool | What it does |
|------|-------------|
| 📄 **Contract generator** | Employment contracts aligned with Employment Act 2007 |
| 💰 **Payroll calculator** | NSSF + NHIF + PAYE deductions — net pay to the cent |
| ❓ **HR Q&A** | Plain-language answers to Kenya employment law questions |
| 🗓️ **Leave tracker** | Annual, sick, maternity, paternity, compassionate leave |
| ⚠️ **Compliance checker** | Audit your HR practices against Employment Act requirements |

## Payroll calculation (KES)

```python
from kazi_ai import PayrollCalculator

calc = PayrollCalculator()
result = calc.calculate(gross_salary=85000, period="2026-04")

print(result)
# GrossSalary:   KES 85,000
# NSSF:          KES 2,160  (employer KES 2,160)
# NHIF:          KES 1,700
# Taxable income:KES 81,140
# PAYE:          KES 16,397
# Net Pay:       KES 64,743
# Employer cost: KES 87,160
```

## Contract generation

```python
from kazi_ai import ContractGenerator

contract = ContractGenerator().generate(
    employee_name="Jane Akinyi",
    job_title="Software Engineer",
    gross_salary=120000,
    start_date="2026-05-01",
    contract_type="permanent",
)
print(contract)  # Full Employment Act-compliant contract text
```

## Live app

🌐 [kazi-ai.streamlit.app](https://kazi-ai.streamlit.app) — calculate payroll, check compliance, generate contracts.

## Disclaimer

**KaziAI is a decision-support tool, not a law firm.** Statutory rates are updated as published by KRA, NSSF, and NHIF. Always verify with a qualified HR practitioner or lawyer for specific employment disputes.

## Related

- [TumaPesa](https://tumapesa.streamlit.app) — Diaspora remittance tool
- [mpesa-mcp](https://github.com/gabrielmahia/mpesa-mcp) — M-Pesa MCP server
- [gabrielmahia.github.io](https://gabrielmahia.github.io) — Full portfolio

## IP & Collaboration

© 2026 Gabriel Mahia · [contact@aikungfu.dev](mailto:contact@aikungfu.dev)
License: CC BY-NC-ND 4.0
Not affiliated with KRA, NSSF, NHIF, or the Government of Kenya.
