import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

try:
    from kazi_ai.payroll import PayrollCalculator
    HAS_KAZI = True
except ImportError:
    HAS_KAZI = False

try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

st.set_page_config(page_title="KaziAI", page_icon="⚖️", layout="centered")

if not HAS_KAZI:
    st.error("KaziAI is temporarily unavailable. Please try again shortly.")
    st.stop()

st.title("⚖️ KaziAI — Kenya HR Compliance")
st.caption("NSSF · NHIF · PAYE · Employment Act 2007 · Plain language")

ENV_KEY = os.getenv("ANTHROPIC_API_KEY", "")

tab1, tab2, tab3 = st.tabs(["💰 Payroll Calculator", "❓ HR Q&A", "📄 Contract"])

with tab1:
    st.subheader("Payroll Calculator")
    st.caption("NSSF 2024 (Tier I+II) · NHIF Finance Act 2024 · KRA PAYE FY2025/26 · AHL 1.5%")
    gross = st.number_input("Gross monthly salary (KES):", min_value=15000,
                             max_value=5000000, value=85000, step=5000)
    period = st.text_input("Period (e.g. 2026-04):", value="2026-04")
    if st.button("Calculate net pay", type="primary"):
        try:
            result = PayrollCalculator().calculate(gross, period)
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Gross Salary",   f"KES {result.gross_salary:,.0f}")
                st.metric("NSSF (employee)", f"KES {result.nssf_employee:,.0f}")
                st.metric("NHIF",            f"KES {result.nhif_employee:,.0f}")
                st.metric("PAYE",            f"KES {result.paye:,.0f}")
            with col2:
                st.metric("Net Pay",
                          f"KES {result.net_pay:,.0f}",
                          delta=f"-{result.gross_salary - result.net_pay:,.0f} deductions")
                st.metric("Employer NSSF",  f"KES {result.nssf_employer:,.0f}")
                st.metric("Total Cost",     f"KES {result.employer_cost:,.0f}")
            st.info("Rates are updated regularly but always verify with KRA/NSSF/NHIF for official figures.")
        except Exception:
            st.error("Could not calculate payroll. Please check your inputs.")

def _get_api_key(key_label: str) -> str:
    """Return API key from env or prompt safely."""
    if ENV_KEY:
        return ENV_KEY
    if not HAS_ANTHROPIC:
        st.warning("AI features not available in this environment.")
        return ""
    key = st.text_input(key_label, type="password",
                        placeholder="AIza... or sk-ant-...",
                        help="Gemini keys (AIza...) are free at aistudio.google.com. Anthropic keys (sk-ant-) at console.anthropic.com.")
    if key and not (key.startswith("AIza") or key.startswith("sk-ant-")):
        st.caption("⚠️ Unrecognised key format. Gemini starts with AIza, Anthropic with sk-ant-")
        return ""
    return key

with tab2:
    st.subheader("HR & Employment Law Q&A")
    st.caption("Ask about Employment Act 2007, leave entitlements, NSSF, NHIF, termination procedures.")

    api_key2 = _get_api_key("Anthropic API key (needed for AI answers):")
    q = st.text_area("Your question:", placeholder="e.g. What is the minimum notice period for permanent employees?")

    if st.button("Get answer", type="primary", key="ask_btn"):
        if not api_key2:
            st.info("Add an API key above to get AI answers. Get a free key at console.anthropic.com")
        elif not q.strip():
            st.warning("Please type a question first.")
        else:
            with st.spinner("Checking the Employment Act..."):
                try:
                    if api_key2.startswith("AIza") and HAS_GEMINI:
                        genai.configure(api_key=api_key2)
                        model = genai.GenerativeModel(
                            "gemini-2.0-flash",
                            system_instruction=(
                                "You are a Kenya HR compliance assistant. Answer questions about "
                                "Employment Act 2007, NSSF, NHIF, KRA PAYE, leave, and labour law. "
                                "Always cite the relevant Act and section. "
                                "End every answer with: "
                                "⚠️ This is general guidance — consult a qualified HR practitioner for specific cases."
                            )
                        )
                        resp = model.generate_content(q)
                        st.write(resp.text)
                    else:
                        client = anthropic.Anthropic(api_key=api_key2)
                        msg = client.messages.create(
                            model="claude-haiku-4-5-20251001", max_tokens=600,
                            system=(
                                "You are a Kenya HR compliance assistant. Answer questions about "
                                "Employment Act 2007, NSSF, NHIF, KRA PAYE, leave, and labour law in Kenya. "
                                "Always cite the relevant Act and section. "
                                "End every answer with: "
                                "⚠️ This is general guidance — consult a qualified HR practitioner for specific cases."
                            ),
                            messages=[{"role": "user", "content": q}])
                        st.write(msg.content[0].text)
                except anthropic.AuthenticationError:
                    st.error("API key not recognised. Please check it and try again.")
                except anthropic.RateLimitError:
                    st.error("Too many requests — please wait a moment and try again.")
                except Exception:
                    st.error("Could not get an answer right now. Please try again.")

with tab3:
    st.subheader("Employment Contract Generator")
    st.warning("⚠️ This generates a template only. Always have a qualified lawyer review before signing.")

    api_key3 = _get_api_key("Anthropic API key (needed to generate contract):")

    with st.form("contract_form"):
        name     = st.text_input("Employee full name:")
        title    = st.text_input("Job title:")
        salary   = st.number_input("Gross monthly salary (KES):", min_value=15000, value=50000)
        start    = st.date_input("Start date:")
        employer = st.text_input("Employer / company name:")
        ct       = st.radio("Contract type:", ["Permanent", "Fixed-term (1 year)"], horizontal=True)
        generate = st.form_submit_button("Generate contract", type="primary")

    if generate:
        if not api_key3:
            st.info("Add an API key above to generate a contract.")
        elif not name or not title or not employer:
            st.warning("Please fill in employee name, job title, and employer name.")
        else:
            with st.spinner("Generating Employment Act-aligned contract..."):
                try:
                    client = anthropic.Anthropic(api_key=api_key3)
                    prompt = (
                        f"Generate a Kenya Employment Act 2007-compliant employment contract:\n"
                        f"Employee: {name}, Title: {title}, Gross: KES {salary:,}/month, "
                        f"Start: {start}, Employer: {employer}, Type: {ct}.\n"
                        f"Include: parties, role, salary, statutory deductions, leave entitlements, "
                        f"notice period, termination, governing law (Laws of Kenya).\n"
                        f"Add [SIGNATURE LINES] at the end."
                    )
                    msg = client.messages.create(
                        model="claude-haiku-4-5-20251001", max_tokens=1500,
                        messages=[{"role": "user", "content": prompt}])
                    contract_text = msg.content[0].text
                    st.text_area("Contract:", contract_text, height=400)
                    st.download_button(
                        "📥 Download contract (.txt)",
                        contract_text,
                        file_name=f"contract_{name.replace(' ','_').lower()}.txt",
                        mime="text/plain"
                    )
                except anthropic.AuthenticationError:
                    st.error("API key not recognised. Please check it.")
                except Exception:
                    st.error("Could not generate the contract. Please try again.")

st.divider()
st.caption("⚠️ General guidance only — not legal advice. © 2026 Gabriel Mahia · CC BY-NC-ND 4.0 · contact@aikungfu.dev")
