import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
import urllib.error

try:
    from kazi_ai.payroll import PayrollCalculator
    HAS_KAZI = True
except ImportError:
    HAS_KAZI = False

# ── AI helper — Gemini first (free tier), Anthropic fallback ────────────
_GEMINI_BASE = "https://generativelanguage.googleapis.com"
_GEMINI_MODELS = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-flash-8b"]

def _get_gemini_key():
    try:
        k = st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY")
        if k: return k
    except Exception:
        pass
    return os.environ.get("GOOGLE_API_KEY") or os.environ.get("GEMINI_API_KEY", "")

def _get_anthropic_key():
    try:
        k = st.secrets.get("ANTHROPIC_API_KEY")
        if k: return k
    except Exception:
        pass
    return os.environ.get("ANTHROPIC_API_KEY", "")

def _call_gemini(system: str, user: str, api_key: str) -> str:
    import urllib.request as _req, json as _json
    payload = {
        "contents": [{"role": "user", "parts": [{"text": f"{system}\n\n{user}"}]}],
        "generationConfig": {"maxOutputTokens": 1024, "temperature": 0.3},
    }
    for model in _GEMINI_MODELS:
        url = f"{_GEMINI_BASE}/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            r = _req.urlopen(_req.Request(url,
                data=_json.dumps(payload).encode(),
                headers={"Content-Type": "application/json"},
                method="POST"), timeout=20)
            d = _json.loads(r.read())
            return d["candidates"][0]["content"]["parts"][0]["text"]
        except urllib.error.HTTPError as e:
            if e.code in (400, 404):
                continue
            raise
    raise RuntimeError("All Gemini models unavailable")

def _call_anthropic(system: str, user: str, api_key: str) -> str:
    import anthropic as _ant
    client = _ant.Anthropic(api_key=api_key)
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=1024,
        system=system,
        messages=[{"role": "user", "content": user}])
    return msg.content[0].text

def ai_call(system: str, user: str,
            gemini_key: str = "", anthropic_key: str = "") -> str:
    """Try Gemini first (free tier), fall back to Anthropic."""
    gkey = gemini_key or _get_gemini_key()
    akey = anthropic_key or _get_anthropic_key()
    if gkey:
        try:
            return _call_gemini(system, user, gkey)
        except Exception:
            pass
    if akey:
        return _call_anthropic(system, user, akey)
    raise RuntimeError("No AI key available")

def has_any_key() -> bool:
    return bool(_get_gemini_key() or _get_anthropic_key())

def which_provider() -> str:
    if _get_gemini_key(): return "gemini"
    if _get_anthropic_key(): return "anthropic"
    return "none"
# ────────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="KaziAI", page_icon="⚖️", layout="centered")

if not HAS_KAZI:
    st.error("KaziAI is temporarily unavailable. Please try again shortly.")
    st.stop()

st.title("⚖️ KaziAI — Kenya HR Compliance")
st.caption("NSSF · NHIF · PAYE · Employment Act 2007 · Plain language")

provider = which_provider()

def _ai_key_widget(label_suffix: str = "") -> tuple[str, str]:
    """Show key inputs only if no server-side key configured."""
    if which_provider() != "none":
        return _get_gemini_key(), _get_anthropic_key()
    gkey = st.text_input(f"Google Gemini key (free){label_suffix}:",
        type="password", placeholder="AIza...",
        help="Free at aistudio.google.com — no credit card needed.")
    st.caption("— or use Anthropic instead —")
    akey = st.text_input(f"Anthropic key{label_suffix}:",
        type="password", placeholder="sk-ant-...")
    return gkey, akey

tab1, tab2, tab3 = st.tabs(["💰 Payroll Calculator", "❓ HR Q&A", "📄 Contract"])

with tab1:
    st.subheader("Payroll Calculator")
    st.caption("NSSF 2024 (Tier I+II) · NHIF Finance Act 2024 · KRA PAYE FY2025/26 · AHL 1.5%")
    gross  = st.number_input("Gross monthly salary (KES):", min_value=15000,
                              max_value=5000000, value=85000, step=5000)
    period = st.text_input("Period:", value="2026-04")
    if st.button("Calculate net pay", type="primary"):
        try:
            result = PayrollCalculator().calculate(gross, period)
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Gross Salary",    f"KES {result.gross_salary:,.0f}")
                st.metric("NSSF (employee)", f"KES {result.nssf_employee:,.0f}")
                st.metric("NHIF",            f"KES {result.nhif_employee:,.0f}")
                st.metric("PAYE",            f"KES {result.paye:,.0f}")
            with c2:
                st.metric("Net Pay",
                          f"KES {result.net_pay:,.0f}",
                          delta=f"-{result.gross_salary - result.net_pay:,.0f}")
                st.metric("Employer NSSF",   f"KES {result.nssf_employer:,.0f}")
                st.metric("Total Cost",      f"KES {result.employer_cost:,.0f}")
            st.info("Always verify statutory rates with KRA/NSSF/NHIF directly.")
        except Exception:
            st.error("Could not calculate. Please check your inputs.")

HR_SYSTEM = (
    "You are a Kenya HR compliance assistant. Answer questions about "
    "Employment Act 2007, NSSF Act, NHIF Act, KRA PAYE, leave entitlements, "
    "termination, and labour court processes. "
    "Always cite the relevant Act and section number. "
    "End every answer with: "
    "⚠️ General guidance only — consult a qualified HR practitioner for specific cases."
)

with tab2:
    st.subheader("HR & Employment Law Q&A")
    if provider == "none":
        st.info("Add a free Gemini key below to enable AI answers.")
    gkey2, akey2 = _ai_key_widget(" (tab 2)")
    active2 = gkey2 or akey2
    q = st.text_area("Your question:",
        placeholder="e.g. What is the minimum notice period for a permanent employee?")
    if st.button("Get answer", type="primary", key="ask_btn"):
        if not active2:
            st.info("Add a Gemini or Anthropic key above. Gemini is free at aistudio.google.com")
        elif not q.strip():
            st.warning("Please type a question first.")
        else:
            with st.spinner("Checking the Employment Act..."):
                try:
                    st.write(ai_call(HR_SYSTEM, q, gkey2, akey2))
                except RuntimeError:
                    st.error("API key not working. Please check it and try again.")
                except Exception:
                    st.error("Could not get an answer right now. Please try again.")

CONTRACT_SYSTEM = (
    "Generate Kenya Employment Act 2007-compliant employment contracts. "
    "Be precise and cite the relevant sections. "
    "Include all statutory requirements."
)

with tab3:
    st.subheader("Employment Contract Generator")
    st.warning("Template only — always have a lawyer review before signing.")
    if provider == "none":
        st.info("Add a free Gemini key below to generate contracts.")
    gkey3, akey3 = _ai_key_widget(" (tab 3)")
    with st.form("contract_form"):
        name     = st.text_input("Employee full name:")
        title    = st.text_input("Job title:")
        salary   = st.number_input("Gross monthly salary (KES):", min_value=15000, value=50000)
        start    = st.date_input("Start date:")
        employer = st.text_input("Employer / company name:")
        ct       = st.radio("Contract type:", ["Permanent", "Fixed-term (1 year)"], horizontal=True)
        generate = st.form_submit_button("Generate contract", type="primary")
    if generate:
        active3 = gkey3 or akey3
        if not active3:
            st.info("Add a Gemini or Anthropic key above to generate a contract.")
        elif not name or not title or not employer:
            st.warning("Fill in employee name, job title, and employer name.")
        else:
            with st.spinner("Generating..."):
                try:
                    prompt = (
                        f"Generate a Kenya Employment Act 2007-compliant employment contract. "
                        f"Employee: {name} | Title: {title} | Gross: KES {salary:,}/month | "
                        f"Start: {start} | Employer: {employer} | Type: {ct}. "
                        f"Include: parties, role, salary, NSSF/NHIF/PAYE deductions, leave, "
                        f"notice period, termination, governing law (Laws of Kenya). "
                        f"Add [SIGNATURE LINES] at the end."
                    )
                    text = ai_call(CONTRACT_SYSTEM, prompt, gkey3, akey3)
                    st.text_area("Contract:", text, height=400)
                    st.download_button("📥 Download (.txt)", text,
                        file_name=f"contract_{name.replace(' ','_').lower()}.txt",
                        mime="text/plain")
                except RuntimeError:
                    st.error("API key not working. Please check it.")
                except Exception:
                    st.error("Could not generate contract. Please try again.")

st.divider()
st.caption("⚠️ General guidance — not legal advice. © 2026 Gabriel Mahia · CC BY-NC-ND 4.0")
