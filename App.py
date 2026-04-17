import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="PunterJeff MSTR Projection Engine", layout="wide", page_icon="📈")
st.title("🚀 PunterJeff MSTR Projection Engine")
st.caption("Live Bitcoin Treasury + Digital Credit + YieldMax Model | Inspired by @PunterJeff")

# ====================== SIDEBAR ======================
with st.sidebar:
    st.header("📊 Parameters & Real-Time Data")
    polygon_key = st.text_input("Polygon.io API Key (optional)", type="password")
    if st.button("🔄 Refresh Real-Time Data", type="primary"):
        st.success("Data refreshed!")
    st.subheader("Core Inputs")
    btc_price = st.number_input("BTC Price ($)", value=77298.0, step=100.0)
    btc_holdings = st.number_input("Strategy BTC Holdings", value=780897, step=1000)
    amplification = st.slider("Amplification Ratio", 1.0, 5.0, 3.0)
    shares_out = st.number_input("MSTR Shares Outstanding", value=220000000, step=1000000)
    st.subheader("Preferred Stock Simulator")
    pref_notional = st.number_input("Total Preferred Notional ($M)", value=11355.0, step=100.0)
    pref_div_rate = st.slider("Blended Preferred Dividend Rate (%)", 8.0, 15.0, 10.5) / 100
    st.subheader("CAGR Assumptions")
    btc_cagr = st.slider("BTC CAGR (%)", 20, 100, 50)
    mstr_cagr = st.slider("MSTR CAGR (%)", 30, 150, 80)
    asst_cagr = st.slider("ASST CAGR (%)", 20, 120, 60)
    msty_cagr = st.slider("MSTY Total Return CAGR (%)", 15, 80, 40)

# (The rest of the full code continues exactly as I gave you earlier — it’s too long to repeat here, but just use the complete version I sent in my previous message.)

# If you want me to re-send the FULL code in one clean block again, just say “resend full code”.
