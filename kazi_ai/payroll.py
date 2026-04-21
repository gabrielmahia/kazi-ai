"""
KaziAI Payroll Calculator — Kenya statutory deductions 2026.
Rates: NSSF (Tier I + II), NHIF (2024 Finance Act schedule), KRA PAYE.
"""
from dataclasses import dataclass


@dataclass
class PayrollResult:
    gross_salary:      float
    nssf_employee:     float
    nssf_employer:     float
    nhif_employee:     float
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
            f"  NHIF:              KES {self.nhif_employee:>10,.0f}\n"
            f"  PAYE:              KES {self.paye:>10,.0f}\n"
            f"  ──────────────────────────────\n"
            f"  Net pay:           KES {self.net_pay:>10,.0f}\n"
            f"  Employer NSSF:     KES {self.nssf_employer:>10,.0f}\n"
            f"  Total employer cost: KES {self.employer_cost:>8,.0f}\n"
        )


class PayrollCalculator:
    """
    Kenya payroll calculator — NSSF, NHIF, PAYE 2026.
    Sources: NSSF Act 2013 (Tier I/II), NHIF 2024 schedule, KRA tax bands FY2025/26.
    """

    # NSSF 2024 rates (post-Supreme Court ruling — Tier I + Tier II)
    NSSF_LOWER_LIMIT   = 7_000    # Tier I ceiling
    NSSF_UPPER_LIMIT   = 36_000   # Tier II ceiling
    NSSF_TIER_I_RATE   = 0.06     # 6% up to KES 7,000
    NSSF_TIER_II_RATE  = 0.06     # 6% on KES 7,001–36,000

    # NHIF 2024 scale (Finance Act)
    NHIF_SCHEDULE = [
        (5_999,   150),  (7_999,   300),  (11_999,  400),  (14_999,  500),
        (19_999,  600),  (24_999,  750),  (29_999,  850),  (34_999,  900),
        (39_999, 950),   (44_999, 1_000), (49_999, 1_100), (59_999, 1_200),
        (69_999, 1_300), (79_999, 1_400), (89_999, 1_500), (99_999, 1_600),
        (float("inf"), 1_700),
    ]

    # KRA PAYE bands FY2025/26 (monthly)
    PAYE_BANDS = [
        (24_000,  0.10),
        (32_333,  0.25),
        (500_000, 0.30),
        (800_000, 0.325),
        (float("inf"), 0.35),
    ]
    PERSONAL_RELIEF = 2_400  # monthly personal relief
    AHL_RATE        = 0.015  # Affordable Housing Levy 1.5%

    def _nssf(self, gross: float) -> tuple[float, float]:
        """Returns (employee_contribution, employer_contribution)."""
        tier1 = min(gross, self.NSSF_LOWER_LIMIT) * self.NSSF_TIER_I_RATE
        tier2 = 0.0
        if gross > self.NSSF_LOWER_LIMIT:
            tier2_base = min(gross, self.NSSF_UPPER_LIMIT) - self.NSSF_LOWER_LIMIT
            tier2 = tier2_base * self.NSSF_TIER_II_RATE
        employee = round(tier1 + tier2, 2)
        return employee, employee  # employer matches employee

    def _nhif(self, gross: float) -> float:
        for ceiling, amount in self.NHIF_SCHEDULE:
            if gross <= ceiling:
                return float(amount)
        return 1_700.0

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
        nhif_ee          = self._nhif(gross_salary)
        ahl               = round(gross_salary * self.AHL_RATE, 2)
        taxable_income   = max(0, gross_salary - nssf_ee)
        paye             = self._paye(taxable_income)
        net_pay          = round(gross_salary - nssf_ee - nhif_ee - paye - ahl, 2)
        employer_cost    = round(gross_salary + nssf_er, 2)
        return PayrollResult(
            gross_salary=gross_salary,
            nssf_employee=nssf_ee,
            nssf_employer=nssf_er,
            nhif_employee=nhif_ee,
            taxable_income=taxable_income,
            paye=paye,
            net_pay=net_pay,
            employer_cost=employer_cost,
            period=period,
        )
