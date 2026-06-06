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
        {"Date": "2026-06-04", "Year": "2026", "Month": "2026-06", "Amount": 1000.0, "Type": "Credit", "Purpose": "Allowance/Pocket Money", "Details": "From Amma", "Account": "Liquid Wallet"},
        {"Date": "2026-06-05", "Year": "2026", "Month": "2026-06", "Amount": 450.0, "Type": "Debit", "Purpose": "Pantry", "Details": "Sugar, Tea Powder, Ghee", "Account": "Online Account"}
    ]

# --- 2. LAYOUT CONFIGURATION ---
st.set_page_config(page_title="Personal Finance Tracker", layout="wide")

# --- HEADER & METRICS ---
st.title("Personal Finance Tracker")
st.caption(f"Welcome Gopika • {datetime.now().strftime('%A, %d %B %Y')}")

total_net = st.session_state.liquid_cash + st.session_state.online_cash
c1, c2, c3 = st.columns(3)
with c1: st.metric("Total Balance", f"₹{total_net:,.2f}")
with c2: st.metric("Liquid Wallet", f"₹{st.session_state.liquid_cash:,.2f}")
with c3: st.metric("Online Account", f"₹{st.session_state.online_cash:,.2f}")

st.divider()

df = pd.DataFrame(st.session_state.history)

# --- 3. TOP ROW: TRANSACTION MANAGEMENT ---
col_form, col_table = st.columns([1, 1.5])

with col_form:
    st.subheader("Add Transaction")
    typ = st.radio("Type", ["Debit", "Credit"], horizontal=True)
    
    with st.form("transaction_entry_form", clear_on_submit=True):
        input_date = st.date_input("Date", datetime.now())
        acc = st.selectbox("Account Source", ["Online Account", "Liquid Wallet"])
        
        if typ == "Credit":
            purp = st.selectbox("Category", ["Allowance/Pocket Money", "Gift", "Other Credit"])
            details = st.text_input("Description", placeholder="e.g. Received money details")
        else:
            purp = st.selectbox("Category", ["Vegetables", "Pantry", "Utensils/Bills"])
            if purp == "Utensils/Bills":
                details = st.selectbox("Bill Type", ["Electricity Bill", "Water Bill", "Gas Bill", "Kitchen Utensils"])
            else:
                details = st.text_input("Description", placeholder="e.g. Item details or notes")

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

with col_table:
    st.subheader("Transaction Ledger")
    if not df.empty:
        st.dataframe(
            df[["Date", "Type", "Purpose", "Details", "Amount", "Account"]].rename(
                columns={"Purpose": "Category", "Details": "Description"}
            ).sort_values("Date", ascending=False), 
            use_container_width=True, 
            hide_index=True
        )

st.divider()

# --- 4. BOTTOM ROW: UPDATED ANALYTICS ---
st.subheader("Analytics Dashboard")
col_chart1, col_chart2 = st.columns([1, 1])

with col_chart1:
    st.markdown("### Spending by Category")
    if not df.empty:
        debits = df[df['Type'] == "Debit"]
        if not debits.empty:
            chart_data = debits.groupby("Purpose", as_index=False)["Amount"].sum()
            
            # Horizontal Bar Chart with indicators inside
            bars = alt.Chart(chart_data).mark_bar(color="#2563eb", cornerRadiusEnd=4).encode(
                x=alt.X('Amount:Q', title="Total Spent (₹)"),
                y=alt.Y('Purpose:N', title=None, sort='-x'),
                tooltip=['Purpose', 'Amount']
            ).properties(height=200)

            text = bars.mark_text(
                align='left',
                baseline='middle',
                dx=5,
                color='white'
            ).encode(
                text='Amount:Q'
            )
            
            st.altair_chart(bars + text, use_container_width=True)
        else:
            st.caption("No expenses to show.")

with col_chart2:
    st.markdown("### Daily Spending (Money vs Day)")
    if not df.empty and not df[df['Type'] == 'Debit'].empty:
        # Grouping by Date to show money spent per day
        daily_spent = df[df['Type'] == 'Debit'].groupby("Date", as_index=False)["Amount"].sum()
        
        # Clean line graph with points
        line_chart = alt.Chart(daily_spent).mark_line(
            color="#dc2626", 
            strokeWidth=3,
            point=alt.OverlayMarkDef(color="#dc2626", size=60)
        ).encode(
            x=alt.X('Date:T', title="Day"),
            y=alt.Y('Amount:Q', title="Money Spent (₹)"),
            tooltip=['Date', 'Amount']
        ).properties(height=200)
        
        st.altair_chart(line_chart, use_container_width=True)
    else:
        st.caption("Insufficient data for trend.")
