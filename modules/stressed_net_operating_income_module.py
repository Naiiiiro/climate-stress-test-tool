from .net_operating_income_loss_module import NetOperatingIncomeLossCalculator

def calculate_stressed_net_operating_income(net_revenue, industry, city, district, credit):
    from decimal import Decimal, getcontext
    getcontext().prec = 10

    calculator = NetOperatingIncomeLossCalculator(
        './data/Transition_Risk/classification_table_by_industry.json',
        './data/Transition_Risk/impact_on_industries_percentage_by_risk_level.json',
        './data/Physical_Risk/revenue_loss_by_region_and_scenario_risk_level.json',
        './data/Physical_Risk/revenue_loss_percentage_by_risk_level.json'
    )

    income_risk = calculator.get_company_risk_levels_and_impacts(
        industry,
        city,
        district
    )

    stressed_net_income_ratios = {}
    if income_risk:
        for scenario, risk_percentage in income_risk.items():
            stressed_net_income_ratios[scenario] = float(Decimal(net_revenue) * (Decimal(1) - Decimal(risk_percentage) / Decimal(100)) / Decimal(credit))
    return stressed_net_income_ratios

def calculate_net_operating_income(net_revenue, credit):
    """
    計算淨營業收入與信用額度的比例。
    
    Parameters:
    net_revenue (float): 淨營業收入。
    credit (float): 信用額度。
    
    Returns:
    float: 淨營業收入比例。
    """
    net_income_ratios = net_revenue / credit
    return net_income_ratios