import requests
import json
from config import GURUFOCUS_API_KEY

ticker = "AAPL"

url = f"https://api.gurufocus.com/public/user/{GURUFOCUS_API_KEY}/stock/{ticker}/financials"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()

    with open(f"data/{ticker}_financials.json", "w") as file:
        json.dump(data, file, indent=4)

    print(f"Datos de {ticker} guardados correctamente.")
else:
    print("Error:", response.status_code)
    print(response.text)
