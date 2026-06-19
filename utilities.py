from pypdf import PdfReader
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import re


def configure_gemini(api_key):
    genai.configure(api_key=api_key)


def extract_text_from_pdf(pdf_file):
    try:
        reader = PdfReader(pdf_file)
        text = "".join(page.extract_text() or "" for page in reader.pages)
        return text
    except Exception:
        return "Error reading PDF"


def extract_claims(text):
    prompt = """
    Extract 8-15 key factual claims containing:
    - statistics
    - percentages
    - dates
    - numbers

    Return ONLY a Python list:
    ["claim 1", "claim 2"]
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            prompt + "\n\nText:\n" + text[:10000]
        )

        claims_text = response.text
        claims = re.findall(r'"([^"]+)"', claims_text)

        if not claims:
            claims = [
                line.strip()
                for line in claims_text.split("\n")
                if len(line.strip()) > 20
            ]

        return [c for c in claims if len(c) > 15][:15]

    except Exception:
        return re.findall(
            r'.*?(?:\d+%|\d{4}|\$\d+|[0-9,.]+).*?[.!?]',
            text
        )[:12]


def verify_claim(claim):
    try:
        query = claim.replace(" ", "+") + "+2025+OR+2026"

        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(
            f"https://www.google.com/search?q={query}",
            headers=headers,
            timeout=8
        )

        soup = BeautifulSoup(response.text, "html.parser")

        snippet = (
            soup.find("div", class_="VwiC3b")
            or soup.find("span", class_="hgKElc")
        )

        snippet_text = (
            snippet.get_text()[:600]
            if snippet
            else "No strong evidence found"
        )

        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
        Claim: {claim}

        Evidence:
        {snippet_text}

        Classify as:
        - Verified
        - Inaccurate
        - False

        Give a short explanation and correction if needed.
        """

        result = model.generate_content(prompt)

        return result.text

    except Exception as e:
        return f"Verification error: {str(e)}"
