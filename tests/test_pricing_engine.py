import pytest
from services.pricing_engine import calculate_booking_price, PricingError

# Sample hotel contract for testing
hotel_contract = {
    "hotel_name": "Serena Beach",
    "seasons": [
        {
            "name": "High Season",
            "start_date": "2026-07-01",
            "end_date": "2026-08-31",
            "rates": {"pps": 150, "single": 220},
            "commission": 20,
            "markup_rule": "HALF_COMMISSION",
            "kids_policy": {
                "allowed": True,
                "rules": [
                    {"min_age": 0, "max_age": 5, "type": "FREE"},
                    {"min_age": 6, "max_age": 11, "type": "PERCENT_PPS", "value": 50}
                ]
            }
        },
        {
            "name": "Low Season",
            "start_date": "2026-11-01",
            "end_date": "2026-12-15",
            "rates": {"pps": 110, "single": 170},
            "commission": 15,
            "markup_rule": "HALF_COMMISSION",
            "kids_policy": {"allowed": False}
        }
    ]
}

def test_high_season_adults_only():
    result = calculate_booking_price(
        contract=hotel_contract,
        travel_date="2026-07-10",
        nights=2,
        adults={"pps": 2, "single": 1},
        kids_ages=[]
    )

    # PPS calculation: 150 + 10% markup = 165 per night, 2 nights = 330 per PPS adult
    # Single calculation: 220 + 10% markup = 242 per night, 2 nights = 484
    expected_total_adults = (2 * 330) + 484  # 1144
    assert result["totals"]["adults"] == expected_total_adults

def test_high_season_with_kids():
    result = calculate_booking_price(
        contract=hotel_contract,
        travel_date="2026-07-15",
        nights=1,
        adults={"pps": 2},
        kids_ages=[4, 9]
    )
    totals = result["totals"]

    # Kid age 4 → FREE
    assert any(k["price"] == 0 for k in result["kids"] if k["age"] == 4)
    # Kid age 9 → 50% of PPS 150 = 75, markup 10% = 82.5
    assert any(k["price"] == 82.5 for k in result["kids"] if k["age"] == 9)
    # Grand total should sum adults + kids
    expected_adult_total = 2 * (150*1.1)  # 2 PPS adults, 1 night
    expected_grand_total = expected_adult_total + 82.5 + 0
    assert totals["grand_total"] == round(expected_grand_total, 2)

def test_low_season_kids_not_allowed():
    with pytest.raises(PricingError):
        calculate_booking_price(
            contract=hotel_contract,
            travel_date="2026-11-05",
            nights=1,
            adults={"pps": 2},
            kids_ages=[7]
        )

def test_no_season_found():
    with pytest.raises(PricingError):
        calculate_booking_price(
            contract=hotel_contract,
            travel_date="2026-09-15",  # Not in any season
            nights=1,
            adults={"pps": 2},
            kids_ages=[]
        )
