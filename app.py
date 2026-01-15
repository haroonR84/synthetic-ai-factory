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

    if records:
        df = pd.DataFrame(records)

        st.subheader("Structured Dataset Preview")
        st.dataframe(df)

        # CSV Download
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV",
            data=csv,
            file_name="synthetic_data.csv",
            mime="text/csv"
        )

        # Excel Download
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False)
        st.download_button(
            "Download Excel",
            data=excel_buffer.getvalue(),
            file_name="synthetic_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.error("No structured records returned. Try again.")
