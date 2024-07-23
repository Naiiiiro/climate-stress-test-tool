from decimal import Decimal, getcontext
getcontext().prec = 10

def calculate_dbr_value(consumer_unsecured_credit, annual_income):
    """
    Calculate the Debt Burden Ratio (DBR) which is the ratio of consumer unsecured credit to monthly income.
    
    Parameters:
    consumer_unsecured_credit (float): Amount of consumer unsecured credit.
    annual_income (float): Annual income.
    
    Returns:
    float: Debt Burden Ratio (DBR) or None if the calculation is not possible.
    """
    dbr = float(Decimal(consumer_unsecured_credit) / (Decimal(annual_income)/12))
    if dbr is None:
        return None
    
    return dbr

