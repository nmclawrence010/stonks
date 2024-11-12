import numpy as np
from tabulate import tabulate

def calculate_wacc(risk_free_rate, market_return, beta, market_cap, debt=0, tax_rate=0.21):
    cost_of_equity = risk_free_rate + beta * (market_return - risk_free_rate)
    firm_value = market_cap + debt
    weight_equity = market_cap / firm_value
    weight_debt = debt / firm_value
    cost_of_debt = 0  # Since Zoom has no debt
    wacc = weight_equity * cost_of_equity + weight_debt * cost_of_debt * (1 - tax_rate)
    return wacc

def dcf_valuation(fcf_projections, terminal_growth, discount_rate):
    years = len(fcf_projections)
    terminal_value = fcf_projections[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
    pv_factors = [(1 + discount_rate) ** -i for i in range(1, years + 1)]
    pv_fcf = sum(np.multiply(fcf_projections, pv_factors))
    pv_terminal = terminal_value * pv_factors[-1]
    return pv_fcf + pv_terminal

def calculate_segment_fcf(initial_revenue, growth_rates, fcf_margins):
    revenue = [initial_revenue]
    for growth in growth_rates:
        revenue.append(revenue[-1] * (1 + growth))
    return [rev * margin for rev, margin in zip(revenue, fcf_margins)]

def run_scenario(name, segments, terminal_growth, discount_rate):
    total_fcf = [sum(seg_fcf) for seg_fcf in zip(*[segment['fcf'] for segment in segments])]
    ev = dcf_valuation(total_fcf, terminal_growth, discount_rate)
    
    cash = 6.5  # $6.5 billion in cash
    equity_value = ev - cash  # Assuming no debt
    shares_outstanding = 308  # millions
    price_per_share = equity_value * 1000 / shares_outstanding
    price_to_fcf = price_per_share / (total_fcf[0] * 1000 / shares_outstanding)
    
    return {
        "name": name,
        "ev": ev,
        "equity_value": equity_value,
        "price_per_share": price_per_share,
        "price_to_fcf": price_to_fcf,
        "fcf_projections": total_fcf
    }

# WACC Calculation
risk_free_rate = 0.035  # 3.5%, based on 10-year Treasury yield
market_return = 0.10   # 10%, long-term stock market return
beta = 1.0             # As per our previous discussion
market_cap = 20.68     # billion, current market cap
wacc = calculate_wacc(risk_free_rate, market_return, beta, market_cap)
print(f"Calculated WACC: {wacc:.2%}")

# Segment definitions
segments = [
    {
        "name": "Enterprise",
        "initial_revenue": 2.7051,  # 60% of total
        "growth_rates": {
            "base": [0.06, 0.07, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.03],
            "optimistic": [0.08, 0.09, 0.10, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04],
            "pessimistic": [0.04, 0.05, 0.06, 0.05, 0.04, 0.03, 0.02, 0.02, 0.02]
        },
        "fcf_margins": {
            "base": [0.32] * 10,
            "optimistic": [0.35] * 10,
            "pessimistic": [0.28] * 10
        }
    },
    {
        "name": "SMB",
        "initial_revenue": 1.3525,  # 30% of total
        "growth_rates": {
            "base": [0.04, 0.05, 0.06, 0.05, 0.04, 0.03, 0.02, 0.02, 0.02],
            "optimistic": [0.06, 0.07, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.03],
            "pessimistic": [0.02, 0.03, 0.04, 0.03, 0.02, 0.02, 0.01, 0.01, 0.01]
        },
        "fcf_margins": {
            "base": [0.28] * 10,
            "optimistic": [0.30] * 10,
            "pessimistic": [0.25] * 10
        }
    },
    {
        "name": "Consumer",
        "initial_revenue": 0.4509,  # 10% of total
        "growth_rates": {
            "base": [0.02, 0.03, 0.04, 0.03, 0.02, 0.02, 0.01, 0.01, 0.01],
            "optimistic": [0.04, 0.05, 0.06, 0.05, 0.04, 0.03, 0.02, 0.02, 0.02],
            "pessimistic": [0.00, 0.01, 0.02, 0.01, 0.00, 0.00, -0.01, -0.01, -0.01]
        },
        "fcf_margins": {
            "base": [0.25] * 10,
            "optimistic": [0.28] * 10,
            "pessimistic": [0.22] * 10
        }
    }
]

# Run Scenarios
scenarios = []
for case in ["base", "optimistic", "pessimistic"]:
    segments_case = []
    for segment in segments:
        fcf = calculate_segment_fcf(
            segment["initial_revenue"],
            segment["growth_rates"][case],
            segment["fcf_margins"][case]
        )
        segments_case.append({"name": segment["name"], "fcf": fcf})
    
    terminal_growth = 0.03 if case == "base" else (0.04 if case == "optimistic" else 0.02)
    scenarios.append(run_scenario(f"{case.capitalize()} Case", segments_case, terminal_growth, wacc))

# Print results
headers = ["Metric", "Base Case", "Optimistic Case", "Pessimistic Case"]
table = [
    ["Enterprise Value ($B)", f"${scenarios[0]['ev']:.2f}", f"${scenarios[1]['ev']:.2f}", f"${scenarios[2]['ev']:.2f}"],
    ["Equity Value ($B)", f"${scenarios[0]['equity_value']:.2f}", f"${scenarios[1]['equity_value']:.2f}", f"${scenarios[2]['equity_value']:.2f}"],
    ["Price per Share", f"${scenarios[0]['price_per_share']:.2f}", f"${scenarios[1]['price_per_share']:.2f}", f"${scenarios[2]['price_per_share']:.2f}"],
    ["Price-to-FCF Ratio", f"{scenarios[0]['price_to_fcf']:.2f}", f"{scenarios[1]['price_to_fcf']:.2f}", f"{scenarios[2]['price_to_fcf']:.2f}"]
]

print(tabulate(table, headers, tablefmt="grid"))

# Print FCF projections
print("\nTotal FCF Projections (in billions):")
fcf_table = []
for year in range(10):
    fcf_table.append([
        f"FY '{year+24}",
        f"${scenarios[0]['fcf_projections'][year]:.3f}",
        f"${scenarios[1]['fcf_projections'][year]:.3f}",
        f"${scenarios[2]['fcf_projections'][year]:.3f}"
    ])

print(tabulate(fcf_table, headers, tablefmt="grid"))