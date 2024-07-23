import json

class PDParameterLoader:
    def __init__(self, pd_corp_file_path=None, pd_person_file_path=None, sector_file_path=None, pd_person_other_file_path=None, pd_overseas_file_path=None):
        """
        Initialize the PDParameterLoader with optional file paths to load different PD data.

        Parameters:
        pd_corp_file_path (str): Path to the corporate PD JSON file.
        pd_person_file_path (str): Path to the personal mortgage PD JSON file.
        sector_file_path (str): Path to the sector mapping JSON file.
        pd_person_other_file_path (str): Path to the other personal PD JSON file.
        pd_overseas_file_path (str): Path to the overseas PD JSON file.
        """
        self.pd_corp_data = self.load_json(pd_corp_file_path)
        self.pd_person_data = self.load_json(pd_person_file_path)
        self.pd_person_other_data = self.load_json(pd_person_other_file_path)
        self.pd_overseas_data = self.load_json(pd_overseas_file_path)
        self.mapper = self.load_sector_mapper(sector_file_path)

    def load_json(self, file_path):
        """
        Load JSON data from a given file path.

        Parameters:
        file_path (str): Path to the JSON file.

        Returns:
        dict: Loaded JSON data.
        """
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        return None

    def load_sector_mapper(self, sector_file_path):
        """
        Load the IndustryToSectorMapper if a sector file path is provided.

        Parameters:
        sector_file_path (str): Path to the sector mapping JSON file.

        Returns:
        IndustryToSectorMapper: Instance of the sector mapper.
        """
        if sector_file_path:
            from .common import IndustryToSectorMapper
            return IndustryToSectorMapper(sector_file_path)
        return None

    def query_parameters__industry(self, sector, scenario, ratio, collateral_ratio):
        """
        Query PD parameters for a given industry based on the sector, scenario, operating income ratio, and collateral ratio.

        Parameters:
        sector (str): Sector of the industry.
        scenario (str): Scenario.
        ratio (float): Operating income ratio.
        collateral_ratio (float): Collateral ratio.

        Returns:
        float: PD parameter for the given inputs.
        """
        if sector not in self.pd_corp_data or scenario not in self.pd_corp_data[sector]:
            return None

        sorted_ratio_ranges = self.sort_ranges(self.pd_corp_data[sector][scenario].keys())
        for ratio_range in sorted_ratio_ranges:
            if self.in_range(ratio, ratio_range):
                collateral_dict = self.pd_corp_data[sector][scenario][ratio_range]
                sorted_collateral_ranges = self.sort_ranges(collateral_dict.keys())
                for collateral_range in sorted_collateral_ranges:
                    if self.in_range(collateral_ratio, collateral_range):
                        return collateral_dict[collateral_range]
        return None
    
    def query_parameters__personal_mortgage(self, scenario, dbr, cltv):
        """
        Query PD parameters for personal mortgage based on the scenario, DBR, and CLTV.

        Parameters:
        scenario (str): Scenario.
        dbr (float): Debt burden ratio.
        cltv (float): Combined loan-to-value ratio.

        Returns:
        float: PD parameter for the given inputs.
        """
        if scenario not in self.pd_person_data:
            return None

        sorted_cltv_dict = self.sort_ranges(self.pd_person_data[scenario].keys())
        for cltv_range in sorted_cltv_dict:
            if self.in_range(dbr, cltv_range):
                bdr_dict = self.pd_person_data[scenario][cltv_range]
                sorted_cltv_ranges = self.sort_ranges(bdr_dict.keys())
                for cltv_range in sorted_cltv_ranges:
                    if self.in_range(cltv, cltv_range):
                        return bdr_dict[cltv_range]
        return None

    def query_parameters__personal_other(self, scenario, dbr, is_collateral):
        """
        Query PD parameters for other personal loans based on the scenario, DBR, and collateral status.

        Parameters:
        scenario (str): Scenario.
        dbr (float): Debt burden ratio.
        is_collateral (bool): Whether the loan has collateral.

        Returns:
        float: PD parameter for the given inputs.
        """
        data_section = '個人其他有擔' if is_collateral else '個人其他無擔'
        if scenario not in self.pd_person_other_data.get(data_section, {}):
            return None

        sorted_dbr_ranges = self.sort_ranges(self.pd_person_other_data[data_section][scenario].keys())
        for dbr_range in sorted_dbr_ranges:
            if self.in_range(dbr, str(dbr_range)):
                return self.pd_person_other_data[data_section][scenario][dbr_range]
        return None
        
    def load_and_query_parameters__industry(self, companies):
        """
        Load and query PD parameters for multiple companies in an industry.

        Parameters:
        companies (list): List of company data dictionaries.

        Returns:
        list: List of results with PD parameters for each company.
        """
        results = []
        for company in companies:
            industry = company.get("industry")
            sector = self.mapper.get_sector(industry) if self.mapper else None
            ratios = company.get("ratios")
            collateral_ratios = company.get("collateral_ratios")

            for scenario in ratios.keys():
                ratio = ratios[scenario]
                collateral_ratio = collateral_ratios[scenario]
                result = self.query_parameters__industry(sector, scenario, ratio, collateral_ratio)
                if result:
                    results.append({
                        "客戶名": company["client"],
                        "產業別": sector,
                        "情境": scenario,
                        "營授比": ratio,
                        "十足擔保比率": collateral_ratio,
                        "違約率": result
                    })
        return results
    
    def load_and_query_parameters__personal_mortgage(self, people):
        """
        Load and query PD parameters for multiple personal mortgage clients.

        Parameters:
        people (list): List of personal mortgage data dictionaries.

        Returns:
        list: List of results with PD parameters for each client.
        """
        results = []
        for person in people:
            dbr_values = person.get("dbr")
            cltv_values = person.get("cltv")

            for scenario in dbr_values.keys():
                dbr_value = dbr_values[scenario]
                cltv_value = cltv_values[scenario]
                result = self.query_parameters__personal_mortgage(scenario, cltv_value, dbr_value)
                if result:
                    results.append({
                        "客戶名": person["client"],
                        "情境": scenario,
                        "DBR": dbr_value,
                        "CLTV": cltv_value,
                        "違約率": result
                    })
        return results
    
    def load_and_query_parameters__personal_other(self, people):
        """
        Load and query PD parameters for multiple personal other loan clients.

        Parameters:
        people (list): List of personal other loan data dictionaries.

        Returns:
        list: List of results with PD parameters for each client.
        """
        results = []
        for person in people:
            dbr_values = person.get("dbr")
            is_collateral = person.get("is_collateral")
            for scenario in dbr_values.keys():
                dbr_value = dbr_values[scenario]
                result = self.query_parameters__personal_other(scenario, dbr_value, is_collateral)
                if result:
                    results.append({
                        "客戶名": person["client"],
                        "情境": scenario,
                        "DBR": dbr_value,
                        "違約率": result
                    })
        return results

    def in_range(self, value, range_str):
        """
        Check if a value falls within a given range string.

        Parameters:
        value (float): The value to check.
        range_str (str): The range string.

        Returns:
        bool: Whether the value falls within the range.
        """
        if isinstance(value, dict):
            return False
        try:
            if "or" in range_str:
                parts = range_str.split(" or ")
                for part in parts:
                    if self.in_range(value, part):
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
                return float(range_str) == value
        except ValueError:
            return False
        
    def sort_ranges(self, ranges):
        """
        Sort a list of range strings.

        Parameters:
        ranges (list): List of range strings.

        Returns:
        list: Sorted list of range strings.
        """
        float_ranges = []
        str_ranges = []
        for r in ranges:
            try:
                if "=" in r:
                    float_ranges.append(float(r[1:])) 
                else:
                    float_ranges.append(float(r))
            except ValueError:
                str_ranges.append(r)
        return sorted(float_ranges, reverse=True) + sorted(str_ranges, key=self.range_key, reverse=True)

    def range_key(self, range_str):
        """
        Generate a sorting key for a range string.

        Parameters:
        range_str (str): The range string.

        Returns:
        float: Sorting key.
        """
        try:
            if "or" in range_str:
                parts = range_str.split(" or ")
                return max(self.range_key(part) for part in parts)
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
            elif "=" in range_str:
                return float(range_str[1:])
            else:
                return float(range_str)
        except ValueError:
            return float(range_str)