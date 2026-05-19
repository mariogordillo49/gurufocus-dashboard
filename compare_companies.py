import json
import pandas as pd

tickers = ["AAPL", "NVDA", "AMZN", "GOOGL", "COST", "META", "MSFT", "TSLA"]

results = []

for ticker in tickers:

    with open(f"data/{ticker}_financials.json", "r") as file:
        data = json.load(file)

    annuals = data["financials"]["annuals"]

    income_statement = annuals["income_statement"]
    balance_sheet = annuals["balance_sheet"]
    cashflow_statement = annuals["cashflow_statement"]
    ratios = annuals["common_size_ratios"]

    company_data = {
        "Ticker": ticker,

        "Revenue": income_statement.get("Revenue"),
        "Operating Income": income_statement.get("Operating Income"),
        "Net Income": income_statement.get("Net Income"),
        "EBITDA": income_statement.get("EBITDA"),

        "Free Cash Flow": cashflow_statement.get("Free Cash Flow"),
        "CapEx": cashflow_statement.get("Capital Expenditure"),

        "Cash": balance_sheet.get("Cash and Cash Equivalents"),
        "Total Assets": balance_sheet.get("Total Assets"),

        "ROE %": ratios.get("ROE %"),
        "ROIC %": ratios.get("ROIC %"),

        "Gross Margin %": ratios.get("Gross Margin %"),
        "Operating Margin %": ratios.get("Operating Margin %"),
        "Net Margin %": ratios.get("Net Margin %"),

        "Debt-to-Equity": ratios.get("Debt-to-Equity")
    }

    results.append(company_data)

df = pd.DataFrame(results)

df.to_csv("data/company_comparison.csv", index=False)

print(df)

print("\nArchivo CSV creado correctamente.")
