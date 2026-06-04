import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. INITIAL SESSION STATE SETUP ---
# This keeps your money and history saved during your browser session
if 'liquid_cash' not in st.session_state:
    st.session_state.liquid_cash = 5000.0
if 'bank_cash' not in st.session_state:
    st.session_state.bank_cash = 50000.0
if 'history' not in st.session_state:
    st.session_state.history = []

# --- 2. DASHBOARD VISUALS ---
st.set_page_config(page_title="MyPersonalBanker", layout="wide")
st.title("🏦 MyPersonalBanker Dashboard")

total_net_worth = st.session_state.liquid_cash + st.session_state.bank_cash

# Metric cards at the top
col1, col2, col3 = st.columns(3)
col1.metric("Total Net Worth", f"₹{total_net_worth:,.2f}")
col2.metric("Liquid Cash Wallet", f"₹{st.session_state.liquid_cash:,.2f}")
col3.metric("Bank Account Balance", f"₹{st.session_state.bank_cash:,.2f}")

st.divider()

# --- 3. THE UPDATED TRANSACTION FORM ---
st.subheader("📝 Transaction Ledger")
with st.form("transaction_form", clear_on_submit=True):
    account_source = st.selectbox("Select Account Source", ["Liquid Cash Wallet", "Bank Account Balance"])
    trans_type = st.radio("Transaction Type", ["Debit (Spend Money)", "Credit (Add Money)"], horizontal=True)
    amount = st.number_input("Amount", min_value=0.0, step=10.0)
    purpose = st.selectbox("Purpose", ["Vegetables/Groceries", "Salary/Income", "Rent/Utilities", "Dining Out", "Other Shopping"])
    
    # NEW CONDITIONAL FIELDS
    item_details = ""
    frequency = "N/A"
    if purpose in ["Vegetables/Groceries", "Other Shopping"]:
        item_details = st.text_input("What did you buy?", placeholder="e.g., Onions, Sugar, Oil")
        frequency = st.selectbox("Item Frequency Type", [
            "High-Frequency (Weekly items like veggies, milk)", 
            "Low-Frequency (Occasional items like salt, sugar, oil)"
        ])

    submit = st.form_submit_button("Log to Ledger")

# --- 4. TRANSACTION LOGIC ---
if submit:
    if amount <= 0:
        st.error("Please enter a valid amount.")
    else:
        # Check current balance for debits
        current_bal = st.session_state.liquid_cash if account_source == "Liquid Cash Wallet" else st.session_state.bank_cash
        
        if trans_type == "Debit (Spend Money)" and amount > current_bal:
            st.error(f"Insufficient funds in {account_source}!")
        else:
            # Mathematical update of balances
            multiplier = -1 if "Debit" in trans_type else 1
            if account_source == "Liquid Cash Wallet":
                st.session_state.liquid_cash += (amount * multiplier)
            else:
                st.session_state.bank_cash += (amount * multiplier)
            
            # Store the record in history
            record = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Account": account_source,
                "Type": trans_type,
                "Amount": amount,
                "Purpose": purpose,
                "Items": item_details,
                "Frequency": frequency
            }
            st.session_state.history.append(record)
            st.success("Transaction successfully logged!")
            st.rerun()

# --- 5. PANTRY TRACKER & HISTORY ---
st.divider()
tab1, tab2 = st.tabs(["📊 Pantry Insights", "📜 Full History"])

with tab1:
    st.subheader("Inventory Refresh Reminders")
    if st.session_state.history:
        df_history = pd.DataFrame(st.session_state.history)
        # Ensure timestamp is readable for math
        df_history['Timestamp'] = pd.to_datetime(df_history['Timestamp'])
        
        col_a, col_b = st.columns(2)
        
        # Sub-section A: High-Frequency (Weekly)
        with col_a:
            st.markdown("#### 🍅 Weekly Essentials Tracker")
            hf_df = df_history[df_history['Frequency'].str.contains("High-Frequency", na=False)]
            if not hf_df.empty:
                last_hf = hf_df.iloc[-1]
                days_since = (datetime.now() - last_hf['Timestamp']).days
                st.info(f"**Last Purchase:** {last_hf['Items']}\n\n**Days Elapsed:** {days_since} days ago")
            else:
                st.write("No weekly essentials logged.")

        # Sub-section B: Low-Frequency (Occasional)
        with col_b:
            st.markdown("#### 🧂 Occasional Staples Tracker")
            lf_df = df_history[df_history['Frequency'].str.contains("Low-Frequency", na=False)]
            if not lf_df.empty:
                last_lf = lf_df.iloc[-1]
                days_since = (datetime.now() - last_lf['Timestamp']).days
                st.warning(f"**Last Purchase:** {last_lf['Items']}\n\n**Days Elapsed:** {days_since} days ago")
            else:
                st.write("No staples logged.")
    else:
        st.info("Log your first grocery purchase to see tracker insights.")

with tab2:
    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)
    else:
        st.info("No transaction history available yet.")
