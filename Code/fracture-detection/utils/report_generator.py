import os
import re
import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

def create_pdf_report(
    report_data: list,
    img_clean_path: str,
    img_detailed_path: str,
    logo_path: str,
    output_pdf_path: str,
) -> str:
 
    styles_dict = get_styles()
    doc = SimpleDocTemplate(output_pdf_path, pagesize=A4)
    story = []   
    story.append(Paragraph("AI Doctor Fracture Analysis Report", styles_dict["title"]))
    story.append(Paragraph(
        f"Date: {datetime.date.today().strftime('%B %d, %Y')}",
        styles_dict["date"]
    ))
    story.append(Paragraph(
        "This report summarises detected fracture zones and AI-guided "
        "clinical recommendations.  Scroll through the pages for detailed "
        "analysis and annotated imaging.",
        styles_dict["welcome"]
    ))
    if logo_path and os.path.exists(logo_path):
        story.append(Image(logo_path, width=5 * inch, height=5 * inch))
    else:
        story.append(Paragraph("Logo not found — skipping.", styles_dict["welcome"]))
    story.append(PageBreak())
    story.append(Paragraph("Fracture Detection Summary", styles_dict["title"]))
    story.append(Spacer(1, 10))
    table_data = [["Zone", "Uncertainty (%)", "Shift (mm)", "Shape Diff"]]
    for entry in report_data:
        table_data.append([
            entry.get("Zone", "N/A"),
            entry.get("Uncertainty (%)", "N/A"),
            entry.get("Shift (mm)", "N/A"),
            entry.get("Shape Diff", "N/A"),
        ])

    table = Table(
        table_data,
        hAlign="LEFT",
        colWidths=[2.2 * inch, 1.5 * inch, 1.5 * inch, 1.3 * inch],
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "EmojiFont"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 0.7, colors.black),
    ]))
    story.append(table)

    
    story.append(Spacer(1, 25))
    story.append(Paragraph("AI Doctor Observations", styles_dict["title"]))
    story.append(Spacer(1, 12))

    _card_style = ParagraphStyle(
        "CardStyle",
        fontName="EmojiFont",
        fontSize=10.5,
        leading=15,
        textColor=colors.black,
        spaceBefore=4,
        spaceAfter=4,
    )

    for entry in report_data:
        zone_header = f"<b>{entry.get('Zone', 'Unknown Zone')}</b>"
        summary_text = (
            f"<font color='darkblue'><b>Uncertainty:</b></font> "
            f"{entry.get('Uncertainty (%)', 'N/A')}%&nbsp;&nbsp;"
            f"<font color='darkgreen'><b>Shift:</b></font> "
            f"{entry.get('Shift (mm)', 'N/A')} mm&nbsp;&nbsp;"
            f"<font color='darkred'><b>Shape Diff:</b></font> "
            f"{entry.get('Shape Diff', 'N/A')}"
        )
        
        doctor_notes = clean_text(entry.get("AI Doctor Notes", ""))
        for label, emoji in [
            ("Severity:", "Severity:"),
            ("Findings:", "Findings:"),
            ("Advice:", "Advice:"),
            ("Nutrition Tip:", "Nutrition Tip:"),
            ("General Tip:", "General Tip:"),
        ]:
            doctor_notes = re.sub(rf"({re.escape(label)})", rf"<b>\1</b>", doctor_notes)
        doctor_notes = doctor_notes.replace("\n", "<br/>")

        card_content = f"{zone_header}<br/><br/>{summary_text}<br/><br/>{doctor_notes}"
        card_table = Table([[Paragraph(card_content, _card_style)]], colWidths=[6.5 * inch])
        card_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
            ("BOX", (0, 0), (-1, -1), 1, colors.grey),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(card_table)
        story.append(Spacer(1, 15))

    story.append(Paragraph(
        "Refer to the next pages for annotated images.",
        ParagraphStyle(
            "NextPage",
            fontName="EmojiFont",
            fontSize=12,
            textColor=colors.darkred,
            alignment=TA_CENTER,
        ),
    ))
    story.append(PageBreak())
   
    story.append(Paragraph("Detected Zones — Clean Bounding Boxes", styles_dict["title"]))
    if os.path.exists(img_clean_path):
        story.append(Image(img_clean_path, width=6 * inch, height=6 * inch))
    else:
        story.append(Paragraph("Clean image not found.", styles_dict["welcome"]))

    story.append(PageBreak())
    story.append(Paragraph("Detailed Fracture Analysis — Annotated Overlay", styles_dict["title"]))
    if os.path.exists(img_detailed_path):
        story.append(Image(img_detailed_path, width=6 * inch, height=6 * inch))
    else:
        story.append(Paragraph("Detailed image not found.", styles_dict["welcome"]))

    doc.build(story)
    print(f"Report saved → {output_pdf_path}")
    return output_pdf_path
