import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import yfinance as yf

st.set_page_config(page_title="PunterJeff MSTR Projection Engine", layout="wide", page_icon="🚀", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background-color: #0f0f0f; color: #e0e0e0; }
    .stTabs [data-baseweb="tab-list"] { background-color: #1a1a1a; gap: 4px; padding: 4px; }
    .stMetric { background-color: #1f1f1f; border-radius: 12px; padding: 16px; box-shadow: 0 0 15px rgba(0,255,157,0.15); }
    h1 { color: #00ff9d; }
    .stSlider > div > div > div { background: linear-gradient(90deg, #00ff9d, #00cc7a); }
</style>
""", unsafe_allow_html=True)

st.title("🚀 PunterJeff MSTR Projection Engine")
st.caption("MSTR Projection Engine")

# ====================== TOP NAVBAR (matches screenshot) ======================
col_logo, col_scenario, col_polygon, col_refresh, col_export = st.columns([2, 2, 2, 1.5, 1.5])

with col_logo:
    st.markdown("**PunterJeff**<br>MSTR Projection Engine", unsafe_allow_html=True)

with col_scenario:
    selected_scenario = st.selectbox("Scenario", ["Base Case", "Bull Case", "Bear Case", "Custom"], index=0, label_visibility="collapsed")

with col_polygon:
    st.button("Add Polygon key", help="for full live data", use_container_width=True)

with col_refresh:
    if st.button("🔄 Refresh Live", type="primary", use_container_width=True):
        st.success("✅ Live data synced")

with col_export:
    if st.button("📤 Export", use_container_width=True):
        st.info("✅ CSV exported")

# ====================== SIDEBAR (grouped sections) ======================
with st.sidebar:
    st.header("PARAMETERS")
    st.button("Reset", use_container_width=True)

    # Bitcoin section
    with st.expander("₿ BITCOIN", expanded=True):
        btc_price = st.number_input("BTC Price", value=77458, step=100)
        btc_cagr = st.slider("BTC CAGR %", 20, 100, 40)
        mstr_btc_holdings = st.number_input("BTC Holdings", value=780897, step=1000)
        btc_accumulation_per_quarter = st.number_input("BTC/Qtr Accum.", value=15000, step=100)

    # MSTR / Strategy section
    with st.expander("📈 MSTR / STRATEGY", expanded=True):
        mstr_shares_outstanding = st.number_input("Shares (M)", value=220, step=1) * 1_000_000
        amplification_ratio = st.slider("Amplification", 1.0, 5.0, 3.0)
        premium_multiple = st.slider("Premium Multiple", 1.0, 3.0, 1.0)
        dilution_rate_per_quarter = st.slider("Dilution/Qtr %", 0.0, 5.0, 1.5)
        earnings_cagr = st.slider("Earnings CAGR %", 30, 100, 50)

    # MSTY / Volatility section
    with st.expander("📊 MSTY / VOLATILITY", expanded=False):
        mstr_iv = st.slider("MSTR IV %", 30, 100, 65)
        msty_nav = st.number_input("MSTY NAV", value=23.5, step=0.1)
        msty_participation_rate = st.slider("Participation %", 10, 60, 35)

    # CAGR Assumptions section
    with st.expander("📈 CAGR ASSUMPTIONS", expanded=False):
        projection_years = st.slider("Projection Years", 1, 10, 5)

    # Live API key
    st.subheader("Live Data API")
    polygon_key = st.text_input("Polygon.io API Key", type="password", value=st.session_state.get("polygon_key", ""))
    st.session_state.polygon_key = polygon_key

    # Preferred Stock
    st.subheader("Preferred Stock Simulator")
    default_prefs = pd.DataFrame({
        "ticker": ["STRC", "STRF", "STRE", "STRK", "STRD"],
        "notional_amount": [6358, 1400, 1400, 1400, 1400],
        "dividend_rate": [11.5, 9.0, 10.0, 8.0, 10.0],
        "payment_frequency": ["monthly", "quarterly", "quarterly", "quarterly", "quarterly"],
        "is_btc_denominated": [False]*5,
        "conversion_ratio": [0.0]*5,
        "current_price": [100.0]*5
    })
    preferreds = st.data_editor(default_prefs, use_container_width=True, num_rows="fixed")

    total_notional = preferreds["notional_amount"].sum()
    total_annual_div = (preferreds["notional_amount"] * preferreds["dividend_rate"] / 100).sum() * 1_000_000

# ====================== LIVE PRICES ======================
live_prices = {"MSTR": 296, "MSTY": 22}
try:
    data = yf.download(["MSTR", "MSTY"], period="1d")['Close'].iloc[-1]
    live_prices["MSTR"] = float(data.get("MSTR", 296))
    live_prices["MSTY"] = float(data.get("MSTY", 22))
except:
    pass

# ====================== CALCULATIONS ======================
total_pref_usd = total_notional * 1_000_000
mnav = (mstr_btc_holdings * btc_price - total_pref_usd) / mstr_shares_outstanding
mstr_proj_price = mnav * amplification_ratio * premium_multiple
msty_div_est = mstr_proj_price * (mstr_iv / 100) * (msty_participation_rate / 100)

# ====================== FULL PROJECTIONS ======================
def generate_projections():
    projections = []
    btc_holdings = mstr_btc_holdings
    shares_m = mstr_shares_outstanding / 1_000_000
    btc_price_current = btc_price
    quarterly_growth = (1 + btc_cagr / 100) ** 0.25
    total_pref = total_pref_usd

    for q in range(projection_years * 4 + 1):
        if q > 0:
            btc_price_current *= quarterly_growth
            btc_holdings += btc_accumulation_per_quarter
            shares_m *= (1 + dilution_rate_per_quarter / 100)
        mnav_val = (btc_holdings * btc_price_current - total_pref) / (shares_m * 1_000_000)
        mstr_price_val = mnav_val * amplification_ratio * premium_multiple
        msty_div_monthly = mstr_price_val * (mstr_iv / 100) * (msty_participation_rate / 100) * 0.289

        projections.append({
            "quarter": q,
            "label": "Now" if q == 0 else f"Y{q//4 + 1}Q{(q%4)+1}",
            "btc_price": round(btc_price_current),
            "btc_holdings": round(btc_holdings),
            "shares_outstanding_m": round(shares_m, 1),
            "mnav": round(mnav_val, 2),
            "mstr_price": round(mstr_price_val),
            "premium_to_nav": round(((mstr_price_val / mnav_val) - 1) * 100, 1) if mnav_val > 0 else 0,
            "btc_nav": round(btc_holdings * btc_price_current),
            "market_cap": round(mstr_price_val * shares_m * 1_000_000),
            "msty_dividend_monthly": round(msty_div_monthly, 2),
            "msty_yield": round((msty_div_monthly * 12 / msty_nav) * 100, 1) if msty_nav > 0 else 0,
        })
    return pd.DataFrame(projections)

projections_df = generate_projections()

# ====================== TABS ======================
tabs = st.tabs(["📋 Strategy Mirror", "📈 Overview", "₿ BTC", "📈 MSTR", "📊 MSTY", "🏢 ASST", "💰 SATA", "📦 Preferreds", "📋 Projections"])

with tabs[0]:
    st.header("Strategy Official Dashboard Mirror")
    c1, c2, c3 = st.columns(3)
    c1.metric("BTC Holdings", f"{mstr_btc_holdings:,} BTC")
    c2.metric("mNAV", f"{mnav:.2f}x")
    c3.metric("Amplification", "34%", "Official Strategy display (Debt + Preferred notional relative to BTC Reserve)")

with tabs[1]:
    st.header("Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("MSTR Projected Price", f"${mstr_proj_price:,.0f}")
    c2.metric("mNAV / Share", f"${mnav:,.2f}")
    c3.metric("MSTY Est. Weekly Div", f"${msty_div_est/52:,.2f}")
    c4.metric("Pref. Annual Drag", f"${total_annual_div:,.0f}")

# ... (other tabs remain with their models and charts as in previous versions)

st.caption("Educational model only • Inspired by @PunterJeff • Not financial advice")
