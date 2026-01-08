#!/usr/bin/env python
# coding: utf-8

# In[3]:


# 1. Import Libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from ipywidgets import interact, widgets
from IPython.display import display, clear_output

 
# 2. Core Simulator Class
class MarketRiskSimulator:
    """Monte-Carlo Market Risk Engine using GBM"""
    
    def __init__(self, initial_price=100, mu=0.05, sigma=0.2, 
                 time_horizon=1, time_steps=252, n_simulations=10000):
        self.S0 = initial_price
        self.mu = mu
        self.sigma = sigma
        self.T = time_horizon
        self.N = time_steps
        self.M = n_simulations
        self.simulated_paths = None
        self.returns = None
        
    def simulate_gbm(self, seed=42):
        """Simulate GBM stock price paths"""
        dt = self.T / self.N
        np.random.seed(seed)
        Z = np.random.standard_normal((self.N, self.M))
        daily_returns = np.exp((self.mu - 0.5 * self.sigma**2) * dt + self.sigma * np.sqrt(dt) * Z)
        price_paths = np.zeros_like(daily_returns)
        price_paths[0] = self.S0
        for t in range(1, self.N):
            price_paths[t] = price_paths[t-1] * daily_returns[t]
        self.simulated_paths = price_paths
        return price_paths
    
    def calculate_returns(self):
        if self.simulated_paths is None:
            self.simulate_gbm()
        final_prices = self.simulated_paths[-1]
        self.returns = (final_prices - self.S0) / self.S0
        return self.returns
    
    def calculate_var(self, confidence_level=0.95):
        if self.returns is None:
            self.calculate_returns()
        sorted_returns = np.sort(self.returns)
        var_index = int((1 - confidence_level) * len(sorted_returns))
        var = -sorted_returns[var_index]
        return var
    
    def calculate_expected_shortfall(self, confidence_level=0.95):
        if self.returns is None:
            self.calculate_returns()
        sorted_returns = np.sort(self.returns)
        var_index = int((1 - confidence_level) * len(sorted_returns))
        tail_returns = sorted_returns[:var_index]
        es = -np.mean(tail_returns)
        return es
    
    def generate_report(self, confidence_levels=[0.95, 0.99]):
        if self.returns is None:
            self.calculate_returns()
        report = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "parameters": {
                "initial_price": self.S0,
                "expected_return": f"{self.mu*100:.2f}%",
                "volatility": f"{self.sigma*100:.2f}%",
                "time_horizon_years": self.T,
                "time_steps": self.N,
                "simulations": self.M
            },
            "statistics": {
                "mean_return": f"{np.mean(self.returns)*100:.2f}%",
                "std_return": f"{np.std(self.returns)*100:.2f}%",
                "min_return": f"{np.min(self.returns)*100:.2f}%",
                "max_return": f"{np.max(self.returns)*100:.2f}%",
                "skewness": f"{stats.skew(self.returns):.4f}",
                "kurtosis": f"{stats.kurtosis(self.returns):.4f}"
            },
            "risk_metrics": {}
        }
        for cl in confidence_levels:
            report["risk_metrics"][f"CL_{int(cl*100)}%"] = {
                "VaR": f"{self.calculate_var(cl)*100:.2f}%",
                "Expected_Shortfall": f"{self.calculate_expected_shortfall(cl)*100:.2f}%"
            }
        return report


# 3. Interactive Simulation with Widgets

def interactive_simulation(initial_price=100, expected_return=5.0, volatility=20.0,
                          time_horizon=1.0, n_simulations=10000, confidence_level=95):
    mu = expected_return / 100
    sigma = volatility / 100
    cl = confidence_level / 100
    simulator = MarketRiskSimulator(initial_price, mu, sigma, time_horizon, 252, n_simulations)
    paths = simulator.simulate_gbm()
    returns = simulator.calculate_returns()
    var = simulator.calculate_var(cl)
    es = simulator.calculate_expected_shortfall(cl)
    report = simulator.generate_report([0.90, 0.95, 0.99, cl])
    
    clear_output(wait=True)
    print("="*70)
    print("MARKET RISK MONTE-CARLO SIMULATOR")
    print("="*70)
    print(f"Parameters:\n• Initial Price: ${initial_price:.2f}\n• Expected Return: {expected_return:.1f}%\n• Volatility: {volatility:.1f}%\n• Time Horizon: {time_horizon} yr(s)\n• Simulations: {n_simulations:,}\n• Confidence Level: {confidence_level}%")
    print(f"\nRisk Metrics:\n• {confidence_level}% VaR: {-var*100:.2f}%\n• {confidence_level}% Expected Shortfall: {-es*100:.2f}%")
    
    # Plot sample paths and return histogram
    fig, axes = plt.subplots(2,1,figsize=(12,8))
    axes[0].plot(paths[:,:50], alpha=0.5)
    axes[0].set_title("First 50 Simulated Price Paths")
    axes[0].set_ylabel("Price ($)")
    axes[0].grid(True)
    axes[1].hist(returns*100, bins=50, alpha=0.7)
    axes[1].axvline(-var*100, color='red', linestyle='dashed', label=f'{confidence_level}% VaR')
    axes[1].set_title("Return Distribution")
    axes[1].set_xlabel("Return (%)")
    axes[1].set_ylabel("Frequency")
    axes[1].legend()
    plt.tight_layout()
    plt.show()
    
    return simulator, report


# Widgets
initial_slider = widgets.FloatSlider(value=100, min=1, max=500, step=10, description='Initial Price ($):')
return_slider = widgets.FloatSlider(value=5.0, min=-10, max=30, step=0.5, description='Exp. Return (%):')
volatility_slider = widgets.FloatSlider(value=20.0, min=1, max=100, step=1, description='Volatility (%):')
time_slider = widgets.FloatSlider(value=1.0, min=0.1, max=5.0, step=0.1, description='Time Horizon (yrs):')
simulations_dropdown = widgets.Dropdown(options=[1000,5000,10000,20000], value=10000, description='Simulations:')
confidence_slider = widgets.IntSlider(value=95, min=90, max=99, step=1, description='Confidence Level (%):')

display(initial_slider, return_slider, volatility_slider, time_slider, simulations_dropdown, confidence_slider)

run_button = widgets.Button(description="🚀 Run Simulation", button_style='success')
output = widgets.Output()

def on_button_clicked(b):
    with output:
        interactive_simulation(
            initial_price=initial_slider.value,
            expected_return=return_slider.value,
            volatility=volatility_slider.value,
            time_horizon=time_slider.value,
            n_simulations=simulations_dropdown.value,
            confidence_level=confidence_slider.value
        )

run_button.on_click(on_button_clicked)
display(run_button, output)


# 4. Generate Excel Report

def generate_excel_report(simulator, report, filename="risk_report.xlsx"):
    params_df = pd.DataFrame({'Parameter': list(report['parameters'].keys()), 'Value': list(report['parameters'].values())})
    stats_df = pd.DataFrame({'Statistic': list(report['statistics'].keys()), 'Value': list(report['statistics'].values())})
    risk_df = pd.DataFrame([{'Confidence Level': cl, **metrics} for cl, metrics in report['risk_metrics'].items()])
    returns_df = pd.DataFrame({'Simulation_Index': range(len(simulator.returns)), 'Return': simulator.returns, 'Return_Percent': simulator.returns*100})
    
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        params_df.to_excel(writer, sheet_name='Parameters', index=False)
        stats_df.to_excel(writer, sheet_name='Statistics', index=False)
        risk_df.to_excel(writer, sheet_name='Risk Metrics', index=False)
        returns_df.to_excel(writer, sheet_name='Raw Returns', index=False)
    print(f"✅ Excel report saved as: {filename}")
    return filename


# In[4]:


import streamlit as st
import numpy as np
import pandas as pd

st.title("🎯 Market Risk Monte-Carlo Simulator")
S0 = st.number_input("Initial Price ($)", value=100.0)
mu = st.slider("Expected Return (%)", -10, 20, 5)/100
sigma = st.slider("Volatility (%)", 1, 100, 20)/100
T = st.slider("Time Horizon (Years)", 0.1, 5.0, 1.0)
M = st.selectbox("Simulations", [1000,5000,10000,20000], index=2)
cl = st.slider("Confidence Level (%)", 90, 99, 95)/100

if st.button("🚀 Run Simulation"):
    N = 252
    dt = T / N
    Z = np.random.standard_normal((N, M))
    daily_returns = np.exp((mu-0.5*sigma**2)*dt + sigma*np.sqrt(dt)*Z)
    paths = np.zeros_like(daily_returns)
    paths[0] = S0
    for t in range(1,N):
        paths[t] = paths[t-1]*daily_returns[t]
    returns = (paths[-1]-S0)/S0
    sorted_returns = np.sort(returns)
    var = -sorted_returns[int((1-cl)*M)]
    es = -np.mean(sorted_returns[:int((1-cl)*M)])
    st.write(f"{int(cl*100)}% VaR: {var*100:.2f}%, Expected Shortfall: {es*100:.2f}%")
    st.line_chart(paths[:,:50])


# In[ ]:




