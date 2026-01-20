import pandas as pd
import os
from datetime import datetime

# Create folders if they don't exist
UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Data for sample Excel
data = [
    # High Season adults + kids rules
    {
        "Hotel Name": "Serena Beach",
        "Season Name": "High",
        "Start Date": datetime(2026, 7, 1),
        "End Date": datetime(2026, 8, 31),
        "PPS": 150,
        "Single": 220,
        "Commission %": 20,
        "Kids Min Age": 0,
        "Kids Max Age": 5,
        "Kids Type": "FREE",
        "Kids Value": None
    },
    {
        "Hotel Name": "Serena Beach",
        "Season Name": "High",
        "Start Date": datetime(2026, 7, 1),
        "End Date": datetime(2026, 8, 31),
        "PPS": 150,
        "Single": 220,
        "Commission %": 20,
        "Kids Min Age": 6,
        "Kids Max Age": 11,
        "Kids Type": "PERCENT_PPS",
        "Kids Value": 50
    },
    # Low Season - kids not allowed
    {
        "Hotel Name": "Serena Beach",
        "Season Name": "Low",
        "Start Date": datetime(2026, 11, 1),
        "End Date": datetime(2026, 12, 15),
        "PPS": 110,
        "Single": 170,
        "Commission %": 15,
        "Kids Min Age": None,
        "Kids Max Age": None,
        "Kids Type": "NOT_ALLOWED",
        "Kids Value": None
    }
]

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
excel_path = os.path.join(UPLOADS_DIR, "sample_rates.xlsx")
df.to_excel(excel_path, index=False, sheet_name="Rates")

print(f"Sample Excel generated at: {excel_path}")
