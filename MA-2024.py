import numpy as np
from tabulate import tabulate

def calculate_wacc(risk_free_rate, market_return, beta, market_cap, debt, cash, tax_rate=0.21):
    cost_of_equity = risk_free_rate + beta * (market_return - risk_free_rate)
    total_value = market_cap + debt - cash
    weight_equity = market_cap / total_value
    weight_debt = (debt - cash) / total_value
    cost_of_debt = 0.04  # Assuming a 4% cost of debt
    wacc = weight_equity * cost_of_equity + weight_debt * cost_of_debt * (1 - tax_rate)
    return wacc

def dcf_valuation(fcf_projections, terminal_growth, discount_rate):
    years = len(fcf_projections)
    terminal_value = fcf_projections[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
    pv_factors = [(1 + discount_rate) ** -i for i in range(1, years + 1)]
    pv_fcf = sum(np.multiply(fcf_projections, pv_factors))
    pv_terminal = terminal_value * pv_factors[-1]
    return pv_fcf + pv_terminal

def calculate_fcf_with_margin_expansion(known_fcf_values, revenue_growth_rates, initial_margin, target_margin, years_to_target):
    """Calculate FCF considering margin expansion after known FCF values"""
    fcf = known_fcf_values.copy()  # Start with known FCF values
    
    # Calculate the revenue for the last known year
    last_known_revenue = known_fcf_values[-1] / (initial_margin + (target_margin - initial_margin) * (len(known_fcf_values)-1) / years_to_target)
    current_revenue = last_known_revenue
    
    # Calculate the current margin after known years
    current_margin = initial_margin + (target_margin - initial_margin) * len(known_fcf_values) / years_to_target
    margin_step = (target_margin - initial_margin) / years_to_target
    
    # Process remaining years
    for year, growth in enumerate(revenue_growth_rates[len(known_fcf_values):]):
        # Update margin (only if still in expansion period)
        if year + len(known_fcf_values) < years_to_target:
            current_margin += margin_step
        elif year + len(known_fcf_values) >= years_to_target:
            current_margin = target_margin
            
        # Calculate next year's revenue and FCF
        current_revenue = current_revenue * (1 + growth)
        next_fcf = current_revenue * current_margin
        fcf.append(next_fcf)
    
    return fcf

def calculate_yearly_share_count(initial_shares, buyback_rate, years):
    shares = [initial_shares]
    for _ in range(years - 1):
        shares.append(shares[-1] * (1 - buyback_rate))
    return shares

def run_scenario(name, known_fcf_values, revenue_growth_rates, terminal_growth, discount_rate, initial_shares, 
                buyback_rate, initial_margin, target_margin, years_to_target):
    fcf_projections = calculate_fcf_with_margin_expansion(
        known_fcf_values, revenue_growth_rates, initial_margin, target_margin, years_to_target
    )
    share_count = calculate_yearly_share_count(initial_shares, buyback_rate, len(fcf_projections))
    
    ev = dcf_valuation(fcf_projections, terminal_growth, discount_rate)
    net_debt = debt - cash
    equity_value = ev - net_debt
    
    yearly_share_prices = [
        (dcf_valuation(fcf_projections[i:], terminal_growth, discount_rate) - net_debt) * 1000 / share_count[i]
        for i in range(len(fcf_projections))
    ]
    
    final_price_per_share = yearly_share_prices[-1]
    price_to_fcf = final_price_per_share / (fcf_projections[-1] * 1000 / share_count[-1])
    
    return {
        "name": name,
        "ev": ev,
        "equity_value": equity_value,
        "final_price_per_share": final_price_per_share,
        "price_to_fcf": price_to_fcf,
        "fcf_projections": fcf_projections,
        "share_count": share_count,
        "yearly_share_prices": yearly_share_prices
    }

# Mastercard specific inputs
market_cap = 477.823  # billion
cash = 9.2  # billion
debt = 1.3  # billion
initial_shares = 930  # million
beta = 1.1
risk_free_rate = 0.04457
market_return = 0.095
annual_buyback_rate = 0.02

# Known FCF values for first three years
known_fcf_values = [13.0, 14.7, 16.5]  # FY2024, FY2025, FY2026

# Margin assumptions
initial_margin = 0.45  # Current 45% margin
target_margin = 0.55  # Target 55% margin (Visa's level)
years_to_target = 5   # Assume 5 years to reach target margin

# Calculate WACC
wacc = calculate_wacc(risk_free_rate, market_return, beta, market_cap, debt, cash)
print(f"Calculated WACC: {wacc:.2%}")
	
# Calculate implied growth rates from your specific projections
growth_2025 = 14.7/13.0 - 1  # ~13.1%
growth_2026 = 16.5/14.7 - 1  # ~12.2%

# Updated growth rates (now only need rates for years after 2026)
base_case_growth = [growth_2025, growth_2026, 0.11, 0.10, 0.09, 0.08, 0.07, 0.06, 0.05, 0.05]
optimistic_case_growth = [growth_2025, growth_2026, 0.12, 0.11, 0.10, 0.09, 0.08, 0.07, 0.06, 0.06]
pessimistic_case_growth = [growth_2025, growth_2026, 0.10, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04, 0.04]

base_case_terminal_growth = 0.04
optimistic_case_terminal_growth = 0.05
pessimistic_case_terminal_growth = 0.03

# Run Scenarios
scenarios = [
    run_scenario("Pessimistic Case", known_fcf_values, pessimistic_case_growth, pessimistic_case_terminal_growth, 
                wacc, initial_shares, annual_buyback_rate, initial_margin, target_margin, years_to_target),
    run_scenario("Base Case", known_fcf_values, base_case_growth, base_case_terminal_growth, 
                wacc, initial_shares, annual_buyback_rate, initial_margin, target_margin, years_to_target),
    run_scenario("Optimistic Case", known_fcf_values, optimistic_case_growth, optimistic_case_terminal_growth, 
                wacc, initial_shares, annual_buyback_rate, initial_margin, target_margin, years_to_target)
]

# Print results
headers = ["Metric", "Pessimistic Case", "Base Case", "Optimistic Case"]
table = [
    ["Enterprise Value ($B)", f"${scenarios[0]['ev']:.2f}", f"${scenarios[1]['ev']:.2f}", f"${scenarios[2]['ev']:.2f}"],
    ["Equity Value ($B)", f"${scenarios[0]['equity_value']:.2f}", f"${scenarios[1]['equity_value']:.2f}", f"${scenarios[2]['equity_value']:.2f}"],
    ["Final Price per Share", f"${scenarios[0]['final_price_per_share']:.2f}", f"${scenarios[1]['final_price_per_share']:.2f}", f"${scenarios[2]['final_price_per_share']:.2f}"],
    ["Final Price-to-FCF Ratio", f"{scenarios[0]['price_to_fcf']:.2f}", f"{scenarios[1]['price_to_fcf']:.2f}", f"{scenarios[2]['price_to_fcf']:.2f}"]
]

print(tabulate(table, headers, tablefmt="grid"))

# Print year-by-year projections
print("\nYear-by-Year Projections:")
yearly_table = []
for year in range(10):
    fiscal_year = 2024 + year
    yearly_table.append([
        f"FY {fiscal_year}",
        f"FCF: ${scenarios[0]['fcf_projections'][year]:.3f}B | Shares: {scenarios[0]['share_count'][year]:.1f}M | Price: ${scenarios[0]['yearly_share_prices'][year]:.2f}",
        f"FCF: ${scenarios[1]['fcf_projections'][year]:.3f}B | Shares: {scenarios[1]['share_count'][year]:.1f}M | Price: ${scenarios[1]['yearly_share_prices'][year]:.2f}",
        f"FCF: ${scenarios[2]['fcf_projections'][year]:.3f}B | Shares: {scenarios[2]['share_count'][year]:.1f}M | Price: ${scenarios[2]['yearly_share_prices'][year]:.2f}"
    ])

print(tabulate(yearly_table, headers, tablefmt="grid"))