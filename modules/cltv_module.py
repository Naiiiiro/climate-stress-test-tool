from decimal import Decimal, getcontext

# Set the precision for Decimal calculations
getcontext().prec = 10

def calculate_stressed_cltv_value(city_input, district_input, current_mortgage, collateral_value):
    """
    Calculate the ratio of the current mortgage to the stressed collateral value.

    Parameters:
    city_input (str): Name of the city.
    district_input (str): Name of the district.
    current_mortgage (float): Current mortgage loan amount.
    collateral_value (float): Value of the collateral.

    Returns:
    dict: CLTV values for different scenarios.
    """
    from .stressed_collateral_ratio_module import calculate_stressed_collateral_value
    
    # Calculate stressed collateral values for different scenarios
    stressed_collateral_value = calculate_stressed_collateral_value(
        city_input, 
        district_input, 
        collateral_value
    )
    
    if stressed_collateral_value is None:
        # If no stressed collateral values are available, return None for all scenarios
        return {scenario: None for scenario in [
            "基準情境", "2050淨零轉型 2030", "2050淨零轉型 2050",
            "無序轉型 2030", "無序轉型 2050", "無政策情境 2030",
            "無政策情境 2050", "無政策情境 2090"
        ]}
    
    # Calculate CLTV values for each scenario using Decimal for precision
    stressed_cltv_values = {scenario: float(Decimal(current_mortgage) / Decimal(value)) for scenario, value in stressed_collateral_value.items()}
    
    return stressed_cltv_values

def calculate_cltv_value(current_mortgage, collateral_value):
    """
    Calculate the ratio of the current mortgage to the collateral value.

    Parameters:
    current_mortgage (float): Current mortgage loan amount.
    collateral_value (float): Value of the collateral.

    Returns:
    float: The ratio of the current mortgage to the collateral value (CLTV).
    """
    # Calculate CLTV using Decimal for precision
    cltv = float(Decimal(current_mortgage) / Decimal(collateral_value))
    return cltv
