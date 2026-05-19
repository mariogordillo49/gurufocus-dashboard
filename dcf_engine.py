import json

ticker = "AAPL"

# Supuestos DCF
growth_rate = 0.08
wacc = 0.09
terminal_growth = 0.025
years = 5

with open(f"data/{ticker}_financials.json", "r") as file:
    data = json.load(file)

annuals = data["financials"]["annuals"]

cashflow = annuals["cashflow_statement"]
balance = annuals["balance_sheet"]
income = annuals["income_statement"]

# Obtener listas
fcf_list = cashflow.get("Free Cash Flow")
cash_list = balance.get("Cash and Cash Equivalents")
lt_debt_list = balance.get("Long-Term Debt")
st_debt_list = balance.get("Short-Term Debt")
shares_list = income.get("Shares Outstanding (Diluted Average)")

# Último valor disponible
fcf = float(fcf_list[-1])
cash = float(cash_list[-1])

lt_debt = float(lt_debt_list[-1]) if lt_debt_list else 0
st_debt = float(st_debt_list[-1]) if st_debt_list else 0

total_debt = lt_debt + st_debt

shares = float(shares_list[-1])

# Proyección DCF
projected_fcfs = []

for year in range(1, years + 1):
    projected_fcf = fcf * ((1 + growth_rate) ** year)

    discounted_fcf = projected_fcf / ((1 + wacc) ** year)

    projected_fcfs.append(discounted_fcf)

# Valor terminal
terminal_value = (
    projected_fcfs[-1]
    * (1 + terminal_growth)
    / (wacc - terminal_growth)
)

discounted_terminal_value = (
    terminal_value
    / ((1 + wacc) ** years)
)

# Enterprise Value
enterprise_value = (
    sum(projected_fcfs)
    + discounted_terminal_value
)

# Equity Value
equity_value = enterprise_value + cash - total_debt

# Valor intrínseco
intrinsic_value_per_share = equity_value / shares

# Resultados
print("\nDCF para:", ticker)

print("\nFCF Base:", round(fcf, 2))
print("Cash:", round(cash, 2))
print("Long-Term Debt:", round(lt_debt, 2))
print("Short-Term Debt:", round(st_debt, 2))
print("Total Debt:", round(total_debt, 2))

print("\nEnterprise Value:", round(enterprise_value, 2))
print("Equity Value:", round(equity_value, 2))

print("\nValor Intrínseco por Acción:",
      round(intrinsic_value_per_share, 2))