# Data Science Report: Trader Behavior & Market Sentiment

## **Objective**
The objective of this analysis is to explore the relationship between trader performance (PnL, Win Rate) and market sentiment (Fear vs Greed Index). This report summarizes the findings derived from the historical trading data and sentiment index.

## **Methodology**
1. **Data Preprocessing**: 
   - Historical trader data was cleaned and aligned with daily Fear & Greed Index values.
   - Timestamps were converted to daily resolution for merging.
2. **Analysis Metrics**:
   - Pearson Correlation between Sentiment Value and Trading Performance (PnL, Size).
   - Average PnL across different Sentiment Categories (Fear, Greed, Neutral, etc.).
   - Win Rate (Frequency of Positive PnL) across Sentiment Categories.

## **Key Insights**

### **1. Correlation Analysis**
The linear correlation between the Fear/Greed Index and trading metrics is weak.
- **Correlation (Sentiment vs PnL)**: ~0.008 (Very weak positive)
- **Correlation (Sentiment vs Size)**: ~-0.03 (Very weak negative)

This suggests that market sentiment alone is not a strong linear predictor of individual trade outcomes for this trader, implying other factors (technical, fundamental) play a larger role.

### **2. Performance by Sentiment Category**
Despite low linear correlation, distinct patterns emerge when grouping by sentiment category:

| Sentiment Category | Average PnL (USD) | Win Rate (%) |
|-------------------|-------------------|--------------|
| **Extreme Greed** | **$67.89**        | **46.5%**    |
| **Fear**          | $54.29            | 42.1%        |
| **Greed**         | $42.74            | 38.5%        |
| **Extreme Fear**  | $34.54            | 37.1%        |
| **Neutral**       | $34.31            | 39.7%        |

### **3. Strategic Observations**
- **Optimal Conditions**: The trader performs significantly better during **Extreme Greed** periods ($67.89/trade avg). This suggests momentum-based strategies might be working well when the market is euphoric.
- **Resilience in Fear**: Performance is also strong during **Fear** ($54.29/trade), potentially indicating effective contrarian plays or shorting strategies during market drops.
- **Weakness in Uncertainty**: Performance drops in "Neutral" and "Extreme Fear" zones, suggesting the trader struggles when market direction is unclear or panic is maximizing volatility unpredictably.

## **Conclusion & Recommendations**
- **Capitalize on Extremes**: Increase position sizing or frequency during "Extreme Greed" phases as the edge is highest.
- **Review "Extreme Fear" Strategy**: With the lowest win rate (37%), the strategy during market crashes needs refinement—perhaps reducing leverage or waiting for stabilization.
- **Automated Alerts**: Implement alerts when Sentiment > 75 (Extreme Greed) to signal high-conviction trading windows.

## **Visualizations**
Please refer to the `outputs/` directory for the following charts:
- `pnl_vs_feargreed.png`: Scatter plot of individual trades.
- `avg_pnl_by_sentiment.png`: Bar chart of average profitability.
- `win_rate_by_sentiment.png`: Win rate analysis.
