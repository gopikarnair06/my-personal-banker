import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. INITIAL SESSION STATE ---
if 'liquid_cash' not in st.session_state:
    st.session_state.liquid_cash = 5000.0
if 'online_cash' not in st.session_state:
    st.session_state.online_cash = 50000.0
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 2. STYLING (The "Moneyflow" Look) ---
st.set_page_config(page_title="MyPersonalBanker", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #eee;
    }
    .welcome-banner {
        background: linear-gradient(90deg, #4b6cb7 0%, #182848 100%);
        color: white;
        padding: 40px;
        border-radius: 20px;
        margin-bottom: 30px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. BLUE HEADER BANNER ---
st.markdown(f"""
    <div class="welcome-banner">
        <h1>Welcome to your Dashboard, Gopika!</h1>
        <p>Keep track of your cash flow and pantry essentials in one place.</p>
    </div>
    """, unsafe_allow_html=True)

total_net_worth = st.session_state.liquid_cash + st.session_state.online_cash

# Top Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Net Worth", f"₹{total_net_worth:,.2f}")
with col2:
    st.metric("Liquid Wallet", f"₹{st.session_state.liquid_cash:,.2f}")
with col3:
    st.metric("Online Account", f"₹{st.session_state.online_cash:,.2f}")

st.divider()

# --- 4. TRANSACTION FORM ---
# Using a clean column layout for the form
st.subheader("➕ Log New Activity")
with st.container():
    with st.form("transaction_form", clear_on_submit=True):
        f_col1, f_col2, f_col3 = st.columns(3)
        with f_col1:
            account_source = st.selectbox("Account Source", ["Liquid Wallet", "Online Account"])
            trans_type = st.radio("Type", ["Debit (Spend)", "Credit (Add)"], horizontal=True)
        with f_col2:
            amount = st.number_input("Amount (₹)", min_value=0.0, step=1.0)
            purpose = st.selectbox("Purpose", ["Vegetables/Groceries", "Salary/Income", "Rent/Utilities", "Dining Out", "Other Shopping"])
        with f_col3:
            # Conditional Fields for Grocery only
            item_details = "N/A"
            quantity = "N/A"
            frequency = "N/A"
            if purpose in ["Vegetables/Groceries", "Other Shopping"]:
                item_details = st.text_input("Item Name")
                quantity = st.text_input("Quantity (kg/pkt)")
                frequency = st.selectbox("Frequency", ["High-Frequency (Weekly)", "Low-Frequency (Occasional)"])
            else:
                st.write("No extra details needed for this category.")
        
        submit = st.form_submit_button("Log Transaction")

# --- 5. TRANSACTION LOGIC ---
if submit:
    current_bal = st.session_state.liquid_cash if account_source == "Liquid Wallet" else st.session_state.online_cash
    if "Debit" in trans_type and amount > current_bal:
        st.error("Insufficient Funds!")
    elif amount <= 0:
        st.warning("Please enter an amount.")
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
            "Items": item_details,
            "Quantity": quantity,
            "Frequency": frequency
        })
        st.success("Successfully Logged!")
        st.rerun()

st.divider()

# --- 6. INSIGHTS SECTION ---
df_history = pd.DataFrame(st.session_state.history)

c1, c2 = st.columns([1, 1])

with c1:
    st.subheader("📋 Today's Flow")
    if not df_history.empty:
        today_data = df_history[df_history['Date'] == datetime.now().strftime("%Y-%m-%d")]
        if not today_data.empty:
            st.dataframe(today_data[["Timestamp", "Account", "Amount", "Purpose", "Items"]], use_container_width=True, hide_index=True)
        else:
            st.info("No activity today yet.")
    else:
        st.info("Log a transaction to start.")

with c2:
    st.subheader("🛒 Pantry Tracker")
    if not df_history.empty:
        # Monthly Pantry Bill calculation
        curr_month = datetime.now().strftime("%Y-%m")
        pantry_total = df_history[(df_history['Purpose'] == "Vegetables/Groceries") & 
                                  (df_history['Date'].str.contains(curr_month))]['Amount'].sum()
        
        st.metric("This Month's Pantry Bill", f"₹{pantry_total:,.2f}")
        
        # Frequency Reminders
        hf = df_history[df_history['Frequency'] == "High-Frequency (Weekly)"]
        if not hf.empty:
            st.info(f"📍 Last Weekly Shop: {hf.iloc[-1]['Items']} ({hf.iloc[-1]['Date']})")
    else:
        st.write("Data will appear here once you log items.")

st.divider()

# --- 7. EXPENSE CHART (Moneyflow Style) ---
st.subheader("📊 Spending Breakdown")
if not df_history.empty:
    debit_df = df_history[df_history['Type'].str.contains("Debit")]
    if not debit_df.empty:
        chart_data = debit_df.groupby("Purpose")["Amount"].sum()
        st.bar_chart(chart_data)
    else:
        st.write("Add some expenses to see the chart.")
