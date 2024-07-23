import json
from decimal import Decimal, getcontext
getcontext().prec = 10

class CollateralValueLossCalculator:
    """
    A class to calculate stressed collateral value under different scenarios.
    """

    def __init__(self, region_data_path, risk_level_data_path):
        """
        Initialize the calculator with paths to JSON data files.

        Parameters:
        region_data_path (str): Path to the JSON file containing regional risk information.
        risk_level_data_path (str): Path to the JSON file containing risk level information.
        """
        with open(region_data_path, 'r', encoding='utf-8') as file:
            self.region_data = json.load(file)

        with open(risk_level_data_path, 'r', encoding='utf-8') as file:
            self.risk_level_data = json.load(file)

    def calculate_stressed_value(self, city, district, collateral_value):
        """
        Calculate the stressed collateral value under different scenarios.

        Parameters:
        city (str): The city name.
        district (str): The district name.
        collateral_value (float): The original collateral value.

        Returns:
        dict: A dictionary of stressed collateral values for different scenarios.
        """
        from .common import find_risk_level_parameters
        record = self.find_parameters(city, district)
        if not record:
            return None 

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
                risk_level_params = find_risk_level_parameters(risk_level)
                if risk_level_params:
                    result = (Decimal(1) - Decimal(risk_level_params[scenario]) / Decimal(100)) * Decimal(collateral_value)
                    results[scenario] = float(result)

        return results