import io
import os
import re
from fpdf import FPDF

def sanitize_pdf_text(text: str) -> str:
    """
    Sanitizes special unicode characters to ASCII/Latin-1 equivalents
    to prevent encoding errors in standard PDF fonts.
    """
    if not text:
        return ""
    replacements = {
        "\u2018": "'",   # left single quote
        "\u2019": "'",   # right single quote
        "\u201c": '"',   # left double quote
        "\u201d": '"',   # right double quote
        "\u2014": " -- ", # em dash
        "\u2013": " - ",  # en dash
        "\u2022": "* ",   # bullet
        "\u2026": "...",  # ellipsis
        "\u00a0": " ",    # non-breaking space
        "\u200b": "",     # zero-width space
        "\u00a9": "(c)",  # copyright
        "\u00ae": "(R)",  # registered
        "\u2122": "TM",   # trademark
    }
    for char, repl in replacements.items():
        text = text.replace(char, repl)
    
    # Strip markdown symbols
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text)
    text = text.replace("`", "")
    
    # Ensure latin-1 encodeable or replace unmappable chars
    return text.encode("latin-1", "replace").decode("latin-1")


class LegalPDF(FPDF):
    def __init__(self, logo_path: str = "assets/logo.png"):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.logo_path = logo_path
        self.set_auto_page_break(auto=True, margin=25)
        self.set_margins(left=20, top=25, right=20)
        self.alias_nb_pages()

    def header(self):
        # Draw header only if on page 1 and subsequent pages
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(15, 23, 42) # Navy

        # Brand Logo if available
        if os.path.exists(self.logo_path):
            try:
                self.image(self.logo_path, x=20, y=8, w=12)
                self.set_xy(35, 10)
                self.cell(100, 5, "LEGALEASE AI", 0, 0, "L")
                self.set_font("Helvetica", "", 7.5)
                self.set_text_color(100, 116, 139)
                self.set_xy(35, 15)
                self.cell(100, 4, "AI-Powered Legal Document Studio", 0, 0, "L")
            except Exception:
                self.set_xy(20, 10)
                self.cell(100, 5, "LEGALEASE AI", 0, 0, "L")
        else:
            self.set_xy(20, 10)
            self.cell(100, 5, "LEGALEASE AI", 0, 0, "L")

        # Top Right note
        self.set_font("Helvetica", "I", 7.5)
        self.set_text_color(100, 116, 139)
        self.set_xy(110, 10)
        self.cell(80, 5, "CONFIDENTIAL LEGAL DRAFT", 0, 0, "R")

        # Header rule
        self.set_draw_color(226, 232, 240)
        self.set_line_width(0.4)
        self.line(20, 21, 190, 21)
        self.ln(10)

    def footer(self):
        self.set_y(-20)
        self.set_draw_color(226, 232, 240)
        self.set_line_width(0.3)
        self.line(20, self.get_y(), 190, self.get_y())
        self.ln(2)

        # Footer Left: Disclaimer
        self.set_font("Helvetica", "I", 6.5)
        self.set_text_color(148, 163, 184)
        self.cell(120, 4, "Informational AI Draft. Does not constitute legal advice. Consult licensed legal counsel.", 0, 0, "L")

        # Footer Right: Page Number
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(100, 116, 139)
        page_str = f"Page {self.page_no()}/{{nb}}"
        self.cell(50, 4, page_str, 0, 0, "R")


def create_pdf(
    document_text: str,
    document_type: str = "Legal Document",
    effective_date: str = "",
    parties: str = "",
    logo_path: str = "assets/logo.png"
) -> io.BytesIO:
    """
    Builds a professional legal PDF document with header, footer,
    metadata box, clause sections, and signature areas.
    """
    pdf = LegalPDF(logo_path=logo_path)
    pdf.add_page()

    # Document Title extraction
    lines = [l.strip() for l in document_text.splitlines() if l.strip()]
    doc_title = document_type.upper()
    if lines:
        first_clean = sanitize_pdf_text(re.sub(r"[#\*_]", "", lines[0]).strip())
        if len(first_clean) < 100:
            doc_title = first_clean
            lines = lines[1:]

    # Document Title
    pdf.set_font("Times", "B", 16)
    pdf.set_text_color(15, 42, 92) # Dark Navy
    pdf.multi_cell(0, 8, doc_title, border=0, align="C")
    pdf.ln(3)

    # Metadata Box (Document Type, Date, Parties)
    pdf.set_fill_color(248, 250, 252) # Soft Slate
    pdf.set_draw_color(203, 213, 225) # Border
    pdf.set_line_width(0.3)
    
    # Save current Y for box
    box_start_y = pdf.get_y()
    pdf.rect(20, box_start_y, 170, 22, style="DF")
    
    pdf.set_xy(24, box_start_y + 3)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(32, 5, "DOCUMENT TYPE:", 0, 0, "L")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(50, 5, sanitize_pdf_text(document_type), 0, 0, "L")

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(32, 5, "EFFECTIVE DATE:", 0, 0, "L")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(50, 5, sanitize_pdf_text(effective_date or "As specified"), 0, 1, "L")

    pdf.set_xy(24, box_start_y + 11)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(30, 58, 138)
    pdf.cell(20, 5, "PARTIES:", 0, 0, "L")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(30, 41, 59)
    sanitized_parties = sanitize_pdf_text(parties.replace("\n", "; ")[:140])
    pdf.cell(140, 5, sanitized_parties, 0, 1, "L")

    pdf.set_y(box_start_y + 26)

    # Document Body & Clauses
    in_signature = False

    for raw_line in lines:
        line = sanitize_pdf_text(raw_line)
        if not line:
            pdf.ln(2)
            continue

        # Signature section detection
        if "EXECUTION" in line.upper() or "SIGNATURE" in line.upper() or "IN WITNESS WHEREOF" in line.upper():
            in_signature = True
            pdf.ln(4)
            pdf.set_font("Times", "B", 12)
            pdf.set_text_color(15, 42, 92)
            pdf.multi_cell(0, 6, line, border=0, align="L")
            pdf.ln(2)
            continue

        # Clause / Heading detection
        is_heading = bool(re.match(r"^(?:CLAUSE|SECTION|ARTICLE)\s+\d+|^\d+\.\s+[A-Z]|^(?:RECITALS|PARTIES|DEFINITIONS|TERMS|BACKGROUND):?", line, re.IGNORECASE))

        if is_heading:
            pdf.ln(3)
            pdf.set_font("Times", "B", 11)
            pdf.set_text_color(15, 42, 92)
            pdf.multi_cell(0, 6, line, border=0, align="L")
            pdf.ln(1)
        elif in_signature and ("Signature:" in line or "Name:" in line or "Title:" in line or "Date:" in line):
            pdf.set_font("Times", "", 10)
            pdf.set_text_color(30, 41, 59)
            pdf.set_x(26)
            pdf.cell(0, 5, line, 0, 1, "L")
        else:
            pdf.set_font("Times", "", 10)
            pdf.set_text_color(30, 41, 59)
            # Use multi_cell for regular paragraph text with clean line height
            pdf.multi_cell(0, 5, line, border=0, align="J")
            pdf.ln(2)

    # Disclaimer note at the end of PDF
    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 7.5)
    pdf.set_text_color(148, 163, 184)
    disclaimer = (
        "Legal Disclaimer: This document is an AI-generated draft for informational purposes only. "
        "It does not constitute legal advice. Please consult a qualified legal professional before using this document for legal purposes."
    )
    pdf.multi_cell(0, 4, disclaimer, border=0, align="C")

    # Output to BytesIO
    pdf_bytes = pdf.output()
    buffer = io.BytesIO(pdf_bytes)
    buffer.seek(0)
    return buffer
