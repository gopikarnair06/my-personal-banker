import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. INITIAL SESSION STATE (Reflecting your specific demo data) ---
if 'liquid_cash' not in st.session_state:
    st.session_state.liquid_cash = 1000.0 
if 'online_cash' not in st.session_state:
    st.session_state.online_cash = 2500.0 
if 'history' not in st.session_state:
    # Pre-loading your specific utility bills and credit from Amma
    st.session_state.history = [
        {"Date": "2026-06-01", "Amount": 529.0, "Purpose": "Rent/Utilities", "Type": "Debit (Spend)", "Items": "Network Bill", "Account": "Online Account"},
        {"Date": "2026-06-02", "Amount": 1792.0, "Purpose": "Rent/Utilities", "Type": "Debit (Spend)", "Items": "Electricity Bill", "Account": "Online Account"},
        {"Date": "2026-06-03", "Amount": 246.0, "Purpose": "Rent/Utilities", "Type": "Debit (Spend)", "Items": "Water Bill", "Account": "Online Account"},
        {"Date": "2026-06-04", "Amount": 1000.0, "Purpose": "Salary/Income", "Type": "Credit (Add)", "Items": "Received from Amma", "Account": "Liquid Wallet"},
        {"Date": "2026-06-04", "Amount": 300.0, "Purpose": "Vegetables/Groceries", "Type": "Debit (Spend)", "Items": "Kovaka, Beans, Carrot", "Account": "Liquid Wallet"}
    ]

# --- 2. STYLING (The "Moneyflow" Aesthetic) ---
st.set_page_config(page_title="MyPersonalBanker", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f4f7f9; }
    [data-testid="stMetricValue"] { color: #1e3a8a !important; font-weight: bold; }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .welcome-banner {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 35px;
        border-radius: 20px;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER & METRICS ---
st.markdown(f"""
    <div class="welcome-banner">
        <h1 style='margin:0;'>Welcome, Gopika</h1>
        <p style='margin:0; opacity: 0.8;'>Tracking Flow & Pantry Essentials</p>
    </div>
    """, unsafe_allow_html=True)

total_net = st.session_state.liquid_cash + st.session_state.online_cash
c1, c2, c3 = st.columns(3)
with c1: st.metric("Total Net Worth", f"₹{total_net:,.2f}")
with c2: st.metric("Liquid Wallet", f"₹{st.session_state.liquid_cash:,.2f}")
with c3: st.metric("Online Account", f"₹{st.session_state.online_cash:,.2f}")

st.divider()

# --- 4. SMART TRANSACTION FORM ---
st.subheader("➕ Log Activity")
with st.form("transaction_form", clear_on_submit=True):
    col_a, col_b = st.columns(2)
    
    with col_a:
        account_source = st.selectbox("Account Source", ["Liquid Wallet", "Online Account"])
        trans_type = st.radio("Type", ["Debit (Spend)", "Credit (Add)"], horizontal=True)
        amount = st.number_input("Amount (₹)", min_value=0.0, step=1.0)
        
    with col_b:
        purpose = st.selectbox("Purpose", ["Vegetables/Groceries", "Other Shopping", "Rent/Utilities", "Salary/Income", "Dining Out"])
        
        # LOGIC: Only show Item List/Frequency if it's Grocery or Shopping
        item_list = "N/A"
        frequency = "N/A"
        if purpose in ["Vegetables/Groceries", "Other Shopping"]:
            item_list = st.text_area("List Items (e.g. Onion - 1kg)", placeholder="Onion - 1kg\nSugar - 1kg")
            frequency = st.selectbox("Frequency", ["High-Frequency (Weekly)", "Low-Frequency (Occasional)"])
        else:
            # For utilities/income, just a simple note field
            item_list = st.text_input("Note (Optional)", placeholder="e.g. Electricity bill")

    if st.form_submit_button("Save to Ledger"):
        # Balance Math
        multiplier = -1 if "Debit" in trans_type else 1
        if account_source == "Liquid Wallet": st.session_state.liquid_cash += (amount * multiplier)
        else: st.session_state.online_cash += (amount * multiplier)
        
        st.session_state.history.append({
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Amount": amount,
            "Purpose": purpose,
            "Type": trans_type,
            "Items": item_list,
            "Account": account_source
        })
        st.rerun()

st.divider()

# --- 5. DATA VISUALS (History & Graph) ---
df = pd.DataFrame(st.session_state.history)

v1, v2 = st.columns([1, 1])

with v1:
    st.subheader("📋 Transaction History")
    if not df.empty:
        st.dataframe(df.tail(10), use_container_width=True, hide_index=True)

with v2:
    st.subheader("📉 Expense Breakdown")
    if not df.empty:
        # Filter only debits for the chart
        debits_only = df[df['Type'] == "Debit (Spend)"]
        if not debits_only.empty:
            chart_data = debits_only.groupby("Purpose")["Amount"].sum()
            st.bar_chart(chart_data)
        else:
            st.write("No expenses logged yet.")
