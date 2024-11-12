import numpy as np
from tabulate import tabulate

def calculate_wacc(risk_free_rate, market_return, beta, market_cap, debt, cash, tax_rate=0.21):
    cost_of_equity = risk_free_rate + beta * (market_return - risk_free_rate)
    total_value = market_cap + debt - cash
    weight_equity = market_cap / total_value
    weight_debt = (debt - cash) / total_value
    cost_of_debt = 0  # Toast has no debt
    wacc = weight_equity * cost_of_equity + weight_debt * cost_of_debt * (1 - tax_rate)
    return wacc

def dcf_valuation(fcf_projections, terminal_growth, discount_rate):
    years = len(fcf_projections)
    terminal_value = fcf_projections[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
    pv_factors = [(1 + discount_rate) ** -i for i in range(1, years + 1)]
    pv_fcf = sum(np.multiply(fcf_projections, pv_factors))
    pv_terminal = terminal_value * pv_factors[-1]
    return pv_fcf + pv_terminal

def calculate_fcf(initial_revenue, growth_rates, fcf_margins):
    revenue = [initial_revenue]
    for growth in growth_rates:
        revenue.append(revenue[-1] * (1 + growth))
    return [rev * margin for rev, margin in zip(revenue, fcf_margins)]

def calculate_yearly_share_count(initial_shares, dilution_rate, years):
    shares = [initial_shares]
    for _ in range(years - 1):
        shares.append(shares[-1] * (1 + dilution_rate))
    return shares

def run_scenario(name, initial_revenue, growth_rates, fcf_margins, terminal_growth, discount_rate, initial_shares, dilution_rate):
    fcf_projections = calculate_fcf(initial_revenue, growth_rates, fcf_margins)
    share_count = calculate_yearly_share_count(initial_shares, dilution_rate, len(fcf_projections))
    
    ev = dcf_valuation(fcf_projections, terminal_growth, discount_rate)
    net_debt = debt - cash
    equity_value = ev - net_debt
    
    final_price_per_share = equity_value * 1e9 / (share_count[-1] * 1e6)  # Convert billions to millions
    price_to_fcf = final_price_per_share / (fcf_projections[-1] * 1e9 / (share_count[-1] * 1e6))
    
    yearly_share_prices = [
        (dcf_valuation(fcf_projections[i:], terminal_growth, discount_rate) - net_debt) * 1e9 / (share_count[i] * 1e6)
        for i in range(len(fcf_projections))
    ]
    
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

# Toast specific inputs
market_cap = 15.82  # billion
current_revenue = 4.899  # billion (2023)
cash = 1.1  # billion
debt = 0  # billion
initial_shares = 562  # million
beta = 1.77
risk_free_rate = 0.0406
market_return = 0.10
annual_dilution_rate = 0.02  # Based on share increase from 502M to 562M in about a year

# Calculate WACC
wacc = calculate_wacc(risk_free_rate, market_return, beta, market_cap, debt, cash)
print(f"Calculated WACC: {wacc:.2%}")

# Updated Scenario definitions (10-year projections) with higher growth rates
base_case_growth = [0.22, 0.19, 0.18, 0.17, 0.16, 0.15, 0.14, 0.13, 0.12, 0.11]
optimistic_case_growth = [0.24, 0.21, 0.20, 0.19, 0.18, 0.17, 0.16, 0.15, 0.14, 0.13]
pessimistic_case_growth = [0.20, 0.17, 0.16, 0.15, 0.14, 0.13, 0.12, 0.11, 0.10, 0.09]

# Adjusted FCF margins to reflect potential economies of scale with higher growth
base_case_fcf_margins = [0.0456, 0.0694, 0.0775, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15]
optimistic_case_fcf_margins = [0.0456, 0.0694, 0.0775, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16]
pessimistic_case_fcf_margins = [0.0456, 0.0694, 0.0775, 0.085, 0.09, 0.095, 0.10, 0.105, 0.11, 0.115]

base_case_terminal_growth = 0.04
optimistic_case_terminal_growth = 0.05
pessimistic_case_terminal_growth = 0.03

# Run Scenarios
scenarios = [
    run_scenario("Pessimistic Case", current_revenue, pessimistic_case_growth, pessimistic_case_fcf_margins, pessimistic_case_terminal_growth, wacc, initial_shares, annual_dilution_rate),
    run_scenario("Base Case", current_revenue, base_case_growth, base_case_fcf_margins, base_case_terminal_growth, wacc, initial_shares, annual_dilution_rate),
    run_scenario("Optimistic Case", current_revenue, optimistic_case_growth, optimistic_case_fcf_margins, optimistic_case_terminal_growth, wacc, initial_shares, annual_dilution_rate)
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

# Print FCF projections, share count, and yearly share prices
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