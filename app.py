import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. INITIAL SESSION STATE ---
if 'liquid_cash' not in st.session_state:
    st.session_state.liquid_cash = 1000.0 
if 'online_cash' not in st.session_state:
    st.session_state.online_cash = 2500.0 
if 'history' not in st.session_state:
    # Pre-loaded history matched with your new categories
    st.session_state.history = [
        {"Date": "2026-06-01", "Year": "2026", "Amount": 529.0, "Type": "Debit", "Purpose": "Utensils/Bills", "Details": "Electricity Bill", "Account": "Online Account"},
        {"Date": "2026-06-02", "Year": "2026", "Amount": 1792.0, "Type": "Debit", "Purpose": "Utensils/Bills", "Details": "Water Bill", "Account": "Online Account"},
        {"Date": "2026-06-03", "Year": "2026", "Amount": 300.0, "Type": "Debit", "Purpose": "Vegetables", "Details": "Kovaka, Beans, Carrot", "Account": "Liquid Wallet"},
        {"Date": "2026-06-04", "Year": "2026", "Amount": 1000.0, "Type": "Credit", "Purpose": "Income/Gift", "Details": "From Amma", "Account": "Liquid Wallet"},
        {"Date": "2026-06-05", "Year": "2026", "Amount": 450.0, "Type": "Debit", "Purpose": "Pantry", "Details": "Sugar, Tea Powder, Ghee", "Account": "Online Account"}
    ]

# --- 2. UI STYLING & CLEAN LAYOUT ---
st.set_page_config(page_title="Personal Banker", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    [data-testid="stMetricValue"] { color: #0f172a !important; font-size: 32px; font-weight: 700; }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
    }
    .welcome-banner {
        background: #1e293b;
        color: white;
        padding: 25px;
        border-radius: 14px;
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. OPENING INTERFACE (Welcome & Balance Display) ---
st.markdown(f"""
    <div class="welcome-banner">
        <h1 style='margin:0; font-size: 28px;'>My Personal Banker</h1>
        <p style='margin:5px 0 0 0; opacity: 0.8;'>Welcome Gopika • {datetime.now().strftime('%A, %d %B %Y')}</p>
    </div>
    """, unsafe_allow_html=True)

total_net = st.session_state.liquid_cash + st.session_state.online_cash
c1, c2, c3 = st.columns(3)
with c1: st.metric("Current Balance (Total)", f"₹{total_net:,.2f}")
with c2: st.metric("Liquid Wallet", f"₹{st.session_state.liquid_cash:,.2f}")
with c3: st.metric("Online Account", f"₹{st.session_state.online_cash:,.2f}")

st.divider()

# --- 4. MAIN LAYOUT: Split into Logging Form (Left) & Expense Chart (Right) ---
left_col, right_col = st.columns([1.4, 1])

with left_col:
    st.subheader("➕ Log New Transaction")
    with st.form("transaction_form", clear_on_submit=True):
        acc = st.selectbox("Account Source", ["Online Account", "Liquid Wallet"])
        typ = st.radio("Transaction Type", ["Debit", "Credit"], horizontal=True)
        purp = st.selectbox("Purpose", ["Vegetables", "Pantry", "Utensils/Bills", "Income/Gift"])
        
        # Dynamic conditional inputs based on selected purpose
        specific_details = ""
        if purp == "Utensils/Bills":
            specific_details = st.selectbox("Select Bill Type", ["Electricity Bill", "Water Bill", "Gas Bill", "Kitchen Utensils", "Other Utilities"])
        elif purp == "Vegetables":
            specific_details = st.text_input("List Raw Vegetables", placeholder="e.g., Tomato, Onion, Potato")
        elif purp == "Pantry":
            specific_details = st.text_input("Specify Pantry Items", placeholder="e.g., Rice, Dal, Spices, Oil")
        else:
            specific_details = st.text_input("Notes / Source", placeholder="e.g., Pocket money, Allowance")
            
        amt = st.number_input("Total Bill Amount (₹)", min_value=0.0, step=10.0)
        
        if st.form_submit_button("Save Entry"):
            if amt > 0:
                mult = -1 if typ == "Debit" else 1
                if acc == "Liquid Wallet": 
                    st.session_state.liquid_cash += (amt * mult)
                else: 
                    st.session_state.online_cash += (amt * mult)
                
                st.session_state.history.append({
                    "Date": datetime.now().strftime("%Y-%m-%d"),
                    "Year": datetime.now().strftime("%Y"),
                    "Amount": amt,
                    "Type": typ,
                    "Purpose": purp,
                    "Details": specific_details,
                    "Account": acc
                })
                st.success("Transaction logged successfully!")
                st.rerun()
            else:
                st.error("Please enter an amount greater than 0.")

with right_col:
    st.subheader("📊 Spending Breakdown")
    df = pd.DataFrame(st.session_state.history)
    
    if not df.empty:
        debits = df[df['Type'] == "Debit"]
        if not debits.empty:
            chart_data = debits.groupby("Purpose")["Amount"].sum()
            st.plotly_chart({
                "data": [{"labels": chart_data.index, "values": chart_data.values, "type": "pie", "hole": .4}],
                "layout": {
                    "margin": {"t": 20, "b": 20, "l": 20, "r": 20},
                    "height": 280,
                    "showlegend": True
                }
            }, use_container_width=True)
        else:
            st.info("No expense data available to display chart.")
    else:
        st.info("No records available.")

st.divider()

# --- 5. CONDITIONAL VIEWS (Available only via options) ---
st.subheader("🔍 View History Options")
show_history = st.checkbox("Show Past Transactions History")
show_groceries = st.checkbox("Show Past Grocery & Pantry Purchases")

if show_history:
    st.markdown("### 📜 Complete Ledger")
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.write("No transactions recorded yet.")

if show_groceries:
    st.markdown("### 🛒 Grocery & Pantry Archive")
    if not df.empty:
        # Filter down strictly to Vegetables and Pantry tracking by Year
        grocery_df = df[df['Purpose'].isin(["Vegetables", "Pantry"])].copy()
        if not grocery_df.empty:
            # Sort or group by Year dropdown filter for easier browsing
            available_years = grocery_df['Year'].unique()
            selected_year = st.selectbox("Filter Archive by Year", sorted(available_years, reverse=True))
            
            filtered_grocery = grocery_df[grocery_df['Year'] == selected_year]
            st.dataframe(filtered_grocery[["Date", "Year", "Purpose", "Details", "Amount", "Account"]], 
                         use_container_width=True, hide_index=True)
        else:
            st.info("No specific grocery or pantry items logged in the system yet.")
    else:
        st.write("No transactions recorded yet.")
