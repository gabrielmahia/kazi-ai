"""Payroll tests with hand-computed expectations (arithmetic checks of the implemented rules, NOT legal advice).

The previous tests asserted only `> 0`, so a repealed scheme (NHIF) and out-of-date NSSF limits passed for months.
Rules under test (see kazi_ai/payroll.py for sources and what was not re-checked): NSSF 6% each side on pay up to KES 108,000 (Tier I up to 9,000);
SHIF 2.75% of gross, minimum KES 300; Housing Levy 1.5% each side; NSSF + SHIF + levy reduce taxable income; PAYE bands and KES 2,400 relief unchanged."""
from pathlib import Path

import pytest

from kazi_ai.payroll import PayrollCalculator

CASES = [  # gross, nssf, shif, ahl, taxable, paye, net, employer_cost
    (5_000,   300.0,  300.0,   75.0,   4_325.0,      0.0,   4_325.0,   5_375.0),   # below the NSSF lower limit; SHIF minimum applies
    (20_000, 1_200.0, 550.0,  300.0,  17_950.0,      0.0,  17_950.0,  21_500.0),   # PAYE wiped out by the personal relief
    (100_000, 6_000.0, 2_750.0, 1_500.0, 89_750.0, 19_308.35, 70_441.65, 107_500.0),
    (200_000, 6_480.0, 5_500.0, 3_000.0, 185_020.0, 47_889.35, 137_130.65, 209_480.0),  # above the NSSF upper limit: contribution capped
]


@pytest.mark.parametrize("gross,nssf,shif,ahl,taxable,paye,net,cost", CASES)
def test_hand_computed_cases(gross, nssf, shif, ahl, taxable, paye, net, cost):
    r = PayrollCalculator().calculate(gross, "2026-10")
    assert (r.nssf_employee, r.nssf_employer) == (nssf, nssf)
    assert (r.shif_employee, r.ahl_employee, r.ahl_employer) == (shif, ahl, ahl)
    assert (r.taxable_income, r.paye, r.net_pay, r.employer_cost) == (taxable, paye, net, cost)


def test_nssf_is_capped_at_the_upper_earnings_limit():
    c = PayrollCalculator()
    assert c.calculate(108_000).nssf_employee == c.calculate(500_000).nssf_employee == 6_480.0


def test_shif_has_a_floor_and_no_cap():
    c = PayrollCalculator()
    assert c.calculate(1_000).shif_employee == 300.0
    assert c.calculate(1_000_000).shif_employee == 27_500.0


def test_the_repealed_scheme_is_gone():
    r = PayrollCalculator().calculate(50_000)
    assert not hasattr(r, "nhif_employee") and not hasattr(PayrollCalculator, "NHIF_SCHEDULE")


def test_deductions_reduce_taxable_income():
    r = PayrollCalculator().calculate(100_000)
    assert r.taxable_income == r.gross_salary - r.nssf_employee - r.shif_employee - r.ahl_employee


def test_readme_example_matches_the_code():
    readme = (Path(__file__).resolve().parents[1] / "README.md").read_text(encoding="utf-8")
    for line in str(PayrollCalculator().calculate(85_000, "2026-04")).rstrip("\n").splitlines():
        assert "# " + line in readme, f"README example is stale: {line!r}"
