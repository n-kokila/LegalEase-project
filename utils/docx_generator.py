import io
import os
import re
from datetime import datetime
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Sets background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def create_docx(
    document_text: str,
    document_type: str = "Legal Document",
    effective_date: str = "",
    parties: str = "",
    logo_path: str = "assets/logo.png"
) -> io.BytesIO:
    """
    Generates a beautifully formatted DOCX document with LegalEase branding,
    professional legal typography, headers, footers, and signature sections.
    """
    doc = Document()

    # Set page margins (1 inch)
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

        # Header
        header = section.header
        header_p = header.paragraphs[0]
        header_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        h_run = header_p.add_run("LEGALEASE AI  |  PROFESSIONAL LEGAL DOCUMENT DRAFT")
        h_run.font.name = "Calibri"
        h_run.font.size = Pt(8.5)
        h_run.font.color.rgb = RGBColor(100, 116, 139)

        # Footer
        footer = section.footer
        footer_p = footer.paragraphs[0]
        footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        f_run = footer_p.add_run("CONFIDENTIAL & PRIVILEGED  •  GENERATED VIA LEGALEASE AI PLATFORM")
        f_run.font.name = "Calibri"
        f_run.font.size = Pt(8)
        f_run.font.color.rgb = RGBColor(148, 163, 184)

    # Palette
    NAVY = RGBColor(15, 42, 92)
    SLATE = RGBColor(71, 85, 105)
    DARK = RGBColor(30, 41, 59)
    GOLD = RGBColor(217, 119, 6)

    # Top Brand / Header Table
    brand_table = doc.add_table(rows=1, cols=2)
    brand_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    brand_table.autofit = False
    brand_table.columns[0].width = Inches(4.5)
    brand_table.columns[1].width = Inches(2.0)

    # Left cell: Brand title
    left_cell = brand_table.cell(0, 0)
    lp = left_cell.paragraphs[0]
    lp.paragraph_format.space_before = Pt(0)
    lp.paragraph_format.space_after = Pt(2)
    brand_run = lp.add_run("LEGALEASE")
    brand_run.font.name = "Calibri"
    brand_run.font.size = Pt(14)
    brand_run.font.bold = True
    brand_run.font.color.rgb = NAVY

    sub_lp = left_cell.add_paragraph()
    sub_lp.paragraph_format.space_after = Pt(4)
    sub_run = sub_lp.add_run("AI-Powered Legal Document Studio")
    sub_run.font.name = "Calibri"
    sub_run.font.size = Pt(9)
    sub_run.font.color.rgb = SLATE

    # Right cell: Logo image if available
    right_cell = brand_table.cell(0, 1)
    rp = right_cell.paragraphs[0]
    rp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if os.path.exists(logo_path):
        try:
            r_run = rp.add_run()
            r_run.add_picture(logo_path, width=Inches(0.85))
        except Exception:
            pass

    # Horizontal Divider
    divider_p = doc.add_paragraph()
    divider_p.paragraph_format.space_before = Pt(4)
    divider_p.paragraph_format.space_after = Pt(16)
    d_run = divider_p.add_run("―" * 48)
    d_run.font.size = Pt(8)
    d_run.font.color.rgb = RGBColor(203, 213, 225)
    divider_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Extract Title from document text or use document_type
    lines = [l.strip() for l in document_text.splitlines() if l.strip()]
    raw_title = document_type.upper()
    if lines:
        first_line = re.sub(r"[#\*_]", "", lines[0]).strip()
        if len(first_line) < 100:
            raw_title = first_line
            # Remove title from lines to avoid duplicate
            lines = lines[1:]

    # Document Title
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_before = Pt(8)
    title_p.paragraph_format.space_after = Pt(4)
    title_run = title_p.add_run(raw_title)
    title_run.font.name = "Times New Roman"
    title_run.font.size = Pt(18)
    title_run.font.bold = True
    title_run.font.color.rgb = NAVY

    # Metadata Banner Box (if effective_date or parties provided)
    if effective_date or parties:
        meta_table = doc.add_table(rows=2, cols=2)
        meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        meta_table.columns[0].width = Inches(3.25)
        meta_table.columns[1].width = Inches(3.25)

        for row in meta_table.rows:
            for cell in row.cells:
                set_cell_background(cell, "F1F5F9")
                cell.paragraphs[0].paragraph_format.space_before = Pt(3)
                cell.paragraphs[0].paragraph_format.space_after = Pt(3)

        # Row 0
        c00 = meta_table.cell(0, 0).paragraphs[0]
        r = c00.add_run("DOCUMENT TYPE: ")
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = NAVY
        c00.add_run(document_type).font.size = Pt(8.5)

        c01 = meta_table.cell(0, 1).paragraphs[0]
        r = c01.add_run("EFFECTIVE DATE: ")
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = NAVY
        c01.add_run(effective_date or "As specified herein").font.size = Pt(8.5)

        # Row 1 (merged for parties)
        c10 = meta_table.cell(1, 0)
        c11 = meta_table.cell(1, 1)
        c10.merge(c11)
        p_row = c10.paragraphs[0]
        r = p_row.add_run("PARTIES: ")
        r.bold = True
        r.font.size = Pt(8.5)
        r.font.color.rgb = NAVY
        p_row.add_run(parties.replace("\n", "; ")[:250]).font.size = Pt(8.5)

        # Spacing after meta table
        doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # Process remaining document text
    in_signature_block = False

    for line in lines:
        line_clean = re.sub(r"^\s*#{1,6}\s*", "", line)
        line_clean = re.sub(r"\*\*(.*?)\*\*", r"\1", line_clean)
        line_clean = line_clean.strip()

        if not line_clean:
            continue

        # Check for signature header
        if "EXECUTION" in line_clean.upper() or "SIGNATURE" in line_clean.upper() or "IN WITNESS WHEREOF" in line_clean.upper():
            in_signature_block = True
            head_p = doc.add_paragraph()
            head_p.paragraph_format.space_before = Pt(18)
            head_p.paragraph_format.space_after = Pt(6)
            hrun = head_p.add_run(line_clean)
            hrun.font.name = "Times New Roman"
            hrun.font.size = Pt(12)
            hrun.font.bold = True
            hrun.font.color.rgb = NAVY
            continue

        # Check for clause / section headings
        is_heading = bool(re.match(r"^(?:CLAUSE|SECTION|ARTICLE)\s+\d+|^\d+\.\s+[A-Z]|^(?:RECITALS|PARTIES|DEFINITIONS|TERMS|BACKGROUND):?", line_clean, re.IGNORECASE))

        if is_heading:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            run = p.add_run(line_clean)
            run.font.name = "Times New Roman"
            run.font.size = Pt(11.5)
            run.font.bold = True
            run.font.color.rgb = NAVY
        elif in_signature_block and ("Signature:" in line_clean or "Name:" in line_clean or "Title:" in line_clean or "Date:" in line_clean):
            # Signature details
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.left_indent = Inches(0.25)
            run = p.add_run(line_clean)
            run.font.name = "Times New Roman"
            run.font.size = Pt(10)
            run.font.color.rgb = DARK
        else:
            # Regular legal body text
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.15
            run = p.add_run(line_clean)
            run.font.name = "Times New Roman"
            run.font.size = Pt(10.5)
            run.font.color.rgb = DARK

    # Disclaimer note at the end of DOCX
    disc_p = doc.add_paragraph()
    disc_p.paragraph_format.space_before = Pt(24)
    disc_p.paragraph_format.space_after = Pt(6)
    disc_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    disc_run = disc_p.add_run(
        "Disclaimer: This document is an AI-generated draft for informational purposes only. "
        "It does not constitute legal advice. Please consult a qualified legal professional before using this document for legal purposes."
    )
    disc_run.font.name = "Calibri"
    disc_run.font.size = Pt(8)
    disc_run.font.italic = True
    disc_run.font.color.rgb = RGBColor(148, 163, 184)

    # Save to BytesIO
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
