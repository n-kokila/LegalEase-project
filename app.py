import os
import io
import time
import json
from datetime import datetime, date
from pathlib import Path
import requests
import streamlit as st
from dotenv import load_dotenv

# Load local environment
load_dotenv()

# Internal imports for direct generation fallback
try:
    from ai_core.gemini_generator import generate_legal_document, DOCUMENT_TYPES
    from utils.docx_generator import create_docx
    from utils.pdf_generator import create_pdf
    from utils.document_formatter import clean_text_for_export, parse_document_sections
except ImportError:
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from ai_core.gemini_generator import generate_legal_document, DOCUMENT_TYPES
    from utils.docx_generator import create_docx
    from utils.pdf_generator import create_pdf
    from utils.document_formatter import clean_text_for_export, parse_document_sections

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="LegalEase – AI-Powered Legal Document Generator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- BACKEND API CONFIG ---
def resolve_backend_url() -> str:
    env_url = os.getenv("BACKEND_URL")
    if env_url:
        return env_url.rstrip("/")
    port_file = Path(__file__).resolve().parent / ".backend_port"
    if port_file.exists():
        try:
            port = port_file.read_text(encoding="utf-8").strip()
            if port.isdigit():
                return f"http://127.0.0.1:{port}"
        except Exception:
            pass
    return "http://127.0.0.1:8000"

BACKEND_URL = resolve_backend_url()
LOGO_PATH = os.path.join(os.path.dirname(__file__), "assets", "logo.png")

# --- CUSTOM CSS (Modern Legal-Tech Theme) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&display=swap');

    :root {
        --primary: #1e3a8a;
        --primary-dark: #0f172a;
        --accent: #2563eb;
        --gold: #d97706;
        --bg-light: #f8fafc;
        --card-bg: #ffffff;
        --border-color: #e2e8f0;
        --text-main: #1e293b;
        --text-muted: #64748b;
    }

    /* Overall Layout & Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text-main);
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Header & Hero Branding */
    .hero-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        color: #ffffff;
        padding: 2.2rem 2.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15), 0 8px 10px -6px rgba(15, 23, 42, 0.1);
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        margin: 0;
        color: #ffffff !important;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .hero-subtitle {
        font-size: 1.15rem;
        font-weight: 400;
        color: #93c5fd;
        margin-top: 0.5rem;
        letter-spacing: 0.01em;
    }
    .hero-tag {
        display: inline-block;
        background: rgba(255, 255, 255, 0.15);
        color: #e2e8f0;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* Feature Cards */
    .feature-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        height: 100%;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .feature-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
        border-color: #cbd5e1;
    }
    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.75rem;
    }
    .feature-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.5rem;
    }
    .feature-desc {
        font-size: 0.92rem;
        color: #64748b;
        line-height: 1.5;
    }

    /* Legal Folio Document Paper Preview */
    .legal-paper {
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 10px;
        padding: 3rem 3.5rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
        font-family: 'Merriweather', Georgia, serif;
        color: #1e293b;
        line-height: 1.8;
        font-size: 0.98rem;
        white-space: pre-wrap;
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
        position: relative;
    }
    .legal-paper::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 6px;
        background: linear-gradient(90deg, #1e3a8a, #3b82f6, #d97706);
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
    }

    /* Disclaimer Box */
    .disclaimer-box {
        background: #fffbeb;
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        padding: 1rem 1.25rem;
        margin-top: 1.5rem;
        font-size: 0.88rem;
        color: #92400e;
        line-height: 1.5;
    }

    /* Metric Badges */
    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #f1f5f9;
        color: #334155;
        padding: 5px 12px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid #e2e8f0;
    }

    /* Buttons Styling */
    div.stButton > button:first-child {
        background-color: #1e3a8a;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 0.55rem 1.25rem;
        transition: all 0.2s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #1d4ed8;
        box-shadow: 0 4px 12px rgba(30, 58, 138, 0.25);
    }

    /* Status indicators */
    .status-badge-online {
        color: #16a34a;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .status-badge-offline {
        color: #d97706;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# --- PRESET EXAMPLES FOR QUICK TESTING ---
SAMPLE_PRESETS = {
    "Select a preset...": None,
    "Non-Disclosure Agreement (NDA)": {
        "document_type": "NDA",
        "parties": "Disclosing Party: Apex Technologies Inc. (100 Innovation Way, Austin, TX)\nReceiving Party: Quantum Consulting Group LLC (500 Market St, San Francisco, CA)",
        "terms": "1. Confidential Information encompasses technical architectures, source code, neural network models, customer lists, and financial roadmaps.\n2. Non-disclosure obligations remain binding for a period of three (3) years from the Effective Date.\n3. Receiving Party shall apply reasonable degree of care and restrict access to authorized personnel under written confidentiality obligations.\n4. Exclusions include information that enters public domain through no fault of Receiving Party.",
        "effective_date": date.today(),
        "jurisdiction": "State of Delaware"
    },
    "Freelance Work Contract": {
        "document_type": "Freelance Work Contract",
        "parties": "Client: Horizon Media Group Inc. (New York, NY)\nFreelancer: Elena Vance (Independent UI/UX Design Specialist, Seattle, WA)",
        "terms": "1. Scope: High-fidelity mobile app design, wireframes, component library, and interactive prototypes.\n2. Compensation: Total fixed project fee of $7,500 payable in 3 milestones (30% upfront deposit, 40% upon prototype approval, 30% upon final design handoff).\n3. Intellectual Property: Complete assignment of all work product to Client upon receipt of full payment.\n4. Timeline: Project duration of 6 weeks commencing from Effective Date.",
        "effective_date": date.today(),
        "jurisdiction": "State of New York"
    },
    "Residential Lease Agreement": {
        "document_type": "Lease Agreement",
        "parties": "Landlord: Sterling Property Holdings LLC\nTenant: Marcus Wright and Samantha Wright",
        "terms": "1. Leased Premises: Apartment 4B, 742 Evergreen Terrace, Springfield.\n2. Term: Fixed term of 12 months.\n3. Rent: Monthly rent of $2,400 payable on the first day of each calendar month.\n4. Security Deposit: $2,400 refundable upon lease termination subject to property condition inspection.\n5. Utilities: Water and trash included; electricity and gas paid by Tenant.",
        "effective_date": date.today(),
        "jurisdiction": "State of Illinois"
    },
    "Employment Offer Letter": {
        "document_type": "Employment Offer Letter",
        "parties": "Employer: CloudScale Systems Inc. (San Jose, CA)\nCandidate: David Chen (Candidate for Senior DevOps Engineer)",
        "terms": "1. Position: Senior DevOps Engineer reporting to the VP of Engineering.\n2. Annual Base Salary: $165,000 paid semi-monthly.\n3. Benefits: Comprehensive healthcare coverage, 401(k) with 4% employer match, 20 days paid time off.\n4. Equity: Option grant of 15,000 stock units vesting over 4 years with a 1-year cliff.\n5. At-will employment status.",
        "effective_date": date.today(),
        "jurisdiction": "State of California"
    },
    "Legal Notice": {
        "document_type": "Legal Notice",
        "parties": "Sender / Claimant: Precision Industrial Supplies Ltd. (represented by Counsel)\nRecipient / Addressee: Global Logistics Hub Corp.",
        "terms": "1. Formal demand for immediate settlement of unpaid invoices totaling $34,800 under Purchase Order #PO-8821.\n2. Services and hardware goods were duly delivered and accepted on July 15, 2026.\n3. Recipient is granted fifteen (15) business days from receipt of this notice to cure the default.\n4. Failure to remit payment will result in the immediate commencement of legal proceedings without further notice.",
        "effective_date": date.today(),
        "jurisdiction": "State of Texas"
    }
}

# --- INITIALIZE SESSION STATE ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"
if "generated_document" not in st.session_state:
    st.session_state.generated_document = ""
if "generation_metadata" not in st.session_state:
    st.session_state.generation_metadata = {}
if "document_type" not in st.session_state:
    st.session_state.document_type = "Agreement"
if "parties_input" not in st.session_state:
    st.session_state.parties_input = ""
if "terms_input" not in st.session_state:
    st.session_state.terms_input = ""
if "effective_date_input" not in st.session_state:
    st.session_state.effective_date_input = date.today()
if "jurisdiction_input" not in st.session_state:
    st.session_state.jurisdiction_input = "Applicable State/Federal Law"
if "is_editing" not in st.session_state:
    st.session_state.is_editing = False

# --- BACKEND HEALTH CHECK ---
def check_backend_health():
    try:
        resp = requests.get(f"{BACKEND_URL}/health", timeout=1.5)
        return resp.status_code == 200
    except Exception:
        return False

backend_is_online = check_backend_health()

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=110)
    
    st.markdown("### **LegalEase AI**")
    st.caption("AI-Powered Legal Document Generator")

    # Backend Connection Status
    if backend_is_online:
        st.markdown(f'<p class="status-badge-online">🟢 FastAPI Backend: Connected ({BACKEND_URL.replace("http://", "")})</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-badge-offline">🟡 FastAPI Backend: Standalone / Internal Mode</p>', unsafe_allow_html=True)
        st.caption("Direct AI generator fallback active. Works seamlessly!")

    st.markdown("---")

    # Navigation Selection
    nav_choice = st.radio(
        "Navigation",
        options=["🏠 Home", "📝 Document Generator", "📚 Sample Templates", "ℹ️ About & Security"],
        index=0 if st.session_state.current_page == "Home" else 1
    )

    if nav_choice == "🏠 Home" and st.session_state.current_page != "Home":
        st.session_state.current_page = "Home"
        st.rerun()
    elif nav_choice == "📝 Document Generator" and st.session_state.current_page != "Generator":
        st.session_state.current_page = "Generator"
        st.rerun()
    elif nav_choice == "📚 Sample Templates" and st.session_state.current_page != "Templates":
        st.session_state.current_page = "Templates"
        st.rerun()
    elif nav_choice == "ℹ️ About & Security" and st.session_state.current_page != "About":
        st.session_state.current_page = "About"
        st.rerun()

    st.markdown("---")

    # Optional Gemini API Key configuration
    with st.expander("🔑 Gemini API Key Settings"):
        current_env_key = os.getenv("GEMINI_API_KEY", "")
        key_status = "Configured in .env" if (current_env_key and current_env_key != "your_gemini_api_key_here") else "Not configured"
        st.caption(f"Status: **{key_status}**")
        
        user_key = st.text_input("Enter/Override Gemini API Key", type="password", help="Stored only in memory during session. Get a key at https://aistudio.google.com/")
        if user_key:
            os.environ["GEMINI_API_KEY"] = user_key
            st.success("API key set for this session!")

    # Quick Presets Selector
    st.markdown("### ⚡ Quick Presets")
    st.caption("Load a pre-configured template to test instantly:")
    selected_preset = st.selectbox(
        "Choose Template Preset",
        options=list(SAMPLE_PRESETS.keys()),
        label_visibility="collapsed"
    )

    if selected_preset and selected_preset != "Select a preset...":
        preset_data = SAMPLE_PRESETS[selected_preset]
        if st.button("Apply This Preset", use_container_width=True):
            st.session_state.document_type = preset_data["document_type"]
            st.session_state.parties_input = preset_data["parties"]
            st.session_state.terms_input = preset_data["terms"]
            st.session_state.effective_date_input = preset_data["effective_date"]
            st.session_state.jurisdiction_input = preset_data["jurisdiction"]
            st.session_state.current_page = "Generator"
            st.toast(f"Loaded '{selected_preset}' preset!", icon="✅")
            st.rerun()

    st.markdown("---")
    st.caption("LegalEase v1.0.0 • Professional Legal-Tech")


# ==============================================================================
# VIEW 1: HOME PAGE
# ==============================================================================
if st.session_state.current_page == "Home":
    # Hero Section
    col_hero_text, col_hero_img = st.columns([3, 1])
    with col_hero_text:
        st.markdown("""
        <div class="hero-card">
            <h1 class="hero-title">⚖️ LegalEase</h1>
            <p class="hero-subtitle">AI-Powered Legal Document Generator</p>
            <p style="color: #cbd5e1; font-size: 0.95rem; margin-top: 0.75rem; max-width: 620px;">
                Draft attorney-grade contracts, NDAs, lease agreements, and corporate legal notices in seconds. 
                Engineered with strict legal standards, professional formatting, and instantaneous DOCX, PDF, and TXT exports.
            </p>
            <span class="hero-tag">Enterprise Legal-Tech • Powered by Google Gemini</span>
        </div>
        """, unsafe_allow_html=True)
    with col_hero_img:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=180)

    # Primary Action CTA
    col_cta1, col_cta2, col_cta3 = st.columns([1, 2, 1])
    with col_cta2:
        if st.button("🚀 Start Creating Document", use_container_width=True, type="primary"):
            st.session_state.current_page = "Generator"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # Value Proposition Cards
    st.markdown("### Why Choose LegalEase?")
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🛡️</div>
            <div class="feature-title">Strict Legal Structure</div>
            <div class="feature-desc">
                Generates complete recitals, operative clauses, governing law, severability, and formal execution & signature tables. Never invents user-provided facts.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_f2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">Google Gemini Core</div>
            <div class="feature-desc">
                Leverages advanced Gemini language models via structured prompt engineering to formulate airtight legal draft terminology with high consistency.
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_f3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📁</div>
            <div class="feature-title">Ready-to-Sign Exports</div>
            <div class="feature-desc">
                Instantly export to publication-ready PDF, editable Microsoft Word DOCX with headers/footers, or raw text format.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Supported Document Types Grid
    st.markdown("### Supported Legal Document Types")
    doc_cols = st.columns(3)
    types_list = [
        ("🔒 Non-Disclosure Agreement (NDA)", "Protect proprietary IP, trade secrets, and customer lists."),
        ("🤝 General Agreement", "Mutual rights and covenants between businesses or individuals."),
        ("📑 Commercial Contract", "Formal binding contracts for transactions and engagements."),
        ("🏠 Lease Agreement", "Residential or commercial leasing covenants, terms, and rent."),
        ("💼 Employment Contract", "Full-time or part-time staff obligations, benefits, and salary."),
        ("✉️ Employment Offer Letter", "Official corporate hiring offers, equity, and start terms."),
        ("💻 Freelance Work Contract", "Milestone-based independent contractor service covenants."),
        ("⚖️ Legal Notice", "Formal demand letters, notifications to cure defaults, or claims."),
        ("📜 Affidavit", "Sworn statements of truth, verification, and legal oaths.")
    ]

    for i, (title, desc) in enumerate(types_list):
        with doc_cols[i % 3]:
            st.markdown(f"""
            <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem;">
                <strong style="color: #1e3a8a; font-size: 0.95rem;">{title}</strong>
                <p style="color: #64748b; font-size: 0.84rem; margin: 4px 0 0 0;">{desc}</p>
            </div>
            """, unsafe_allow_html=True)


# ==============================================================================
# VIEW 2: DOCUMENT GENERATOR STUDIO
# ==============================================================================
elif st.session_state.current_page == "Generator":
    st.markdown("## 📝 Document Generator Studio")
    st.caption("Fill in the fields below to create a fully customized legal document draft.")

    # Generator Form Layout: 2 Columns (Inputs on left, Tips/Status on right)
    col_form, col_guidance = st.columns([2.3, 1])

    with col_form:
        # Document Type Selection
        doc_type_index = DOCUMENT_TYPES.index(st.session_state.document_type) if st.session_state.document_type in DOCUMENT_TYPES else 0
        selected_doc_type = st.selectbox(
            "1. Document Type *",
            options=DOCUMENT_TYPES,
            index=doc_type_index,
            help="Select the category of legal instrument to generate."
        )
        st.session_state.document_type = selected_doc_type

        # Parties Involved
        parties_input = st.text_area(
            "2. Parties Involved *",
            value=st.session_state.parties_input,
            height=90,
            placeholder="e.g.,\nParty 1: Acme Corp, 123 Tech Blvd, Austin, TX (Disclosing Party)\nParty 2: John Smith, 456 Oak Lane, Denver, CO (Receiving Party)",
            help="Specify exact names, addresses, and legal roles of all parties."
        )
        st.session_state.parties_input = parties_input

        # Dates & Jurisdiction in 2 sub-columns
        c_date, c_jur = st.columns(2)
        with c_date:
            eff_date = st.date_input(
                "3. Effective Date *",
                value=st.session_state.effective_date_input if isinstance(st.session_state.effective_date_input, date) else date.today(),
                help="The date from which this agreement takes legal effect."
            )
            st.session_state.effective_date_input = eff_date
        with c_jur:
            jur_input = st.text_input(
                "4. Governing Jurisdiction",
                value=st.session_state.jurisdiction_input,
                placeholder="e.g., State of California, United States",
                help="The governing legal jurisdiction for interpretation and disputes."
            )
            st.session_state.jurisdiction_input = jur_input

        # Terms & Conditions
        terms_input = st.text_area(
            "5. Key Terms, Covenants & Conditions *",
            value=st.session_state.terms_input,
            height=140,
            placeholder="e.g.,\n- Duration: 2 years from effective date\n- Non-disclosure of financial details and proprietary source code\n- Mutual confidentiality obligations\n- Permitted disclosures under court subpoena with 5-day prior notice",
            help="Detail the key terms, financial considerations, deliverables, restrictions, and milestones."
        )
        st.session_state.terms_input = terms_input

        # Optional Special Clauses
        with st.expander("➕ Additional Custom Instructions / Special Clauses (Optional)"):
            addl_notes = st.text_area(
                "Custom Clauses or Notes",
                placeholder="e.g., Include mandatory binding arbitration clause in San Francisco; add 10% late fee on overdue amounts.",
                height=70
            )

        # Generate Button
        col_btn, col_reset = st.columns([2, 1])
        with col_btn:
            generate_clicked = st.button("⚡ Generate Document", use_container_width=True, type="primary")
        with col_reset:
            if st.button("🔄 Clear Form", use_container_width=True):
                st.session_state.parties_input = ""
                st.session_state.terms_input = ""
                st.session_state.generated_document = ""
                st.session_state.is_editing = False
                st.rerun()

    with col_guidance:
        st.markdown("""
        <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 1.25rem;">
            <h4 style="margin-top: 0; color: #1e3a8a;">💡 Drafting Tips</h4>
            <ul style="font-size: 0.85rem; color: #475569; padding-left: 1.2rem; line-height: 1.6;">
                <li><strong>Be specific with parties:</strong> Include full legal names and organizational structures.</li>
                <li><strong>Clear dates:</strong> Use precise effective and termination dates.</li>
                <li><strong>Financial items:</strong> Mention currency, payment schedules, and milestones.</li>
                <li><strong>Strict Anti-Hallucination:</strong> Gemini is strictly prompted NOT to invent facts. Any omitted variable will use standard placeholders.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.generated_document:
            stats = parse_document_sections(st.session_state.generated_document)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("#### 📊 Document Metrics")
            st.markdown(f'<span class="badge-pill">📝 Words: {stats["word_count"]}</span>', unsafe_allow_html=True)
            st.markdown(f'<span class="badge-pill">⚖️ Clauses: {stats["clause_count"]}</span>', unsafe_allow_html=True)
            st.markdown(f'<span class="badge-pill">⏱️ Read time: ~{stats["estimated_reading_minutes"]} min</span>', unsafe_allow_html=True)

    # --- EXECUTE AI GENERATION ---
    if generate_clicked:
        # Validation checks
        if not parties_input.strip():
            st.error("⚠️ Please specify the 'Parties Involved' before generating.")
        elif not terms_input.strip():
            st.error("⚠️ Please specify the 'Terms & Conditions' before generating.")
        else:
            with st.spinner("🤖 Consulting AI legal core and formulating structured draft..."):
                formatted_date_str = eff_date.strftime("%B %d, %Y")
                generation_successful = False
                generated_text = ""
                meta_info = {}

                # 1. Attempt generation via FastAPI Backend
                if backend_is_online:
                    try:
                        payload = {
                            "document_type": selected_doc_type,
                            "parties": parties_input,
                            "terms": terms_input,
                            "dates": formatted_date_str,
                            "jurisdiction": jur_input,
                            "additional_clauses": addl_notes if 'addl_notes' in locals() else None
                        }
                        api_response = requests.post(
                            f"{BACKEND_URL}/generate",
                            json=payload,
                            timeout=45
                        )
                        if api_response.status_code == 200:
                            data = api_response.json()
                            generated_text = data.get("generated_document") or data.get("document", "")
                            meta_info = data.get("metadata", {})
                            generation_successful = True
                    except Exception as api_err:
                        st.warning(f"Backend API call encountered an issue ({str(api_err)[:60]}...). Switching to internal engine.")

                # 2. Fallback to direct generation if backend wasn't reached or returned error
                if not generation_successful:
                    try:
                        direct_res = generate_legal_document(
                            document_type=selected_doc_type,
                            parties=parties_input,
                            terms=terms_input,
                            effective_date=formatted_date_str,
                            jurisdiction=jur_input
                        )
                        generated_text = direct_res.get("document", "")
                        meta_info = {
                            "mode": direct_res.get("mode", "direct"),
                            "model": direct_res.get("model", "standard"),
                            "message": direct_res.get("message", "")
                        }
                        generation_successful = True
                    except Exception as direct_err:
                        st.error(f"❌ Document generation failed: {str(direct_err)}")

                if generation_successful and generated_text:
                    st.session_state.generated_document = generated_text
                    st.session_state.generation_metadata = meta_info
                    st.session_state.is_editing = False
                    st.success("🎉 Legal document successfully generated!")
                    st.rerun()

    # --- DOCUMENT PREVIEW & DOWNLOAD SECTION ---
    if st.session_state.generated_document:
        st.markdown("---")
        st.markdown("### 📄 Document Preview & Studio")

        # Top Action Bar for Preview (Edit Toggle + Metadata Note)
        col_bar_left, col_bar_right = st.columns([3, 1])
        with col_bar_left:
            if st.session_state.generation_metadata.get("message"):
                st.info(f"ℹ️ {st.session_state.generation_metadata.get('message')}")
        with col_bar_right:
            edit_btn_label = "👁️ View Formatted Paper" if st.session_state.is_editing else "✏️ Edit Document"
            if st.button(edit_btn_label, use_container_width=True):
                st.session_state.is_editing = not st.session_state.is_editing
                st.rerun()

        # In-Place Editor Mode OR Formatted Paper Preview Mode
        if st.session_state.is_editing:
            st.markdown("#### ✏️ In-Place Document Editor")
            st.caption("You can modify clauses, insert custom terms, or adjust signatures below. Changes will be saved to your exports.")
            edited_content = st.text_area(
                "Document Text",
                value=st.session_state.generated_document,
                height=500,
                label_visibility="collapsed"
            )
            if st.button("💾 Apply & Save Modifications", type="primary"):
                st.session_state.generated_document = edited_content
                st.session_state.is_editing = False
                st.toast("Modifications applied successfully!", icon="✅")
                st.rerun()
        else:
            # Formatted parchment view
            st.markdown(f"""
            <div class="legal-paper">
{st.session_state.generated_document}
            </div>
            """, unsafe_allow_html=True)

        # --- DOWNLOAD OPTIONS ---
        st.markdown("### 📥 Download Options")
        st.caption("Export your finalized legal document in your preferred format:")

        formatted_date_val = st.session_state.effective_date_input.strftime("%B %d, %Y") if isinstance(st.session_state.effective_date_input, date) else str(st.session_state.effective_date_input)
        clean_name_prefix = st.session_state.document_type.lower().replace(" ", "_")
        date_str = datetime.now().strftime("%Y%m%d")

        col_d1, col_d2, col_d3 = st.columns(3)

        # 1. Download as TXT
        with col_d1:
            txt_clean = clean_text_for_export(st.session_state.generated_document)
            st.download_button(
                label="📄 Download as TXT",
                data=txt_clean,
                file_name=f"{clean_name_prefix}_{date_str}.txt",
                mime="text/plain",
                use_container_width=True
            )

        # 2. Download as DOCX
        with col_d2:
            try:
                docx_buffer = create_docx(
                    document_text=st.session_state.generated_document,
                    document_type=st.session_state.document_type,
                    effective_date=formatted_date_val,
                    parties=st.session_state.parties_input,
                    logo_path=LOGO_PATH
                )
                st.download_button(
                    label="📘 Download as DOCX",
                    data=docx_buffer.getvalue(),
                    file_name=f"{clean_name_prefix}_{date_str}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error preparing DOCX: {e}")

        # 3. Download as PDF
        with col_d3:
            try:
                pdf_buffer = create_pdf(
                    document_text=st.session_state.generated_document,
                    document_type=st.session_state.document_type,
                    effective_date=formatted_date_val,
                    parties=st.session_state.parties_input,
                    logo_path=LOGO_PATH
                )
                st.download_button(
                    label="📑 Download as PDF",
                    data=pdf_buffer.getvalue(),
                    file_name=f"{clean_name_prefix}_{date_str}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error preparing PDF: {e}")

        # --- MANDATORY LEGAL DISCLAIMER ---
        st.markdown("""
        <div class="disclaimer-box">
            <strong>⚠️ Legal Disclaimer:</strong> This document is an AI-generated draft for informational purposes only. 
            It does not constitute legal advice. Please consult a qualified legal professional before using this document for legal purposes.
        </div>
        """, unsafe_allow_html=True)


# ==============================================================================
# VIEW 3: SAMPLE TEMPLATES
# ==============================================================================
elif st.session_state.current_page == "Templates":
    st.markdown("## 📚 Sample Legal Templates & Presets")
    st.caption("Explore standard legal contract frameworks available on LegalEase.")

    for title, data in SAMPLE_PRESETS.items():
        if not data:
            continue
        with st.expander(f"📋 {title} ({data['document_type']})", expanded=False):
            st.markdown(f"**Document Type:** `{data['document_type']}`")
            st.markdown(f"**Jurisdiction:** `{data['jurisdiction']}`")
            st.markdown("**Parties:**")
            st.code(data["parties"], language="text")
            st.markdown("**Key Terms:**")
            st.code(data["terms"], language="text")
            if st.button(f"Load '{title}' into Generator", key=f"btn_load_{title}"):
                st.session_state.document_type = data["document_type"]
                st.session_state.parties_input = data["parties"]
                st.session_state.terms_input = data["terms"]
                st.session_state.effective_date_input = data["effective_date"]
                st.session_state.jurisdiction_input = data["jurisdiction"]
                st.session_state.current_page = "Generator"
                st.rerun()


# ==============================================================================
# VIEW 4: ABOUT & SECURITY
# ==============================================================================
elif st.session_state.current_page == "About":
    st.markdown("## ℹ️ About LegalEase & Security Policy")
    
    st.markdown("""
    ### 🛡️ Enterprise Security & Privacy Guarantees
    1. **Zero Secret Leakage:** The Google Gemini API key is securely stored in `.env` or memory and is never exposed in client bundles or public endpoints.
    2. **Factual Fidelity Principle:** The AI core prompt forbids inventing fictitious party identities, corporate registration numbers, or unstated compensation. Standard legal brackets (`[Insert Detail]`) are utilized for unspecified data.
    3. **Ephemeral Processing:** User drafts are generated on-demand and are not saved to persistent commercial databases without your explicit command.

    ### 🛠️ Architecture Stack
    - **Backend API:** FastAPI (Python 3.11) with CORS middleware, Pydantic data schemas, and health endpoints.
    - **Frontend:** Streamlit with custom CSS legal-tech design system and in-place document editor.
    - **AI Core:** Google Gemini Generative AI (Flash & Pro models) with structured prompt templates.
    - **Document Engines:** `python-docx` for styled Microsoft Word documents, `fpdf2` for publication-ready PDF rendering.

    ### ⚖️ Legal Disclaimer
    *This application produces automated preliminary drafts for informational and productivity purposes only. It does not create an attorney-client relationship. Always have legal instruments reviewed by a licensed attorney within your applicable jurisdiction prior to execution.*
    """)
