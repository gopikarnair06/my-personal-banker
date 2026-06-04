import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. INITIAL SESSION STATE ---
if 'liquid_cash' not in st.session_state:
    st.session_state.liquid_cash = 1000.0 
if 'online_cash' not in st.session_state:
    st.session_state.online_cash = 2500.0 
if 'history' not in st.session_state:
    # Pre-loading your specific demo data
    st.session_state.history = [
        {"Date": "2026-06-01", "Time": "09:15 AM", "Amount": 529.0, "Purpose": "Utilities (Bill)", "Type": "Debit", "Items": "Network Bill", "Account": "Online"},
        {"Date": "2026-06-02", "Time": "06:30 PM", "Amount": 1792.0, "Purpose": "Utilities (Bill)", "Type": "Debit", "Items": "Electricity Bill", "Account": "Online"},
        {"Date": "2026-06-03", "Time": "11:00 AM", "Amount": 246.0, "Purpose": "Utilities (Bill)", "Type": "Debit", "Items": "Water Bill", "Account": "Online"},
        {"Date": "2026-06-04", "Time": "08:00 AM", "Amount": 1000.0, "Purpose": "Income/Gift", "Type": "Credit", "Items": "From Amma", "Account": "Liquid"},
        {"Date": "2026-06-04", "Time": "05:45 PM", "Amount": 300.0, "Purpose": "Vegetables/Pantry", "Type": "Debit", "Items": "Kovaka, Beans, Carrot", "Account": "Liquid"}
    ]

# --- 2. UI STYLING (Moneyflow Aesthetic) ---
st.set_page_config(page_title="Gopika's Personal Banker", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f4f8; }
    [data-testid="stMetricValue"] { color: #1e3a8a !important; font-size: 28px; }
    .stMetric {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 18px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        border-left: 5px solid #3b82f6;
    }
    .welcome-banner {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        color: white;
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 30px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown(f"""
    <div class="welcome-banner">
        <h1 style='margin:0;'>My Personal Banker</h1>
        <p style='margin:0; opacity: 0.8;'>Welcome Gopika • {datetime.now().strftime('%A, %d %B')}</p>
    </div>
    """, unsafe_allow_html=True)

total_net = st.session_state.liquid_cash + st.session_state.online_cash
c1, c2, c3 = st.columns(3)
with c1: st.metric("Current Balance", f"₹{total_net:,.2f}")
with c2: st.metric("Liquid Wallet", f"₹{st.session_state.liquid_cash:,.2f}")
with c3: st.metric("Online Account", f"₹{st.session_state.online_cash:,.2f}")

st.divider()

# --- 4. SMART FORM ---
st.subheader("➕ Log Activity")
with st.form("main_form", clear_on_submit=True):
    col_x, col_y = st.columns(2)
    with col_x:
        acc = st.selectbox("Account Source", ["Liquid Wallet", "Online Account"])
        typ = st.radio("Type", ["Debit", "Credit"], horizontal=True)
        amt = st.number_input("Amount (₹)", min_value=0.0)
    with col_y:
        purp = st.selectbox("Purpose", ["Vegetables/Pantry", "Utilities (Bill)", "Personal", "Income/Gift"])
        
        # Logic for grocery-specific fields
        items = "N/A"
        freq = "N/A"
        if purp == "Vegetables/Pantry":
            items = st.text_area("Shopping List", placeholder="Onion - 1kg\nSugar - 500g")
            freq = st.selectbox("Frequency", ["High-Frequency (Weekly)", "Low-Frequency (Occasional)"])
        else:
            items = st.text_input("Note (e.g. WiFi Bill)", placeholder="Electricity")

    if st.form_submit_button("Save to Ledger"):
        mult = -1 if typ == "Debit" else 1
        if acc == "Liquid Wallet": st.session_state.liquid_cash += (amt * mult)
        else: st.session_state.online_cash += (amt * mult)
        
        st.session_state.history.append({
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Time": datetime.now().strftime("%I:%M %p"),
            "Amount": amt,
            "Purpose": purp,
            "Type": typ,
            "Items": items,
            "Account": acc
        })
        st.rerun()

st.divider()

# --- 5. HISTORY & PIE CHART ---
df = pd.DataFrame(st.session_state.history)
v1, v2 = st.columns([1.5, 1])

with v1:
    st.subheader("📜 Recent Transactions")
    if not df.empty:
        st.dataframe(df.tail(8), use_container_width=True, hide_index=True)
    else:
        st.info("No records yet.")

with v2:
    st.subheader("📊 Spending Breakdown")
    if not df.empty:
        debits = df[df['Type'] == "Debit"]
        if not debits.empty:
            chart_data = debits.groupby("Purpose")["Amount"].sum()
            # Plotly Pie Chart
            st.plotly_chart({
                "data": [{"labels": chart_data.index, "values": chart_data.values, "type": "pie", "hole": .4}],
                "layout": {"margin": {"t":0, "b":0, "l":0, "r":0}}
            }, use_container_width=True)
        else:
            st.write("No expenses logged yet.")
