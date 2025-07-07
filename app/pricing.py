# app/utils/pricing.py

import json
import os
from src.logger_config import PATH
# Load pricing data once
with open(os.path.join(PATH, "static", "Pricing.json"), 'r', encoding='utf-8') as f:
    pricing_data = json.load(f)

def find_exact_match(cold_type, tonnage):
    for item in pricing_data['cold_storages'][cold_type]:
        if item['capacity_ton'] == tonnage:
            item['estimated'] = False
            # Multiply prices by 10 (as per your logic)
            item['price_million_toman'] = [price * 10 for price in item['price_million_toman']]
            return item
    return None

def interpolate_value(cap1, cap2, val1, val2, target_cap):
    return val1 + ((target_cap - cap1) / (cap2 - cap1)) * (val2 - val1)

def estimate_price(cold_type, tonnage):
    items = pricing_data['cold_storages'][cold_type]
    items_sorted = sorted(items, key=lambda x: x['capacity_ton'])

    # Find base values for interpolation
    if tonnage < items_sorted[0]['capacity_ton']:
        base1, base2 = items_sorted[0], items_sorted[1]
    elif tonnage > items_sorted[-1]['capacity_ton']:
        base1, base2 = items_sorted[-2], items_sorted[-1]
    else:
        for i in range(len(items_sorted) - 1):
            if items_sorted[i]['capacity_ton'] < tonnage < items_sorted[i + 1]['capacity_ton']:
                base1, base2 = items_sorted[i], items_sorted[i + 1]
                break

    cap1 = base1['capacity_ton']
    cap2 = base2['capacity_ton']

    def interp(field):
        val1 = base1[field] if isinstance(base1[field], (int, float)) else base1[field][0]
        val2 = base2[field] if isinstance(base2[field], (int, float)) else base2[field][0]
        return round(interpolate_value(cap1, cap2, val1, val2, tonnage), 2)

    def interp_dim(index):
        return round(interpolate_value(cap1, cap2, base1['dimensions_m'][index], base2['dimensions_m'][index], tonnage), 2)

    def interp_cost(key):
        val1 = base1['cost_breakdown'][key][0]
        val2 = base2['cost_breakdown'][key][0]
        return round(interpolate_value(cap1, cap2, val1, val2, tonnage), 2)

    avg_price1 = sum(base1['price_million_toman']) / 2
    avg_price2 = sum(base2['price_million_toman']) / 2
    base_price = interpolate_value(cap1, cap2, avg_price1, avg_price2, tonnage)

    # Final price range
    price_min = round(base_price * 0.95 * 10, 2)
    price_max = round(base_price * 1.05 * 10, 2)

    return {
        "name": f"سردخانه {int(tonnage) if tonnage == int(tonnage) else tonnage} تنی",
        "capacity_ton": tonnage,
        "price_million_toman": [price_min, price_max],
        "compressor_power_hp": interp('compressor_power_hp'),
        "dimensions_m": [interp_dim(0), interp_dim(1), interp_dim(2)],
        "cost_breakdown": {
            "equipment": [round(interp_cost('equipment') * 0.95, 2), round(interp_cost('equipment') * 1.05, 2)],
            "insulation": [round(interp_cost('insulation') * 0.95, 2), round(interp_cost('insulation') * 1.05, 2)],
            "installation": [round(interp_cost('installation') * 0.95, 2), round(interp_cost('installation') * 1.05, 2)]
        },
        "estimated": True
    }
def increase_all_prices(percentage_increase: float):
    """
    Increase all relevant prices in pricing.json by a specified percentage.

    :param percentage_increase: The percentage to increase the prices (e.g., 10 for 10%).
    """
    # Load pricing data
    with open(os.path.join(PATH, "static", "Pricing.json"), 'r', encoding='utf-8') as f:
        pricing_data = json.load(f)

    # Iterate through all cold storage types and items
    for cold_type, items in pricing_data['cold_storages'].items():
        for item in items:
            # Increase price_million_toman
            item['price_million_toman'] = [
                round(price * (1 + (percentage_increase / 100))) for price in item['price_million_toman']
            ]
            # Increase equipment costs
            item['cost_breakdown']['equipment'] = [
                round(cost * (1 + (percentage_increase / 100))) for cost in item['cost_breakdown']['equipment']
            ]
            # Increase insulation costs
            item['cost_breakdown']['insulation'] = [
                round(cost * (1 + (percentage_increase / 100))) for cost in item['cost_breakdown']['insulation']
            ]
            # Increase installation costs
            item['cost_breakdown']['installation'] = [
                round(cost * (1 + (percentage_increase / 100))) for cost in item['cost_breakdown']['installation']
            ]

    # Save updated pricing data back to the JSON file
    with open(os.path.join(PATH, "static", "Pricing.json"), 'w', encoding='utf-8') as f:
        json.dump(pricing_data, f, ensure_ascii=False, indent=2)

    print(f"All relevant prices increased by {percentage_increase}% in pricing.json.")
