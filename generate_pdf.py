from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(44, 62, 80)
        self.cell(0, 10, 'Data Science Report: Trader Behavior & Market Sentiment', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(52, 152, 219)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, f"  {title}", 0, 1, 'L', 1)
        self.set_text_color(0, 0, 0)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 6, body)
        self.ln()

    def add_chart(self, img_path, title, description=None):
        if os.path.exists(img_path):
            self.add_page()
            self.chapter_title(title)
            if description:
                self.set_font('Arial', 'I', 11)
                self.multi_cell(0, 6, description)
                self.ln(5)
            
            # Center image
            # A4 width is 210mm. If image is 170mm, margin is (210-170)/2 = 20
            self.image(img_path, x=20, w=170)
        else:
            print(f"Warning: Image {img_path} not found.")

pdf = PDF()

# --- Page 1: Executive Summary ---
pdf.add_page()
pdf.set_font('Arial', 'B', 20)
pdf.cell(0, 15, "Executive Summary", 0, 1, 'L')
pdf.ln(5)

executive_text = """
This report analyzes over 500 algorithmic trades to determine the impact of market sentiment (Fear & Greed Index) on profitability and risk management.

Key Findings:
1. Greed is Good (For This Strategy): The highest average PnL ($67.89 per trade) occurs during "Extreme Greed" markets. The strategy naturally scales up position sizes in bullish conditions.

2. Hidden Risk: While profitable, "Extreme Greed" comes with the highest volatility (Fat Tail Risk). The strategy takes its biggest losses here, despite the high average win.

3. Optimization Opportunity: The "Extreme Fear" zone shows the lowest Win Rate (37%). We recommend reducing position sizing by 20% when the Fear & Greed Index drops below 25.
"""
pdf.set_font('Arial', '', 12)
pdf.multi_cell(0, 7, executive_text)

# --- Page 2: Detailed Methodology ---
pdf.add_page()
pdf.chapter_title("1. Methodology & Data Sources")
methodology_text = """
- Data Integration: Historical trade logs were merged with daily Fear & Greed Index data using forward-fill alignment.
- Metrics: Calculated Win Rate %, Sharpe Ratio proxies (Avg PnL / StdDev), and sizing correlations.
- Constraints: 'Leverage' column was missing, so 'Size USD' acts as the primary proxy for conviction.
"""
pdf.chapter_body(methodology_text)

pdf.chapter_title("2. Strategy Recommendations")
recs_text = """
- Leverage the 'Safety of Fear': During Fear markets, win rates stabilize (42%). This is a solid environment for consistent, lower-risk compounding.
- Cut Cut Fat Tails: Implement a trailing stop-loss specifically during 'Extreme Greed' to capture upside momentum while mitigating the large drawdown risk identified in the Violin Plots.
"""
pdf.chapter_body(recs_text)

# --- Visual Gallery ---
output_dir = "ds_anjum/outputs"

# Group 1: Core Performance
pdf.add_chart(
    os.path.join(output_dir, "cumulative_pnl.png"), 
    "Cumulative Performance", 
    "The equity curve showing total portfolio growth over the analyzed period."
)

pdf.add_chart(
    os.path.join(output_dir, "daily_performance.png"),
    "Daily Performance Analysis (New)",
    "Total PnL broken down by day of the week. Identifies which days offer the best market conditions for this strategy."
)

# Group 2: Risk & Volatility
pdf.add_chart(
    os.path.join(output_dir, "risk_volatility.png"),
    "Volatility Profile",
    "Standard Deviation of PnL by sentiment zone. Higher bars indicate less predictable outcomes."
)

pdf.add_chart(
    os.path.join(output_dir, "pnl_distribution_violin.png"),
    "Risk Distribution (Violin Plot)",
    "Visualizes the spread of returns. Note the 'fat tails' (wider distribution) in Greed zones compared to the tighter control in Fear."
)

pdf.add_chart(
    os.path.join(output_dir, "pnl_vs_size_scatter.png"),
    "Risk-Reward Scatter (New)",
    "Scatter plot of Position Size vs. PnL. (Image generation pending)"
) if os.path.exists(os.path.join(output_dir, "pnl_vs_size_scatter.png")) else None

# Group 3: Behavior & Win Rate
pdf.add_chart(
    os.path.join(output_dir, "position_sizing.png"),
    "Behavioral Analysis: Sizing",
    "Average position size (USD) across different sentiment zones. Confirming if the strategy 'doubles down' in greed."
)

pdf.add_chart(
    os.path.join(output_dir, "win_rate_by_sentiment.png"),
    "Win Rate Efficiency (New)",
    "Win Rate percentage by sentiment. A drop in this metric during 'Extreme Fear' validates the recommendation to reduce risk there."
) if os.path.exists(os.path.join(output_dir, "win_rate_by_sentiment.png")) else None

# Output
pdf.output("ds_anjum/ds_report.pdf")
print("New PDF Report generated successfully.")
