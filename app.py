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

# --- 2. CONFIG & STYLING ---
st.set_page_config(page_title="Personal Finance Tracker", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Streamlit Personal Finance Tracker")
st.caption(f"Welcome Gopika • {datetime.now().strftime('%A, %d %B %Y')}")
st.divider()

df = pd.DataFrame(st.session_state.history)

# --- 3. THREE-COLUMN LAYOUT (Matching Proposed Design) ---
col_left, col_mid, col_right = st.columns([1, 1.3, 1])

# === LEFT COLUMN: ADD EXPENSE & EXPORTS ===
with col_left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Add Expense")
    with st.form("add_expense_form", clear_on_submit=True):
        input_date = st.date_input("Date", datetime.now())
        acc = st.selectbox("Account Source", ["Online Account", "Liquid Wallet"])
        typ = st.radio("Type", ["Debit", "Credit"], horizontal=True)
        purp = st.selectbox("Category", ["Vegetables", "Pantry", "Utensils/Bills", "Income/Gift"])
        
        # Contextual dynamic fields
        details = ""
        if purp == "Utensils/Bills":
            details = st.selectbox("Bill Type", ["Electricity Bill", "Water Bill", "Gas Bill", "Kitchen Utensils"])
        elif purp == "Vegetables":
            details = st.text_input("List Raw Vegetables", placeholder="e.g. Tomato, Onion")
        elif purp == "Pantry":
            details = st.text_input("Specify Pantry Items", placeholder="e.g. Rice, Spices")
        else:
            details = st.text_input("Notes / Source", placeholder="e.g. Pocket money")
            
        amt = st.number_input("Amount", min_value=0.0, step=10.0)
        
        if st.form_submit_button("Add Expense", use_container_width=True):
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
    st.markdown('</div>', unsafe_allow_html=True)

    # Upload and Download Area
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Upload and Download")
    st.file_uploader("Upload expenses.csv", type=["csv"])
    
    # Export to Excel / CSV logic
    if not df.empty:
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(label="Download CSV", data=csv_buffer.getvalue(), file_name="expenses.csv", mime="text/csv", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# === MIDDLE COLUMN: FILTERS & TRANSACTION TABLE ===
with col_mid:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Filters")
    
    cat_filter = st.selectbox("Category", ["All"] + list(df['Purpose'].unique()) if not df.empty else ["All"])
    month_filter = st.selectbox("Date (Month)", ["All"] + sorted(list(df['Month'].unique()), reverse=True) if not df.empty else ["All"])
    
    # Apply Filters
    filtered_df = df.copy()
    if cat_filter != "All":
        filtered_df = filtered_df[filtered_df['Purpose'] == cat_filter]
    if month_filter != "All":
        filtered_df = filtered_df[filtered_df['Month'] == month_filter]
        
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Transaction Table")
    if not filtered_df.empty:
        st.dataframe(filtered_df[["Date", "Purpose", "Details", "Amount", "Account"]].rename(columns={"Purpose": "Category", "Details": "Description"}), use_container_width=True, hide_index=True)
    else:
        st.info("No transactions found matching filters.")
    st.markdown('</div>', unsafe_allow_html=True)


# === RIGHT COLUMN: SUMMARY, PIE CHART & SPENDING OVER TIME ===
with col_right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Summary")
    total_debits = df[df['Type'] == 'Debit']['Amount'].sum() if not df.empty else 0.0
    st.metric("Total Spending", f"₹{total_debits:,.2f}")
    
    # Small breakdown of balances
    st.text(f"Liquid Wallet: ₹{st.session_state.liquid_cash:,.2f}")
    st.text(f"Online Account: ₹{st.session_state.online_cash:,.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Expenses by Category")
    if not df.empty:
        debits = df[df['Type'] == "Debit"]
        if not debits.empty:
            chart_data = debits.groupby("Purpose", as_index=False)["Amount"].sum()
            
            # Using Altair for the Pie/Donut Chart -> avoids ModuleNotFoundError entirely
            pie = alt.Chart(chart_data).mark_arc(innerRadius=40).encode(
                theta=alt.Theta(field="Amount", type="quantitative"),
                color=alt.Color(field="Purpose", type="nominal", title="Category"),
                tooltip=["Purpose", "Amount"]
            ).properties(height=200)
            st.altair_chart(pie, use_container_width=True)
        else:
            st.write("No debits logged.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Spending Over Time")
    if not df.empty and not df[df['Type'] == 'Debit'].empty:
        time_data = df[df['Type'] == 'Debit'].groupby("Month", as_index=False)["Amount"].sum()
        line = alt.Chart(time_data).mark_line(point=True).encode(
            x=alt.X('Month:N', title='Month'),
            y=alt.Y('Amount:Q', title='Total Spending'),
            tooltip=['Month', 'Amount']
        ).properties(height=150)
        st.altair_chart(line, use_container_width=True)
    else:
        st.write("Not enough timeline data.")
    st.markdown('</div>', unsafe_allow_html=True)import streamlit as st
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

# --- 2. CONFIG & STYLING ---
st.set_page_config(page_title="Personal Finance Tracker", layout="wide")
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    .card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Streamlit Personal Finance Tracker")
st.caption(f"Welcome Gopika • {datetime.now().strftime('%A, %d %B %Y')}")
st.divider()

df = pd.DataFrame(st.session_state.history)

# --- 3. THREE-COLUMN LAYOUT (Matching Proposed Design) ---
col_left, col_mid, col_right = st.columns([1, 1.3, 1])

# === LEFT COLUMN: ADD EXPENSE & EXPORTS ===
with col_left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Add Expense")
    with st.form("add_expense_form", clear_on_submit=True):
        input_date = st.date_input("Date", datetime.now())
        acc = st.selectbox("Account Source", ["Online Account", "Liquid Wallet"])
        typ = st.radio("Type", ["Debit", "Credit"], horizontal=True)
        purp = st.selectbox("Category", ["Vegetables", "Pantry", "Utensils/Bills", "Income/Gift"])
        
        # Contextual dynamic fields
        details = ""
        if purp == "Utensils/Bills":
            details = st.selectbox("Bill Type", ["Electricity Bill", "Water Bill", "Gas Bill", "Kitchen Utensils"])
        elif purp == "Vegetables":
            details = st.text_input("List Raw Vegetables", placeholder="e.g. Tomato, Onion")
        elif purp == "Pantry":
            details = st.text_input("Specify Pantry Items", placeholder="e.g. Rice, Spices")
        else:
            details = st.text_input("Notes / Source", placeholder="e.g. Pocket money")
            
        amt = st.number_input("Amount", min_value=0.0, step=10.0)
        
        if st.form_submit_button("Add Expense", use_container_width=True):
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
    st.markdown('</div>', unsafe_allow_html=True)

    # Upload and Download Area
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Upload and Download")
    st.file_uploader("Upload expenses.csv", type=["csv"])
    
    # Export to Excel / CSV logic
    if not df.empty:
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(label="Download CSV", data=csv_buffer.getvalue(), file_name="expenses.csv", mime="text/csv", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


# === MIDDLE COLUMN: FILTERS & TRANSACTION TABLE ===
with col_mid:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Filters")
    
    cat_filter = st.selectbox("Category", ["All"] + list(df['Purpose'].unique()) if not df.empty else ["All"])
    month_filter = st.selectbox("Date (Month)", ["All"] + sorted(list(df['Month'].unique()), reverse=True) if not df.empty else ["All"])
    
    # Apply Filters
    filtered_df = df.copy()
    if cat_filter != "All":
        filtered_df = filtered_df[filtered_df['Purpose'] == cat_filter]
    if month_filter != "All":
        filtered_df = filtered_df[filtered_df['Month'] == month_filter]
        
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Transaction Table")
    if not filtered_df.empty:
        st.dataframe(filtered_df[["Date", "Purpose", "Details", "Amount", "Account"]].rename(columns={"Purpose": "Category", "Details": "Description"}), use_container_width=True, hide_index=True)
    else:
        st.info("No transactions found matching filters.")
    st.markdown('</div>', unsafe_allow_html=True)


# === RIGHT COLUMN: SUMMARY, PIE CHART & SPENDING OVER TIME ===
with col_right:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Summary")
    total_debits = df[df['Type'] == 'Debit']['Amount'].sum() if not df.empty else 0.0
    st.metric("Total Spending", f"₹{total_debits:,.2f}")
    
    # Small breakdown of balances
    st.text(f"Liquid Wallet: ₹{st.session_state.liquid_cash:,.2f}")
    st.text(f"Online Account: ₹{st.session_state.online_cash:,.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Expenses by Category")
    if not df.empty:
        debits = df[df['Type'] == "Debit"]
        if not debits.empty:
            chart_data = debits.groupby("Purpose", as_index=False)["Amount"].sum()
            
            # Using Altair for the Pie/Donut Chart -> avoids ModuleNotFoundError entirely
            pie = alt.Chart(chart_data).mark_arc(innerRadius=40).encode(
                theta=alt.Theta(field="Amount", type="quantitative"),
                color=alt.Color(field="Purpose", type="nominal", title="Category"),
                tooltip=["Purpose", "Amount"]
            ).properties(height=200)
            st.altair_chart(pie, use_container_width=True)
        else:
            st.write("No debits logged.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("Spending Over Time")
    if not df.empty and not df[df['Type'] == 'Debit'].empty:
        time_data = df[df['Type'] == 'Debit'].groupby("Month", as_index=False)["Amount"].sum()
        line = alt.Chart(time_data).mark_line(point=True).encode(
            x=alt.X('Month:N', title='Month'),
            y=alt.Y('Amount:Q', title='Total Spending'),
            tooltip=['Month', 'Amount']
        ).properties(height=150)
        st.altair_chart(line, use_container_width=True)
    else:
        st.write("Not enough timeline data.")
    st.markdown('</div>', unsafe_allow_html=True)
