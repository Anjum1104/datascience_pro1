
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np

# --- Configuration ---
st.set_page_config(page_title="Trader Behavior Dashboard", page_icon="📈", layout="wide")

# Apply custom CSS for a "premium" look
st.markdown("""
<style>
    .metric-card {
        background-color: #262730;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2ecc71;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    .stMetricIsDecrease { color: #e74c3c !important; }
    .stMetricIsIncrease { color: #2ecc71 !important; }
</style>
""", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data():
    data_dir = r"ds_anjum/csv_files"
    hist_file = os.path.join(data_dir, "historical_data.csv")
    fg_file = os.path.join(data_dir, "fear_greed.csv")

    try:
        df_hist = pd.read_csv(hist_file)
        df_fg = pd.read_csv(fg_file)
    except FileNotFoundError:
        return None, None

    # Preprocessing
    df_hist['Timestamp IST'] = df_hist['Timestamp IST'].astype(str).str.strip()
    df_hist['Dt'] = pd.to_datetime(df_hist['Timestamp IST'], format='%d-%m-%Y %H:%M', errors='coerce')
    df_hist['Date'] = df_hist['Dt'].dt.date
    
    df_fg['date'] = pd.to_datetime(df_fg['date'], errors='coerce').dt.date
    df_fg.rename(columns={'value': 'fg_value', 'classification': 'fg_class'}, inplace=True)
    df_fg['fg_value'] = pd.to_numeric(df_fg['fg_value'])

    # Merge
    df_merged = pd.merge(df_hist, df_fg, left_on='Date', right_on='date', how='left')
    df_merged.dropna(subset=['Dt', 'fg_value'], inplace=True)
    df_merged.sort_values(by='Dt', inplace=True)
    
    return df_merged, df_fg

df_main, df_fg_raw = load_data()

if df_main is None:
    st.error("Data files not found! Please ensure 'historical_data.csv' and 'fear_greed.csv' are in 'ds_anjum/csv_files'.")
    st.stop()

# --- Sidebar Controls ---
st.sidebar.title("Configuration")

# Date Filter
min_date = df_main['Date'].min()
max_date = df_main['Date'].max()
start_date, end_date = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# Sentiment Filter
all_sentiments = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']
selected_sentiments = st.sidebar.multiselect("Filter by Market Sentiment", all_sentiments, default=all_sentiments)

# Simulator Inputs
st.sidebar.markdown("---")
st.sidebar.subheader("💰 Strategy Simulator")
initial_capital = st.sidebar.number_input("Initial Capital ($)", value=10000, step=1000)
risk_per_trade = st.sidebar.slider("Risk Factor (Leverage Proxy)", 0.5, 3.0, 1.0)

# --- Filtering Data ---
mask = (
    (df_main['Date'] >= start_date) & 
    (df_main['Date'] <= end_date) & 
    (df_main['fg_class'].isin(selected_sentiments))
)
df_filtered = df_main.loc[mask].copy()

if df_filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# --- Main Dashboard ---
st.title("📊 Trader Behavior & Market Sentiment")
st.markdown("Analyze how trading performance correlates with market fear and greed.")

# KPI Row
col1, col2, col3, col4 = st.columns(4)

total_pnl = df_filtered['Closed PnL'].sum()
win_rate = (df_filtered['Closed PnL'] > 0).mean() * 100
avg_pnl = df_filtered['Closed PnL'].mean()
total_trades = len(df_filtered)

with col1:
    st.metric("Total PnL", f"${total_pnl:,.2f}", delta_color="normal")
with col2:
    st.metric("Win Rate", f"{win_rate:.1f}%")
with col3:
    st.metric("Avg PnL per Trade", f"${avg_pnl:.2f}")
with col4:
    st.metric("Total Trades", total_trades)

# --- Visualizations ---

# 1. Cumulative PnL Curve
st.subheader("📈 Cumulative Performance")
df_filtered['Simulated PnL'] = df_filtered['Closed PnL'] * risk_per_trade
df_filtered['Equity Curve'] = initial_capital + df_filtered['Simulated PnL'].cumsum()

fig_equity = px.line(df_filtered, x='Dt', y='Equity Curve', title=f"Account Growth (Starting ${initial_capital:,})",
                     labels={'Dt': 'Date', 'Equity Curve': 'Account Balance ($)'})
fig_equity.update_traces(line_color='#2ecc71', line_width=3)
fig_equity.update_layout(template="plotly_dark")
st.plotly_chart(fig_equity, use_container_width=True)

# 2. Risk & Distribution Analysis
st.subheader("⚖️ Risk & Behavior Analysis")
col_left, col_right = st.columns(2)

with col_left:
    # Violin/Box Plot for PnL Distribution
    fig_dist = px.box(df_filtered, x='fg_class', y='Closed PnL', color='fg_class',
                      category_orders={'fg_class': all_sentiments},
                      title="PnL Distribution by Sentiment",
                      color_discrete_sequence=px.colors.qualitative.Vivid)
    fig_dist.update_layout(showlegend=False, template="plotly_dark")
    st.plotly_chart(fig_dist, use_container_width=True)

with col_right:
    # Average Position Size
    avg_size = df_filtered.groupby('fg_class')['Size USD'].mean().reset_index()
    fig_size = px.bar(avg_size, x='fg_class', y='Size USD', color='fg_class',
                      category_orders={'fg_class': all_sentiments},
                      title="Avg Position Size by Sentiment (Conviction)",
                      color_discrete_sequence=px.colors.qualitative.Bold)
    fig_size.update_layout(showlegend=False, template="plotly_dark")
    st.plotly_chart(fig_size, use_container_width=True)

# 3. Data Table (Raw Data View)
with st.expander("📄 View Raw Trade Data"):
    st.dataframe(df_filtered[['Dt', 'Coin', 'Side', 'Size USD', 'Closed PnL', 'fg_class', 'fg_value']].sort_values(by='Dt', ascending=False))

# --- Summary & Recommendations ---
st.markdown("---")
st.subheader("💡 Automated Insights")

best_sentiment = df_filtered.groupby('fg_class')['Closed PnL'].mean().idxmax()
worst_sentiment = df_filtered.groupby('fg_class')['Closed PnL'].mean().idxmin()

st.info(f"""
- **Best Performing Limit**: You trade best during **{best_sentiment}** markets.
- **Risk Alert**: The lowest average PnL occurs during **{worst_sentiment}**. Consider reducing position size in these conditions.
- **Current Simulator**: With a risk factor of **{risk_per_trade}x**, your final account balance would be **${df_filtered['Equity Curve'].iloc[-1]:,.2f}**.
""")
