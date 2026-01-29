
import nbformat as nbf

nb = nbf.v4.new_notebook()

text_intro = """# Trader Behavior & Market Sentiment Analysis

## Objective
Analyze how trading behavior (profitability, risk, sizing) aligns or diverges from overall market sentiment (fear vs greed).
This notebook is designed to be run in Google Colab.

## Setup
Please ensure the `historical_data.csv` and `fear_greed.csv` files are uploaded to the `csv_files/` directory in Colab.
"""

code_setup = """# Install necessary libraries if not present
!pip install pandas matplotlib seaborn
"""

code_imports = """import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# Set Premium Style
sns.set(style="whitegrid", context="talk")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 120

DATA_DIR = "csv_files"
"""

code_load = """# Load Data
try:
    df_hist = pd.read_csv(os.path.join(DATA_DIR, "historical_data.csv"))
    df_fg = pd.read_csv(os.path.join(DATA_DIR, "fear_greed.csv"))
    print("Data loaded successfully.")
except FileNotFoundError as e:
    print(f"Error loading files: {e}")
    print("Please make sure you have created a 'csv_files' folder and uploaded the CSVs.")
"""

code_clean = """# Preprocessing

# 1. Clean Timestamp in Historical Data
df_hist['Timestamp IST'] = df_hist['Timestamp IST'].astype(str).str.strip()
df_hist['Dt'] = pd.to_datetime(df_hist['Timestamp IST'], format='%d-%m-%Y %H:%M', errors='coerce')
df_hist['Date'] = df_hist['Dt'].dt.date

# 2. Clean Fear Greed Data
df_fg['date'] = pd.to_datetime(df_fg['date'], errors='coerce').dt.date
df_fg.rename(columns={'value': 'fg_value', 'classification': 'fg_class'}, inplace=True)
df_fg['fg_value'] = pd.to_numeric(df_fg['fg_value'])

# 3. Merge Datasets
df_merged = pd.merge(df_hist, df_fg, left_on='Date', right_on='date', how='left')
df_merged.dropna(subset=['Dt', 'fg_value'], inplace=True)
df_merged.sort_values(by='Dt', inplace=True) # Ensure sorted by time

print(f"Merged Data Shape: {df_merged.shape}")
"""

text_analysis = """## 1. Cumulative Performance
Visualizing the growth of the portfolio over time.
"""

code_cum_pnl = """# Cumulative PnL Curve
df_merged['Cumulative PnL'] = df_merged['Closed PnL'].cumsum()

plt.figure(figsize=(14, 7))
sns.lineplot(data=df_merged, x='Dt', y='Cumulative PnL', color='#2ecc71', linewidth=2)
plt.title("Cumulative PnL Over Time")
plt.xlabel("Date")
plt.ylabel("Cumulative PnL (USD)")
plt.show()
"""

text_risk = """## 2. Risk & Volatility Analysis
Does the trader take more risk (bigger positions or more volatile PnL) during certain market conditions?
"""

code_risk = """# Violin Plot: PnL Distribution by Sentiment
plt.figure(figsize=(12, 7))
sns.violinplot(data=df_merged, x='fg_class', y='Closed PnL', palette='viridis', 
               order=['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'])
plt.title("PnL Distribution & Risk Profile")
plt.ylim(-500, 1000) # Focusing on the core distribution
plt.show()
"""

code_sizing = """# Position Sizing Analysis
plt.figure(figsize=(10, 6))
sns.barplot(data=df_merged, x='fg_class', y='Size USD', estimator=np.mean, errorbar=None, palette='magma', 
            order=['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'])
plt.title("Average Position Size (USD) by Sentiment")
plt.ylabel("Avg Position Size ($)")
plt.show()
"""

text_stats = """## 3. Summary Statistics
Key performance metrics across sentiment zones.
"""

code_stats = """# Win Rate & Avg PnL
summary = df_merged.groupby('fg_class').agg({
    'Closed PnL': ['mean', 'std', 'sum'],
    'Size USD': 'mean'
})
summary.columns = ['Avg PnL', 'PnL StdDev (Risk)', 'Total PnL', 'Avg Size']
summary['Win Rate'] = df_merged.groupby('fg_class').apply(lambda x: (x['Closed PnL'] > 0).mean())

print(summary)
"""

nb['cells'] = [
    nbf.v4.new_markdown_cell(text_intro),
    nbf.v4.new_code_cell(code_setup),
    nbf.v4.new_code_cell(code_imports),
    nbf.v4.new_code_cell(code_load),
    nbf.v4.new_code_cell(code_clean),
    nbf.v4.new_markdown_cell(text_analysis),
    nbf.v4.new_code_cell(code_cum_pnl),
    nbf.v4.new_markdown_cell(text_risk),
    nbf.v4.new_code_cell(code_risk),
    nbf.v4.new_code_cell(code_sizing),
    nbf.v4.new_markdown_cell(text_stats),
    nbf.v4.new_code_cell(code_stats)
]

with open('ds_anjum/notebook_1.ipynb', 'w') as f:
    nbf.write(nb, f)

print("Notebook created.")
