from ta.momentum import RSIIndicator
import config
import robin_stocks as rh
r = rh.robinhood
import datetime as dt
import time
import yfinance as yf
from configparser import ConfigParser
import pandas as pd


# Other important variables
configur = ConfigParser()
configur.read('config.ini')
TESTING = False



import requests
from lxml import etree
from bs4 import BeautifulSoup

def get_stock_price(stock_name):
    url = f"https://finance.yahoo.com/quote/{stock_name}"
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")
    dom = etree.HTML(str(soup))
    price_elem = dom.xpath('//*[@id="quote-header-info"]/div[3]/div[1]/div/fin-streamer[1]/span')
    if price_elem and price_elem[0] is not None:
        return float(price_elem.text)
    else:
        # print(f"Error: could not find stock price for {stock_name}")
        return None

"""
Makes it easier to edit the config file
"""
def editConfig(section, id, value):
    # update the value of the 'network_id' key in the 'registration' section
    
    configur.set(section, id, value)

    # write the changes back to the config.ini file
    with open('../config.ini', 'w') as configfile:
        configur.write(configfile)





#account functions
def login(days):
    time_logged = 60*60*24*days #converts days to seconds
    print(rh.robinhood.authentication.login(username=config.USERNAME,password=config.PASSWORD,expiresIn=time_logged,scope="internal",by_sms=True, store_session=True))

def logout():
    rh.robinhood.authentication.logout()



#market related functions
def openMarket():
    #if we are testing just bypass this
    if TESTING:
        return True

    market = False
    time_now = dt.datetime.now().time()

    marketOpen = dt.time(6,30,0)
    marketClose = dt.time(12,59,0)

    if (time_now > marketOpen) and (time_now < marketClose):
        market = True

    return market

def get_rsi(ticker):
    # Download historical data from Yahoo Finance
    stock = yf.Ticker(ticker)
    hist = stock.history(period="max")

    # Calculate RSI
    delta = hist["Close"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # Return the latest RSI value
    return rsi.iloc[-1]


def get_current_rsi(ticker, timeFrame):
    # Create a yfinance Ticker object for the stock
    stock = yf.Ticker(ticker)
    
    # Get the stock's historical price data
    historical_data = stock.history(period=timeFrame)
    
    # Create an RSI indicator using the historical data
    rsi_indicator = RSIIndicator(historical_data["Close"])
    
    # Get the current RSI value
    current_rsi = rsi_indicator.rsi()[-1]
    
    return current_rsi