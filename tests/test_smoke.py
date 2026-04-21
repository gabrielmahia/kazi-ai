"""Smoke tests — KaziAI payroll calculator."""
from kazi_ai.payroll import PayrollCalculator

def test_basic_payroll():
    r = PayrollCalculator().calculate(85000, "2026-04")
    assert r.gross_salary == 85000
    assert r.net_pay > 0
    assert r.net_pay < 85000
    assert r.nssf_employee > 0
    assert r.nhif_employee > 0
    assert r.paye >= 0

def test_low_salary():
    r = PayrollCalculator().calculate(15000)
    assert r.net_pay > 0

def test_employer_cost_includes_nssf():
    r = PayrollCalculator().calculate(50000)
    assert r.employer_cost > r.gross_salary
