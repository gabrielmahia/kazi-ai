"""KaziAI Streamlit app — Kenya HR compliance tools."""
import os, streamlit as st
from kazi_ai.payroll import PayrollCalculator
import anthropic

st.set_page_config(page_title="KaziAI", page_icon="⚖️", layout="centered")
st.title("⚖️ KaziAI — Kenya HR Compliance")
st.caption("NSSF · NHIF · PAYE · Employment Act 2007 · Plain language")

tab1, tab2, tab3 = st.tabs(["💰 Payroll Calculator", "❓ HR Q&A", "📄 Contract"])

with tab1:
    st.subheader("Payroll Calculator")
    gross = st.number_input("Gross monthly salary (KES):", min_value=15000, max_value=5000000,
                             value=85000, step=5000)
    period = st.text_input("Period (e.g. 2026-04):", value="2026-04")
    if st.button("Calculate", type="primary"):
        calc   = PayrollCalculator()
        result = calc.calculate(gross, period)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Gross Salary", f"KES {result.gross_salary:,.0f}")
            st.metric("NSSF (employee)", f"KES {result.nssf_employee:,.0f}")
            st.metric("NHIF", f"KES {result.nhif_employee:,.0f}")
            st.metric("PAYE", f"KES {result.paye:,.0f}")
        with col2:
            st.metric("Net Pay", f"KES {result.net_pay:,.0f}", delta=f"-{result.gross_salary - result.net_pay:,.0f}")
            st.metric("Employer NSSF", f"KES {result.nssf_employer:,.0f}")
            st.metric("Total Employer Cost", f"KES {result.employer_cost:,.0f}")
        st.info("Rates: NSSF 2024 (Tier I+II) · NHIF Finance Act 2024 · KRA PAYE FY2025/26 · AHL 1.5%")

with tab2:
    st.subheader("HR & Employment Law Q&A")
    api_key = st.text_input("Anthropic API key:", type="password", value=os.getenv("ANTHROPIC_API_KEY",""))
    q = st.text_area("Ask about Kenya employment law:", placeholder="e.g. What is the minimum notice period for permanent employees under the Employment Act?")
    if st.button("Ask", type="primary", key="ask_btn") and q and api_key:
        with st.spinner("Checking Employment Act..."):
            client = anthropic.Anthropic(api_key=api_key)
            msg = client.messages.create(
                model="claude-haiku-4-5-20251001", max_tokens=600,
                system=(
                    "You are a Kenya HR compliance assistant. Answer questions about: "
                    "Employment Act 2007, NSSF Act, NHIF Act, KRA PAYE, leave entitlements, "
                    "termination procedures, and labour court processes in Kenya. "
                    "Always cite the relevant Act and section. "
                    "End every answer with: ⚠️ This is general guidance — consult a qualified HR practitioner for specific cases."
                ),
                messages=[{"role":"user","content":q}],
            )
        st.write(msg.content[0].text)

with tab3:
    st.subheader("Employment Contract Generator")
    st.info("Generates a basic employment contract aligned with Employment Act 2007. Always have a lawyer review before signing.")
    api_key2 = st.text_input("Anthropic API key:", type="password", value=os.getenv("ANTHROPIC_API_KEY",""), key="api_key2")
    with st.form("contract_form"):
        name      = st.text_input("Employee name:")
        title     = st.text_input("Job title:")
        salary    = st.number_input("Gross salary (KES):", min_value=15000, value=50000)
        start     = st.date_input("Start date:")
        employer  = st.text_input("Employer / company name:")
        ct        = st.radio("Contract type:", ["Permanent", "Fixed-term (1 year)"], horizontal=True)
        generate  = st.form_submit_button("Generate contract", type="primary")
    if generate and api_key2 and name and title and employer:
        with st.spinner("Generating..."):
            client = anthropic.Anthropic(api_key=api_key2)
            prompt = (
                f"Generate a Kenya Employment Act 2007-compliant employment contract for:\n"
                f"Employee: {name}, Title: {title}, Gross salary: KES {salary:,}/month, "
                f"Start: {start}, Employer: {employer}, Type: {ct}.\n"
                f"Include: parties, position, salary, statutory deductions, leave, notice, termination, governing law (Laws of Kenya).\n"
                f"Mark [SIGNATURE LINES] at the end."
            )
            msg = client.messages.create(
                model="claude-haiku-4-5-20251001", max_tokens=1500,
                messages=[{"role":"user","content":prompt}])
        st.text_area("Contract:", msg.content[0].text, height=400)
        st.download_button("Download contract",
                           msg.content[0].text,
                           file_name=f"contract_{name.replace(' ','_')}.txt")

st.divider()
st.caption("⚠️ General guidance only. Not legal advice. © 2026 Gabriel Mahia · CC BY-NC-ND 4.0")
