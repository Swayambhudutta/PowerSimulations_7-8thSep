import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm

# Set up the Streamlit app
st.title("IEX Price Simulation Dashboard - 1 Year Horizon")
st.markdown("Simulate IEX prices for 1 year using Monte Carlo simulations with adjustable parameters.")

# Sidebar inputs
st.sidebar.header("Simulation Parameters")

# Coal and Gas price variation sliders
coal_variation = st.sidebar.slider("Coal Price Variation (%)", -50, 50, 0)
gas_variation = st.sidebar.slider("Gas Price Variation (%)", -50, 50, 0)

# Renewable energy growth sliders
solar_growth = st.sidebar.slider("Solar Growth (%)", 5, 50, 20)
hydro_growth = st.sidebar.slider("Hydro Growth (%)", 5, 50, 20)
wind_growth = st.sidebar.slider("Wind Growth (%)", 5, 50, 20)
other_re_growth = st.sidebar.slider("Other Renewables Growth (%)", 5, 50, 20)

# Confidence interval slider
confidence_interval = st.sidebar.slider("Confidence Interval (%)", 70, 100, 90)

# Function to simulate prices for 1 year
def simulate_prices(coal_var, gas_var, solar, hydro, wind, other, n_simulations=1000):
    base_price = 5.0  # base IEX price in ₹/kWh

    # Calculate impact factors
    fuel_factor = 1 + (coal_var + gas_var) / 200  # average impact of coal and gas
    re_total_growth = (solar + hydro + wind + other) / 4
    re_factor = 1 - re_total_growth / 100 * 0.3  # assume RE growth reduces price volatility
    mean_price = base_price * fuel_factor * (1 - re_total_growth / 100 * 0.1)
    std_dev = 0.5 * re_factor  # standard deviation decreases with RE growth

    prices = np.random.normal(loc=mean_price, scale=std_dev, size=n_simulations)
    return prices, mean_price, std_dev

# Simulate prices
prices, mean_price, std_dev = simulate_prices(coal_variation, gas_variation,
                                              solar_growth, hydro_growth,
                                              wind_growth, other_re_growth)

# Plot normal distribution
st.subheader("Simulated IEX Price Distribution - Year 1")
x_vals = np.linspace(mean_price - 3*std_dev, mean_price + 3*std_dev, 500)
y_vals = norm.pdf(x_vals, mean_price, std_dev)

fig = go.Figure()
fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name='Price Distribution'))

# Highlight confidence interval
ci_low = norm.ppf((1 - confidence_interval / 100) / 2, mean_price, std_dev)
ci_high = norm.ppf(1 - (1 - confidence_interval / 100) / 2, mean_price, std_dev)
fig.add_vrect(x0=ci_low, x1=ci_high, fillcolor="green", opacity=0.2,
              layer="below", line_width=0, annotation_text=f"{confidence_interval}% CI",
              annotation_position="top left")

fig.update_layout(title="Simulated IEX Price Distribution - Year 1",
                  xaxis_title="Price (₹/kWh)",
                  yaxis_title="Probability Density")

st.plotly_chart(fig)

# Display confidence interval range
st.markdown(f"**{confidence_interval}% Confidence Interval:** ₹{ci_low:.2f} to ₹{ci_high:.2f} per kWh")
