#!/usr/bin/env python
# coding: utf-8

# In[1]:


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




