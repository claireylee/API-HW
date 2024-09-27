import requests
import pandas as pd
import json
import matplotlib.pyplot as plt

apikey = 'your key'

def fetch_stock_data(stock_symbol):
    # Base URL for stock data
    url = "https://yfapi.net/v6/finance/quote"
    querystring = {"symbols": stock_symbol, "region": "US", "lang": "en"}

    headers = {
        'x-api-key': apikey
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        stock_json = response.json()
        results = stock_json['quoteResponse']['result']

        if len(results) > 0:
            stock_info = results[0]
            return {
                "Ticker": stock_info.get("symbol"),
                "Full Name": stock_info.get("longName"),
                "Current Market Price": stock_info.get("regularMarketPrice"),
                "Target Mean Price": stock_info.get("targetMeanPrice"),
                "52 Week High": stock_info.get("fiftyTwoWeekHigh"),
                "52 Week Low": stock_info.get("fiftyTwoWeekLow"),
            }
        else:
            print("No data found for the specified ticker symbol.")
            return None
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

def fetch_historical_data(stock_symbol):
    # Base URL for historical data
    url = f"https://yfapi.net/v6/finance/history"
    querystring = {
        "symbol": stock_symbol,
        "period1": int((pd.Timestamp.now() - pd.Timedelta(days=5)).timestamp()),
        "period2": int(pd.Timestamp.now().timestamp()),
        "interval": "1d",
        "events": "history"
    }

    headers = {
        'x-api-key': apikey
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code == 200:
        historical_json = response.json()
        return historical_json['prices']
    else:
        print(f"Error fetching historical data: {response.status_code}")
        return None

def fetch_trending_stocks():
    # Base URL for trending stocks
    url = "https://yfapi.net/v1/finance/trending/US"

    headers = {
        'x-api-key': apikey
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        trending_json = response.json()
        return [item['symbol'] for item in trending_json['finance']['result'][0]['quotes'][:5]]
    else:
        print(f"Error fetching trending stocks: {response.status_code}")
        return []

# Get stock input from user
stock_symbol = input("Enter the stock ticker symbol (e.g., AAPL): ").strip().upper()
stock_data = fetch_stock_data(stock_symbol)

if stock_data:
    # Display stock data to use
    print("\nStock Information:")
    for key, value in stock_data.items():
        print(f"{key}: {value}")

    # Fetch trending stocks
    trending_stocks = fetch_trending_stocks()
    if trending_stocks:
        print("\nCurrent Trending Stocks (Top 5):")
        print(", ".join(trending_stocks))

    # Save data to DataFrame and CSV
    df = pd.DataFrame([stock_data])
    df.to_csv(f"~/Documents/{stock_symbol}_data.csv", index=False)
    print(f"\nData has been saved to {stock_symbol}_data.csv")

    # Fetch and visualize historical stock data
    historical_data = fetch_historical_data(stock_symbol)
    if historical_data:
        # Extract the highest prices
        highest_prices = [day['high'] for day in historical_data if 'high' in day]
        dates = [pd.to_datetime(day['date'], unit='s').date() for day in historical_data if 'date' in day]

        # Plotting
        plt.figure(figsize=(10, 5))
        plt.plot(dates, highest_prices, marker='o')
        plt.title(f'Highest Prices of {stock_symbol} Over the Last 5 Days')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.xticks(rotation=45)
        plt.grid()
        plt.tight_layout()
        plt.show()

    # Save the JSON response to a file
    with open("stock_data.json", "w") as json_file:
        json.dump(stock_data, json_file, indent=4)
else:
    print("No valid stock data found or an error occurred.")

