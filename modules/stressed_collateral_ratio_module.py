from decimal import Decimal, getcontext
getcontext().prec = 10
from .common import standardize_city_name, find_parameters, find_risk_level_parameters

def calculate_stressed_collateral_value(city, district, collateral_value):
    """
    Calculate stressed collateral values under different scenarios.

    Parameters:
    city (str): City name.
    district (str): District name.
    collateral_value (float): Collateral value.

    Returns:
    dict: Stressed collateral values for various scenarios. If no matching parameters are found, returns an empty dictionary.
    """
    from .common import region_data, risk_level_data
    city = standardize_city_name(city)
    record = find_parameters(city, district, region_data)
    if not record:
        return {}  
    
    results = {}
    scenarios = [
        "2050淨零轉型 2030",
        "2050淨零轉型 2050",
        "無序轉型 2030",
        "無序轉型 2050",
        "無政策情境 2030",
        "無政策情境 2050",
        "無政策情境 2090"
    ]
    
    for scenario in scenarios:
        if scenario in record:
            risk_level = Decimal(record[scenario])
            risk_level_params = find_risk_level_parameters(risk_level, risk_level_data)
            if risk_level_params:
                result = (Decimal(1) - Decimal(risk_level_params[scenario]) / Decimal(100)) * Decimal(collateral_value)
                results[scenario] = float(result)
    
    return results

def calculate_stressed_collateral_ratio(total_credit, city_input, district_input, collateral_value):
    """
    Calculate stressed collateral ratios under different scenarios.

    Parameters:
    total_credit (float): Total credit amount.
    city_input (str): City name.
    district_input (str): District name.
    collateral_value (float): Collateral value.

    Returns:
    dict: Stressed collateral ratios for various scenarios.
    """
    results = calculate_stressed_collateral_value(
        city_input, 
        district_input, 
        collateral_value
    )
    if not results:
        return None
    
    stressed_collateral_ratios = {scenario: float(Decimal(val) * Decimal(0.8) / Decimal(total_credit)) for scenario, val in results.items()}
    return stressed_collateral_ratios

def calculate_collateral_ratio(collateral_value, total_credit):
    """
    Calculate the ratio of collateral value to total credit.

    Parameters:
    collateral_value (float): Collateral value.
    total_credit (float): Total credit amount.

    Returns:
    float: The ratio of collateral value to total credit.
    """
    collateral_ratio = float(Decimal(collateral_value) * Decimal(0.8) / Decimal(total_credit))
    return collateral_ratio
