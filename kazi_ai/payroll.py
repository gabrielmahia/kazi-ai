"""
KaziAI Payroll Calculator: Kenya statutory deductions, as of February 2026 (NSSF Year 4).

Rates were updated on 2026-10-04 from consistent secondary sources (law-firm and payroll-provider summaries, including DLA Piper and FNJ & Associates);
they were NOT checked against the primary KRA, NSSF or SHA publications. Verify before relying on any figure.
  - NSSF: 6% employee + 6% employer on pensionable pay between KES 0 and 108,000 (Tier I up to 9,000, Tier II from 9,000 to 108,000).
  - SHIF (replaced NHIF in October 2024): 2.75% of gross, minimum KES 300, no cap, employee only.
  - Affordable Housing Levy: 1.5% of gross from the employee and 1.5% from the employer.
  - NSSF, SHIF and the Housing Levy reduce taxable income before PAYE.
  - PAYE bands and the KES 2,400 personal relief were carried over unchanged and were NOT re-checked in this update.
"""
from dataclasses import dataclass
from typing import ClassVar


@dataclass
class PayrollResult:
    gross_salary:      float
    nssf_employee:     float
    nssf_employer:     float
    shif_employee:     float
    ahl_employee:      float
    ahl_employer:      float
    taxable_income:    float
    paye:              float
    net_pay:           float
    employer_cost:     float
    period:            str = ""

    def __str__(self):
        return (
            f"Payroll: {self.period}\n"
            f"  Gross salary:      KES {self.gross_salary:>10,.0f}\n"
            f"  NSSF (employee):   KES {self.nssf_employee:>10,.0f}\n"
            f"  SHIF:              KES {self.shif_employee:>10,.0f}\n"
            f"  Housing levy:      KES {self.ahl_employee:>10,.0f}\n"
            f"  PAYE:              KES {self.paye:>10,.0f}\n"
            f"  ──────────────────────────────\n"
            f"  Net pay:           KES {self.net_pay:>10,.0f}\n"
            f"  Employer NSSF:     KES {self.nssf_employer:>10,.0f}\n"
            f"  Employer housing:  KES {self.ahl_employer:>10,.0f}\n"
            f"  Total employer cost: KES {self.employer_cost:>8,.0f}\n"
        )


class PayrollCalculator:
    """
    Kenya payroll calculator: NSSF, SHIF, Affordable Housing Levy and PAYE.
    See the module docstring for the rates, their sources and what was not re-checked.
    """

    # NSSF Year 4 (from 1 February 2026): 6% each side on pensionable pay up to the upper earnings limit.
    NSSF_LOWER_LIMIT   = 9_000     # Tier I ceiling
    NSSF_UPPER_LIMIT   = 108_000   # Tier II ceiling
    NSSF_TIER_I_RATE   = 0.06
    NSSF_TIER_II_RATE  = 0.06

    # SHIF replaced NHIF in October 2024: flat share of gross, with a floor and no cap; employee only.
    SHIF_RATE    = 0.0275
    SHIF_MINIMUM = 300

    # Affordable Housing Levy: 1.5% of gross, matched by the employer.
    AHL_RATE          = 0.015
    AHL_EMPLOYER_RATE = 0.015

    # KRA PAYE bands (monthly), carried over unchanged and not re-checked in the 2026-10-04 update.
    PAYE_BANDS: ClassVar[list[tuple[float, float]]] = [
        (24_000,  0.10),
        (32_333,  0.25),
        (500_000, 0.30),
        (800_000, 0.325),
        (float("inf"), 0.35),
    ]
    PERSONAL_RELIEF = 2_400  # monthly personal relief

    def _nssf(self, gross: float) -> tuple[float, float]:
        """Returns (employee_contribution, employer_contribution)."""
        tier1 = min(gross, self.NSSF_LOWER_LIMIT) * self.NSSF_TIER_I_RATE
        tier2 = 0.0
        if gross > self.NSSF_LOWER_LIMIT:
            tier2_base = min(gross, self.NSSF_UPPER_LIMIT) - self.NSSF_LOWER_LIMIT
            tier2 = tier2_base * self.NSSF_TIER_II_RATE
        employee = round(tier1 + tier2, 2)
        return employee, employee  # employer matches employee

    def _shif(self, gross: float) -> float:
        return max(float(self.SHIF_MINIMUM), round(gross * self.SHIF_RATE, 2))

    def _paye(self, taxable: float) -> float:
        tax = 0.0
        prev = 0.0
        for ceiling, rate in self.PAYE_BANDS:
            band = min(taxable, ceiling) - prev
            if band <= 0:
                break
            tax += band * rate
            prev = ceiling
            if taxable <= ceiling:
                break
        return max(0.0, round(tax - self.PERSONAL_RELIEF, 2))

    def calculate(self, gross_salary: float, period: str = "") -> PayrollResult:
        """Calculate full payroll deductions for a Kenya employee."""
        nssf_ee, nssf_er = self._nssf(gross_salary)
        shif_ee          = self._shif(gross_salary)
        ahl_ee           = round(gross_salary * self.AHL_RATE, 2)
        ahl_er           = round(gross_salary * self.AHL_EMPLOYER_RATE, 2)
        taxable_income   = max(0, round(gross_salary - nssf_ee - shif_ee - ahl_ee, 2))
        paye             = self._paye(taxable_income)
        net_pay          = round(gross_salary - nssf_ee - shif_ee - ahl_ee - paye, 2)
        employer_cost    = round(gross_salary + nssf_er + ahl_er, 2)
        return PayrollResult(
            gross_salary=gross_salary,
            nssf_employee=nssf_ee,
            nssf_employer=nssf_er,
            shif_employee=shif_ee,
            ahl_employee=ahl_ee,
            ahl_employer=ahl_er,
            taxable_income=taxable_income,
            paye=paye,
            net_pay=net_pay,
            employer_cost=employer_cost,
            period=period,
        )
