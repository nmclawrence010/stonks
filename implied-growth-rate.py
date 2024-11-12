import numpy as np

def calculate_implied_growth(market_cap, net_debt, base_fcf, years, terminal_growth, discount_rate, tolerance=0.0001):
    """
    Calculate the implied growth rate based on current market cap and financial metrics.
    
    Parameters:
    market_cap (float): Current market capitalization
    net_debt (float): Net debt (debt minus cash)
    base_fcf (float): Base free cash flow (FCF) for calculations
    years (int): Number of years for projection
    terminal_growth (float): Terminal growth rate
    discount_rate (float): Discount rate (WACC)
    tolerance (float): Tolerance for binary search precision
    
    Returns:
    float: Implied growth rate
    """
    target_ev = market_cap + net_debt
    
    def dcf_value(growth_rate):
        fcf_projections = [base_fcf * (1 + growth_rate) ** i for i in range(1, years + 1)]
        terminal_value = fcf_projections[-1] * (1 + terminal_growth) / (discount_rate - terminal_growth)
        pv_factors = [(1 + discount_rate) ** -i for i in range(1, years + 1)]
        pv_fcf = sum(np.multiply(fcf_projections, pv_factors))
        pv_terminal = terminal_value * pv_factors[-1]
        return pv_fcf + pv_terminal
    
    # Binary search for the growth rate
    low, high = -0.5, 0.5  # Assuming growth rate between -50% and 50%
    while high - low > tolerance:
        mid = (low + high) / 2
        if dcf_value(mid) < target_ev:
            low = mid
        else:
            high = mid
    
    return (low + high) / 2

# Example usage:
if __name__ == "__main__":
    # Example inputs (replace with actual data for the company you're analyzing)
    market_cap = 15.82  # billion
    net_debt = -1.1  # billion (negative indicates net cash position)
    base_fcf = 0.2  # billion
    years = 10
    terminal_growth = 0.03
    discount_rate = 0.15

    implied_growth = calculate_implied_growth(market_cap, net_debt, base_fcf, years, terminal_growth, discount_rate)
    print(f"Implied Growth Rate: {implied_growth:.2%}")