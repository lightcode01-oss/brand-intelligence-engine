import os
import json
import csv
from typing import Any

# Try importing ReportLab with fallback if not pre-installed
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    reportlab_available = True
except ImportError:
    reportlab_available = False

def generate_export_files(data: dict, file_format: str, output_dir: str = "/tmp") -> str:
    """Compiles brand report details into JSON, CSV, Markdown, or PDF format files."""
    # Ensure local directory exists (workspaces fallback)
    workspace_tmp = "./scratch"
    os.makedirs(workspace_tmp, exist_ok=True)
    
    file_name = f"brand_report_{data.get('query', 'nomen')}.{file_format.lower()}"
    full_path = os.path.join(workspace_tmp, file_name)
    
    # 1. JSON Exporter
    if file_format.lower() == "json":
        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return full_path
        
    # 2. CSV Exporter
    elif file_format.lower() == "csv":
        with open(full_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Candidate Name", "BSI Score", "Syllables", "Pronunciation Ease"])
            for item in data.get("candidates", []):
                score = item.get("scorecard", {}).get("bsi_overall", 0)
                syls = item.get("pronunciation", {}).get("syllable_count", 0)
                ease = item.get("pronunciation", {}).get("pronounceability_score", 0)
                writer.writerow([item["name"], score, syls, ease])
        return full_path
        
    # 3. Markdown Exporter
    elif file_format.lower() == "markdown" or file_format.lower() == "md":
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(f"# Nomen Brand Intelligence Report: {data.get('query', 'Brand Naming')}\n\n")
            f.write(f"**Industry**: {data.get('industry', 'General')}\n")
            f.write(f"**Generated Candidates Count**: {len(data.get('candidates', []))}\n\n")
            f.write("| Candidate Name | BSI Score | Syllables | Pronunciation Ease |\n")
            f.write("| :--- | :---: | :---: | :---: |\n")
            for item in data.get("candidates", []):
                score = item.get("scorecard", {}).get("bsi_overall", 0)
                syls = item.get("pronunciation", {}).get("syllable_count", 0)
                ease = item.get("pronunciation", {}).get("pronounceability_score", 0)
                f.write(f"| {item['name']} | {score} | {syls} | {ease} |\n")
        return full_path
        
    # 4. ReportLab PDF Exporter
    elif file_format.lower() == "pdf":
        if not reportlab_available:
            # Safe mock fallback path if ReportLab is missing
            with open(full_path, "w", encoding="utf-8") as f:
                f.write("ReportLab not installed. Mock PDF placeholder file.")
            return full_path
            
        doc = SimpleDocTemplate(full_path, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Heading Styles
        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Heading1"],
            fontSize=24,
            textColor=colors.HexColor("#1A365D"),
            spaceAfter=15
        )
        body_style = styles["Normal"]
        
        story.append(Paragraph(f"Nomen Brand Intelligence Report", title_style))
        story.append(Paragraph(f"<b>Query Context:</b> {data.get('query', 'Nomen')}", body_style))
        story.append(Paragraph(f"<b>Target Industry:</b> {data.get('industry', 'General')}", body_style))
        story.append(Spacer(1, 15))
        
        # Table of Candidates
        table_data = [["Candidate Name", "BSI Score", "Syllables", "Pronunciation"]]
        for item in data.get("candidates", []):
            score = str(item.get("scorecard", {}).get("bsi_overall", 0))
            syls = str(item.get("pronunciation", {}).get("syllable_count", 0))
            ease = str(item.get("pronunciation", {}).get("pronounceability_score", 0))
            table_data.append([item["name"], score, syls, ease])
            
        t = Table(table_data)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A365D")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F7FAFC")),
            ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
        ]))
        story.append(t)
        
        doc.build(story)
        return full_path
        
    else:
        raise ValueError(f"Unsupported export file format: {file_format}")
