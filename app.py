import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from utilities import (
    configure_gemini,
    extract_text_from_pdf,
    extract_claims,
    verify_claim
)

load_dotenv()

st.set_page_config(
    page_title="Fact Check Agent",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Fact Check Agent")
st.markdown(
    "**Truth Layer for Marketing Content** – Upload PDF for Automated Fact-Checking"
)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("GEMINI_API_KEY not found in .env file")
    st.stop()

configure_gemini(api_key)

uploaded_file = st.file_uploader(
    "Upload PDF File",
    type=["pdf"]
)

if uploaded_file:

    with st.spinner("Analyzing PDF..."):

        text = extract_text_from_pdf(uploaded_file)

        claims = extract_claims(text)

        st.success(f"✅ Extracted {len(claims)} claims")

        for idx, claim in enumerate(claims):

            with st.expander(
                f"Claim {idx + 1}: {claim[:80]}..."
            ):

                st.write("### Claim")
                st.write(claim)

                result = verify_claim(claim)

                st.write("### Verification Result")
                st.markdown(result)

    st.download_button(
        label="Download Extracted Text",
        data=text,
        file_name=f"factcheck_{datetime.now().strftime('%Y%m%d')}.txt"
    )

else:
    st.info("Upload a PDF document to begin analysis.")

st.caption("Built for CogCulture Product Management Assessment")
