climate-stress-test-tool/
│
├── README.md
├── requirements.txt
├── climate_stress_test_tool/
│   ├── data/
│   │   ├── Industry_to_Sector/
│   │   │   └── Industry_to_Sector.json
│   │   ├── PD_Conversion/
│   │   │   └── PD_Conversion_Table_for_Domestic_Corporate_Credit.json
│   │   ├── Physical_Risk/
│   │   │   ├── collateral_value_loss_by_region_and_scenario_risk_level.json
│   │   │   ├── collateral_value_loss_percentage_by_risk_level.json
│   │   │   ├── revenue_loss_by_region_and_scenario_risk_level.json
│   │   │   └── revenue_loss_percentage_by_risk_level.json
│   │   └── Transition_Risk/
│   │       ├── impact_on_industries_percentage_by_risk_level.json
│   │       └── impact_on_industries_by_region_and_scenario_risk_level.json
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── calculate/
│   │   │   ├── __init__.py
│   │   │   ├── calculate_ead.py
│   │   │   ├── calculate_lgd.py
│   │   │   └── calculate_pd.py
│   │   ├── stressed_income/
│   │   │   ├── __init__.py
│   │   │   └── stressed_net_operating_income_module.py
│   │   ├── stressed_collateral/
│   │   │   ├── __init__.py
│   │   │   └── stressed_collateral_ratio_module.py
│   │   ├── income/
│   │   │   ├── __init__.py
│   │   │   └── net_operating_income_loss_module.py
│   │   ├── collateral/
│   │   │   ├── __init__.py
│   │   │   └── collateral_value_loss_module.py
│   │   ├── parameters/
│   │   │   ├── __init__.py
│   │   │   └── PD_parameters.py
│   │   └── industry_mapping/
│   │       ├── __init__.py
│   │       └── industry_mapping.py
│   └── main.py
└── data_files/
    ├── example_file.xlsx
    └── 氣候風險壓力測試_結果.xlsx
