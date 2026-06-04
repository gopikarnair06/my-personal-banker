import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. INITIAL SESSION STATE ---
if 'liquid_cash' not in st.session_state:
    st.session_state.liquid_cash = 1000.0 
if 'online_cash' not in st.session_state:
    st.session_state.online_cash = 2500.0 
if 'history' not in st.session_state:
    # Pre-loading your specific bills and credit
    st.session_state.history = [
        {"Date": "2026-06-01", "Time": "09:15 AM", "Amount": 529.0, "Purpose": "Network", "Type": "Debit", "Items": "Monthly Recharge", "Account": "Online"},
        {"Date": "2026-06-02", "Time": "06:30 PM", "Amount": 1792.0, "Purpose": "Electricity", "Type": "Debit", "Items": "KSEB Bill", "Account": "Online"},
        {"Date": "2026-06-03", "Time": "11:00 AM", "Amount": 246.0, "Purpose": "Water", "Type": "Debit", "Items": "Water Authority", "Account": "Online"},
        {"Date": "2026-06-04", "Time": "08:00 AM", "Amount": 1000.0, "Purpose": "Amma", "Type": "Credit", "Items": "Pocket Money", "Account": "Liquid"},
        {"Date": "2026-06-04", "Time": "05:45 PM", "Amount": 300.0, "Purpose": "Vegetables", "Type": "Debit", "Items": "Kovaka, Beans, Carrot", "Account": "Liquid"}
    ]

# --- 2. ADVANCED UI STYLING ---
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
        padding: 40px;
        border-radius: 25px;
        margin-bottom: 35px;
        text-align: center;
    }
    .reminder-card {
        background-color: #fffbeb;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #f59e0b;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DASHBOARD TOP ---
st.markdown(f"""
    <div class="welcome-banner">
        <h1 style='margin:0;'>My Personal Banker</h1>
        <p style='margin:0; opacity: 0.8;'>Smart Finance for Gopika • {datetime.now().strftime('%A, %d %B')}</p>
    </div>
    """, unsafe_allow_html=True)

total_net = st.session_state.liquid_cash + st.session_state.online_cash
c1, c2, c3 = st.columns(3)
with c1: st.metric("Current Balance", f"₹{total_net:,.2f}")
with c2: st.metric("Liquid Cash", f"₹{st.session_state.liquid_cash:,.2f}")
with c3: st.metric("Online Balance", f"₹{st.session_state.online_cash:,.2f}")

# --- 4. DAILY REMINDERS ---
st.markdown('<div class="reminder-card">💡 <b>Daily Tip:</b> Check if your KSEB electricity bill is due this week! You have ₹2500 in your Online Account to cover utilities.</div>', unsafe_allow_html=True)

st.divider()

# --- 5. THE FORM ---
st.subheader("🖋️ Log New Entry")
with st.expander("Click to open Transaction Form", expanded=True):
    with st.form("main_form", clear_on_submit=True):
        col_x, col_y = st.columns(2)
        with col_x:
            acc = st.selectbox("Wallet", ["Liquid Wallet", "Online Account"])
            typ = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            amt = st.number_input("Amount (₹)", min_value=0.0)
        with col_y:
            purp = st.selectbox("Category", ["Vegetables/Pantry", "Utilities (Bill)", "Personal", "Income/Gift"])
            
            # Dynamic fields for Groceries
            items = "N/A"
            if purp == "Vegetables/Pantry":
                items = st.text_area("Shopping List", placeholder="Onion - 1kg\nSugar - 500g")
            else:
                items = st.text_input("Short Note", placeholder="e.g. WiFi Bill")

        if st.form_submit_button("✅ Log Transaction"):
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

# --- 6. HISTORY & PIE CHART ---
df = pd.DataFrame(st.session_state.history)

v1, v2 = st.columns([1.5, 1])

with v1:
    st.subheader("📜 Detailed Ledger")
    if not df.empty:
        # Styling the dataframe to look better
        st.dataframe(df.tail(8), use_container_width=True, hide_index=True)
    else:
        st.info("No transactions logged.")

with v2:
    st.subheader("📊 Expense Distribution")
    if not df.empty:
        debits = df[df['Type'] == "Debit"]
        if not debits.empty:
            # We use a Pie Chart here as requested
            chart_data = debits.groupby("Purpose")["Amount"].sum()
            st.write("Where your money goes:")
            st.plotly_chart({
                "data": [{"labels": chart_data.index, "values": chart_data.values, "type": "pie", "hole": .4, "marker": {"colors": ['#3b82f6', '#1e293b', '#f59e0b', '#ef4444']}}],
                "layout": {"showlegend": True, "margin": {"t":0, "b":0, "l":0, "r":0}}
            }, use_container_width=True)
        else
