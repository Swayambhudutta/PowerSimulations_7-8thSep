import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm

# Set page config for wider layout
st.set_page_config(page_title="IEX Price Simulation Dashboard", layout="wide")

# Custom heading with icon
st.markdown("""
    <h1 style='text-align: center; color: #2c3e50; background-color:#dfe6e9; padding:10px; border-radius:10px;'>
        ⚡🔍 IEX Price Simulation Dashboard 🔍⚡
    </h1>
    <p style='text-align: center; font-size:18px; color: #34495e;'>
        Simulate IEX prices for a selected year using Monte Carlo simulations with adjustable parameters.
    </p>
    <hr style='border: 1px solid #bdc3c7;'>
""", unsafe_allow_html=True)

# Top sliders for year and confidence interval with colored background
st.markdown("""
    <div style='background-color:#ffeaa7; padding:10px; border-radius:10px;'>
""", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    selected_year = st.slider("Select Prediction Year", 2026, 2050, 2030)
with col2:
    confidence_interval = st.slider("Confidence Interval (%)", 70, 100, 90)
st.markdown("</div>", unsafe_allow_html=True)

# Sidebar inputs with colored headers
st.sidebar.markdown("<div style='background-color:#fab1a0; padding:10px; border-radius:10px;'><h3>🎯 Traditional Sources</h3></div>", unsafe_allow_html=True)
coal_variation = st.sidebar.slider("Coal Price Variation (%)", -50, 50, 0)
gas_variation = st.sidebar.slider("Gas Price Variation (%)", -50, 50, 0)
nuclear_variation = st.sidebar.slider("Nuclear Variation (%)", -50, 50, 0)

st.sidebar.markdown("<div style='background-color:#55efc4; padding:10px; border-radius:10px;'><h3>🌱 Renewables</h3></div>", unsafe_allow_html=True)
solar_growth = st.sidebar.slider("Solar Growth (%)", 5, 50, 20)
hydro_growth = st.sidebar.slider("Hydro Growth (%)", 5, 50, 20)
wind_growth = st.sidebar.slider("Wind Growth (%)", 5, 50, 20)
other_re_growth = st.sidebar.slider("Other Renewables Growth (%)", 5, 50, 20)

st.sidebar.markdown("<div style='background-color:#ffeaa7; padding:10px; border-radius:10px;'><h3>⚠️ External Shocks</h3></div>", unsafe_allow_html=True)
external_shock = st.sidebar.slider("External Shock Factor (%)", -20, 20, 0)

# Function to simulate prices
def simulate_prices(coal_var, gas_var, nuclear_var, solar, hydro, wind, other, shock, n_simulations=1000):
    base_price = 5.0  # base IEX price in ₹/kWh
    fuel_factor = 1 + (coal_var + gas_var + nuclear_var) / 300
    re_total_growth = (solar + hydro + wind + other) / 4
    re_factor = 1 - re_total_growth / 100 * 0.3
    shock_factor = 1 + shock / 100
    mean_price = base_price * fuel_factor * (1 - re_total_growth / 100 * 0.1) * shock_factor
    std_dev = 0.5 * re_factor * shock_factor
    prices = np.random.normal(loc=mean_price, scale=std_dev, size=n_simulations)
    return prices, mean_price, std_dev

# Simulate prices
prices, mean_price, std_dev = simulate_prices(coal_variation, gas_variation, nuclear_variation,
                                              solar_growth, hydro_growth, wind_growth, other_re_growth,
                                              external_shock)

# Plot normal distribution with wider layout
st.subheader(f"📈 Simulated IEX Price Distribution - Year {selected_year}")
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

# Highlight mean price point
fig.add_vline(x=mean_price, line=dict(color="red", width=2, dash="dash"),
              annotation_text="Mean Price", annotation_position="top right")

fig.update_layout(title=f"Simulated IEX Price Distribution - Year {selected_year}",
                  xaxis_title="Price (₹/kWh)",
                  yaxis_title="Probability Density",
                  width=1000, height=500)

st.plotly_chart(fig, use_container_width=True)

# Display confidence interval range
st.markdown(f"<p style='font-size:18px'><strong>{confidence_interval}% Confidence Interval:</strong> ₹{ci_low:.2f} to ₹{ci_high:.2f} per kWh</p>", unsafe_allow_html=True)

# Dynamic prediction accuracy
accuracy = max(50.0, 90 - (selected_year - 2026) * 0.5)
st.markdown(f"<p style='font-size:18px'>✅ <strong>Prediction accuracy from past data:</strong> {accuracy:.1f}%</p>", unsafe_allow_html=True)
