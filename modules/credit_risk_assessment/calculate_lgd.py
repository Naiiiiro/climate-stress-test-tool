import pandas as pd
from ..stressed_collateral_ratio_module import calculate_stressed_collateral_value

# Define scenarios and result dictionary
scenarios = [
    "基準情境", "2050淨零轉型 2030", "2050淨零轉型 2050",
    "無序轉型 2030", "無序轉型 2050", "無政策情境 2030",
    "無政策情境 2050", "無政策情境 2090"
]
result = {scenario: [] for scenario in scenarios}
para = {
    "2050淨零轉型 2030": 1.0, 
    "2050淨零轉型 2050": 1.2, 
    "無序轉型 2030": 1.2, 
    "無序轉型 2050": 1.2, 
    "無政策情境 2030": 1.0,  
    "無政策情境 2050": 1.2, 
    "無政策情境 2090": 1.2
}

def process_LGD_domestic_corporate_credit(file_path):
    """
    Process LGD for domestic corporate credits based on different scenarios.

    Parameters:
    file_path (str): Path to the Excel file containing input data.

    Returns:
    tuple: Results for different scenarios.
    """
    data = pd.read_excel(file_path)

    for index, row in data.iterrows():
        if pd.isna(row['客戶名']) or not row['客戶名']:
            continue

        company_data = {
            'city_input': str(row['登記縣市']),
            'district_input': str(row['登記鄉鎮市區']),
            'industry': row['行業別'],
            'collateral_city_input': str(row['擔保品縣市']),
            'collateral_district_input': str(row['擔保品鄉鎮市區']),
            'collateral_value': float(row['擔保品價值']),
            'credit': float(row['授信金額']),
            'is_real_estate': str(row['是否有不動產擔保品']),
            'is_collateral': str(row['是否有其他擔保品']), 
            'recovery_rate': float(row['擔保品/無擔回收率(%)']) if '擔保品/無擔回收率(%)' in row and not pd.isna(row['擔保品/無擔回收率(%)']) else float(75)
        }

        if company_data['is_real_estate'] == '是':
            for scenario in scenarios:
                if scenario == "基準情境":
                    result_entry = {
                        '客戶名': str(row['客戶名']),
                        '情境': "基準情境",
                        'LGD(%)': 1 - company_data['recovery_rate']
                    }
                    result["基準情境"].append(result_entry)
                else:
                    stressed_collateral_value = calculate_stressed_collateral_value(
                        company_data['collateral_city_input'], 
                        company_data['collateral_district_input'], 
                        company_data['collateral_value']
                    )
                    if stressed_collateral_value: 
                        for scenario, ratio in stressed_collateral_value.items():
                            stressed_LGD = max(1 - (ratio * 75 / 100 / company_data['credit']), 10 / 100)
                            result_entry = {
                                '客戶名': str(row['客戶名']),
                                '情境': scenario,
                                'LGD(%)': stressed_LGD
                            }
                            result[scenario].append(result_entry)
                    else:
                        for scenario in scenarios:
                            result_entry = {
                                '客戶名': str(row['客戶名']),
                                '情境': scenario,
                                'LGD(%)': float('nan')
                            }
                            result[scenario].append(result_entry)

        elif company_data['is_collateral'] == '是':
            for scenario in scenarios:
                if scenario == "基準情境":
                    result_entry = {
                        '客戶名': str(row['客戶名']),
                        '情境': "基準情境",
                        'LGD(%)': 1 - company_data['recovery_rate']
                    }
                    result["基準情境"].append(result_entry)
                else:
                    stressed_LGD = max(1 - (company_data['collateral_value'] * float(company_data['recovery_rate']) / 100 / para[scenario]) / company_data['credit'], 10 / 100)
                    result_entry = {
                        '客戶名': str(row['客戶名']),
                        '情境': scenario,
                        'LGD(%)': stressed_LGD
                    }
                    result[scenario].append(result_entry)

        else:
            for scenario in scenarios:
                if scenario == "基準情境":
                    result_entry = {
                        '客戶名': str(row['客戶名']),
                        '情境': "基準情境",
                        'LGD(%)': 1 - company_data['recovery_rate']
                    }
                    result["基準情境"].append(result_entry)
                else:
                    stressed_LGD = max(1 - (company_data['collateral_value'] * float(company_data['recovery_rate']) / 100 / para[scenario]) / company_data['credit'], 10 / 100)
                    result_entry = {
                        '客戶名': str(row['客戶名']),
                        '情境': scenario,
                        'LGD(%)': stressed_LGD
                    }
                    result[scenario].append(result_entry)

    return (result["基準情境"], result["2050淨零轉型 2030"], result["無序轉型 2030"], 
            result["無政策情境 2030"], result["2050淨零轉型 2050"], result["無序轉型 2050"], 
            result["無政策情境 2050"], result["無政策情境 2090"])

def process_LGD_domestic_personal_mortgage(file_path):
    """
    Process LGD for domestic personal mortgage based on different scenarios.

    Parameters:
    file_path (str): Path to the Excel file containing input data.

    Returns:
    tuple: Results for different scenarios.
    """
    data = pd.read_excel(file_path)

    for index, row in data.iterrows():
        if pd.isna(row['客戶名']) or not row['客戶名']:
            continue

        company_data = {
            'collateral_city_input': str(row['擔保品縣市']),
            'collateral_district_input': str(row['擔保品鄉鎮市區']),
            'collateral_value': float(row['擔保品價值']),
            'credit': float(row['授信金額']),
        }

        result_entry = {
            '客戶名': str(row['客戶名']),
            '情境': "基準情境",
            'LGD(%)': max(1 - (company_data['collateral_value'] * 75 / 100 / company_data['credit']), 10 / 100)
        }
        result["基準情境"].append(result_entry)

        stressed_collateral_value = calculate_stressed_collateral_value(
            company_data['collateral_city_input'], 
            company_data['collateral_district_input'], 
            company_data['collateral_value']
        )

        for scenario, ratio in stressed_collateral_value.items():
            stressed_LGD = max(1 - (ratio * 75 / 100 / company_data['credit']), 10 / 100)
            result_entry = {
                '客戶名': str(row['客戶名']),
                '情境': scenario,
                'LGD(%)': stressed_LGD
            }
            result[scenario].append(result_entry)

    return (result["基準情境"], result["2050淨零轉型 2030"], result["無序轉型 2030"], 
            result["無政策情境 2030"], result["2050淨零轉型 2050"], result["無序轉型 2050"], 
            result["無政策情境 2050"], result["無政策情境 2090"])

def process_LGD_domestic_personal_other(file_path):
    """
    Process LGD for domestic personal other credits based on different scenarios.

    Parameters:
    file_path (str): Path to the Excel file containing input data.

    Returns:
    tuple: Results for different scenarios.
    """
    data = pd.read_excel(file_path)

    for index, row in data.iterrows():
        if pd.isna(row['客戶名']) or not row['客戶名']:
            continue

        company_data = {
            'collateral_value': float(row['擔保品價值']),
            'credit': float(row['授信金額']),
            'recovery_rate': float(row['擔保品/無擔回收率(%)']) if not pd.isna(row['擔保品/無擔回收率(%)']) else float(75),
            'is_collateral': str(row['是否有擔保品'])
        }

        for scenario in scenarios:
            if scenario == '基準情境':
                LGD = max(1 - (company_data['collateral_value'] * company_data['recovery_rate'] / 100) / company_data['credit'], 10 / 100)
            else:
                if company_data['is_collateral'] == '是':
                    stressed_LGD = max(1 - (company_data['collateral_value'] * company_data['recovery_rate'] / 100 / para[scenario]) / company_data['credit'], 10 / 100)
                else:
                    stressed_LGD = max(1 - (company_data['credit'] * company_data['recovery_rate'] / 100 / para[scenario]) / company_data['credit'], 10 / 100)
                LGD = stressed_LGD

            result_entry = {
                '客戶名': str(row['客戶名']),
                '情境': scenario,
                'LGD(%)': LGD
            }
            result[scenario].append(result_entry)

    return (
        result["基準情境"], result["2050淨零轉型 2030"], result["無序轉型 2030"], 
        result["無政策情境 2030"], result["2050淨零轉型 2050"], result["無序轉型 2050"], 
        result["無政策情境 2050"], result["無政策情境 2090"]
    )

def process_LGD_overseas_credit(file_path):
    """
    Process LGD for overseas credits based on different scenarios.

    Parameters:
    file_path (str): Path to the Excel file containing input data.

    Returns:
    tuple: Results for different scenarios.
    """
    data = pd.read_excel(file_path)

    for index, row in data.iterrows():
        if pd.isna(row['客戶名']) or not row['客戶名']:
            continue

        company_data = {
            'collateral_value': float(row['擔保品價值']),
            'credit': float(row['授信金額']),
            'recovery_rate': float(row['擔保品/無擔回收率(%)']) if not pd.isna(row['擔保品/無擔回收率(%)']) else float(75),
            'is_collateral': str(row['是否有擔保品'])
        }

        for scenario in scenarios:
            if scenario == '基準情境':
                if company_data['is_collateral'] == '是':
                    LGD = max(1 - (company_data['collateral_value'] * company_data['recovery_rate'] / 100) / company_data['credit'], 10 / 100)
                else:
                    LGD = max(1 - (company_data['credit'] * company_data['recovery_rate'] / 100) / company_data['credit'], 10 / 100)
            else:
                if company_data['is_collateral'] == '是':
                    stressed_LGD = max(1 - (company_data['collateral_value'] * company_data['recovery_rate'] / 100 / para[scenario]) / company_data['credit'], 10 / 100)
                else:
                    stressed_LGD = max(1 - (company_data['credit'] * company_data['recovery_rate'] / 100 / para[scenario]) / company_data['credit'], 10 / 100)
                LGD = stressed_LGD

            result_entry = {
                '客戶名': str(row['客戶名']),
                '情境': scenario,
                'LGD(%)': LGD
            }
            result[scenario].append(result_entry)

    return (
        result["基準情境"], result["2050淨零轉型 2030"], result["無序轉型 2030"], 
        result["2050淨零轉型 2050"], result["無序轉型 2050"]
    )

def process_LGD_domestic_investment(file_path):
    """
    Process LGD for domestic investments based on different scenarios.

    Parameters:
    file_path (str): Path to the Excel file containing input data.

    Returns:
    tuple: Results for different scenarios.
    """
    data = pd.read_excel(file_path)
    
    result = {
        "基準情境": [],
        "2050淨零轉型 2030": [],
        "無序轉型 2030": [],
        "無政策情境 2030": [],
        "2050淨零轉型 2050": [],
        "無序轉型 2050": [],
        "無政策情境 2050": [],
        "無政策情境 2090": []
    }
    
    for index, row in data.iterrows():
        if pd.isna(row['客戶名']) or not row['客戶名']:
            continue

        company_data = {
            'city_input': str(row['登記縣市']),
            'district_input': str(row['登記鄉鎮市區']),
            'industry': row['行業別'],
            'collateral_city_input': str(row['擔保品縣市']),
            'collateral_district_input': str(row['擔保品鄉鎮市區']),
            'collateral_value': float(row['擔保品價值']),
            'credit': float(row['授信金額']),
            'is_real_estate': str(row['是否有不動產擔保品']).strip() == '是',
            'is_collateral': str(row['是否有其他擔保品']).strip() == '是',
            'recovery_rate': float(row['擔保品/無擔回收率(%)']) if not pd.isna(row['擔保品/無擔回收率(%)']) else float(75)
        }

        if company_data['is_real_estate']:
            result_entry = {
                '客戶名': str(row['客戶名']),
                '情境': "基準情境",
                'LGD(%)': 1 - company_data['recovery_rate'] / 100
            }
            result["基準情境"].append(result_entry)
            
            stressed_collateral_value = calculate_stressed_collateral_value(
                company_data['collateral_city_input'], 
                company_data['collateral_district_input'], 
                company_data['collateral_value']
            )
            if stressed_collateral_value:
                for scenario, ratio in stressed_collateral_value.items():
                    stressed_LGD = max(1 - (ratio * 75 / 100 / company_data['credit']), 10 / 100)
                    result_entry = {
                        '客戶名': str(row['客戶名']),
                        '情境': scenario,
                        'LGD(%)': stressed_LGD
                    }
                    result[scenario].append(result_entry)
            else:
                for scenario in scenarios:
                    result_entry = {
                        '客戶名': str(row['客戶名']),
                        '情境': scenario,
                        'LGD(%)': float('nan')
                    }
                    result[scenario].append(result_entry)

        elif company_data['is_collateral']:
            result_entry = {
                '客戶名': str(row['客戶名']),
                '情境': "基準情境",
                'LGD(%)': 1 - company_data['recovery_rate'] / 100
            }
            result["基準情境"].append(result_entry)

            for scenario in scenarios:
                stressed_LGD = max(1 - (company_data['collateral_value'] * company_data['recovery_rate'] / 100) / company_data['credit'], 10 / 100)
                result_entry = {
                    '客戶名': str(row['客戶名']),
                    '情境': scenario,
                    'LGD(%)': stressed_LGD
                }
                result[scenario].append(result_entry)

        else:
            result_entry = {
                '客戶名': str(row['客戶名']),
                '情境': "基準情境",
                'LGD(%)': float('nan')
            }
            result["基準情境"].append(result_entry)

            for scenario in scenarios:
                stressed_LGD = max(1 - (company_data['credit'] * company_data['recovery_rate'] / 100) / company_data['credit'], 10 / 100)
                result_entry = {
                    '客戶名': str(row['客戶名']),
                    '情境': scenario,
                    'LGD(%)': stressed_LGD
                }
                result[scenario].append(result_entry)

    return (result["基準情境"], result["2050淨零轉型 2030"], result["無序轉型 2030"], 
            result["無政策情境 2030"], result["2050淨零轉型 2050"], result["無序轉型 2050"], 
            result["無政策情境 2050"], result["無政策情境 2090"])

def process_LGD_overseas_investment(file_path):
    """
    Process LGD for overseas investments based on different scenarios.

    Parameters:
    file_path (str): Path to the Excel file containing input data.

    Returns:
    tuple: Results for different scenarios.
    """
    data = pd.read_excel(file_path)
    result = {scenario: [] for scenario in scenarios}

    for index, row in data.iterrows():
        if pd.isna(row['客戶名']) or not row['客戶名']:
            continue

        company_data = {
            'collateral_value': float(row['擭保品價值']),
            'credit': float(row['授信金額']),
            'recovery_rate': float(row['擭保品/無擭回收率(%)']) if not pd.isna(row['擭保品/無擭回收率(%)']) else float(75),
            'is_collateral': str(row['是否有擭保品']).strip() == '是'
        }

        for scenario in scenarios:
            if scenario == '基準情境':
                if company_data['is_collateral']:
                    LGD = max(1 - (company_data['collateral_value'] * company_data['recovery_rate'] / 100) / company_data['credit'], 10 / 100)
                else:
                    LGD = max(1 - (company_data['credit'] * company_data['recovery_rate'] / 100) / company_data['credit'], 10 / 100)
            else:
                if company_data['is_collateral']:
                    stressed_LGD = max(1 - (company_data['collateral_value'] * company_data['recovery_rate'] / 100 / para[scenario]) / company_data['credit'], 10 / 100)
                else:
                    stressed_LGD = max(1 - (company_data['credit'] * company_data['recovery_rate'] / 100 / para[scenario]) / company_data['credit'], 10 / 100)
                LGD = stressed_LGD

            result_entry = {
                '客戶名': str(row['客戶名']),
                '情境': scenario,
                'LGD(%)': LGD
            }
            result[scenario].append(result_entry)

    return (
        result["基準情境"], result["2050淨零轉型 2030"], result["無序轉型 2030"], 
        result["2050淨零轉型 2050"], result["無序轉型 2050"]
    )
