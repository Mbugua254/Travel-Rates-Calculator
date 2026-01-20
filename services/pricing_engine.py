from datetime import datetime
from typing import List, Dict, Any


class PricingError(Exception):
    """Custom exception for pricing-related errors."""
    pass


def parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, "%Y-%m-%d")


def date_in_range(date: datetime, start: str, end: str) -> bool:
    return parse_date(start) <= date <= parse_date(end)


def get_applicable_season(seasons: List[Dict[str, Any]], travel_date: str) -> Dict[str, Any]:
    travel_date = parse_date(travel_date)

    for season in seasons:
        if date_in_range(travel_date, season["start_date"], season["end_date"]):
            return season

    raise PricingError("No applicable season found for the selected travel date.")


def calculate_markup_rate(commission_percentage: float) -> float:
    """
    Industry rule:
    Markup = half the hotel commission
    """
    return commission_percentage / 2


def calculate_adult_price(rate: float, markup_percentage: float, nights: int) -> float:
    selling_rate = rate * (1 + markup_percentage / 100)
    return round(selling_rate * nights, 2)


def calculate_kid_price(
    kid_age: int,
    kids_policy: Dict[str, Any],
    pps_rate: float,
    markup_percentage: float,
    nights: int
) -> float:
    if not kids_policy.get("allowed", True):
        raise PricingError("Kids are not allowed at this hotel for the selected season.")

    rules = kids_policy.get("rules", [])

    for rule in rules:
        if rule["min_age"] <= kid_age <= rule["max_age"]:
            rule_type = rule["type"]

            if rule_type == "FREE":
                return 0.0

            if rule_type == "FIXED":
                selling_rate = rule["value"] * (1 + markup_percentage / 100)
                return round(selling_rate * nights, 2)

            if rule_type == "PERCENT_PPS":
                base_rate = pps_rate * (rule["value"] / 100)
                selling_rate = base_rate * (1 + markup_percentage / 100)
                return round(selling_rate * nights, 2)

    raise PricingError(f"No kids pricing rule found for age {kid_age}.")


def calculate_booking_price(
    contract: Dict[str, Any],
    travel_date: str,
    nights: int,
    adults: Dict[str, int],
    kids_ages: List[int]
) -> Dict[str, Any]:
    """
    adults example:
    {
        "pps": 2,
        "single": 1
    }
    """

    season = get_applicable_season(contract["seasons"], travel_date)

    markup_percentage = calculate_markup_rate(season["commission"])

    breakdown = {
        "hotel": contract["hotel_name"],
        "season": season["name"],
        "travel_date": travel_date,
        "nights": nights,
        "adults": [],
        "kids": [],
        "totals": {
            "adults": 0.0,
            "kids": 0.0,
            "grand_total": 0.0
        }
    }

    # Adults pricing
    for rate_type, count in adults.items():
        if count <= 0:
            continue

        if rate_type not in season["rates"]:
            raise PricingError(f"Rate type '{rate_type}' not available for this season.")

        rate = season["rates"][rate_type]

        for _ in range(count):
            price = calculate_adult_price(rate, markup_percentage, nights)
            breakdown["adults"].append({
                "type": rate_type.upper(),
                "price": price
            })
            breakdown["totals"]["adults"] += price

    # Kids pricing
    for age in kids_ages:
        price = calculate_kid_price(
            kid_age=age,
            kids_policy=season.get("kids_policy", {}),
            pps_rate=season["rates"]["pps"],
            markup_percentage=markup_percentage,
            nights=nights
        )
        breakdown["kids"].append({
            "age": age,
            "price": price
        })
        breakdown["totals"]["kids"] += price

    breakdown["totals"]["grand_total"] = round(
        breakdown["totals"]["adults"] + breakdown["totals"]["kids"], 2
    )

    return breakdown
