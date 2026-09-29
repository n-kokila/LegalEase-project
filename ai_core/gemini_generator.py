import os
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

DOCUMENT_TYPES = [
    "Agreement",
    "Contract",
    "NDA",
    "Lease Agreement",
    "Employment Contract",
    "Employment Offer Letter",
    "Freelance Work Contract",
    "Legal Notice",
    "Affidavit"
]

def build_legal_prompt(
    document_type: str,
    parties: str,
    terms: str,
    effective_date: str,
    jurisdiction: Optional[str] = None,
    additional_notes: Optional[str] = None
) -> str:
    """
    Constructs a comprehensive, formal legal prompt for Google Gemini.
    Strictly instructs the AI to adhere to professional legal drafting standards
    and never invent user-provided facts.
    """
    jurisdiction_clause = jurisdiction if jurisdiction and jurisdiction.strip() else "Applicable State and Federal Jurisdiction"
    notes_clause = f"\nAdditional Instructions / Clauses:\n{additional_notes}" if additional_notes and additional_notes.strip() else ""

    prompt = f"""You are an elite Senior Corporate Attorney and Contract Drafting Specialist.
Your task is to draft a comprehensive, enforceable, and professionally formatted legal document draft based ONLY on the specifications below.

============================================================
DOCUMENT SPECIFICATIONS:
============================================================
Document Type: {document_type}
Parties Involved: {parties}
Effective Date: {effective_date}
Governing Jurisdiction: {jurisdiction_clause}
Core Terms, Covenants & Conditions:
{terms}
{notes_clause}

============================================================
DRAFTING RULES & CONSTRAINTS:
============================================================
1. PROFESSIONAL LEGAL STRUCTURE:
   Draft must contain all appropriate sections in standard legal order:
   - OFFICIAL DOCUMENT TITLE (in ALL CAPS, centered)
   - PREAMBLE / COMMENCEMENT CLAUSE (identifying all named parties, their legal capacity, and effective date)
   - RECITALS / BACKGROUND (clear "WHEREAS" clauses explaining the premise)
   - DEFINITIONS & INTERPRETATION (where relevant)
   - OPERATIVE CLAUSES & TERMS (clearly numbered: Clause 1, Clause 2, etc.)
   - FINANCIAL / CONSIDERATION CLAUSES (if applicable)
   - TERM, RENEWAL & TERMINATION CLAUSE
   - CONFIDENTIALITY & PROPRIETARY RIGHTS (where relevant)
   - INDEMNIFICATION, WARRANTIES & LIMITATION OF LIABILITY
   - GOVERNING LAW & DISPUTE RESOLUTION (Arbitration / Court Jurisdiction)
   - MISCELLANEOUS / BOILERPLATE (Severability, Entire Agreement, Amendments, Counterparts)
   - FORMAL EXECUTION & SIGNATURE SECTION (signature lines, printed names, titles, dates, and witness spaces for all parties)

2. STRICT FACTUAL FIDELITY (DO NOT INVENT FACTS):
   - You MUST NOT invent fictitious facts, names, corporate addresses, monetary amounts, or terms that were not provided.
   - Incorporate all user-supplied parties and terms accurately.
   - If a standard contract requires specific factual details that were not provided (such as a registered address, specific dollar amount, or exact notice email), use a clean bracketed placeholder (e.g., [Insert Registered Address], [Insert Agreed Sum], [Insert Notice Email]).

3. TONE & VOCABULARY:
   - Use precise, formal, unambiguous legal terminology.
   - Maintain active legal phrasing ("shall", "agrees that", "hereby covenants").

4. OUTPUT FORMAT:
   - Provide the complete, finalized draft in clean, well-structured text.
   - Do NOT include conversational filler, introductory remarks, or concluding disclaimers (e.g., do not say "Here is your contract:").
   - Begin immediately with the Document Title.
"""
    return prompt.strip()


def generate_template_fallback(
    document_type: str,
    parties: str,
    terms: str,
    effective_date: str,
    jurisdiction: Optional[str] = None
) -> str:
    """
    High-grade fallback template engine that constructs a complete legal document draft
    when the Gemini API key is missing or when network connectivity is offline.
    """
    clean_type = document_type.upper()
    jur = jurisdiction.strip() if jurisdiction and jurisdiction.strip() else "[Applicable Jurisdiction / State Law]"
    
    # Format terms into clauses
    terms_lines = [line.strip() for line in terms.split("\n") if line.strip()]
    if not terms_lines:
        terms_lines = ["The parties agree to fulfill all covenants specified herein in good faith and compliance with applicable law."]

    clause_sections = ""
    for idx, t in enumerate(terms_lines, start=3):
        clause_sections += f"\nCLAUSE {idx}. OPERATIONAL TERMS & COVENANTS\n{t}\n"

    draft = f"""{clean_type}

THIS {clean_type} (the "Agreement") is entered into and made effective as of {effective_date} (the "Effective Date"), by and between the following parties:

PARTIES:
{parties}
(Collectively referred to as the "Parties", or individually as a "Party").

RECITALS:
WHEREAS, the Parties desire to formally define their respective rights, covenants, responsibilities, and obligations under this {clean_type}; and
WHEREAS, each Party represents that it has full legal power, capacity, and authority to enter into and execute this Agreement.

NOW, THEREFORE, in consideration of the mutual covenants, promises, and valuable considerations contained herein, the receipt and sufficiency of which are hereby acknowledged, the Parties agree as follows:

CLAUSE 1. DEFINITIONS AND INTERPRETATION
1.1 "Effective Date" means the date first written above.
1.2 "Applicable Law" refers to all relevant statutes, rules, regulations, and judicial orders in {jur}.
1.3 Terms defined in the singular shall include the plural and vice versa unless the context clearly indicates otherwise.

CLAUSE 2. SCOPE AND ENGAGEMENT
2.1 The Parties shall abide by and execute the agreements, services, or obligations outlined in this Agreement diligently and with professional competence.
2.2 Neither Party may assign or transfer its rights or obligations under this Agreement without the prior written consent of the other Party.
{clause_sections}
CLAUSE {len(terms_lines) + 3}. TERM AND TERMINATION
This Agreement shall commence on the Effective Date and shall continue in full force and effect until terminated by mutual written agreement or upon thirty (30) days' prior written notice in the event of a material breach by either Party.

CLAUSE {len(terms_lines) + 4}. CONFIDENTIALITY AND NON-DISCLOSURE
Each Party agrees to maintain in strict confidence all proprietary, technical, operational, and non-public business information disclosed by one Party to the other in connection with this Agreement.

CLAUSE {len(terms_lines) + 5}. GOVERNING LAW AND JURISDICTION
This Agreement shall be governed by, construed, and enforced in accordance with the laws of {jur}, without regard to its conflict of laws principles. Any legal suit, action, or proceeding arising out of or related to this Agreement shall be instituted exclusively in the competent courts situated in {jur}.

CLAUSE {len(terms_lines) + 6}. SEVERABILITY AND ENTIRE AGREEMENT
If any provision of this Agreement is held to be invalid or unenforceable, such provision shall be severed and the remaining provisions shall continue in full force and effect. This instrument constitutes the entire agreement between the Parties and supersedes all prior negotiations or understandings.

============================================================
EXECUTION AND SIGNATURE BLOCK
============================================================
IN WITNESS WHEREOF, the Parties hereto have executed this {clean_type} as of the Effective Date written above.

FIRST PARTY:
Signature: _______________________________
Printed Name: ____________________________
Title: ___________________________________
Date: {effective_date}

SECOND PARTY:
Signature: _______________________________
Printed Name: ____________________________
Title: ___________________________________
Date: {effective_date}

WITNESS 1:
Signature: _______________________________
Name: ____________________________________
Date: ____________________________________

WITNESS 2:
Signature: _______________________________
Name: ____________________________________
Date: ____________________________________
"""
    return draft.strip()


def generate_legal_document(
    document_type: str,
    parties: str,
    terms: str,
    effective_date: str,
    jurisdiction: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main AI generator function:
    1. Validates inputs
    2. Retrieves Gemini API Key
    3. Prompts Google Gemini
    4. Returns dict with generated text, model used, and metadata.
    """
    # Validation
    if not document_type or not document_type.strip():
        raise ValueError("Document Type is required.")
    if not parties or not parties.strip():
        raise ValueError("Parties Involved is required.")
    if not terms or not terms.strip():
        raise ValueError("Terms & Conditions are required.")
    if not effective_date or not effective_date.strip():
        raise ValueError("Effective Date is required.")

    # Check API key from argument, environment, or .env
    key = api_key or os.getenv("GEMINI_API_KEY", "").strip()

    structured_prompt = build_legal_prompt(
        document_type=document_type.strip(),
        parties=parties.strip(),
        terms=terms.strip(),
        effective_date=effective_date.strip(),
        jurisdiction=jurisdiction.strip() if jurisdiction else None
    )

    if not key or key in ["your_gemini_api_key_here", ""]:
        # Fallback to high-grade template generator when no API key is provided
        fallback_text = generate_template_fallback(
            document_type=document_type,
            parties=parties,
            terms=terms,
            effective_date=effective_date,
            jurisdiction=jurisdiction
        )
        return {
            "success": True,
            "document": fallback_text,
            "mode": "standard_template",
            "message": "Generated using LegalEase Standard Professional Engine (Gemini API key not configured)."
        }

    # Check if this is an OpenRouter or OpenAI-compatible key (e.g. sk-or-v1-...)
    if key.startswith("sk-or-") or key.startswith("sk-"):
        import requests
        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "LegalEase"
        }
        for model_id in ["google/gemini-2.5-flash", "google/gemini-flash-1.5", "google/gemini-2.0-flash-exp:free"]:
            try:
                payload = {
                    "model": model_id,
                    "messages": [
                        {"role": "user", "content": structured_prompt}
                    ],
                    "max_tokens": 3500
                }
                resp = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60
                )
                if resp.status_code == 200:
                    resp_data = resp.json()
                    content = resp_data["choices"][0]["message"]["content"]
                    if content and content.strip():
                        return {
                            "success": True,
                            "document": content.strip(),
                            "mode": "gemini_ai",
                            "model": model_id,
                            "message": f"Successfully generated via Google Gemini ({model_id}) on OpenRouter."
                        }
                else:
                    last_error = f"OpenRouter HTTP {resp.status_code}: {resp.text[:150]}"
            except Exception as e:
                last_error = e
                continue

    # Attempt generation using direct Gemini SDK (for Google AI Studio keys)
    # 1. Try google.genai (Google GenAI SDK)
    try:
        from google import genai
        client = genai.Client(api_key=key)
        for model_name in ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-2.0-flash"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=structured_prompt
                )
                if response and response.text:
                    return {
                        "success": True,
                        "document": response.text.strip(),
                        "mode": "gemini_ai",
                        "model": model_name,
                        "message": f"Successfully generated via Gemini AI ({model_name})."
                    }
            except Exception as e:
                last_error = e
                continue
    except ImportError:
        pass
    except Exception as e:
        last_error = e

    # 2. Try google.generativeai (Legacy Google Generative AI SDK)
    try:
        import google.generativeai as gai
        gai.configure(api_key=key)
        for model_name in ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]:
            try:
                model = gai.GenerativeModel(model_name)
                response = model.generate_content(structured_prompt)
                if response and response.text:
                    return {
                        "success": True,
                        "document": response.text.strip(),
                        "mode": "gemini_ai",
                        "model": model_name,
                        "message": f"Successfully generated via Gemini AI ({model_name})."
                    }
            except Exception as e:
                last_error = e
                continue
    except ImportError:
        pass
    except Exception as e:
        last_error = e

    # If Gemini failed due to quota/network, return template with clear warning
    fallback_text = generate_template_fallback(
        document_type=document_type,
        parties=parties,
        terms=terms,
        effective_date=effective_date,
        jurisdiction=jurisdiction
    )
    return {
        "success": True,
        "document": fallback_text,
        "mode": "fallback_after_error",
        "error_detail": str(last_error),
        "message": f"Gemini API error ({str(last_error)[:120]}...). Document successfully generated using LegalEase Standard Professional Engine."
    }
