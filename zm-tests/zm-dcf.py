import numpy as np

def dcf_valuation(fcf_current, growth_rate, terminal_growth, discount_rate, years):
    # Project Free Cash Flows
    fcf_projections = [fcf_current * (1 + growth_rate) ** i for i in range(1, years + 1)]
    
    # Calculate Terminal Value
    terminal_value = fcf_projections[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
    
    # Discount Cash Flows
    pv_factors = [(1 + discount_rate) ** -i for i in range(1, years + 1)]
    pv_fcf = sum(np.multiply(fcf_projections, pv_factors))
    pv_terminal = terminal_value * pv_factors[-1]
    
    # Enterprise Value
    enterprise_value = pv_fcf + pv_terminal
    
    return enterprise_value

# Example usage (replace with actual Zoom data)
fcf_current = 1.530  # $1.7 billion current FCF
growth_rate = 0.05  # 10% annual growth rate
terminal_growth = 0.03  # 3% terminal growth rate
discount_rate = 0.09  # 8% discount rate
years = 5  # 5-year projection

ev = dcf_valuation(fcf_current, growth_rate, terminal_growth, discount_rate, years)
print(f"Estimated Enterprise Value: ${ev:.2f}B")

# To get equity value, subtract net debt
net_debt = -7  # Zoom has $7 billion in cash, treating as negative debt
equity_value = ev + net_debt
print(f"Estimated Equity Value: ${equity_value:.2f}B")

# Assuming 300 million shares outstanding (replace with actual)
shares_outstanding = 309
price_per_share = equity_value * 1000 / shares_outstanding  # Convert to millions
print(f"Estimated Price per Share: ${price_per_share:.2f}")