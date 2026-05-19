import json
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="GuruFocus Financial Dashboard", layout="wide")

tickers = ["AAPL", "NVDA", "AMZN", "GOOGL", "META", "MSFT", "TSLA"]

growth_rate = 0.08
wacc = 0.09
terminal_growth = 0.025
years = 5


def last_value(x):
    if x is None or len(x) == 0:
        return None
    return x[-1]


def safe_float(x):
    try:
        if x is None or x == "N/A":
            return None
        return float(x)
    except:
        return None


def calculate_dcf(fcf, cash, short_debt, long_debt, shares):
    if fcf is None or cash is None or shares is None:
        return None

    total_debt = (short_debt or 0) + (long_debt or 0)
    discounted_fcfs = []

    for year in range(1, years + 1):
        projected_fcf = fcf * ((1 + growth_rate) ** year)
        discounted_fcf = projected_fcf / ((1 + wacc) ** year)
        discounted_fcfs.append(discounted_fcf)

    terminal_value = discounted_fcfs[-1] * (1 + terminal_growth) / (wacc - terminal_growth)
    discounted_terminal = terminal_value / ((1 + wacc) ** years)

    enterprise_value = sum(discounted_fcfs) + discounted_terminal
    equity_value = enterprise_value + cash - total_debt

    return equity_value / shares


def get_series(section, key):
    values = section.get(key)
    if values is None:
        return []
    return [safe_float(v) for v in values]


results = []
historical_data = {}

for ticker in tickers:
    try:
        with open(f"data/{ticker}_financials.json", "r") as file:
            data = json.load(file)

        annuals = data["financials"]["annuals"]

        income = annuals["income_statement"]
        balance = annuals["balance_sheet"]
        cashflow = annuals["cashflow_statement"]
        ratios = annuals["common_size_ratios"]
        valuation = annuals["valuation_and_quality"]

        revenue = safe_float(last_value(income.get("Revenue")))
        net_income = safe_float(last_value(income.get("Net Income")))
        ebitda = safe_float(last_value(income.get("EBITDA")))
        fcf = safe_float(last_value(cashflow.get("Free Cash Flow")))

        cash = safe_float(last_value(balance.get("Cash and Cash Equivalents")))
        short_debt = safe_float(last_value(balance.get("Short-Term Debt")))
        long_debt = safe_float(last_value(balance.get("Long-Term Debt")))
        shares = safe_float(last_value(income.get("Shares Outstanding (Diluted Average)")))

        roe = safe_float(last_value(ratios.get("ROE %")))
        roic = safe_float(last_value(ratios.get("ROIC %")))
        gross_margin = safe_float(last_value(ratios.get("Gross Margin %")))
        operating_margin = safe_float(last_value(ratios.get("Operating Margin %")))
        net_margin = safe_float(last_value(ratios.get("Net Margin %")))

        stock_price = safe_float(last_value(valuation.get("Month End Stock Price")))
        pe = safe_float(last_value(valuation.get("PE Ratio")))

        intrinsic_value = calculate_dcf(fcf, cash, short_debt, long_debt, shares)

        upside = None
        if stock_price and intrinsic_value:
            upside = ((intrinsic_value / stock_price) - 1) * 100

        fcf_yield = None
        if fcf and stock_price and shares:
            market_cap = stock_price * shares
            fcf_yield = (fcf / market_cap) * 100

        results.append({
            "Ticker": ticker,
            "Revenue": revenue,
            "Net Income": net_income,
            "EBITDA": ebitda,
            "FCF": fcf,
            "ROE %": roe,
            "ROIC %": roic,
            "Gross Margin %": gross_margin,
            "Operating Margin %": operating_margin,
            "Net Margin %": net_margin,
            "PE": pe,
            "FCF Yield %": fcf_yield,
            "Stock Price": stock_price,
            "Intrinsic Value": intrinsic_value,
            "Upside %": upside
        })

        historical_data[ticker] = {
            "Revenue": get_series(income, "Revenue"),
            "FCF": get_series(cashflow, "Free Cash Flow"),
            "ROIC %": get_series(ratios, "ROIC %"),
            "Operating Margin %": get_series(ratios, "Operating Margin %"),
            "Net Margin %": get_series(ratios, "Net Margin %")
        }

    except Exception as e:
        st.warning(f"Error cargando {ticker}: {e}")


df = pd.DataFrame(results)

df["Score"] = 0

df.loc[df["ROIC %"] > 25, "Score"] += 3
df.loc[df["ROIC %"] > 15, "Score"] += 2

df.loc[df["Operating Margin %"] > 30, "Score"] += 3
df.loc[df["Operating Margin %"] > 20, "Score"] += 2

df.loc[df["FCF Yield %"] > 5, "Score"] += 3
df.loc[df["FCF Yield %"] > 3, "Score"] += 2

df.loc[df["ROE %"] > 30, "Score"] += 3
df.loc[df["ROE %"] > 15, "Score"] += 2

df.loc[df["Upside %"] > 30, "Score"] += 3
df.loc[df["Upside %"] > 10, "Score"] += 2


def classify(score):
    if score >= 12:
        return "Strong Buy"
    elif score >= 9:
        return "Buy"
    elif score >= 6:
        return "Hold"
    else:
        return "Avoid"


df["Rating"] = df["Score"].apply(classify)
df = df.sort_values(by="Score", ascending=False)

st.title("GuruFocus Financial Dashboard")

st.subheader("Ranking Hedge Fund")

ranking_cols = [
    "Ticker",
    "Score",
    "Rating",
    "ROIC %",
    "FCF Yield %",
    "Operating Margin %",
    "Upside %"
]

st.dataframe(df[ranking_cols], width="stretch")

st.subheader("Comparativo General")
st.dataframe(df, width="stretch")

selected = st.selectbox("Selecciona una empresa", df["Ticker"])
company = df[df["Ticker"] == selected].iloc[0]

st.subheader(f"Resumen de {selected}")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Revenue", f"{company['Revenue']:,.0f}")
col2.metric("FCF", f"{company['FCF']:,.0f}")
col3.metric("ROIC %", f"{company['ROIC %']:.2f}")
col4.metric("Operating Margin %", f"{company['Operating Margin %']:.2f}")

col5, col6, col7, col8 = st.columns(4)

col5.metric("PE", f"{company['PE']:.2f}" if pd.notna(company["PE"]) else "N/A")
col6.metric("FCF Yield %", f"{company['FCF Yield %']:.2f}" if pd.notna(company["FCF Yield %"]) else "N/A")
col7.metric("Intrinsic Value", f"{company['Intrinsic Value']:.2f}" if pd.notna(company["Intrinsic Value"]) else "N/A")
col8.metric("Upside %", f"{company['Upside %']:.2f}" if pd.notna(company["Upside %"]) else "N/A")

col9, col10 = st.columns(2)

col9.metric("Score", company["Score"])
col10.metric("Rating", company["Rating"])

st.subheader("Gráficas Profesionales")

fig1 = px.bar(
    df,
    x="Ticker",
    y="ROIC %",
    color="Rating",
    title="ROIC % Comparativo"
)
st.plotly_chart(fig1, width="stretch")

fig2 = px.bar(
    df,
    x="Ticker",
    y="Operating Margin %",
    color="Rating",
    title="Operating Margin % Comparativo"
)
st.plotly_chart(fig2, width="stretch")

fig3 = px.bar(
    df,
    x="Ticker",
    y="FCF",
    color="Rating",
    title="Free Cash Flow Comparativo"
)
st.plotly_chart(fig3, width="stretch")

fig4 = px.bar(
    df,
    x="Ticker",
    y="Upside %",
    color="Rating",
    title="Upside / Downside vs DCF"
)
st.plotly_chart(fig4, width="stretch")

fig5 = px.scatter(
    df,
    x="ROIC %",
    y="FCF Yield %",
    size="Revenue",
    color="Rating",
    hover_name="Ticker",
    title="Quality vs Cash Yield"
)
st.plotly_chart(fig5, width="stretch")

st.subheader(f"Histórico de {selected}")

selected_history = historical_data[selected]

hist_df = pd.DataFrame(selected_history)
hist_df["Year"] = range(1, len(hist_df) + 1)

fig6 = px.line(
    hist_df,
    x="Year",
    y="Revenue",
    markers=True,
    title=f"{selected} Revenue Histórico"
)
st.plotly_chart(fig6, width="stretch")

fig7 = px.line(
    hist_df,
    x="Year",
    y="FCF",
    markers=True,
    title=f"{selected} Free Cash Flow Histórico"
)
st.plotly_chart(fig7, width="stretch")

fig8 = px.line(
    hist_df,
    x="Year",
    y=["ROIC %", "Operating Margin %", "Net Margin %"],
    markers=True,
    title=f"{selected} Margins & ROIC Histórico"
)
st.plotly_chart(fig8, width="stretch")

st.subheader("Heatmap Cuantitativo")

heatmap_cols = [
    "Ticker",
    "ROIC %",
    "Operating Margin %",
    "FCF Yield %",
    "Upside %",
    "Score"
]

st.dataframe(
    df[heatmap_cols].style.background_gradient(cmap="RdYlGn"),
    width="stretch"
)

df.to_excel("hedgefund_dashboard_enhanced.xlsx", index=False)

st.success("Dashboard actualizado correctamente.")
