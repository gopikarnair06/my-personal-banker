import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import io

# --- 1. INITIAL SESSION STATE ---
if 'liquid_cash' not in st.session_state:
    st.session_state.liquid_cash = 1000.0 
if 'online_cash' not in st.session_state:
    st.session_state.online_cash = 2500.0 
if 'history' not in st.session_state:
    st.session_state.history = [
        {"Date": "2026-06-01", "Year": "2026", "Month": "2026-06", "Amount": 529.0, "Type": "Debit", "Purpose": "Utensils/Bills", "Details": "Electricity Bill", "Account": "Online Account"},
        {"Date": "2026-06-02", "Year": "2026", "Month": "2026-06", "Amount": 1792.0, "Type": "Debit", "Purpose": "Utensils/Bills", "Details": "Water Bill", "Account": "Online Account"},
        {"Date": "2026-06-03", "Year": "2026", "Month": "2026-06", "Amount": 300.0, "Type": "Debit", "Purpose": "Vegetables", "Details": "Kovaka, Beans, Carrot", "Account": "Liquid Wallet"},
        {"Date": "2026-06-04", "Year": "2026", "Month": "2026-06", "Amount": 1000.0, "Type": "Credit", "Purpose": "Income/Gift", "Details": "From Amma", "Account": "Liquid Wallet"},
        {"Date": "2026-06-05", "Year": "2026", "Month": "2026-06", "Amount": 450.0, "Type": "Debit", "Purpose": "Pantry", "Details": "Sugar, Tea Powder, Ghee", "Account": "Online Account"}
    ]

# --- 2. CONFIG & MINIMALIST STYLING ---
st.set_page_config(page_title="Personal Finance Tracker", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #fafafa; }
    .reportview-container { padding-top: 0px; }
    h1 { margin-top: 0px; font-weight: 700; color: #1e293b; }
    h3 { font-size: 18px; font-weight: 600; color: #334155; margin-bottom: 10px; }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 12px 20px;
        border-radius: 8px;
        border: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER & BALANCE ROW ---
st.title("Personal Finance Tracker")
st.caption(f"Welcome Gopika • {datetime.now().strftime('%A, %d %B %Y')}")

total_net = st.session_state.liquid_cash + st.session_state.online_cash
c1, c2, c3 = st.columns(3)
with c1: st.metric("Total Balance", f"₹{total_net:,.2f}")
with c2: st.metric("Liquid Wallet", f"₹{st.session_state.liquid_cash:,.2f}")
with c3: st.metric("Online Account", f"₹{st.session_state.online_cash:,.2f}")

st.divider()

df = pd.DataFrame(st.session_state.history)

# --- 3. CLEAN THREE-COLUMN LAYOUT ---
col_left, col_mid, col_right = st.columns([1, 1.3, 1])

# === LEFT COLUMN: SMART DYNAMIC FORM ===
with col_left:
    st.markdown("### ➕ Add Transaction")
    with st.form("add_transaction_form", clear_on_submit=True):
        input_date = st.date_input("Date", datetime.now())
        acc = st.selectbox("Account Source", ["Online Account", "Liquid Wallet"])
        typ = st.radio("Type", ["Debit", "Credit"], horizontal=True)
        
        # Smart Filtering based on Credit / Debit choice
        if typ == "Credit":
            purp = st.selectbox("Category", ["Income/Gift", "Other Credit"])
            details = st.text_input("Notes / Source", placeholder="e.g. Allowance from Amma")
        else:
            purp = st.selectbox("Category", ["Vegetables", "Pantry", "Utensils/Bills"])
            
            # Sub-options conditional on selected Debit Category
            if purp == "Utensils/Bills":
                details = st.selectbox("Bill Type", ["Electricity Bill", "Water Bill", "Gas Bill", "Kitchen Utensils"])
            elif purp == "Vegetables":
                details = st.text_input("List Raw Vegetables", placeholder="e.g. Tomato, Onion, Chili")
            elif purp == "Pantry":
                details = st.text_input("Specify Pantry Items", placeholder="e.g. Rice, Coconut Oil, Tea")

        amt = st.number_input("Amount (₹)", min_value=0.0, step=10.0)
        
        if st.form_submit_button("Save to Ledger", use_container_width=True):
            if amt > 0:
                mult = -1 if typ == "Debit" else 1
                if acc == "Liquid Wallet": st.session_state.liquid_cash += (amt * mult)
                else: st.session_state.online_cash += (amt * mult)
                
                st.session_state.history.append({
                    "Date": input_date.strftime("%Y-%m-%d"),
                    "Year": input_date.strftime("%Y"),
                    "Month": input_date.strftime("%Y-%m"),
                    "Amount": amt,
                    "Type": typ,
                    "Purpose": purp,
                    "Details": details,
                    "Account": acc
                })
                st.rerun()

    # Minimalist download area
    if not df.empty:
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(label="📥 Export Ledger to CSV", data=csv_buffer.getvalue(), file_name="expenses.csv", mime="text/csv", use_container_width=True)


# === MIDDLE COLUMN: FILTERS & TRANSACTIONS ===
with col_mid:
    st.markdown("### 🔍 Filters")
    f_c1, f_c2 = st.columns(2)
    with f_c1:
        cat_filter = st.selectbox("Filter Category", ["All"] + list(df['Purpose'].unique()) if not df.empty else ["All"])
    with f_c2:
        month_filter = st.selectbox("Filter Month", ["All"] + sorted(list(df['Month'].unique()), reverse=True) if not df.empty else ["All"])
    
    filtered_df = df.copy()
    if cat_filter != "All":
        filtered_df = filtered_df[filtered_df['Purpose'] == cat_filter]
    if month_filter != "All":
        filtered_df = filtered_df[filtered_df['Month'] == month_filter]

    st.markdown("### 📜 Transaction Ledger")
    if not filtered_df.empty:
        st.dataframe(
            filtered_df[["Date", "Type", "Purpose", "Details", "Amount", "Account"]].rename(
                columns={"Purpose": "Category", "Details": "Description"}
            ), 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.info("No matching records found.")


# === RIGHT COLUMN: VISUALIZATIONS ===
with col_right:
    st.markdown("### 📊 Expenses by Category")
    if not df.empty:
        debits = df[df['Type'] == "Debit"]
        if not debits.empty:
            chart_data = debits.groupby("Purpose", as_index=False)["Amount"].sum()
            pie = alt.Chart(chart_data).mark_arc(innerRadius=45).encode(
                theta=alt.Theta(field="Amount", type="quantitative"),
                color=alt.Color(field="Purpose", type="nominal", title=None),
                tooltip=["Purpose", "Amount"]
            ).properties(height=200)
            st.altair_chart(pie, use_container_width=True)
        else:
            st.caption("No debit data to show chart.")
            
    st.markdown("### 📈 Spending Trend")
    if not df.empty and not df[df['Type'] == 'Debit'].empty:
        time_data = df[df['Type'] == 'Debit'].groupby("Month", as_index=False)["Amount"].sum()
        line = alt.Chart(time_data).mark_line(point=True, color="#3b82f6").encode(
            x=alt.X('Month:N', title=None),
            y=alt.Y('Amount:Q', title=None),
            tooltip=['Month', 'Amount']
        ).properties(height=140)
        st.altair_chart(line, use_container_width=True)
    else:
        st.caption("No timeline trend data.")
