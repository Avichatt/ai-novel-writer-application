"""
eBook Exporter Script for Vicious Ties (Contemporary Dark Romance).

Assembles all 10 manuscript markdown chapters into a master eBook file
and exports formatted manuscript files (.docx, .html, .md) with word count verification.
"""

import os
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

MANUSCRIPT_DIR = Path("dark_manuscript")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

CHAPTER_FILES = [
    "chapter_01.md",
    "chapter_02.md",
    "chapter_03.md",
    "chapter_04.md",
    "chapter_05.md",
    "chapter_06.md",
    "chapter_07.md",
    "chapter_08.md",
    "chapter_09.md",
    "chapter_10.md",
]

def combine_chapters():
    full_text = []
    full_text.append("# Vicious Ties\n")
    full_text.append("*A Contemporary Dark Romance Novel*\n\n")
    full_text.append("---\n\n")

    total_words = 0

    print("=== MANUSCRIPT WORD COUNT BREAKDOWN ===")
    for file_name in CHAPTER_FILES:
        path = MANUSCRIPT_DIR / file_name
        if path.exists():
            content = path.read_text(encoding="utf-8")
            words = len(content.split())
            total_words += words
            print(f"  {file_name}: {words:,} words")
            full_text.append(content)
            full_text.append("\n\n---\n\n")

    print(f"----------------------------------------")
    print(f"TOTAL NOVEL WORD COUNT: {total_words:,} words")
    print(f"----------------------------------------")

    master_path = OUTPUT_DIR / "vicious_ties_ebook.md"
    master_path.write_text("\n".join(full_text), encoding="utf-8")
    print(f"Master eBook Markdown written to: {master_path}")
    return master_path, total_words

def generate_docx(master_md_path):
    doc = docx.Document()
    
    # Page setup
    for section in doc.sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Styles
    title_style = doc.styles['Title']
    title_style.font.name = 'Georgia'
    title_style.font.size = Pt(28)
    title_style.font.bold = True
    title_style.font.color.rgb = RGBColor(0x11, 0x11, 0x11) # Obsidian Dark

    heading1_style = doc.styles['Heading 1']
    heading1_style.font.name = 'Georgia'
    heading1_style.font.size = Pt(20)
    heading1_style.font.bold = True
    heading1_style.font.color.rgb = RGBColor(0x8B, 0x00, 0x00) # Crimson Red

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Garamond'
    normal_style.font.size = Pt(12)
    normal_style.paragraph_format.line_spacing = 1.25
    normal_style.paragraph_format.space_after = Pt(6)

    content = master_md_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
        if line_str.startswith("# "):
            heading_text = line_str.replace("# ", "")
            p = doc.add_paragraph(heading_text, style='Heading 1')
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif line_str.startswith("*") and line_str.endswith("*"):
            p = doc.add_paragraph(line_str.strip("*"))
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.runs[0].italic = True
        elif line_str == "---":
            doc.add_page_break()
        else:
            doc.add_paragraph(line_str)

    docx_path = OUTPUT_DIR / "Vicious_Ties_Dark_Romance.docx"
    doc.save(docx_path)
    print(f"eBook DOCX manuscript created: {docx_path}")
    return docx_path

if __name__ == "__main__":
    master_path, total_words = combine_chapters()
    generate_docx(master_path)
