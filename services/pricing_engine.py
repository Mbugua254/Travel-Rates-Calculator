# services/pricing_engine.py

def calculate_per_person_rates(contract: dict) -> dict:
    """
    Returns the commissioned and marked-up rates per person for each season.
    Does NOT calculate totals based on guest count.
    """

    result = {"hotel": contract["hotel_name"], "seasons": []}

    for season in contract["seasons"]:
        season_result = {
            "name": season["name"],
            "start_date": season["start_date"],
            "end_date": season["end_date"],
            "rates": {}
        }

        commission = season["commission"]
        markup = commission / 2  # half commission rule

        # Adults
        season_result["rates"]["pps"] = round(season["rates"]["pps"] * (1 + markup/100), 2)
        season_result["rates"]["single"] = round(season["rates"]["single"] * (1 + markup/100), 2)

        # Kids
        kids_prices = []
        if season["kids_policy"]["allowed"]:
            for rule in season["kids_policy"]["rules"]:
                if rule["type"] == "FREE":
                    price = 0
                elif rule["type"] == "FIXED":
                    price = rule["value"]
                elif rule["type"] == "PERCENT_PPS":
                    price = season_result["rates"]["pps"] * (rule["value"]/100)
                kids_prices.append({
                    "min_age": rule["min_age"],
                    "max_age": rule["max_age"],
                    "price": round(price, 2)
                })
        season_result["rates"]["kids"] = kids_prices

        result["seasons"].append(season_result)

    return result
