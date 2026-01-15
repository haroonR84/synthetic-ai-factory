import streamlit as st
import pandas as pd
from io import BytesIO
from openai import OpenAI

# -------------------------
# OpenAI Client
# -------------------------
client = OpenAI()

# -------------------------
# Streamlit Page Setup
# -------------------------
st.set_page_config(page_title="Synthetic Text Generator", layout="centered")
st.title("Synthetic Text Data Generator (Fast Mode)")

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

Instructions:
- Apply rules consistently
- Do not invent criteria
- Output ONLY the structure below

STRUCTURE:
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
structure_hint = """
Output ONLY the following structure.
Repeat the structure exactly for each record.
Do not include explanations or extra text.

NAME:
ROLE:
SKILLS:
YEARS_EXPERIENCE:
TOOLS:
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
# Parser Function
# -------------------------
def parse_records(text):
    records = []
    current = {}

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip().upper()
            value = value.strip()

            if key in ["NAME", "ROLE", "SKILLS", "YEARS_EXPERIENCE", "TOOLS"]:
                current[key] = value

        if len(current) == 5:
            records.append(current)
            current = {}

    return records
def make_decision(record):
    prompt = decision_prompt_template.format(**record)

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )
    output = response.output_text
    decision_data = {}

    for line in output.splitlines():
        if ":" not in line:
            continu
        key, value = line.split(":", 1)
        clean_key = key.strip().upper()
        clean_value = value.strip()
        if clean_key == "DECISION":
            if clean_value.lower() in ["hire", "accept"]:
                clean_value = "Hire"
            elif clean_value.lower() == "review":
                clean_value = "Review"
            else:
                clean_value = "Reject"

        if clean_key == "CONFIDENCE_SCORE":
            digits = "".join(filter(str.isdigit, clean_value))
            if digits:
                score = int(digits)
                clean_value = score * 10 if score <= 10 else score
            else:
                clean_value = 0

        decision_data[clean_key] = clean_value

    return decision_data
# -------------------------
# Generate Button
# -------------------------
if st.button("Generate"):
    with st.spinner("Generating with OpenAI (fast)..."):
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )

    raw_output = response.output_text
    records = parse_records(raw_output)

    decision_results = []

    for record in records:
        decision = make_decision(record)
        combined = {**record, **decision}
        decision_results.append(combined)

    if decision_results:
        df = pd.DataFrame(decision_results)
        st.subheader("Decision Dataset Preview")
        st.dataframe(df)

        # CSV Download
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV",
            data=csv,
            file_name="decision_data.csv",
            mime="text/csv"
        )

        # Excel Download
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        st.download_button(
            "Download Excel",
            data=excel_buffer.getvalue(),
            file_name="decision_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("No decisions could be generated.")
