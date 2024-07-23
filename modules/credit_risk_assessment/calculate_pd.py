import math
import pandas as pd
from collections import OrderedDict
import os
from ..PD_parameters import PDParameterLoader
from ..PD_overseas_credit import RiskAssessment, load_and_query_parameters__overseas

# Define file paths
current_dir = os.path.dirname(os.path.abspath(__file__))
pd_corp_file_path = os.path.join(current_dir, '../../data/PD_Conversion/Domestic_Corporate_Credit.json')
pd_person_file_path = os.path.join(current_dir, '../../data/PD_Conversion/Domestic_Personal_Mortgage.json')
sector_file_path = os.path.join(current_dir, '../../data/Industry_to_Sector/Industry_to_Sector.json')
pd_person_other_file_path = os.path.join(current_dir, '../../data/PD_Conversion/Domestic_Personal_Other.json')
pd_overseas_file_path = os.path.join(current_dir, '../../data/PD_Conversion/Overseas_Credit.json')
country_file = os.path.join(current_dir, '../../data/Transition_Risk/classification_table_by_country.json')
industry_file = os.path.join(current_dir, '../../data/Transition_Risk/classification_table_by_industry.json')
scenario_adjustment_table = os.path.join(current_dir, '../../data/Transition_Risk/scenario_adjustment_table.json')

# Define scenarios
scenarios = ["基準情境", "2050淨零轉型 2030", "2050淨零轉型 2050", 
            "無序轉型 2030", "無序轉型 2050", 
            "無政策情境 2030", "無政策情境 2050", "無政策情境 2090"]
result = {scenario: [] for scenario in scenarios}

def process_PD_domestic_corporate_credit(file_path):
    """
    Process PD for domestic corporate credit.

    Parameters:
    file_path (str): Path to the Excel file containing input data.

    Returns:
    tuple: Results for different scenarios.
    """
    from ..stressed_collateral_ratio_module import calculate_stressed_collateral_ratio, calculate_collateral_ratio
    from ..stressed_net_operating_income_module import calculate_stressed_net_operating_income, calculate_net_operating_income
    from ..PD_parameters import PDParameterLoader

    data = pd.read_excel(file_path)
    loader = PDParameterLoader(pd_corp_file_path, pd_person_file_path, sector_file_path, pd_person_other_file_path, pd_overseas_file_path)

    results = {scenario: [] for scenario in scenarios}

    for index, row in data.iterrows():
        if pd.isna(row['客戶名']):
            continue

        company_data = {
            'city_input': str(row['登記縣市']),
            'district_input': str(row['登記鄉鎮市區']),
            'industry': row['行業別'],
            'collateral_city_input': str(row['擔保品縣市']),
            'collateral_district_input': str(row['擔保品鄉鎮市區']),
            'net_revenue': float(row['營業淨額']),
            'total_market_credit': float(row['全市場授信金額']),
            'total_credit': float(row['貸放額度']),
            'collateral_value': float(row['擔保品價值'])
        }

        # Calculate collateral and net operating income risks
        collateral_ratio = calculate_collateral_ratio(company_data['collateral_value'], company_data['total_credit'])
        net_operating_income_risk = calculate_net_operating_income(company_data['net_revenue'], company_data['total_market_credit'])
        stressed_collateral_ratio = calculate_stressed_collateral_ratio(company_data['total_credit'], company_data['collateral_city_input'], company_data['collateral_district_input'], company_data['collateral_value'])
        stressed_net_operating_income_risk = calculate_stressed_net_operating_income(company_data['net_revenue'], company_data['industry'], company_data['city_input'], company_data['district_input'], company_data['total_market_credit'])

        if net_operating_income_risk and stressed_collateral_ratio and collateral_ratio and stressed_net_operating_income_risk:
            ordered_stressed_net_operating_income_risk = OrderedDict([('基準情境', net_operating_income_risk)])
            ordered_stressed_net_operating_income_risk.update(stressed_net_operating_income_risk)
            ordered_stressed_collateral_ratio = OrderedDict([('基準情境', collateral_ratio)])
            ordered_stressed_collateral_ratio.update(stressed_collateral_ratio)
            stressed_companies = [{"client": str(row['客戶名']), "industry": company_data['industry'], "ratios": ordered_stressed_net_operating_income_risk, "collateral_ratios": ordered_stressed_collateral_ratio}]
            stressed_PD = loader.load_and_query_parameters__industry(stressed_companies)
            for stressed_PD_scenario in stressed_PD:
                scenario = stressed_PD_scenario['情境']
                collateral_ratio_value = ordered_stressed_collateral_ratio.get(scenario)
                net_operating_income_risk_value = ordered_stressed_net_operating_income_risk.get(scenario)
                if isinstance(stressed_PD_scenario["違約率"], dict):
                    para_a = stressed_PD_scenario["違約率"]["para_a"]
                    para_b = stressed_PD_scenario["違約率"]["para_b"]
                    pd_value = para_a * math.exp(para_b * net_operating_income_risk_value)
                else:
                    pd_value = stressed_PD_scenario["違約率"]
                result_entry = {
                    '客戶名': str(row['客戶名']),
                    '情境': scenario,
                    'PD(%)': pd_value,
                    '十足擔保比率': collateral_ratio_value,
                    '營授比': net_operating_income_risk_value,
                }
                results[scenario].append(result_entry)
        else:
            for scenario in results.keys():
                result_entry = {
                    '客戶名': str(row['客戶名']),
                    '情境': scenario,
                    'PD(%)': float('nan'),
                    '十足擔保比率': float('nan'),
                    '營授比': float('nan'),
                }
                results[scenario].append(result_entry)

    return (
        results["基準情境"], results["2050淨零轉型 2030"], results["無序轉型 2030"], 
        results["無政策情境 2030"], results["2050淨零轉型 2050"], results["無序轉型 2050"], 
        results["無政策情境 2050"], results["無政策情境 2090"]
    )

def process_PD_domestic_personal_mortgage(file_path):
    """
    Process PD for domestic personal mortgage based on different scenarios.

    Parameters:
    file_path (str): Path to the Excel file containing input data.

    Returns:
    tuple: Results for different scenarios.
    """
    from ..cltv_module import calculate_cltv_value, calculate_stressed_cltv_value
    from ..dbr_module import calculate_dbr_value
    data = pd.read_excel(file_path)
    loader = PDParameterLoader(pd_corp_file_path=None, pd_person_file_path=pd_person_file_path, sector_file_path=sector_file_path, pd_person_other_file_path=None, pd_overseas_file_path=None)

    for index, row in data.iterrows():
        if pd.isna(row['客戶名']):
            continue

        client_data = {
            'collateral_city_input': str(row['擔保品縣市']),
            'collateral_district_input': str(row['擔保品鄉鎮市區']),
            'collateral_value': float(row['擔保品價值']),
            'current_mortgage': float(row['貸放額度']),
            'consumer_unsecured_credit': float(row['消金無擔保授信金額']),
            'annual_income': float(row['年收入'])
        }

        # Calculate CLTV and DBR values
        cltv_value = calculate_cltv_value(client_data['current_mortgage'], client_data['collateral_value'])
        dbr_value = calculate_dbr_value(client_data['consumer_unsecured_credit'], client_data['annual_income'])
        dbr_values = {scenario: dbr_value for scenario in scenarios}

        stressed_cltv_value = calculate_stressed_cltv_value(client_data['collateral_city_input'], client_data['collateral_district_input'], client_data['current_mortgage'], client_data['collateral_value'])
        
        result_entry = {
            '客戶名': str(row['客戶名']),
            '情境': "基準情境",
            'PD(%)': float('nan'),
            'CLTV': float(cltv_value),
            'DBR': float(dbr_values['基準情境']),
        }
        result["基準情境"].append(result_entry)
        
        if dbr_values and stressed_cltv_value and cltv_value:
            stressed_cltv_value['基準情境'] = cltv_value
            stressed_clients = [{"client": str(row['客戶名']), "dbr": dbr_values, "cltv": stressed_cltv_value}]
            stressed_PD = loader.load_and_query_parameters__personal_mortgage(stressed_clients)
            for stressed_PD_scenario in stressed_PD:
                scenario = stressed_PD_scenario['情境']
                cltv_value_ = stressed_cltv_value.get(scenario)
                if isinstance(stressed_PD_scenario["違約率"], dict):
                    para_a = stressed_PD_scenario["違約率"]["para_a"]
                    para_b = stressed_PD_scenario["違約率"]["para_b"]
                    pd_value = para_a * math.exp(para_b * cltv_value_)
                else:
                    pd_value = stressed_PD_scenario["違約率"]
                result_entry = {
                    '客戶名': str(row['客戶名']),
                    '情境': scenario,
                    'PD(%)': pd_value,
                    'CLTV': cltv_value_,
                    'DBR': dbr_value,
                }
                result[scenario].append(result_entry)
        else:
            for scenario in scenarios:
                result_entry = {
                    '客戶名': str(row['客戶名']),
                    '情境': scenario,
                    'PD(%)': float('nan'),
                    'CLTV': float('nan'),
                    'DBR': float('nan'),
                }
                result[scenario].append(result_entry)

    return (
        result["基準情境"], result["2050淨零轉型 2030"], result["無序轉型 2030"], 
        result["無政策情境 2030"], result["2050淨零轉型 2050"], result["無序轉型 2050"], 
        result["無政策情境 2050"], result["無政策情境 2090"]
    )

def process_PD_domestic_personal_other(file_path):
    """
    Process PD for domestic personal other credit based on different scenarios.

    Parameters:
    file_path (str): Path to the Excel file containing input data.

    Returns:
    tuple: Results for different scenarios.
    """
    from ..dbr_module import calculate_dbr_value
    loader = PDParameterLoader(pd_corp_file_path=None, pd_person_file_path=None, sector_file_path=None, pd_person_other_file_path=pd_person_other_file_path, pd_overseas_file_path=None)

    data = pd.read_excel(file_path)

    for index, row in data.iterrows():
        if pd.isna(row['客戶名']):
            continue

        client_data = {
            'consumer_unsecured_credit': float(row['消金無擔保授信金額']),
            'annual_income': float(row['年收入']),
            'is_collateral': str(row['是否有擔保品']).strip() == '是'
        }

        # Calculate DBR value
        dbr_value = calculate_dbr_value(client_data['consumer_unsecured_credit'], client_data['annual_income'])
        dbr_values = {scenario: dbr_value for scenario in scenarios}

        result_entry = {
            '客戶名': str(row['客戶名']),
            '情境': "基準情境",
            'PD(%)': float('nan'),
            'DBR': dbr_values["基準情境"]
        }
        result["基準情境"].append(result_entry)

        if dbr_values:
            stressed_clients = [{"client": str(row['客戶名']), "dbr": dbr_values, "is_collateral": client_data['is_collateral']}]
            stressed_PD = loader.load_and_query_parameters__personal_other(stressed_clients)
            for stressed_PD_scenario in stressed_PD:
                scenario = stressed_PD_scenario['情境']
                if isinstance(stressed_PD_scenario["違約率"], dict):
                    para_a = stressed_PD_scenario["違約率"]["para_a"]
                    para_b = stressed_PD_scenario["違約率"]["para_b"]
                    pd_value = para_a * math.exp(para_b * dbr_values[scenario])
                else:
                    pd_value = stressed_PD_scenario["違約率"]
                result_entry = {
                    '客戶名': str(row['客戶名']),
                    '情境': scenario,
                    'PD(%)': pd_value,
                    'DBR': dbr_values[scenario]
                }
                result[scenario].append(result_entry)
        else:
            for scenario in scenarios:
                result_entry = {
                    '客戶名': str(row['客戶名']),
                    '情境': scenario,
                    'PD(%)': float('nan'),
                    'DBR': float('nan')
                }
                result[scenario].append(result_entry)

    return (
        result["基準情境"], result["2050淨零轉型 2030"], result["無序轉型 2030"], 
        result["無政策情境 2030"], result["2050淨零轉型 2050"], result["無序轉型 2050"], 
        result["無政策情境 2050"], result["無政策情境 2090"]
    )

def process_PD_overseas_credit(file_path):
    """
    Process PD for overseas credit based on different scenarios.

    Parameters:
    file_path (str): Path to the Excel file containing input data.

    Returns:
    tuple: Results for different scenarios.
    """
    data = pd.read_excel(file_path)
    risk_assessment = RiskAssessment(country_file, industry_file, scenario_adjustment_table)

    results = {scenario: [] for scenario in scenarios[:-3]}

    for index, row in data.iterrows():
        if pd.isna(row['客戶名']):
            continue

        # Default credit rating if not available
        credit_rating = str(row['S&P信用評級']) if not pd.isna(row['S&P信用評級']) else 'BB'
        pd_value = load_and_query_parameters__overseas(pd_overseas_file_path, credit_rating, [0])[0]

        result_entry = {
            '客戶名': str(row['客戶名']),
            '情境': "基準情境",
            'PD(%)': pd_value
        }
        results["基準情境"].append(result_entry)

        scenario_adjustments = risk_assessment.process_country_industry_risk(row['國家別'], row['行業別'])
        if scenario_adjustments:
            pd_values = load_and_query_parameters__overseas(pd_overseas_file_path, credit_rating, scenario_adjustments)

            scenario_names = ["2050淨零轉型 2030", "2050淨零轉型 2050", "無序轉型 2030", "無序轉型 2050"]

            for i, scenario in enumerate(scenario_names):
                result_entry = {
                    '客戶名': str(row['客戶名']),
                    '情境': scenario,
                    'PD(%)': pd_values[i]
                }
                results[scenario].append(result_entry)

    return (
        results["基準情境"], results["2050淨零轉型 2030"], results["2050淨零轉型 2050"], 
        results["無序轉型 2030"], results["無序轉型 2050"]
    )

def process_PD_domestic_investment(file_path):
    """
    Process PD for domestic investments based on different scenarios.

    Parameters:
    file_path (str): Path to the Excel file containing input data.

    Returns:
    tuple: Results for different scenarios.
    """
    from ..stressed_collateral_ratio_module import calculate_stressed_collateral_ratio, calculate_collateral_ratio
    from ..stressed_net_operating_income_module import calculate_stressed_net_operating_income, calculate_net_operating_income
    data = pd.read_excel(file_path)
    
    loader = PDParameterLoader(pd_corp_file_path, pd_person_file_path, sector_file_path, pd_person_other_file_path, pd_overseas_file_path)
    
    results = {scenario: [] for scenario in scenarios}
    
    for index, row in data.iterrows():
        if pd.isna(row['客戶名']):
            continue

        company_data = {
            'city_input': str(row['登記縣市']),
            'district_input': str(row['登記鄉鎮市區']),
            'industry': row['行業別'],
            'collateral_city_input': str(row['擔保品縣市']),
            'collateral_district_input': str(row['擔保品鄉鎮市區']),
            'net_revenue': float(row['營業淨額']),
            'total_market_credit': float(row['全市場授信金額']),
            'total_credit': float(row['貸放額度']),
            'collateral_value': float(row['擔保品價值'])
        }

        # Calculate collateral and net operating income risks
        collateral_ratio = calculate_collateral_ratio(company_data['collateral_value'], company_data['total_credit'])
        net_operating_income_risk = calculate_net_operating_income(company_data['net_revenue'], company_data['total_market_credit'])
        stressed_collateral_ratio = calculate_stressed_collateral_ratio(company_data['total_credit'], company_data['collateral_city_input'], company_data['collateral_district_input'], company_data['collateral_value'])
        stressed_net_operating_income_risk = calculate_stressed_net_operating_income(company_data['net_revenue'], company_data['industry'], company_data['city_input'], company_data['district_input'], company_data['total_market_credit'])

        if net_operating_income_risk and stressed_collateral_ratio and collateral_ratio and stressed_net_operating_income_risk:
            ordered_stressed_net_operating_income_risk = OrderedDict([('基準情境', net_operating_income_risk)])
            ordered_stressed_net_operating_income_risk.update(stressed_net_operating_income_risk)
            ordered_stressed_collateral_ratio = OrderedDict([('基準情境', collateral_ratio)])
            ordered_stressed_collateral_ratio.update(stressed_collateral_ratio)
            stressed_companies = [{"client": str(row['客戶名']), "industry": company_data['industry'], "ratios": ordered_stressed_net_operating_income_risk, "collateral_ratios": ordered_stressed_collateral_ratio}]
            stressed_PD = loader.load_and_query_parameters__industry(stressed_companies)
            for stressed_PD_scenario in stressed_PD:
                scenario = stressed_PD_scenario['情境']
                collateral_ratio_value = ordered_stressed_collateral_ratio.get(scenario)
                net_operating_income_risk_value = ordered_stressed_net_operating_income_risk.get(scenario)
                if isinstance(stressed_PD_scenario["違約率"], dict):
                    para_a = stressed_PD_scenario["違約率"]["para_a"]
                    para_b = stressed_PD_scenario["違約率"]["para_b"]
                    pd_value = para_a * math.exp(para_b * net_operating_income_risk_value)
                else:
                    pd_value = stressed_PD_scenario["違約率"]
                result_entry = {
                    '客戶名': str(row['客戶名']),
                    '情境': scenario,
                    'PD(%)': pd_value,
                    '十足擔保比率': collateral_ratio_value,
                    '營授比': net_operating_income_risk_value,
                }
                results[scenario].append(result_entry)
        else:
            for scenario in results.keys():
                result_entry = {
                    '客戶名': str(row['客戶名']),
                    '情境': scenario,
                    'PD(%)': float('nan'),
                    '十足擔保比率': float('nan'),
                    '營授比': float('nan'),
                }
                results[scenario].append(result_entry)

    return (
        results["基準情境"], results["2050淨零轉型 2030"], results["無序轉型 2030"], 
        results["無政策情境 2030"], results["2050淨零轉型 2050"], results["無序轉型 2050"], 
        results["無政策情境 2050"], results["無政策情境 2090"]
    )

def process_PD_overseas_investment(file_path):
    """
    Process PD for overseas investments based on different scenarios.

    Parameters:
    file_path (str): Path to the Excel file containing input data.

    Returns:
    tuple: Results for different scenarios.
    """
    data = pd.read_excel(file_path)
    risk_assessment = RiskAssessment(country_file, industry_file, scenario_adjustment_table)

    results = {scenario: [] for scenario in scenarios[:-3]}

    for index, row in data.iterrows():
        if pd.isna(row['客戶名']):
            continue

        # Default credit rating if not available
        credit_rating = str(row['S&P信用評級']) if not pd.isna(row['S&P信用評級']) else 'BB'
        pd_value = load_and_query_parameters__overseas(pd_overseas_file_path, credit_rating, [0])[0]

        result_entry = {
            '客戶名': str(row['客戶名']),
            '情境': "基準情境",
            'PD(%)': pd_value
        }
        results["基準情境"].append(result_entry)
        
        scenario_adjustments = risk_assessment.process_country_industry_risk(row['國家別'], row['行業別'])
        if scenario_adjustments:
            pd_values = load_and_query_parameters__overseas(pd_overseas_file_path, credit_rating, scenario_adjustments)
            
            scenario_names = ["2050淨零轉型 2030", "2050淨零轉型 2050", "無序轉型 2030", "無序轉型 2050"]

            for i, scenario in enumerate(scenario_names):
                result_entry = {
                    '客戶名': str(row['客戶名']),
                    '情境': scenario,
                    'PD(%)': pd_values[i]
                }
                results[scenario].append(result_entry)

    return (
        results["基準情境"], results["2050淨零轉型 2030"], results["2050淨零轉型 2050"], 
        results["無序轉型 2030"], results["無序轉型 2050"]
    )
