import streamlit as st
import subprocess

st.set_page_config(page_title="Synthetic Text Generator", layout="centered")
st.title("Synthetic Text Data Generator")

data_type = st.selectbox(
    "Select data type",
    ["Resume", "Support Ticket", "Invoice"]
)

count = st.slider("How many records?", 1, 10, 3)

prompt_map = {
    "Resume": "Create realistic synthetic resumes for a Junior Data Analyst.",
    "Support Ticket": "Create realistic customer support tickets for an e-commerce app.",
    "Invoice": "Create realistic synthetic invoices for a small IT services company."
}

prompt = f"""
{prompt_map[data_type]}
Rules:
- Create {count} unique items
- No real people or companies
- Clean, readable bullet points
"""

if st.button("Generate"):
    with st.spinner("Generating locally with Ollama..."):
        result = subprocess.run(
            ["ollama", "run", "qwen3:4b"],
            input=prompt,
            text=True,
            capture_output=True
        )
        st.text_area("Output", result.stdout, height=350)