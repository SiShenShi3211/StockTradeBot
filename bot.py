import config
import robin_stocks as rh
from utils import *
r = rh.robinhood
import datetime as dt
import time
import yfinance as yf
from configparser import ConfigParser
import pandas as pd
from ta.momentum import RSIIndicator

# Other important variables
configur = ConfigParser()
configur.read('config.ini')
waitTime = 30
# computer_id = configur.get("registration", "machine_id")
# editConfig("registration", "network_id", new_network_id)

"""
60: 33.56
65: 36.15
70: 39.69
"""

# Create global variables to customize easily
global money 
global startmoney
global ownedShares
global priceBought
global rsiMaxDist
global emaBuffer
global exchangeAmount
global stopLossPercent
global profitMarginMin
global profitTax

money = 10000 # Starting cash


# Do not touch these varibles
exchangeAmount = 0 #Tracks amount of times we exchange something (DNT)
startmoney = money # Tracks our starting money (DNT)
ownedShares = 0 # Tracks the shares we own (DNT)
priceBought = 0 #Tracks the price we bought at last stock (DNT)

# Not in use
rsiMaxDist = 100 #Buffer for maximum RSI difference, not in use (DNT)

# Settings
emaBuffer = 100000 # Max distance buffer from moving average, Higher = less effect
stopLossPercent = 0.90 #Cut off our losses at what percent (.98 = 2% max loss)

profitMarginMin = 1.02 # Minimun profit per sell without RSI
lowerProfitMarginMin = 1.015 # min profit with high RSI

sellRSI = 65 # Can be greater than this and valid
buyRSI = 35 #can be less than this and valid
buyOnce = True #Can we buy only one time before selling?
profitTax = 0.15 #What percent of our profit is taxed?

"""
Bull strats

Calculating historical bear/bull percentage

1. 
Go through historical data, calculate relative high and low
High - low  bear percentage 
low - high bull percentage
Take averages
Calcuate bear/bull and perdicted progression

Timespan: month

example:
bear: 20%
bull: 20%

if we are in bull, and current is 10%, sell at 18% (some buffer)

if we are bear, Current strategy until we hit the percentage

-----------

2. 
Take one year price change (big)
Take one month price change (small)

Big = Positive, small = positive (Bull)
Big = Negative, small = negatice (Bear)

Big = positive, Small = negative (Enter bear)
Big = negative, Small = positive (Enter bull)


Interval: month


"""


STOCKS = config.STOCKS

class tradingBot:
    def __init__(self, percent) -> None:
        self.money = int(configur.get("registration", "money"))
        self.alreadyBought = bool(configur.get("registration", "alreadyBought"))
        self.buyPercent = percent # Captial we risk
        self.ownedShares = int(configur.get("registration", "shares"))
        pass

        """Main logic for the bot"""
    
    def decide(self):
        print("deciding")
        # prices = rh.robinhood.stocks.get_latest_price(STOCKS)
        stockPrice = get_stock_price("SPY")

        if not stockPrice:
            stockPrice = rh.robinhood.stocks.get_latest_price(STOCKS)[0]

            
        print("Price: ", str(stockPrice)[:6])

        RSI= get_current_rsi("SPY", "3mo")
        if not RSI:
            RSI = get_rsi("SPY")
        print("RSI: ", str(RSI)[:9])
        print("------------------")

        


        captialMoney = self.money * self.buyPercent
        

        # Buy if rsi <= 35 and we have not already bought
        if RSI <= 35 and not self.alreadyBought:
            while captialMoney > stockPrice:
                self.money -= stockPrice
                captialMoney -= stockPrice
                self.ownedShares += 1
                self.alreadyBought = True
            editConfig("registration", "money", str(self.money))
            editConfig("registration", "stocks", str(self.ownedShares))
            editConfig("registration", "alreadyBought", "True")

        # Sell if rsi >= 60, reset self.alreadyBought
        if RSI >= 60:
            while self.ownedShares > 0:
                self.ownedShares -= 1
                self.money += stockPrice
                self.alreadyBought = False
            editConfig("registration", "money", str(self.money))
            editConfig("registration", "stocks", str(self.ownedShares))
            editConfig("registration", "alreadyBought", "")


        """Starts the bot up, bot should login then begin the buying / selling / waiting loop"""
    

    def simulate_determine_bear_or_bull(self, day, hist):
        # Take average averge derivative of last 300, 100, 50, and 20 days (Long term to short term trends)
        # Rise / run will be for the derivative
        #Rise = current Price - X days ago price
        # Run = day amount

        print(hist["Close"][100])
        time.sleep(1000)
        pass



    """
    Decides given parameters from simulate, returns (money, stockAmount)
    """
    def simulate_decide(self, stockPrice, RSI, money, ownedShares, priceBought=0, above_ema=False, exchangeAmount=0):

        global profitMarginMin
        global profitTax
        """
        percent change from bought / sold
        """
        # Stop loss
        global stopLossPercent
        percentDifference = stockPrice/priceBought # Current price to bought ratio


        """
        MACD (Blue) / Signal line (orange)

        MACD: Measurement of estimated stock price over period of time
        Signal: Measurement of estimated stock price over longer period of time

        MACD crosses Signal from above: TO SELL
        MACD crosses Signal from below: TO BUY

        MACD = 12 day EMA
        Signal = 26 day EMA


        (Test for with RSI and without RSI) track also without RSI entirely
        """


        captialMoney = money * self.buyPercent
        # print("Capital money: ", captialMoney, "      Stock price: ", stockPrice)
        
        

        # Buy if rsi <= 35 and we have not already bought
        if RSI <= buyRSI and above_ema and ((not self.alreadyBought) or not buyOnce):
            # print("AAAAAA\n")
            if captialMoney > stockPrice:
                exchangeAmount +=1
            while captialMoney > stockPrice:
                print("[!]  BUY ", RSI , " <= ", buyRSI)

                money -= stockPrice
                captialMoney -= stockPrice
                ownedShares += 1
                self.alreadyBought = True
                priceBought = stockPrice



        # Sell if hit stoploss, rsi >= sellRsi AND lower profit min, OR we hit the normal profit gain
        if (stopLossPercent >= percentDifference) or (RSI >= sellRSI and (stockPrice >= (priceBought * lowerProfitMarginMin))) or (stockPrice >= (priceBought * profitMarginMin)):
            # print("BBBBBBBB\n")
            # pass
            profitPerStock = (stockPrice - priceBought)
            totalProfit = 0

            # If shares and we need sell, increase exchange
            if ownedShares > 0:
                exchangeAmount +=1

            
            # Sell all of our stocks
            while ownedShares > 0:
                print("[!]  Sell ()")
                ownedShares -= 1
                money += stockPrice
                self.alreadyBought = False
                totalProfit += profitPerStock

            
                
            # Take tax into account
            if totalProfit > 0:
                deduce = totalProfit * profitTax
                money -= deduce

        return (money, ownedShares, priceBought, exchangeAmount)



    """
    Function should simulate this stock from X years ago until today using the same algorithm
    """
    def simulate(self, stock_name, years_ago):
            # Get the historical prices of the stock
        stock = yf.Ticker(stock_name)
        hist_prices = stock.history(period=f"{years_ago}y")

        # Calculate the RSI for each day
        rsi = RSIIndicator(hist_prices['Close'], window=14)
        hist_prices['RSI'] = rsi.rsi()
        hist_prices['moving_average'] = hist_prices['Close'].rolling(window=200).mean()

        # Load in settings
        global money
        global startmoney
        global ownedShares
        global priceBought
        global rsiMaxDist
        global emaBuffer
        global exchangeAmount

        

        
        rows = hist_prices.iterrows()

        # Calculate normal stock amount
        """stockRows = list(rows)
        print(str(stockRows[0]))
        print((str(stockRows[0]).split("\n")[2]).split("             ")[1])
        print("\n\n")

        print(str(stockRows[len(stockRows)-1]))
        print((str(stockRows[len(stockRows)-1]).split("\n")[2]).split("             ")[1])
        exit()
        profitPerStock = (rows[0]["Close"] - rows[len(rows)]["Close"])
        moneyEx = money * self.buyPercent
        originalMoney = 0
        while moneyEx > rows[0]["Close"]:
            moneyEx -= rows[0]["Close"]
            originalMoney += rows[len(rows)]["Close"]"""


        # Simulate the bot's trading for each day
        for i, row in rows:
            price = row['Close']
            rsi = row['RSI']
            
            

            # Get the 200-day EMA for the current day
            current_ema = hist_prices.loc[i-pd.Timedelta(days=200):i, 'Close'].ewm(span=200, adjust=False).mean().iloc[-1]

            # bear_or_bull = self.simulate_determine_bear_or_bull(day=i, hist=hist_prices)


            # Check if the current day's price is above the 200-day EMA
            above_ema = (price > (current_ema - emaBuffer))
            print("DAY: ", i, "  PRICE: ", price, "  RSI: ", rsi)
            money, ownedShares, priceBought, exchangeAmount = self.simulate_decide(stockPrice=price, RSI=rsi, money=money, ownedShares=ownedShares, priceBought=priceBought, above_ema=above_ema, exchangeAmount=exchangeAmount)
        print("MONEY BEFORE", str(int(profitTax*100)) + "%","TAX: ", money/(1-profitTax))
        print("FINAL VALUES:         Money: ", money, "        Owned shares: ", ownedShares)
        print("Final money with stock in account: ", (money + (ownedShares * price)))
        print("Profit percentage: ", ((((money + (ownedShares * price))-startmoney)/startmoney) * 100), "%")
        print("Exchange amount: ", exchangeAmount)
        # print("Money from investing normally: ", originalMoney)
    
    def start(self):
        #Login to the robinhood
        login(days=1)


        #Get stocks from config
        print("Stocks: ", STOCKS)


        #this bot should work while the market is on
        while openMarket():

            # Make a decision based on given information
            try:
                self.decide()
            except:
                print("error, waiting instead")

            time.sleep(waitTime)
        print("Market is closed")
