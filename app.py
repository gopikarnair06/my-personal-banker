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
    with st.form("transaction_entry_form", clear_on_submit=True):
        input_date = st.date_input("Date", datetime.now())
        acc = st.selectbox("Account Source", ["Online Account", "Liquid Wallet"])
        typ = st.radio("Type", ["Debit", "Credit"], horizontal=True)
        
        # Fixed: Cleaner dynamic options for Credit vs Debit
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
                # Math calculation that alters the balance instantly
                mult = -1 if typ == "Debit" else 1
                if acc == "Liquid Wallet": 
                    st.session_state.liquid_cash += (amt * mult)
                else: 
                    st.session_state.online_cash += (amt * mult)
                
                # Append to active session history
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

    if not df.empty:
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(label="Export Ledger to CSV", data=csv_buffer.getvalue(), file_name="expenses.csv", mime="text/csv", use_container_width=True)

with col_table:
    st.subheader("Filters")
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

    st.subheader("Transaction Ledger")
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

st.divider()

# --- 4. BOTTOM ROW: ANALYTICS VISUALIZATIONS ---
st.subheader("Analytics")
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("### Expenses by Category")
    if not df.empty:
        debits = df[df['Type'] == "Debit"]
        if not debits.empty:
            chart_data = debits.groupby("Purpose", as_index=False)["Amount"].sum()
            pie = alt.Chart(chart_data).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="Amount", type="quantitative"),
                color=alt.Color(field="Purpose", type="nominal", title=None),
                tooltip=["Purpose", "Amount"]
            ).properties(height=240)
            st.altair_chart(pie, use_container_width=True)
        else:
            st.caption("No debit history available to generate categorical charts.")

with col_chart2:
    st.markdown("### Spending Trend")
    if not df.empty and not df[df['Type'] == 'Debit'].empty:
        time_data = df[df['Type'] == 'Debit'].groupby("Month", as_index=False)["Amount"].sum()
        line = alt.Chart(time_data).mark_line(point=True, color="#2563eb").encode(
            x=alt.X('Month:N', title="Reporting Period"),
            y=alt.Y('Amount:Q', title="Aggregate Expenses (₹)"),
            tooltip=['Month', 'Amount']
        ).properties(height=240)
        st.altair_chart(line, use_container_width=True)
    else:
        st.caption("Insufficient historical data points to generate timelines.")
