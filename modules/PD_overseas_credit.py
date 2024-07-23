import json
from decimal import Decimal, getcontext

# Set the precision for Decimal calculations
getcontext().prec = 10

def load_json(file_path):
    """
    Load JSON data from a file.

    Parameters:
    file_path (str): Path to the JSON file.

    Returns:
    dict: Loaded JSON data.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def load_and_query_parameters__overseas(pd_overseas_file_path, credit_rating, downgrade):
    """
    Load and query PD parameters for overseas credits based on credit rating and downgrade scenarios.

    Parameters:
    pd_overseas_file_path (str): Path to the PD overseas JSON file.
    credit_rating (str): Current credit rating.
    downgrade (list): List of downgrade steps.

    Returns:
    list: List of PD values for the given downgrades.
    """
    with open(pd_overseas_file_path, 'r', encoding='utf-8') as file:
        pd_overseas_data = json.load(file)

    ratings_list = [
        "AAA", "AA+", "AA", "AA-", "A+", "A", "A-", 
        "BBB+", "BBB", "BBB-", "BB+", "BB", "BB-", 
        "B+", "B", "B-", "C", "CCC"
    ]

    pd_values = []

    if pd_overseas_data and credit_rating in pd_overseas_data:
        current_index = ratings_list.index(credit_rating)
        for down in downgrade:
            if isinstance(down, float):
                lower_index = int(current_index + down // 1)
                upper_index = int(current_index + down // 1 + 1)
                if lower_index < len(ratings_list) and upper_index < len(ratings_list):
                    lower_rating = ratings_list[lower_index]
                    upper_rating = ratings_list[upper_index]
                    lower_value = pd_overseas_data.get(lower_rating, None)
                    upper_value = pd_overseas_data.get(upper_rating, None)
                    if lower_value is not None and upper_value is not None:
                        average_value = (lower_value + upper_value) / 2
                        pd_values.append(average_value)
                    else:
                        pd_values.append(None)
                else:
                    pd_values.append(None)
            else:
                new_index = current_index + down
                if new_index < len(ratings_list):
                    new_rating = ratings_list[new_index]
                    pd_values.append(pd_overseas_data.get(new_rating, None))
                else:
                    pd_values.append(None)
        return pd_values
    else:
        return [None] * len(downgrade)

class RiskAssessment:
    """
    A class for assessing risks based on country, industry, and scenarios.
    """
    def __init__(self, country_file, industry_file, scenario_adjustment_table):
        """
        Initialize the RiskAssessment class.

        Parameters:
        country_file (str): Path to the JSON file containing country risk levels.
        industry_file (str): Path to the JSON file containing industry classifications.
        scenario_adjustment_table (str): Path to the JSON file containing scenario adjustments.
        """
        self.classification_data = load_json(country_file)
        self.industry_data = load_json(industry_file)
        self.scenario_adjustment_table = load_json(scenario_adjustment_table)

    def get_country_risk_level(self, country):
        """
        Get the risk level for a given country.

        Parameters:
        country (str): Country name.

        Returns:
        str: Risk level of the country.
        """
        for entry in self.classification_data['countries']:
            if country in (entry['name_chinese'], entry['name_english']):
                return entry['risk_level']
        return None

    def get_industry_risk_level(self, industry):
        """
        Get the risk level for a given industry.

        Parameters:
        industry (str): Industry name.

        Returns:
        str: Risk level of the industry.
        """
        for group, industries in self.industry_data.items():
            for entry in industries:
                if industry == entry['Industry']:
                    return group
        return None

    def get_letter_grade(self, country_risk, industry_risk):
        """
        Get the letter grade based on country and industry risk levels.

        Parameters:
        country_risk (str): Risk level of the country.
        industry_risk (str): Risk level of the industry.

        Returns:
        str: Letter grade.
        """
        if country_risk == "低":
            if industry_risk in ["Group 1", "Group 2"]:
                return 'A'
            elif industry_risk in ["Group 3", "Group 4"]:
                return 'B'
            elif industry_risk == "Group 5":
                return 'C'
        elif country_risk == "中低":
            if industry_risk == "Group 1":
                return 'A'
            elif industry_risk in ["Group 2", "Group 3"]:
                return 'B'
            elif industry_risk == "Group 4":
                return 'C'
            elif industry_risk == "Group 5":
                return 'D'
        elif country_risk == "中":
            if industry_risk in ["Group 1", "Group 2"]:
                return 'B'
            elif industry_risk == "Group 3":
                return 'C'
            elif industry_risk in ["Group 4", "Group 5"]:
                return 'D'
        elif country_risk == "中高":
            if industry_risk == "Group 1":
                return 'B'
            elif industry_risk == "Group 2":
                return 'C'
            elif industry_risk in ["Group 3", "Group 4"]:
                return 'D'
            elif industry_risk == "Group 5":
                return 'E'
        elif country_risk == "高":
            if industry_risk == "Group 1":
                return 'C'
            elif industry_risk in ["Group 2", "Group 3"]:
                return 'D'
            elif industry_risk in ["Group 4", "Group 5"]:
                return 'E'

    def process_country_industry_risk(self, country, industry):
        """
        Process the risk levels for a given country and industry, and return the scenario adjustments.

        Parameters:
        country (str): Country name.
        industry (str): Industry name.

        Returns:
        dict: Scenario adjustments based on the country and industry risk levels.
        """
        scenario_adjustments = None 
        country_risk = self.get_country_risk_level(country)
        industry_risk = self.get_industry_risk_level(industry)

        if country_risk and industry_risk:
            letter_grade = self.get_letter_grade(country_risk, industry_risk)
            scenario_adjustments = self.scenario_adjustment_table.get(letter_grade, None)
        
        return scenario_adjustments
