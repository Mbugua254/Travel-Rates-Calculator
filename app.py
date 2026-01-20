import os
import pandas as pd
from services.file_parser import parse_excel_file
from services.pricing_engine import calculate_per_person_rates

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors

# --- Folders ---
UPLOADS_DIR = "uploads"
OUTPUTS_DIR = "outputs"
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# --- Load contract ---
excel_file = os.path.join(UPLOADS_DIR, "sample_rates.xlsx")
hotel_contract = parse_excel_file(excel_file)

# --- Calculate per-person rates ---
rates_result = calculate_per_person_rates(hotel_contract)

# --- Export to Excel ---
excel_path = os.path.join(OUTPUTS_DIR, "per_person_rates.xlsx")
rows = []

for season in rates_result["seasons"]:
    rows.append({
        "Season": season["name"],
        "Start Date": season["start_date"],
        "End Date": season["end_date"],
        "Category": "PPS",
        "Final Rate": season["rates"]["pps"]
    })
    rows.append({
        "Season": season["name"],
        "Start Date": season["start_date"],
        "End Date": season["end_date"],
        "Category": "Single",
        "Final Rate": season["rates"]["single"]
    })
    for kid in season["rates"]["kids"]:
        rows.append({
            "Season": season["name"],
            "Start Date": season["start_date"],
            "End Date": season["end_date"],
            "Category": f"Kid {kid['min_age']}-{kid['max_age']}",
            "Final Rate": kid["price"]
        })

df = pd.DataFrame(rows)
df.to_excel(excel_path, index=False)
print(f"Per-person rates exported to Excel: {excel_path}")

# --- Export to PDF ---
pdf_path = os.path.join(OUTPUTS_DIR, "per_person_rates.pdf")
doc = SimpleDocTemplate(pdf_path)
elements = []

# Table data for PDF
table_data = [["Season", "Start Date", "End Date", "Category", "Final Rate"]]
for row in rows:
    table_data.append([
        row["Season"],
        row["Start Date"],
        row["End Date"],
        row["Category"],
        row["Final Rate"]
    ])

t = Table(table_data, hAlign='LEFT')
t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.grey),
    ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
    ('ALIGN',(0,0),(-1,-1),'CENTER'),
    ('GRID', (0,0), (-1,-1), 1, colors.black)
]))
elements.append(t)
doc.build(elements)
print(f"Per-person rates exported to PDF: {pdf_path}")
