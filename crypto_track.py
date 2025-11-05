import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import time

# File to store data
DATA_FILE = os.path.join("data", "crypto_data.csv")

def fetch_crypto_data():
    url = "https://coinmarketcap.com/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    data = []
    rows = soup.find_all("tr")[1:11]  # top 10 coins
    for row in rows:
        columns = row.find_all("td")
        if len(columns) > 4:
            name = columns[2].find("p", class_="coin-item-symbol").text.strip()
            price = columns[3].text.strip()
            change = columns[4].text.strip()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data.append([name, price, change, timestamp])
    return data

def save_to_csv(data):
    df = pd.DataFrame(data, columns=["Name", "Price", "Change", "Timestamp"])
    os.makedirs("data", exist_ok=True)
    if os.path.exists(DATA_FILE):
        df.to_csv(DATA_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(DATA_FILE, index=False)
    print(f"[{datetime.now()}] Saved {len(data)} entries")

if __name__ == "__main__":
    while True:
        crypto_data = fetch_crypto_data()
        save_to_csv(crypto_data)
        time.sleep(60)  