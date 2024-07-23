import json
from decimal import Decimal, getcontext

getcontext().prec = 10

class NetOperatingIncomeLossCalculator:
    """
    A class to calculate stressed net operating income under different scenarios.
    """

    def __init__(self, industry_level_data_path, transition_risk_level_data_path, revenue_loss_level_data_path, physical_risk_level_data_path):
        """
        Initialize the calculator with paths to JSON data files.

        Parameters:
        industry_level_data_path (str): Path to the JSON file containing industry level data.
        transition_risk_level_data_path (str): Path to the JSON file containing transition risk level data.
        revenue_loss_level_data_path (str): Path to the JSON file containing revenue loss level data.
        physical_risk_level_data_path (str): Path to the JSON file containing physical risk level data.
        """
        with open(industry_level_data_path, 'r', encoding='utf-8') as file:
            self.industry_level_data = json.load(file)

        with open(transition_risk_level_data_path, 'r', encoding='utf-8') as file:
            self.transition_risk_level_data = json.load(file)

        with open(revenue_loss_level_data_path, 'r', encoding='utf-8') as file:
            self.revenue_loss_level_data = json.load(file)

        with open(physical_risk_level_data_path, 'r', encoding='utf-8') as file:
            self.physical_risk_level_data = json.load(file)

    def find_parameters(self, industry):
        """
        Find risk level parameters based on industry name.

        Parameters:
        industry (str): The industry name.

        Returns:
        dict: The matching record from the dataset.
        """
        for group_number, (group_name, records) in enumerate(self.industry_level_data.items(), start=1):
            for record in records:
                if record.get("Industry") == industry:
                    return {"Group": group_number, "Risk Level": group_number, "Record": record}
        return None

    def find_region_risk_level(self, county, township):
        """
        Find region risk level based on county and township.

        Parameters:
        county (str): The county name.
        township (str): The township name.

        Returns:
        dict: The matching record from the dataset.
        """
        from .common import standardize_city_name
        county = standardize_city_name(county)
        township = standardize_city_name(township)
        for record in self.revenue_loss_level_data:
            if record["縣市"] == county and record["鄉鎮市區"] == township:
                return record
        return None

    def get_company_risk_levels_and_impacts(self, industry, city, district):
        """
        Calculate company risk levels and impacts.

        Parameters:
        industry (str): The industry name.
        city (str): The city name.
        district (str): The district name.

        Returns:
        dict: A dictionary of total impact percentages for different scenarios.
        """
        company = {}
        
        # Find transition risk levels
        risk_info = self.find_parameters(industry)
        if risk_info:
            risk_level = risk_info["Risk Level"]
            for impact in self.transition_risk_level_data:
                if impact["風險等級"] == risk_level:
                    company["Transition Impact Percentages"] = {k: v for k, v in impact.items() if k != "風險等級" and k != "百分位數"}
                    break
        else:
            company["Transition Impact Percentages"] = None

        # Find physical risk levels
        region_info = self.find_region_risk_level(city, district)
        if region_info:
            company["Physical Impact Percentages"] = {}
            for scenario, risk_level in region_info.items():
                if scenario in self.physical_risk_level_data[0]:
                    for impact in self.physical_risk_level_data:
                        if impact["風險等級"] == risk_level:
                            company["Physical Impact Percentages"][scenario] = impact[scenario]
                            break
        else:
            company["Physical Impact Percentages"] = None

        company["Total Impact Percentages"] = {}
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
            transition_impact = company["Transition Impact Percentages"].get(scenario, 0) if company["Transition Impact Percentages"] else 0
            physical_impact = company["Physical Impact Percentages"].get(scenario, 0) if company["Physical Impact Percentages"] else 0
            company["Total Impact Percentages"][scenario] = float(Decimal(transition_impact) + Decimal(physical_impact))

        return company["Total Impact Percentages"]