import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm

# Set up the Streamlit app
st.title("IEX Price Simulation Dashboard")
st.markdown("Simulate IEX prices over a 1 to 10 year horizon using Monte Carlo simulations.")

# Sidebar inputs
st.sidebar.header("Simulation Parameters")
years = st.sidebar.slider("Select prediction horizon (years)", 1, 10, 5)
coal_variation = st.sidebar.slider("Coal/Gas Price Variation (%)", -50, 50, 0)
renewable_growth = st.sidebar.slider("Renewable Energy Growth (%)", 5, 50, 20)
confidence_interval = st.sidebar.slider("Confidence Interval (%)", 70, 100, 90)

# Function to simulate prices for a given year
def simulate_prices(year, coal_var, re_growth, n_simulations=1000):
    base_price = 5.0  # base IEX price in ₹/kWh
    coal_factor = 1 + coal_var / 100
    re_factor = 1 - re_growth / 100 * 0.3  # assume RE growth reduces price volatility
    mean_price = base_price * coal_factor * (1 - re_growth / 100 * 0.1)
    std_dev = 0.5 * re_factor  # standard deviation decreases with RE growth
    prices = np.random.normal(loc=mean_price, scale=std_dev, size=n_simulations)
    return prices, mean_price, std_dev

# Display simulation results for each year
for year in range(1, years + 1):
    st.subheader(f"Year {year} Price Distribution")
    prices, mean_price, std_dev = simulate_prices(year, coal_variation, renewable_growth)

    # Plot normal distribution
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

    fig.update_layout(title=f"Simulated IEX Price Distribution - Year {year}",
                      xaxis_title="Price (₹/kWh)",
                      yaxis_title="Probability Density")

    st.plotly_chart(fig)

    st.markdown(f"**{confidence_interval}% Confidence Interval:** ₹{ci_low:.2f} to ₹{ci_high:.2f} per kWh")
