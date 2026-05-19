import json
import pandas as pd

tickers = ["AAPL", "NVDA", "AMZN", "GOOGL", "META", "MSFT"]

results = []

for ticker in tickers:

    with open(f"data/{ticker}_financials.json", "r") as file:
        data = json.load(file)

    annuals = data["financials"]["annuals"]

    income = annuals["income_statement"]
    cashflow = annuals["cashflow_statement"]
    ratios = annuals["common_size_ratios"]
    valuation = annuals["valuation_and_quality"]

    revenue = income.get("Revenue", [None])[-1]
    net_income = income.get("Net Income", [None])[-1]
    ebitda = income.get("EBITDA", [None])[-1]

    fcf = cashflow.get("Free Cash Flow", [None])[-1]

    roe = ratios.get("ROE %", [None])[-1]
    roic = ratios.get("ROIC %", [None])[-1]
    operating_margin = ratios.get("Operating Margin %", [None])[-1]

    results.append({
        "Ticker": ticker,
        "Revenue": revenue,
        "Net Income": net_income,
        "EBITDA": ebitda,
        "FCF": fcf,
        "ROE": roe,
        "ROIC": roic,
        "Operating Margin": operating_margin
    })

df = pd.DataFrame(results)

print(df)

df.to_excel("hedgefund_dashboard.xlsx", index=False)

print("\nExcel creado correctamente.")
