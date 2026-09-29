import re
from typing import Dict, List, Any

def clean_text_for_export(text: str) -> str:
    """
    Cleans markdown formatting artifacts (excessive asterisks, hashtags, backticks)
    while preserving clean legal headings, spacing, and numbering.
    """
    if not text:
        return ""
    
    # Replace markdown bold/italic asterisks: **text** -> text
    cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    cleaned = re.sub(r"\*(.*?)\*", r"\1", cleaned)
    # Replace markdown headings: ### Heading -> Heading
    cleaned = re.sub(r"^#{1,6}\s*", "", cleaned, flags=re.MULTILINE)
    # Replace backticks
    cleaned = cleaned.replace("`", "")
    
    # Normalize bullet points
    cleaned = re.sub(r"^\s*[\*\-]\s+", "• ", cleaned, flags=re.MULTILINE)
    
    return cleaned.strip()


def parse_document_sections(text: str) -> Dict[str, Any]:
    """
    Splits document into semantic legal blocks:
    - title
    - preamble
    - clauses
    - signature_block
    """
    lines = [line.strip() for line in text.splitlines()]
    non_empty = [l for l in lines if l]
    
    title = non_empty[0] if non_empty else "LEGAL DOCUMENT DRAFT"
    # Remove markdown formatting from title
    title = re.sub(r"[\*#_]", "", title).strip()

    word_count = len(re.findall(r"\w+", text))
    char_count = len(text)
    
    # Count clauses (e.g. CLAUSE 1, SECTION 1, 1.0, 1.)
    clause_matches = re.findall(r"(?:CLAUSE|SECTION|ARTICLE)\s+\d+|^\d+\.\s+[A-Z]", text, flags=re.MULTILINE | re.IGNORECASE)
    clause_count = max(len(clause_matches), 1)

    return {
        "title": title,
        "word_count": word_count,
        "char_count": char_count,
        "clause_count": clause_count,
        "estimated_reading_minutes": max(1, round(word_count / 180))
    }


def format_for_display(text: str) -> str:
    """
    Ensures clean paragraph breaks and consistent indentation.
    """
    cleaned = clean_text_for_export(text)
    return cleaned
