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

def calculate_fcf(initial_fcf, growth_rates):
    fcf = [initial_fcf]
    for growth in growth_rates:
        fcf.append(fcf[-1] * (1 + growth))
    return fcf

def calculate_yearly_share_count(initial_shares, buyback_rate, years):
    shares = [initial_shares]
    for _ in range(years - 1):
        shares.append(shares[-1] * (1 - buyback_rate))
    return shares

def run_scenario(name, initial_fcf, growth_rates, terminal_growth, discount_rate, initial_shares, buyback_rate):
    fcf_projections = calculate_fcf(initial_fcf, growth_rates)
    share_count = calculate_yearly_share_count(initial_shares, buyback_rate, len(fcf_projections))
    
    ev = dcf_valuation(fcf_projections, terminal_growth, discount_rate)
    net_debt = debt - cash
    equity_value = ev - net_debt
    
    yearly_share_prices = [
        (dcf_valuation(fcf_projections[i:], terminal_growth, discount_rate) - net_debt) * 1000 / share_count[i]
        for i in range(len(fcf_projections))
    ]
    
    final_price_per_share = yearly_share_prices[-1]  # Use the last year's calculated share price
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
market_cap = 14.332  # billion
current_fcf = 0.485  # billion
cash = 0.114  # billion
debt = 0.056  # billion
initial_shares = 36.52  # million
beta = 0.86
risk_free_rate = 0.04
market_return = 0.1 # Market minus the dividend yield
annual_buyback_rate = 0.038  # 2% annual reduction in shares outstanding

# Calculate WACC
wacc = calculate_wacc(risk_free_rate, market_return, beta, market_cap, debt, cash)
print(f"Calculated WACC: {wacc:.2%}")

# Scenario definitions
base_case_growth = [0.156, 0.156, 0.17, 0.14, 0.13, 0.12, 0.11, 0.1, 0.09, 0.08]
optimistic_case_growth = [0.14, 0.16, 0.15, 0.14, 0.13, 0.12, 0.11, 0.10, 0.09, 0.08]
pessimistic_case_growth = [0.12, 0.13, 0.10, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03]

base_case_terminal_growth = 0.04
optimistic_case_terminal_growth = 0.05
pessimistic_case_terminal_growth = 0.03

# Run Scenarios
scenarios = [
    run_scenario("Pessimistic Case", current_fcf, pessimistic_case_growth, pessimistic_case_terminal_growth, wacc, initial_shares, annual_buyback_rate),
    run_scenario("Base Case", current_fcf, base_case_growth, base_case_terminal_growth, wacc, initial_shares, annual_buyback_rate),
    run_scenario("Optimistic Case", current_fcf, optimistic_case_growth, optimistic_case_terminal_growth, wacc, initial_shares, annual_buyback_rate)
]

# Print results with reordered columns
headers = ["Metric", "Pessimistic Case", "Base Case", "Optimistic Case"]
table = [
    ["Enterprise Value ($B)", f"${scenarios[0]['ev']:.2f}", f"${scenarios[1]['ev']:.2f}", f"${scenarios[2]['ev']:.2f}"],
    ["Equity Value ($B)", f"${scenarios[0]['equity_value']:.2f}", f"${scenarios[1]['equity_value']:.2f}", f"${scenarios[2]['equity_value']:.2f}"],
    ["Final Price per Share", f"${scenarios[0]['final_price_per_share']:.2f}", f"${scenarios[1]['final_price_per_share']:.2f}", f"${scenarios[2]['final_price_per_share']:.2f}"],
    ["Final Price-to-FCF Ratio", f"{scenarios[0]['price_to_fcf']:.2f}", f"{scenarios[1]['price_to_fcf']:.2f}", f"{scenarios[2]['price_to_fcf']:.2f}"]
]

print(tabulate(table, headers, tablefmt="grid"))

# Print FCF projections, share count, and yearly share prices with updated year labels
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