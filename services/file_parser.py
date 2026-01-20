import pandas as pd

def parse_excel_file(file_path: str) -> dict:
    """
    Parse hotel rates Excel file into a normalized contract object.
    Excel must have:
    - Sheet 'Rates' with columns: Season Name, Start Date, End Date, PPS, Single, Commission %, Kids Min Age, Kids Max Age, Kids Type, Kids Value
    """

    # Read Rates sheet
    rates_df = pd.read_excel(file_path, sheet_name="Rates")

    hotel_name = rates_df["Hotel Name"].iloc[0] if "Hotel Name" in rates_df.columns else "Unknown Hotel"

    seasons = []

    # Group rows by Season Name
    for season_name, group in rates_df.groupby("Season Name"):
        row = group.iloc[0]  # use first row for PPS, Single, Commission
        season_rates = {"pps": row["PPS"], "single": row["Single"]}
        commission = row["Commission %"]

        # Kids rules
        kids_policy = {"allowed": True, "rules": []}
        for _, krow in group.iterrows():
            ktype = str(krow.get("Kids Type", "")).upper()
            if ktype == "NOT_ALLOWED":
                kids_policy["allowed"] = False
                kids_policy["rules"] = []
                break
            elif ktype in ["FREE", "FIXED", "PERCENT_PPS"]:
                rule = {
                    "min_age": int(krow["Kids Min Age"]),
                    "max_age": int(krow["Kids Max Age"]),
                    "type": ktype
                }
                if ktype in ["FIXED", "PERCENT_PPS"]:
                    rule["value"] = float(krow["Kids Value"])
                kids_policy["rules"].append(rule)

        season_obj = {
            "name": season_name,
            "start_date": str(row["Start Date"].date()),
            "end_date": str(row["End Date"].date()),
            "rates": season_rates,
            "commission": float(commission),
            "markup_rule": "HALF_COMMISSION",
            "kids_policy": kids_policy
        }

        seasons.append(season_obj)

    contract = {
        "hotel_name": hotel_name,
        "seasons": seasons
    }
    return contract
