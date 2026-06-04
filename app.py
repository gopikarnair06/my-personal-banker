import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. INITIAL SESSION STATE (Smaller demo amounts) ---
if 'liquid_cash' not in st.session_state:
    st.session_state.liquid_cash = 1000.0  # Reduced for demo
if 'online_cash' not in st.session_state:
    st.session_state.online_cash = 2500.0  # Reduced for demo
if 'history' not in st.session_state:
    # Adding your past demonstration data
    st.session_state.history = [
        {"Date": "2026-06-01", "Timestamp": "10:00:00", "Account": "Liquid Wallet", "Type": "Debit (Spend)", "Amount": 300.0, "Purpose": "Vegetables/Groceries", "Items": "Kovaka (0.5kg), Beans (0.5kg), Carrot (0.5kg)", "Quantity": "1.5kg total", "Frequency": "High-Frequency (Weekly)"},
        {"Date": "2026-06-02", "Timestamp": "11:30:00", "Account": "Online Account", "Type": "Debit (Spend)", "Amount": 320.0, "Purpose": "Other Shopping", "Items": "Sugar (1kg), Oil (1L)", "Quantity": "2 items", "Frequency": "Low-Frequency (Occasional)"}
    ]

# --- 2. STYLING (Fixing the White-on-White text bug) ---
st.set_page_config(page_title="MyPersonalBanker", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    /* Metric Card Fix */
    [data-testid="stMetricValue"] {
        color: #1c1c1c !important; /* Forces text to be dark/visible */
        font-weight: bold;
    }
    [data-testid="stMetricLabel"] {
        color: #4a4a4a !important;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .welcome-banner {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER ---
st.markdown(f"""
    <div class="welcome-banner">
        <h1 style='margin:0;'>Welcome, Gopika</h1>
        <p style='margin:0; opacity: 0.9;'>Managing your expenses & pantry inventory</p>
    </div>
    """, unsafe_allow_html=True)

total_net_worth = st.session_state.liquid_cash + st.session_state.online_cash

col1, col2, col3 = st.columns(3)
with col1: st.metric("Total Net Worth", f"₹{total_net_worth:,.2f}")
with col2: st.metric("Liquid Wallet", f"₹{st.session_state.liquid_cash:,.2f}")
with col3: st.metric("Online Account", f"₹{st.session_state.online_cash:,.2f}")

st.divider()

# --- 4. THE LOGGING FORM ---
st.subheader("➕ Log New Activity")
with st.container():
    with st.form("transaction_form", clear_on_submit=True):
        f_col1, f_col2 = st.columns(2)
        
        with f_col1:
            account_source = st.selectbox("Account Source", ["Liquid Wallet", "Online Account"])
            trans_type = st.radio("Type", ["Debit (Spend)", "Credit (Add)"], horizontal=True)
            amount = st.number_input("Total Bill Amount (₹)", min_value=0.0, step=1.0)
            
        with f_col2:
            purpose = st.selectbox("Purpose", ["Vegetables/Groceries", "Salary/Income", "Rent/Utilities", "Dining Out", "Other Shopping"])
            
            # Conditional fields for the "List" style
            item_list = "N/A"
            frequency = "N/A"
            if purpose in ["Vegetables/Groceries", "Other Shopping"]:
                item_list = st.text_area("Add Your List (Item - Quantity)", placeholder="Onion - 1kg\nKovaka - 0.5kg\nSugar - 1kg")
                frequency = st.selectbox("How often do you buy these?", ["High-Frequency (Weekly)", "Low-Frequency (Occasional)"])
            
        submit = st.form_submit_button("Log Transaction")

# --- 5. LOGIC ---
if submit:
    current_bal = st.session_state.liquid_cash if account_source == "Liquid Wallet" else st.session_state.online_cash
    if "Debit" in trans_type and amount > current_bal:
        st.error("Balance too low for this spend!")
    elif amount <= 0 and "Debit" in trans_type:
        st.warning("Please enter a bill amount.")
    else:
        multiplier = -1 if "Debit" in trans_type else 1
        if account_source == "Liquid Wallet": st.session_state.liquid_cash += (amount * multiplier)
        else: st.session_state.online_cash += (amount * multiplier)
        
        now = datetime.now()
        st.session_state.history.append({
            "Date": now.strftime("%Y-%m-%d"),
            "Timestamp": now.strftime("%H:%M:%S"),
            "Account": account_source,
            "Type": trans_type,
            "Amount": amount,
            "Purpose": purpose,
            "Items": item_list,
            "Frequency": frequency
        })
        st.success("Entry Saved!")
        st.rerun()

st.divider()

# --- 6. HISTORY & PANTRY BILL ---
df_history = pd.DataFrame(st.session_state.history)

c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("📋 Recent Activity")
    if not df_history.empty:
        # Show last 5 entries for a clean look
        st.table(df_history.tail(5)[["Date", "Amount", "Purpose", "Items"]])
    else:
        st.info("No records yet.")

with c2:
    st.subheader("🛒 Monthly Pantry Bill")
    if not df_history.empty:
        curr_month = datetime.now().strftime("%Y-%m")
        pantry_mask = (df_history['Purpose'] == "Vegetables/Groceries") & (df_history['Date'].str.contains(curr_month))
        total_pantry = df_history[pantry_mask]['Amount'].sum()
        
        st.metric("Total Bill (This Month)", f"₹{total_pantry:,.2f}")
        
        # Quick view of items bought
        st.write("**Recently bought items:**")
        last_items = df_history[df_history['Purpose'] == "Vegetables/Groceries"].tail(1)
        if not last_items.empty:
            st.caption(last_items.iloc[0]['Items'])
