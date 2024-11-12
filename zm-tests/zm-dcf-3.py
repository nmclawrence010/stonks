import numpy as np

##Added further out FCF projections - Niall

def dcf_valuation(fcf_projections, terminal_growth, discount_rate):
    years = len(fcf_projections)
    
    # Calculate Terminal Value
    terminal_value = fcf_projections[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
    
    # Discount Cash Flows
    pv_factors = [(1 + discount_rate) ** -i for i in range(1, years + 1)]
    pv_fcf = sum(np.multiply(fcf_projections, pv_factors))
    pv_terminal = terminal_value * pv_factors[-1]
    
    # Enterprise Value
    enterprise_value = pv_fcf + pv_terminal
    
    return enterprise_value

# Extended Zoom-specific FCF projections (in billions)
revenue = [4.5085]  # FY '24 revenue
growth_rates = [0.04, 0.05, 0.06, 0.07]  # FY '25 to FY '33
fcf_margin = 0.30

for growth in growth_rates:
    revenue.append(revenue[-1] * (1 + growth))

fcf_projections = [1.345]  # FY '24 (as per guidance)
fcf_projections.extend([rev * fcf_margin for rev in revenue[1:]])

# Assumptions
terminal_growth = 0.03  # 3% terminal growth rate
discount_rate = 0.08  # 8% discount rate (WACC) - this should be calculated more precisely

ev = dcf_valuation(fcf_projections, terminal_growth, discount_rate)
print(f"Estimated Enterprise Value: ${ev:.2f} billion")

# To get equity value, subtract net debt
cash = 6.5  # $6.5 billion in cash as per the latest report
debt = 0  # Assuming Zoom has no debt, adjust if necessary
net_debt = debt - cash
equity_value = ev + net_debt
print(f"Estimated Equity Value: ${equity_value:.2f} billion")

# Using 308 million shares outstanding as per the report
shares_outstanding = 308
price_per_share = equity_value * 1000 / shares_outstanding  # Convert to millions
print(f"Estimated Price per Share: ${price_per_share:.2f}")

# Calculate implied Price-to-FCF ratio
current_fcf = fcf_projections[0]
price_to_fcf = price_per_share / (current_fcf * 1000 / shares_outstanding)
print(f"Implied Price-to-FCF ratio: {price_to_fcf:.2f}")

# Print out the FCF projections
print("\nFCF Projections (in billions):")
for year, fcf in enumerate(fcf_projections, start=24):  # Starting from FY '24
    print(f"FY '{year}: ${fcf:.3f}")