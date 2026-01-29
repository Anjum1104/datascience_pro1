
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import glob
import os
import numpy as np

# Set style for premium look
sns.set(style="whitegrid", context="talk")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 150

# Define paths
DATA_DIR = r"ds_anjum/csv_files"
OUTPUT_DIR = r"ds_anjum/outputs"
HISTORICAL_FILE = os.path.join(DATA_DIR, "historical_data.csv")
FEAR_GREED_FILE = os.path.join(DATA_DIR, "fear_greed.csv")

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

ensure_dir(OUTPUT_DIR)

print("Loading data...")
try:
    df_hist = pd.read_csv(HISTORICAL_FILE)
    df_fg = pd.read_csv(FEAR_GREED_FILE)
except FileNotFoundError as e:
    print(f"Error: {e}")
    exit(1)

# --- Preprocessing ---

# 1. Process Historical Data
df_hist['Timestamp IST'] = df_hist['Timestamp IST'].astype(str).str.strip()
df_hist['Dt'] = pd.to_datetime(df_hist['Timestamp IST'], format='%d-%m-%Y %H:%M', errors='coerce')
df_hist['Date'] = df_hist['Dt'].dt.date

# 2. Process Fear Greed Data
df_fg['date'] = pd.to_datetime(df_fg['date'], errors='coerce').dt.date
df_fg.rename(columns={'value': 'fg_value', 'classification': 'fg_class'}, inplace=True)

# 3. Merge
df_merged = pd.merge(df_hist, df_fg, left_on='Date', right_on='date', how='left')
df_merged.dropna(subset=['Dt', 'fg_value'], inplace=True)
df_merged['fg_value'] = pd.to_numeric(df_merged['fg_value'])

# Sort by date for cumulative analysis
df_merged.sort_values(by='Dt', inplace=True)

print(f"Merged Data Shape: {df_merged.shape}")

# --- Advanced Analysis ---

# 1. Cumulative PnL with Sentiment Overlay
df_merged['Cumulative PnL'] = df_merged['Closed PnL'].cumsum()

plt.figure(figsize=(14, 7))
ax = sns.lineplot(data=df_merged, x='Dt', y='Cumulative PnL', color='#2ecc71', linewidth=2)
plt.title("Cumulative PnL Over Time", fontsize=16, weight='bold')
plt.xlabel("Date")
plt.ylabel("Cumulative PnL (USD)")

# Overlay background color based on sentiment (approximate by day)
# This is a simplified overlay for visual effect
# We'll take daily average sentiment to color regions
daily_sentiment = df_merged.groupby('Date')['fg_value'].mean()
# (Advanced overlay logic omitted for brevity, keeping simple clean line)

plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "cumulative_pnl.png"))
plt.close()

# 2. Violin Plot: PnL Distribution by Sentiment
plt.figure(figsize=(12, 7))
sns.violinplot(data=df_merged, x='fg_class', y='Closed PnL', palette='viridis', order=['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'])
plt.title("PnL Distribution Risk Profile by Sentiment", fontsize=16)
plt.xlabel("Market Sentiment")
plt.ylabel("Closed PnL Distribution")
plt.ylim(-500, 1000) # Zoom in to see the belly of the distribution
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "pnl_distribution_violin.png"))
plt.close()

# 3. Position Sizing Behavior
plt.figure(figsize=(10, 6))
sns.barplot(data=df_merged, x='fg_class', y='Size USD', estimator=np.mean, errorbar=None, palette='magma', order=['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'])
plt.title("Average Position Size (USD) by Sentiment", fontsize=16)
plt.xlabel("Sentiment Zone")
plt.ylabel("Avg Position Size ($)")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "position_sizing.png"))
plt.close()

# 4. Volatility / Risk Analysis (Std Dev of PnL)
risk_by_class = df_merged.groupby('fg_class')['Closed PnL'].std().sort_values()

plt.figure(figsize=(10, 6))
risk_by_class.plot(kind='bar', color='#e74c3c')
plt.title("PnL Volatility (Standard Deviation) by Sentiment", fontsize=16)
plt.ylabel("Std Dev of PnL ($)")
plt.xlabel("Sentiment Classification")
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "risk_volatility.png"))
plt.close()

# 5. Win Rate by Sentiment
win_rate_by_class = df_merged.groupby('fg_class').apply(lambda x: (x['Closed PnL'] > 0).mean()).reset_index(name='Win Rate')
plt.figure(figsize=(10, 6))
sns.barplot(data=win_rate_by_class, x='fg_class', y='Win Rate', palette='coolwarm', order=['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed'])
plt.title("Win Rate % by Sentiment", fontsize=16)
plt.ylabel("Win Rate (0.0 - 1.0)")
plt.ylim(0, 1)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "win_rate_by_sentiment.png"))
plt.close()

# 6. Risk-Reward Scatter (PnL vs Size)
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df_merged, x='Size USD', y='Closed PnL', hue='fg_class', alpha=0.6, palette='viridis')
plt.title("Risk-Reward: Position Size vs PnL", fontsize=16)
plt.xlabel("Position Size ($)")
plt.ylabel("Closed PnL ($)")
plt.axhline(0, color='gray', linestyle='--')
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "pnl_vs_size_scatter.png"))
plt.close()

# 7. Daily Performance (Bar or Heatmap proxy)
# Aggregating by Day of Week
df_merged['DayOfWeek'] = df_merged['Dt'].dt.day_name()
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
daily_pnl = df_merged.groupby('DayOfWeek')['Closed PnL'].sum().reindex(day_order)

plt.figure(figsize=(10, 6))
daily_pnl.plot(kind='bar', color='#3498db')
plt.title("Total PnL by Day of Week", fontsize=16)
plt.ylabel("Total Closed PnL ($)")
plt.axhline(0, color='black', linewidth=1)
plt.tight_layout()
plt.savefig(os.path.join(OUTPUT_DIR, "daily_performance.png"))
plt.close()

# --- Insights Generation for Report ---
avg_pnl = df_merged.groupby('fg_class')['Closed PnL'].mean()
win_rate = df_merged.groupby('fg_class').apply(lambda x: (x['Closed PnL'] > 0).mean())

with open(os.path.join("ds_anjum", "ds_report_summary.txt"), "w") as f:
    f.write("Analysis Summary\n")
    f.write("================\n\n")
    f.write("A. RISK metrics (Std Dev of PnL):\n")
    f.write(str(risk_by_class) + "\n\n")
    f.write("B. AvG Position Size:\n")
    f.write(str(df_merged.groupby('fg_class')['Size USD'].mean()) + "\n\n")
    f.write("C. Win Rate:\n")
    f.write(str(win_rate) + "\n\n")
    f.write("D. Total PnL:\n")
    f.write(str(df_merged['Closed PnL'].sum()) + "\n")

print("Advanced Analysis complete. Outputs saved in ds_anjum/outputs/")
