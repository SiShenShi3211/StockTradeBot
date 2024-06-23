"""
Steps to this process

1. Figure out how to access RH API

2. Make functions that gather information from stock, also that see how much we have in a stock

3. Make strategy to decide whether to buy/sell SPY stock

4. Make functions to buy/sell stock
"""
import config
import robin_stocks as rh
from bot import tradingBot
from utils import *
r = rh.robinhood
import datetime as dt
import time
import yfinance as yf

"""
TODO: Compare simulation money to that if percentage was invested normally
"""

print("starting...")

"""
Determinte in BEAR/BULL

Determine
    Take 2 year past data
        Average change +: Bull
                       -: bear

Bear:
    Normal function

Bull:
    Seperate function
        Profit margin should increase


"""

#Running commands here
if __name__ == "__main__":
    tr = tradingBot(percent=1)
    tr.simulate("SPY", 1)
    # tr.start()
    



