import json
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
region_data_path = os.path.join(current_dir, '../data/Physical_Risk/collateral_value_loss_by_region_and_scenario_risk_level.json')
risk_level_data_path = os.path.join(current_dir, '../data/Physical_Risk/collateral_value_loss_percentage_by_risk_level.json')
pd_file_path = os.path.join(current_dir, '../data/PD_Conversion/PD_Conversion_Table_for_Domestic_Corporate_Credit.json')
sector_file_path = os.path.join(current_dir, '../data/Industry_to_Sector/Industry_to_Sector.json')

with open(region_data_path, 'r', encoding='utf-8') as file:
    region_data = json.load(file)

with open(risk_level_data_path, 'r', encoding='utf-8') as file:
    risk_level_data = json.load(file)

class IndustryToSectorMapper:
    """
    A class to map industry names to their corresponding sectors based on a JSON mapping file.
    
    Attributes:
    sector_mapping (dict): A dictionary mapping sectors to industries.
    """
    def __init__(self, sector_file_path):
        """
        Initialize the mapper using the path to the JSON file.
        
        Parameters:
        sector_file_path (str): Path to the JSON file containing sector mappings.
        """
        with open(sector_file_path, 'r', encoding='utf-8') as file:
            self.sector_mapping = json.load(file)
    
    def get_sector(self, industry):
        """
        Get the sector for a given industry.
        
        Parameters:
        industry (str): Name of the industry.
        
        Returns:
        str: Sector to which the industry belongs.
        """
        for sector, industries in self.sector_mapping.items():
            if industry in industries:
                return sector
        return None

def standardize_city_name(city):
    """
    Standardize the city name by converting '台' to '臺'.
    
    Parameters:
    city (str): The city name to standardize.
    
    Returns:
    str: The standardized city name.
    """
    if '台' in city:
        city = city.replace('台', '臺')
    return city

def find_parameters(city, district, data):
    """
    Find the corresponding risk level parameters based on city and district.
    
    Parameters:
    city (str): Name of the city.
    district (str): Name of the district.
    data (list): List of data records.
    
    Returns:
    dict: The matching record.
    """
    city = standardize_city_name(city)
    for record in data:
        if record["縣市"] == city and record["鄉鎮市區"] == district:
            return record
    return None

def find_risk_level_parameters(risk_level, risk_level_data):
    """
    Find the corresponding risk level parameters based on the risk level.
    
    Parameters:
    risk_level (Decimal): Risk level.
    risk_level_data (list): List of risk level data records.
    
    Returns:
    dict: The matching record.
    """
    for record in risk_level_data:
        if record["風險等級"] == risk_level:
            return record
    return None

def query_parameters(sector, scenario, ratio, collateral_ratio, pd_data):
    """
    Query the PD parameters based on sector, scenario, operating income ratio, and collateral ratio.
    
    Parameters:
    sector (str): Sector.
    scenario (str): Scenario.
    ratio (float): Operating income ratio.
    collateral_ratio (float): Collateral ratio.
    pd_data (dict): PD data.
    
    Returns:
    float: The corresponding PD parameter.
    """
    if sector not in pd_data or scenario not in pd_data[sector]:
        return None
    
    sorted_ratio_ranges = sort_ranges(pd_data[sector][scenario].keys())
    for ratio_range in sorted_ratio_ranges:
        if in_range(ratio, ratio_range):
            collateral_dict = pd_data[sector][scenario][ratio_range]
            sorted_collateral_ranges = sort_ranges(collateral_dict.keys())
            for collateral_range in sorted_collateral_ranges:
                if in_range(collateral_ratio, collateral_range):
                    return collateral_dict[collateral_range]
    return None

def in_range(value, range_str):
    """
    Determine if a value falls within a given range string.
    
    Parameters:
    value (float): The value to check.
    range_str (str): The range string.
    
    Returns:
    bool: Whether the value falls within the range.
    """
    if isinstance(value, dict):
        return False
    if "or" in range_str:
        parts = range_str.split(" or ")
        for part in parts:
            if in_range(value, part):
                return True
        return False
    if range_str == "None":
        return value is None
    elif range_str.startswith(">="):
        return value >= float(range_str[2:])
    elif range_str.startswith(">"):
        return value > float(range_str[1:])
    elif range_str.startswith("<="):
        return value <= float(range_str[2:])
    elif range_str.startswith("<"):
        return value < float(range_str[1:])
    else:
        raise ValueError(f"Unknown range format: {range_str}")

def sort_ranges(ranges):
    """
    Sort range strings in order.
    
    Parameters:
    ranges (list): List of range strings.
    
    Returns:
    list: Sorted list of range strings.
    """
    return sorted(ranges, key=range_key, reverse=True)

def range_key(range_str):
    """
    Generate a sorting key for a range string.
    
    Parameters:
    range_str (str): The range string.
    
    Returns:
    float: Sorting key.
    """
    if "or" in range_str:
        parts = range_str.split(" or ")
        return max(range_key(part) for part in parts)
    if range_str == "None":
        return float('inf')
    elif ">=" in range_str:
        return float(range_str[2:])
    elif ">" in range_str:
        return float(range_str[1:])
    elif "<=" in range_str:
        return -float(range_str[2:])
    elif "<" in range_str:
        return -float(range_str[1:])
    else:
        raise ValueError(f"Unknown range format: {range_str}")
