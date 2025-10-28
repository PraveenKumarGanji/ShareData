import streamlit as st
import json
from datetime import datetime
import textwrap

st.set_page_config(page_title="SAR Narrative Generator (PoC)", layout="wide")

st.title("SAR Narrative Generator — PoC")
st.markdown(
    """
    Upload structured SAR case data (JSON) or enter details in the form.  
    The app will generate a FinCEN-style SAR narrative using a template-based generator.
    This PoC is intentionally model-agnostic (no external LLM calls). For production, integrate your LLM or API.
    """
)

def template_generate(case):
    # Safe extraction with defaults
    cust = case.get("customer_name", "Unknown Customer")
    cust_type = case.get("customer_type", "Unknown Type")
    linked = case.get("linked_entity", "")
    period = case.get("activity_period", case.get("activity_start","") + " to " + case.get("activity_end","")) if case.get("activity_period") else case.get("activity_period","")
    txs = case.get("transaction_summary", [])
    alert = case.get("alert_reason", "No alert reason provided")
    system = case.get("detection_system", "Unknown System")
    notes = case.get("analyst_notes", "")
    
    # Build transaction details string
    tx_lines = []
    for t in txs:
        if t.get("count") and t.get("amount_range"):
            tx_lines.append(f"{t.get('count')} {t.get('type')}s of {t.get('amount_range')} (approx. {t.get('total','N/A')})")
        elif t.get("count") and t.get("amount"):
            tx_lines.append(f"{t.get('count')} {t.get('type')}s totalling {t.get('amount')}")
        else:
            parts = [f\"{k}: {v}\" for k,v in t.items()]
            tx_lines.append(", ".join(parts))
    tx_text = "; ".join(tx_lines) if tx_lines else "No transaction summary available."
    
    # Template narrative
    narrative = f\"\"\"Between {period}, the subject {cust} ({cust_type}) conducted {tx_text}.
    
The detected activity triggered an alert for: {alert}. The activity was identified by {system}.
    
Linked entity: {linked}.\n\nAnalyst notes: {notes}\n\nReason for suspicion: The observed pattern of transactions (see above) is inconsistent with the customer's known profile and appears designed to evade reporting requirements. The sequence and consolidation of funds suggest possible structuring or layering.\n\nRecommendation: Further investigation is recommended. Consider filing a SAR with FinCEN if the activity is not satisfactorily explained.\n\"\"\"
    # Wrap lines for readability
    return textwrap.dedent(narrative)

st.sidebar.header("Input")

upload = st.sidebar.file_uploader("Upload SAR JSON file", type=["json"])
use_sample = st.sidebar.checkbox("Load sample case", value=False)
manual = st.sidebar.checkbox("Enter case manually (shows form)", value=False)

if upload:
    try:
        case = json.load(upload)
        st.sidebar.success("Loaded uploaded JSON case.")
    except Exception as e:
        st.sidebar.error(f"Failed to load JSON: {e}")
        case = {}
elif use_sample:
    with open("sample_sar.json","r") as f:
        case = json.load(f)
    st.sidebar.success("Loaded sample case.")
else:
    case = {}

if manual:
    st.header("Manual Case Entry")
    case_id = st.text_input("Case ID", value=case.get("case_id","SAR-XXXX-YYYY"))
    customer_name = st.text_input("Customer Name", value=case.get("customer_name",""))
    customer_type = st.selectbox("Customer Type", ["Individual","Business","Other"], index=0)
    linked_entity = st.text_input("Linked Entity", value=case.get("linked_entity",""))
    activity_period = st.text_input("Activity Period", value=case.get("activity_period","2025-09-10 to 2025-09-25"))
    alert_reason = st.text_area("Alert Reason", value=case.get("alert_reason",""))
    detection_system = st.text_input("Detection System", value=case.get("detection_system",""))
    analyst_notes = st.text_area("Analyst Notes", value=case.get("analyst_notes",""))
    # Simple transaction entry as JSON list
    tx_json = st.text_area("Transaction Summary (JSON list)", value=json.dumps(case.get("transaction_summary",[]), indent=2))
    try:
        txs = json.loads(tx_json)
    except Exception as e:
        st.error("Invalid transaction JSON. Please fix.")
        txs = []
    # Build case dict from inputs
    case = {
        "case_id": case_id,
        "customer_name": customer_name,
        "customer_type": customer_type,
        "linked_entity": linked_entity,
        "activity_period": activity_period,
        "transaction_summary": txs,
        "alert_reason": alert_reason,
        "detection_system": detection_system,
        "analyst_notes": analyst_notes
    }

st.header("Case Preview")
st.json(case)

st.header("Generate Narrative")
col1, col2 = st.columns([3,1])

with col1:
    method = st.radio("Generation method", ["Template-based (PoC)", "Local Model (disabled in PoC)"], index=0)
    if method == "Local Model (disabled in PoC)":
        st.info("Local model integration placeholder. In production, call your LLM endpoint or local model here.")
    gen_btn = st.button("Generate SAR Narrative")
    
with col2:
    st.markdown("**Options**")
    wrap_lines = st.checkbox("Wrap lines for readability", value=True)
    include_recommendation = st.checkbox("Include recommendation section", value=True)

if gen_btn:
    narrative = template_generate(case)
    if not include_recommendation:
        narrative = "\n".join(n for n in narrative.splitlines() if 'Recommendation' not in n and 'Recommendation:' not in n)
    st.session_state['generated_narrative'] = narrative
else:
    narrative = st.session_state.get('generated_narrative', '')

st.header("Generated Narrative (editable)")
edited = st.text_area("Edit narrative as needed before export", value=narrative, height=320)

# Simple compliance check
st.header("Simple Compliance Checks")
checks = []
if "structur" in edited.lower() or "smurf" in edited.lower():
    checks.append("Mentions structuring / smurfing — relevant indicator.")
if "ft" in edited.lower() or "terror" in edited.lower():
    checks.append("Mentions potential terrorist financing — escalate to senior review.")
if len(edited.split()) < 50:
    checks.append("Narrative may be short — ensure required details are included.")

if checks:
    for c in checks:
        st.warning(c)
else:
    st.success("Basic checks passed (PoC).")

st.header("Export")
col_export1, col_export2 = st.columns(2)
with col_export1:
    if st.button("Download as .txt"):
        txt = edited
        st.download_button("Click to download narrative (.txt)", data=txt, file_name=f"{case.get('case_id','SAR')}_narrative.txt", mime='text/plain')
with col_export2:
    if st.button("Download JSON package"):
        package = {"case": case, "narrative": edited, "generated_at": datetime.utcnow().isoformat() + 'Z'}
        st.download_button("Download package (.json)", data=json.dumps(package, indent=2), file_name=f"{case.get('case_id','SAR')}_package.json", mime='application/json')

st.markdown("---")
st.markdown("**Notes:** This is a PoC Streamlit app using a deterministic template generator. For production, integrate your LLM endpoint (OpenAI, Anthropic, local transformer) in the generation step, add robust validation, audit logging, access control, and PII redaction.")
