import sys, os, json, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

try:
    from kazi_ai.payroll import PayrollCalculator
    HAS_KAZI = True
except ImportError:
    HAS_KAZI = False


def _get_api_key():
    """Gemini key from Streamlit secrets or env. Free at aistudio.google.com"""
    try:
        import streamlit as st
        k = (st.secrets.get("GOOGLE_API_KEY")
             or st.secrets.get("GEMINI_API_KEY"))
        if k:
            return k
    except Exception:
        pass
    return (os.environ.get("GOOGLE_API_KEY")
            or os.environ.get("GEMINI_API_KEY", ""))


def _call_gemini(system: str, user: str, api_key: str) -> str:
    """Call Gemini REST API directly — no SDK needed. Free tier works."""
    _BASE = "https://generativelanguage.googleapis.com"
    models = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-8b"]
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": [{"text": user}]}],
        "generationConfig": {"maxOutputTokens": 800, "temperature": 0.3},
    }
    last_err = ""
    for model in models:
        url = f"{_BASE}/v1beta/models/{model}:generateContent?key={api_key}"
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read())
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            last_err = f"HTTP {e.code}"
            if e.code in (400, 404):
                continue   # try next model
            raise
        except Exception as e:
            last_err = str(e)
            continue
    raise RuntimeError(f"All Gemini models failed. Last error: {last_err}")


st.set_page_config(page_title="KaziAI", page_icon="⚖️", layout="centered")

if not HAS_KAZI:
    st.error("KaziAI is temporarily unavailable. Please try again shortly.")
    st.stop()

st.title("⚖️ KaziAI — Kenya HR Compliance")
st.caption("NSSF · NHIF · PAYE · Employment Act 2007 · Plain language")

api_key = _get_api_key()

tab1, tab2, tab3 = st.tabs(["💰 Payroll Calculator", "❓ HR Q&A", "📄 Contract"])

with tab1:
    st.subheader("Payroll Calculator")
    st.caption("NSSF 2024 · NHIF Finance Act 2024 · KRA PAYE FY2025/26 · AHL 1.5%")
    gross  = st.number_input("Gross monthly salary (KES):", min_value=15000, max_value=5000000, value=85000, step=5000)
    period = st.text_input("Period:", value="2026-04")
    if st.button("Calculate", type="primary"):
        try:
            r = PayrollCalculator().calculate(gross, period)
            c1, c2 = st.columns(2)
            c1.metric("Gross",         f"KES {r.gross_salary:,.0f}")
            c1.metric("NSSF",          f"KES {r.nssf_employee:,.0f}")
            c1.metric("NHIF",          f"KES {r.nhif_employee:,.0f}")
            c1.metric("PAYE",          f"KES {r.paye:,.0f}")
            c2.metric("Net Pay",       f"KES {r.net_pay:,.0f}",
                      delta=f"-{r.gross_salary - r.net_pay:,.0f}")
            c2.metric("Employer NSSF", f"KES {r.nssf_employer:,.0f}")
            c2.metric("Total Cost",    f"KES {r.employer_cost:,.0f}")
            st.info("Always verify with KRA/NSSF/NHIF for official current rates.")
        except Exception:
            st.error("Could not calculate payroll. Please check your inputs.")

HR_SYSTEM = """You are a Kenya HR compliance assistant. Answer questions about:
Employment Act 2007, NSSF Act, NHIF Act, KRA PAYE, statutory leave, and termination in Kenya.
Always cite the relevant Act and section number.
Keep answers clear and practical for SME owners and HR staff.
End every answer with: ⚠️ General guidance only — consult a qualified HR practitioner for specific cases."""

CONTRACT_SYSTEM = """You generate Kenya Employment Act 2007-compliant employment contract templates.
Include: parties, role, reporting line, salary, statutory deductions (NSSF/NHIF/PAYE),
annual leave (21 days), sick leave, maternity/paternity leave, notice period, termination,
governing law (Laws of Kenya). Add clear [SIGNATURE LINES] at the end.
Note at the top: TEMPLATE ONLY — review with a qualified employment lawyer before signing."""

def _key_input(label: str, key: str) -> str:
    if api_key:
        return api_key
    return st.text_input(label, type="password", key=key,
                          placeholder="AIza...",
                          help="Free at aistudio.google.com — no credit card needed.")

with tab2:
    st.subheader("HR & Employment Law Q&A")
    k2  = _key_input("Google AI key (free at aistudio.google.com):", "k2")
    q   = st.text_area("Your question:", placeholder="e.g. What is the minimum notice period for permanent employees?")
    if st.button("Get answer", type="primary", key="ask_btn"):
        if not k2:
            st.info("Add a free Google AI key above. Get one at [aistudio.google.com](https://aistudio.google.com)")
        elif not q.strip():
            st.warning("Please type a question first.")
        else:
            with st.spinner("Checking the Employment Act..."):
                try:
                    st.write(_call_gemini(HR_SYSTEM, q, k2))
                except urllib.error.HTTPError as e:
                    st.error("API key error." if e.code == 403 else "Too many requests — please wait." if e.code == 429 else "Could not get answer. Try again.")
                except Exception:
                    st.error("Could not get an answer. Please try again.")

with tab3:
    st.subheader("Employment Contract Generator")
    st.warning("⚠️ Template only — have a qualified lawyer review before signing.")
    k3 = _key_input("Google AI key:", "k3")
    with st.form("contract_form"):
        name     = st.text_input("Employee full name:")
        title    = st.text_input("Job title:")
        salary   = st.number_input("Gross monthly salary (KES):", min_value=15000, value=50000)
        start    = st.date_input("Start date:")
        employer = st.text_input("Employer / company name:")
        ct       = st.radio("Contract type:", ["Permanent", "Fixed-term (1 year)"], horizontal=True)
        generate = st.form_submit_button("Generate contract", type="primary")

    if generate:
        if not k3:
            st.info("Add a Google AI key above.")
        elif not name or not title or not employer:
            st.warning("Fill in employee name, job title, and employer name.")
        else:
            with st.spinner("Generating contract..."):
                try:
                    prompt = (f"Employee: {name} | Title: {title} | "
                              f"Gross: KES {salary:,}/month | Start: {start} | "
                              f"Employer: {employer} | Type: {ct}")
                    text = _call_gemini(CONTRACT_SYSTEM, prompt, k3)
                    st.text_area("Contract:", text, height=400)
                    st.download_button("📥 Download (.txt)", text,
                                       file_name=f"contract_{name.replace(' ','_').lower()}.txt")
                except Exception:
                    st.error("Could not generate the contract. Please try again.")

st.divider()
st.caption("⚠️ Not legal advice. © 2026 Gabriel Mahia · CC BY-NC-ND 4.0 · Powered by Google Gemini")
