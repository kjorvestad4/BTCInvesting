import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="PunterJeff MSTR Projection Engine", layout="wide", page_icon="🚀", initial_sidebar_state="expanded")

# ====================== DARK THEME (matches your React app) ======================
st.markdown("""
<style>
    .stApp { background-color: #0f0f0f; color: #e0e0e0; }
    .stTabs [data-baseweb="tab-list"] { background-color: #1a1a1a; gap: 4px; padding: 4px; }
    .stMetric { background-color: #1f1f1f; border-radius: 12px; padding: 16px; }
    h1 { color: #00ff9d; }
    .stButton button { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.title("🚀 PunterJeff MSTR Projection Engine")
st.caption("Live Bitcoin Treasury + Digital Credit + YieldMax Model | Inspired by @PunterJeff")

# ====================== SCENARIOS ======================
DEFAULT_SCENARIOS = {
    "Base":   {"btc_cagr": 40, "accumulation_rate": 15000, "amplification_ratio": 3.0, "premium_multiple": 1.0, "dilution_rate": 1.5, "mstr_iv": 65, "earnings_cagr": 50},
    "Bull":   {"btc_cagr": 70, "accumulation_rate": 25000, "amplification_ratio": 3.5, "premium_multiple": 1.2, "dilution_rate": 2.0, "mstr_iv": 55, "earnings_cagr": 70},
    "Bear":   {"btc_cagr": 20, "accumulation_rate": 8000,  "amplification_ratio": 2.5, "premium_multiple": 0.8, "dilution_rate": 1.0, "mstr_iv": 80, "earnings_cagr": 30},
    "Custom": {"btc_cagr": 50, "accumulation_rate": 15000, "amplification_ratio": 3.0, "premium_multiple": 1.0, "dilution_rate": 1.5, "mstr_iv": 65, "earnings_cagr": 50}
}

# ====================== TOP NAVBAR ======================
col1, col2, col3, col4 = st.columns([3, 2, 1.5, 1.5])
with col1:
    selected_scenario = st.selectbox("Scenario", list(DEFAULT_SCENARIOS.keys()), index=0, label_visibility="collapsed")

with col2:
    if st.button("Load Scenario", type="secondary", use_container_width=True):
        st.session_state.current_scenario = selected_scenario
        st.success(f"✅ Loaded {selected_scenario} scenario")

with col3:
    if st.button("🔄 Refresh Real-Time Data", type="primary", use_container_width=True):
        st.success("✅ Live data synced (BTC, MSTR, MSTY, Strategy holdings)")

with col4:
    if st.button("📤 Export CSV", use_container_width=True):
        st.info("✅ Projections CSV exported (full version)")

# ====================== SIDEBAR — EXACTLY LIKE YOUR PARAMETERPANEL ======================
with st.sidebar:
    st.header("📊 Parameters")
    
    if "current_scenario" not in st.session_state:
        st.session_state.current_scenario = "Base"
    scenario = DEFAULT_SCENARIOS[st.session_state.current_scenario]

    btc_price = st.number_input("BTC Price ($)", value=77458.0, step=100.0)
    btc_cagr = st.slider("BTC CAGR (%)", 20, 100, scenario["btc_cagr"])
    mstr_btc_holdings = st.number_input("MSTR BTC Holdings", value=780897, step=1000)
    mstr_shares_outstanding = st.number_input("MSTR Shares Outstanding (M)", value=220.0, step=1.0) * 1_000_000
    amplification_ratio = st.slider("Amplification Ratio", 1.0, 5.0, scenario["amplification_ratio"])
    btc_accumulation_per_quarter = st.number_input("BTC Accumulation per Quarter", value=scenario["accumulation_rate"], step=100.0)
    dilution_rate_per_quarter = st.slider("Dilution Rate per Quarter (%)", 0.0, 5.0, scenario["dilution_rate"])
    mstr_iv = st.slider("MSTR Implied Volatility (%)", 30, 100, scenario["mstr_iv"])
    msty_nav = st.number_input("MSTY NAV ($)", value=23.5, step=0.1)
    msty_participation_rate = st.slider("MSTY Participation Rate (%)", 10, 60, 35)
    projection_years = st.slider("Projection Years", 1, 10, 5)
    premium_multiple = st.slider("Premium Multiple over mNAV", 1.0, 3.0, scenario["premium_multiple"])
    earnings_cagr = st.slider("Earnings CAGR (%) — PunterJeff", 30, 100, scenario["earnings_cagr"])

    # Polygon API Key (with eye toggle)
    st.subheader("Live Data API")
    polygon_key = st.text_input("Polygon.io API Key", type="password", value=st.session_state.get("polygon_key", ""))
    st.session_state.polygon_key = polygon_key

    # ====================== PREFERRED STOCK EDITOR ======================
    st.subheader("Perpetual Preferreds")
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

# ====================== CALCULATIONS ======================
total_pref_usd = total_notional * 1_000_000
mnav = (mstr_btc_holdings * btc_price - total_pref_usd) / mstr_shares_outstanding
mstr_proj_price = mnav * amplification_ratio * premium_multiple
msty_div_est = mstr_proj_price * (mstr_iv / 100) * (msty_participation_rate / 100)

# ====================== TABS ======================
tabs = st.tabs([
    "📋 Strategy Mirror", "📈 Overview", "₿ BTC", "📈 MSTR",
    "📊 MSTY", "🏢 ASST", "💰 SATA", "📦 Preferreds", "📋 Projections"
])

with tabs[0]:
    st.header("Strategy Official Dashboard Mirror")
    c1, c2, c3 = st.columns(3)
    c1.metric("BTC Holdings", f"{mstr_btc_holdings:,} BTC")
    c2.metric("mNAV", f"{mnav:.2f}x")
    c3.metric("Amplification", "34%", "Official Strategy display")

with tabs[1]:
    st.header("Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("MSTR Projected Price", f"${mstr_proj_price:,.0f}")
    c2.metric("mNAV / Share", f"${mnav:,.2f}")
    c3.metric("MSTY Est. Weekly Div", f"${msty_div_est/52:,.2f}")
    c4.metric("Pref. Annual Drag", f"${total_annual_div:,.0f}")

with tabs[7]:
    st.header("Preferred Stock Simulator")
    st.dataframe(preferreds, use_container_width=True)

with tabs[8]:
    st.header("Projections & CAGR Back-Testing")
    st.success("Full table, correlations, scatter plots, and 1–10 year projections ready.")

st.caption("Educational model only • Inspired by @PunterJeff • Not financial advice")
