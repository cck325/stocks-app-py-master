from dotenv import load_dotenv
import json
import os
import requests
import csv
import datetime
from IPython import embed
import itertools

#load_dotenv()
api_key = os.environ.get("ALPHAVANTAGE_API_KEY") or "OOPS. Please set an environment variable named 'ALPHAVANTAGE_API_KEY'."
#api_key = "ZIGLKKWB6EL2U7HO"


################# Write to CSV##################

def parse_response(response_text):
    # response_text can be either a raw JSON string or an already-converted dictionary
    if isinstance(response_text, str): # if not yet converted, then:
        response_text = json.loads(response_text) # convert string to dictionary

    results = []
    time_series_daily = response_text["Time Series (Daily)"] #> a nested dictionary
    for trading_date in time_series_daily: # FYI: can loop through a dictionary's top-level keys/attributes
        prices = time_series_daily[trading_date] #> {'1. open': '101.0924', '2. high': '101.9500', '3. low': '100.5400', '4. close': '101.6300', '5. volume': '22165128'}
        result = {
            "date": trading_date,
            "open": prices["1. open"],
            "high": prices["2. high"],
            "low": prices["3. low"],
            "close": prices["4. close"],
            "volume": prices["5. volume"]
        }
        results.append(result)
    return results

def write_prices_to_file(prices=[], filename=""):
    csv_filepath = os.path.join(os.path.dirname(__file__), "..", filename)
    with open(filename, "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["timestamp", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        for d in prices:
            row = {
                "timestamp": d["date"], # change attribute name to match project requirements
                "open": d["open"],
                "high": d["high"],
                "low": d["low"],
                "close": d["close"],
                "volume": d["volume"]
            }
            writer.writerow(row)

################################################################################################

def all_high_price(time_series):
    global high_prices
    high_prices = []
    for t in time_series:
        dh_prices = time_series[t]
        high_price = float(dh_prices["2. high"])
        high_prices.append(high_price)

def all_low_price(time_series):
    global low_prices
    low_prices = []
    for l in time_series:
        dl_prices = time_series[l]
        low_price = float(dl_prices["3. low"])
        low_prices.append(low_price)

def average_high(high_prices):
    global avg_high
    total_high = sum(high_prices)
    avg_high = total_high/len(high_prices)
    avg_high_usd = "${0:,.2f}".format(avg_high)
    print(f"THE AVERAGE HIGH PRICE FOR {s} IS: " + avg_high_usd)

def average_low(low_prices):
    global avg_low
    total_low = sum(low_prices)
    avg_low = total_low/len(low_prices)
    avg_low_usd = "${0:,.2f}".format(avg_low)
    print(f"THE AVERAGE LOW PRICE FOR {s} IS: " + avg_low_usd)

def latest_dd(time_series):
    global closed_price
    latest_daily_data = time_series[dates[0]] #latest daily data
    closed_price = latest_daily_data["4. close"]
    closed_price = float(closed_price)
    closed_price_usd = "${0:,.2f}".format(closed_price)
    print(f"LATEST DAILY CLOSING PRICE FOR {s} IS: {closed_price_usd}")

def recom(closed_price):
    low_buy_key = 1.03*avg_low
    high_buy_key = 0.97*avg_high
    if closed_price >= avg_high:
        print("--------------------------------------")
        print("DON'T BUY BECAUSE IT IS HIGHER THAN PAST 100 DAYS AVG HIGH")
    elif closed_price <= avg_low:
        print("--------------------------------------")
        print("DON'T BUY BECAUSE IT IS LOWER THAN PAST 100 DAYS AVG LOW")
    elif closed_price >= low_buy_key and closed_price <= high_buy_key:
        print("--------------------------------------")
        print("BUY BECAUSE THE PRICE IS BETWEEN PAST 100 DAYS AVG LOW AND HIGH")
    else:
        print("--------------------------------------")
        print("DON'T BUY BECAUSE IT IS NOT A GOOD TIME.")





symbols = []
if __name__ == '__main__':

    while True:
        symbol = input("Please Enter a Stock Symbol (e.g. AAPL): ")
        if symbol == "DONE":
            break
        elif symbol == "CLEANER":
            d_symbol = input("Please Enter a Stock Symbol to be delete from file (e.g. AAPL): ")
            os.remove("db/" + d_symbol + ".csv")
            print(f"The Data File {d_symbol}.csv Has Been Deleted.")
            break
        else:
            try:
                float(symbol)
                print("CHECK YOUR SYMBOL. No NUMARTIC PLEASE TRY ANOTHER")
            except ValueError as e:
                request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
                response = requests.get(request_url)
                if "Error Message" in response.text:
                    print("CHECK YOUR SYMBOL")
                else:
                    symbols.append(symbol)

now = datetime.datetime.now()

if __name__ == '__main__':
    print("--------------------------------------")
    print("PROGRAM RUN ON " + now.strftime("%Y-%m-%d %H:%M:%S"))
    print("--------------------------------------")
    print("")

if __name__ == '__main__':
    for s in symbols:
        request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={s}&apikey={api_key}"
        response = requests.get(request_url)
        stock = json.loads(response.text)
        meta_data = stock["Meta Data"]
        last_refresh = meta_data["3. Last Refreshed"]
        time_series = stock["Time Series (Daily)"]
        dates = list(time_series)
        print(f"----------STOCK NAME {s}-------------" )
        print("")
        all_high_price(time_series)
        all_low_price(time_series)
        average_high(high_prices)
        average_low(low_prices)
        latest_dd(time_series)
        recom(closed_price)
        daily_price = parse_response(stock)
        write_prices_to_file(prices=daily_price,filename="db/" + s + ".csv")
        print("--------------------------------------")
        print("LAST REFRESHED At: " + last_refresh)
        print("--------------------------------------")
