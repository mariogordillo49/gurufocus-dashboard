import json

ticker = "AAPL"

with open(f"data/{ticker}_financials.json", "r") as file:
    data = json.load(file)

annuals = data["financials"]["annuals"]

income_statement = annuals["income_statement"]
balance_sheet = annuals["balance_sheet"]
cashflow_statement = annuals["cashflow_statement"]
ratios = annuals["common_size_ratios"]

resumen = {
    "ticker": ticker,

    # Income Statement
    "revenue": income_statement.get("Revenue"),
    "operating_income": income_statement.get("Operating Income"),
    "net_income": income_statement.get("Net Income"),
    "ebitda": income_statement.get("EBITDA"),

    # Cash Flow
    "free_cash_flow": cashflow_statement.get("Free Cash Flow"),
    "capital_expenditure": cashflow_statement.get("Capital Expenditure"),
    "operating_cash_flow": cashflow_statement.get("Cash Flow from Operations"),

    # Balance Sheet
    "cash": balance_sheet.get("Cash and Cash Equivalents"),
    "total_assets": balance_sheet.get("Total Assets"),

    # Margins & Returns
    "gross_margin_pct": ratios.get("Gross Margin %"),
    "operating_margin_pct": ratios.get("Operating Margin %"),
    "net_margin_pct": ratios.get("Net Margin %"),
    "roe_pct": ratios.get("ROE %"),
    "roic_pct": ratios.get("ROIC %"),

    # Debt
    "debt_to_equity": ratios.get("Debt-to-Equity"),
    "debt_to_asset": ratios.get("Debt-to-Asset")
}

with open(f"data/{ticker}_full_resumen.json", "w") as file:
    json.dump(resumen, file, indent=4)

print("Resumen financiero completo creado correctamente.")
