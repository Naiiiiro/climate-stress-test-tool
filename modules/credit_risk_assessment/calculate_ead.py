import pandas as pd

def process_EAD_domestic_corporate_credit(file_path):
    """
    Process EAD for domestic corporate credits.

    Parameters:
    file_path (str): Path to the Excel file containing input data.

    Returns:
    list: A list of dictionaries containing the company name and EAD value.
    """
    data = pd.read_excel(file_path)
    result = []

    for index, row in data.iterrows():
        if pd.isna(row['客戶名']):
            continue
        
        outstanding_loan_balance = float(row['現貸餘額']) if not pd.isna(row['現貸餘額']) else None
        off_balance_sheet_credit_equivalent_amount = float(row['表外交易信用暴險相當額']) if not pd.isna(row['表外交易信用暴險相當額']) else None

        # Calculate EAD based on available data
        if outstanding_loan_balance is not None and off_balance_sheet_credit_equivalent_amount is not None:
            EAD = outstanding_loan_balance + off_balance_sheet_credit_equivalent_amount
        elif outstanding_loan_balance is not None:
            EAD = outstanding_loan_balance
        elif off_balance_sheet_credit_equivalent_amount is not None:
            EAD = off_balance_sheet_credit_equivalent_amount
        else:
            EAD = float('nan')

        result.append({
            '客戶名': str(row['客戶名']),
            'EAD': EAD
        })

    return result

def process_EAD_domestic_personal_mortgage(file_path):
    """
    Process EAD for domestic personal mortgage credits.

    Parameters:
    file_path (str): Path to the Excel file containing input data.

    Returns:
    list: A list of dictionaries containing the company name and EAD value.
    """
    data = pd.read_excel(file_path)
    result = []

    for index, row in data.iterrows():
        if pd.isna(row['客戶名']):
            continue

        company_data = {
            'outstanding_loan_balance': float(row['現貸餘額']) if not pd.isna(row['現貸餘額']) else float('nan'),
        }

        # EAD is simply the outstanding loan balance for personal mortgage credits
        EAD = company_data['outstanding_loan_balance'] 

        result.append({
            '客戶名': str(row['客戶名']),
            'EAD': EAD
        })

    return result

def process_EAD_domestic_personal_other(file_path):
    """
    Process EAD for domestic personal other credits.

    Parameters:
    file_path (str): Path to the Excel file containing input data.

    Returns:
    list: A list of dictionaries containing the company name and EAD value.
    """
    data = pd.read_excel(file_path)
    result = []

    for index, row in data.iterrows():
        if pd.isna(row['客戶名']):
            continue

        outstanding_loan_balance = float(row['現貸餘額']) if not pd.isna(row['現貸餘額']) else None
        unused_effective_limit_of_dual_cards = float(row['本行雙卡未動用之有效額度']) if not pd.isna(row['本行雙卡未動用之有效額度']) else None

        # Calculate EAD based on available data
        if outstanding_loan_balance is not None and unused_effective_limit_of_dual_cards is not None:
            EAD = outstanding_loan_balance + unused_effective_limit_of_dual_cards
        elif outstanding_loan_balance is not None:
            EAD = outstanding_loan_balance
        elif unused_effective_limit_of_dual_cards is not None:
            EAD = unused_effective_limit_of_dual_cards
        else:
            EAD = float('nan')

        result.append({
            '客戶名': str(row['客戶名']),
            'EAD': EAD
        })

    return result

def process_EAD_overseas_credit(file_path):
    """
    Process EAD for overseas corporate credits.

    Parameters:
    file_path (str): Path to the Excel file containing input data.

    Returns:
    list: A list of dictionaries containing the company name and EAD value.
    """
    data = pd.read_excel(file_path)
    result = []

    for index, row in data.iterrows():
        if pd.isna(row['客戶名']):
            continue
        
        outstanding_loan_balance = float(row['現貸餘額']) if not pd.isna(row['現貸餘額']) else None
        off_balance_sheet_credit_equivalent_amount = float(row['表外交易信用暴險相當額']) if not pd.isna(row['表外交易信用暴險相當額']) else None

        # Calculate EAD based on available data
        if outstanding_loan_balance is not None and off_balance_sheet_credit_equivalent_amount is not None:
            EAD = outstanding_loan_balance + off_balance_sheet_credit_equivalent_amount
        elif outstanding_loan_balance is not None:
            EAD = outstanding_loan_balance
        elif off_balance_sheet_credit_equivalent_amount is not None:
            EAD = off_balance_sheet_credit_equivalent_amount
        else:
            EAD = float('nan')

        result.append({
            '客戶名': str(row['客戶名']),
            'EAD': EAD
        })

    return result

def process_EAD_domestic_investment(file_path):
    """
    Process EAD for domestic investments.

    Parameters:
    file_path (str): Path to the Excel file containing input data.

    Returns:
    list: A list of dictionaries containing the company name and EAD value.
    """
    data = pd.read_excel(file_path)
    result = []

    for index, row in data.iterrows():
        if pd.isna(row['客戶名']):
            continue
        
        outstanding_loan_balance = float(row['現貸餘額']) if not pd.isna(row['現貸餘額']) else None
        off_balance_sheet_credit_equivalent_amount = float(row['表外交易信用暴險相當額']) if not pd.isna(row['表外交易信用暴險相當額']) else None

        # Calculate EAD based on available data
        if outstanding_loan_balance is not None and off_balance_sheet_credit_equivalent_amount is not None:
            EAD = outstanding_loan_balance + off_balance_sheet_credit_equivalent_amount
        elif outstanding_loan_balance is not None:
            EAD = outstanding_loan_balance
        elif off_balance_sheet_credit_equivalent_amount is not None:
            EAD = off_balance_sheet_credit_equivalent_amount
        else:
            EAD = float('nan')

        result.append({
            '客戶名': str(row['客戶名']),
            'EAD': EAD
        })

    return result

def process_EAD_overseas_investment(file_path):
    """
    Process EAD for overseas investments.

    Parameters:
    file_path (str): Path to the Excel file containing input data.

    Returns:
    list: A list of dictionaries containing the company name and EAD value.
    """
    data = pd.read_excel(file_path)
    result = []

    for index, row in data.iterrows():
        if pd.isna(row['客戶名']):
            continue
        
        outstanding_loan_balance = float(row['現貸餘額']) if not pd.isna(row['現貸餘額']) else None
        off_balance_sheet_credit_equivalent_amount = float(row['表外交易信用暴險相當額']) if not pd.isna(row['表外交易信用暴險相當額']) else None

        # Calculate EAD based on available data
        if outstanding_loan_balance is not None and off_balance_sheet_credit_equivalent_amount is not None:
            EAD = outstanding_loan_balance + off_balance_sheet_credit_equivalent_amount
        elif outstanding_loan_balance is not None:
            EAD = outstanding_loan_balance
        elif off_balance_sheet_credit_equivalent_amount is not None:
            EAD = off_balance_sheet_credit_equivalent_amount
        else:
            EAD = float('nan')

        result.append({
            '客戶名': str(row['客戶名']),
            'EAD': EAD
        })

    return result
