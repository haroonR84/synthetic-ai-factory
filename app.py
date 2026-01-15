import streamlit as st
import pandas as pd
from io import BytesIO
from openai import OpenAI
from datetime import datetime, timedelta
import random

# -------------------------
# OpenAI Client
# -------------------------
client = OpenAI()

# -------------------------
# Streamlit Page Setup
# -------------------------
st.set_page_config(page_title="Synthetic AI System", layout="centered")
st.title("Synthetic AI System (Decision • Workflow • Risk • Compliance • SLA • Alerts)")

# -------------------------
# UI Controls
# -------------------------
data_type = st.selectbox(
    "Select data type",
    ["Resume", "Support Ticket", "Invoice"]
)

count = st.slider("How many records?", 1, 5, 1)

# -------------------------
# Prompt Templates
# -------------------------
prompt_map = {
    "Resume": "Create synthetic resumes for a Junior Data Analyst.",
    "Support Ticket": "Create synthetic customer support tickets for an e-commerce app.",
    "Invoice": "Create synthetic invoices for a small IT services company."
}

structure_hint = """
Output ONLY this structure.
Repeat it for each record.

NAME:
ROLE:
SKILLS:
YEARS_EXPERIENCE:
TOOLS:
"""

decision_prompt_template = """
You are a strict AI decision engine for HR screening.

Decision Rules:
- Hire: Strong skill match AND experience >= 2 years
- Review: Partial skill match OR experience between 1–2 years
- Reject: Weak skill match OR experience < 1 year

Confidence Score Rules:
- Hire: 75–95
- Review: 45–74
- Reject: 10–44

Output ONLY this structure:

DECISION:
CONFIDENCE_SCORE:
REASON:

CANDIDATE DATA:
NAME: {NAME}
ROLE: {ROLE}
SKILLS: {SKILLS}
YEARS_EXPERIENCE: {YEARS_EXPERIENCE}
TOOLS: {TOOLS}
"""

# -------------------------
# Prompt Builder
# -------------------------
prompt = f"""
{prompt_map[data_type]}

Rules:
- Create {count} unique records
- No real people or companies
- Keep answers short and clean

{structure_hint}
"""

# -------------------------
# Parse Records
# -------------------------
def parse_records(text):
    records = []
    current = {}

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip().upper()
            v = v.strip()
            if k in ["NAME", "ROLE", "SKILLS", "YEARS_EXPERIENCE", "TOOLS"]:
                current[k] = v
        if len(current) == 5:
            records.append(current)
            current = {}
    return records

# -------------------------
# Decision Engine
# -------------------------
def make_decision(record):
    prompt = decision_prompt_template.format(**record)
    response = client.responses.create(model="gpt-4.1-mini", input=prompt)
    output = response.output_text

    data = {}
    for line in output.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k = k.strip().upper()
        v = v.strip()

        if k == "DECISION":
            if v.lower() in ["hire", "accept"]:
                v = "Hire"
            elif v.lower() == "review":
                v = "Review"
            else:
                v = "Reject"

        if k == "CONFIDENCE_SCORE":
            digits = "".join(filter(str.isdigit, v))
            v = int(digits) * 10 if digits and int(digits) <= 10 else int(digits or 0)

        data[k] = v
    return data

# -------------------------
# Workflow Engine
# -------------------------
def assign_workflow(decision):
    return (
        "Send to HR Interview Pipeline" if decision == "Hire"
        else "Send to Manual Review Queue" if decision == "Review"
        else "Archive / Reject"
    )

def workflow_metadata(action):
    if action == "Send to HR Interview Pipeline":
        return {"WORKFLOW_STAGE": "Interview", "OWNER_TEAM": "HR"}
    elif action == "Send to Manual Review Queue":
        return {"WORKFLOW_STAGE": "Manual Review", "OWNER_TEAM": "Hiring Manager"}
    else:
        return {"WORKFLOW_STAGE": "Closed", "OWNER_TEAM": "System"}

# -------------------------
# Risk Engine
# -------------------------
def assess_risk(decision, confidence):
    if decision == "Hire" and confidence < 70:
        return {"RISK_LEVEL": "High", "AUDIT_FLAG": "Yes", "AUDIT_REASON": "Low confidence hire"}
    elif decision == "Review":
        return {"RISK_LEVEL": "Medium", "AUDIT_FLAG": "Yes", "AUDIT_REASON": "Manual review"}
    else:
        return {"RISK_LEVEL": "Low", "AUDIT_FLAG": "No", "AUDIT_REASON": "Acceptable risk"}

# -------------------------
# Compliance Engine
# -------------------------
def assess_compliance(decision, confidence, risk):
    if decision == "Hire" and confidence >= 75 and risk == "Low":
        return {"COMPLIANCE_STATUS": "Compliant", "COMPLIANCE_SCORE": 95, "ESCALATION_REQUIRED": "No", "COMPLIANCE_REASON": "Meets policy"}
    elif decision == "Review":
        return {"COMPLIANCE_STATUS": "Conditional", "COMPLIANCE_SCORE": 70, "ESCALATION_REQUIRED": "Yes", "COMPLIANCE_REASON": "Manual approval required"}
    else:
        return {"COMPLIANCE_STATUS": "Compliant", "COMPLIANCE_SCORE": 85, "ESCALATION_REQUIRED": "No", "COMPLIANCE_REASON": "Within rejection policy"}

# -------------------------
# SLA Engine
# -------------------------
def assess_sla(workflow_stage):
    created_at = datetime.now() - timedelta(hours=random.randint(0, 72))
    sla_hours = 24 if workflow_stage == "Interview" else 48
    elapsed = int((datetime.now() - created_at).total_seconds() / 3600)

    if elapsed > sla_hours:
        return {
            "CREATED_AT": created_at.strftime("%Y-%m-%d %H:%M"),
            "SLA_HOURS": sla_hours,
            "ELAPSED_HOURS": elapsed,
            "SLA_STATUS": "Breached",
            "SLA_REASON": "Exceeded allowed processing time"
        }
    else:
        return {
            "CREATED_AT": created_at.strftime("%Y-%m-%d %H:%M"),
            "SLA_HOURS": sla_hours,
            "ELAPSED_HOURS": elapsed,
            "SLA_STATUS": "On Track",
            "SLA_REASON": "Within SLA window"
        }

# -------------------------
# 🆕 ALERT & ESCALATION ENGINE (Milestone 8)
# -------------------------
def assess_alerts(sla_status, risk_level):
    if sla_status == "Breached" and risk_level == "High":
        return {
            "ALERT_REQUIRED": "Yes",
            "ALERT_SEVERITY": "Critical",
            "ESCALATION_LEVEL": "Director",
            "ESCALATION_REASON": "High risk SLA breach"
        }
    elif sla_status == "Breached":
        return {
            "ALERT_REQUIRED": "Yes",
            "ALERT_SEVERITY": "High",
            "ESCALATION_LEVEL": "Manager",
            "ESCALATION_REASON": "SLA breach detected"
        }
    else:
        return {
            "ALERT_REQUIRED": "No",
            "ALERT_SEVERITY": "Low",
            "ESCALATION_LEVEL": "None",
            "ESCALATION_REASON": "No action required"
        }

# -------------------------
# Generate Button
# -------------------------
if st.button("Generate"):
    response = client.responses.create(model="gpt-4.1-mini", input=prompt)
    records = parse_records(response.output_text)

    results = []
    for r in records:
        decision = make_decision(r)
        workflow = assign_workflow(decision["DECISION"])
        wf_meta = workflow_metadata(workflow)
        risk = assess_risk(decision["DECISION"], decision["CONFIDENCE_SCORE"])
        compliance = assess_compliance(decision["DECISION"], decision["CONFIDENCE_SCORE"], risk["RISK_LEVEL"])
        sla = assess_sla(wf_meta["WORKFLOW_STAGE"])
        alerts = assess_alerts(sla["SLA_STATUS"], risk["RISK_LEVEL"])

        results.append({
            **r,
            **decision,
            "WORKFLOW_ACTION": workflow,
            **wf_meta,
            **risk,
            **compliance,
            **sla,
            **alerts
        })

    df = pd.DataFrame(results)
    st.dataframe(df)

    st.download_button("Download CSV", df.to_csv(index=False).encode("utf-8"), "synthetic_alert_system.csv")
    excel = BytesIO()
    df.to_excel(excel, index=False)
    st.download_button("Download Excel", excel.getvalue(), "synthetic_alert_system.xlsx")
