#!/usr/bin/python3
# these next two lines import libraries into the code so we can use the functions provided by them.
from binance.client import Client
from decimal import *
import sys
import json
import os

# Update your environmental variables with your Key and Secret for Binance API (read only permissions)
key = os.environ['BINKEY']
secret = os.environ['BINSEC']

# Get data from Binance.
try:
    client = Client(key, secret, {"verify": True, "timeout": 20})
except Exception:
    print("Not a valid trading pair.")
    sys.exit(1)

# set the number of transactions to pull from Binance.
try:
    # This is looking for the first value after the script name, these are called command line arguments (CLA).
    callLimit = sys.argv[1]
except IndexError:
    # If the CLA is missing, it will throw an error.
    # Here we're catching that error and prompting the user for the data we need.
    try:
        callLimit = int(input("Number of Transactions to get?: "))
    except ValueError:
        sys.exit(1)




# set the coin you want to pull transactions for.
try:
    # The second CLA is the trading pair name.
    coin = str(sys.argv[2])
except IndexError:
    # Again if it's not found in the CLAs, we'll ask for it in the following prompt.
    try:
        coin = str(input("Enter the trading pair you want to track: "))
    except ValueError:
        sys.exit(2)



# This class sets the colors for output text
class Bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def calc(callLimit, coin):

    # This makes the call to get your orders from binance history.
    trades = client.get_my_trades(symbol=coin, limit=callLimit)
    cPrice = client.get_symbol_ticker(symbol=coin)
    coinPrice = cPrice['price']

    ###############
    # DEBUG: Following lines print raw data from Binance, this is useful if you want to move the data
    #        into excel to check math, or see the full list of data to add to this script. To use this feature, pass
    #        "dump" in the 3rd CLA position.
    try:
        if sys.argv[3] == 'dump':
            print(json.dumps(trades, indent=2))
            exit()
    except IndexError:
        pass
    ###############

    # Get open position for this coin.
    # NOTE: "coin[:-3]" is used to convert trading pairs to assets (e.g. ADAUSD to ADA ).
    # NOTE: If you have 100 coins and an active Sell Limit order for 50 coins, this will report that you have 50 coins.
    position = client.get_asset_balance(asset=coin[:-3])

    # these variables are set so we can increment them in the for loop below.
    buyp: int = 0
    coinsbuy = 0
    sellp = 0
    coinsells = 0
    avgbuy = 0
    avgsell = 0
    totalCoins = 0
    lastbuy = 0

    # Loop through the orders, look for buys then sells and increment each to find the totals foreach.
    for d in trades:
        print('here')
        # Get the executed qty from the binance data "d" for every buy and sell.
        # This is not being used yet.
        # TODO: Check if the buys+sells equal the total in totalCoins.
        totalCoins += Decimal(d['qty'])

        # Is this record a buy?

        if d['isBuyer']:

            # Yes, this is a buy.
            # Add the Qty of coins to the coinsbuy variable.
            coinsbuy += Decimal(d['qty'])
            print(coinsbuy)
            # Add the cost for all coins in this transaction to the buyp variable.
            buyp += Decimal(d['price'])
            print(buyp)

            # This will overwrite the variable 'lastbuy' with the buy price of each order. The value overwrites the variable
            # each time though the loop, leaving the value of the last price paid for the buy which is the latest buy.
            lastbuy = d['price']

            # Is this transaction a sell?
        elif not d['isBuyer']:
            # Yes, this is a sell.
            # Add the Qty of coins to the coinsells variable.
            coinsells += Decimal(d['qty'])
            # Add the price you got for this sale to the sellp variable.
            sellp += Decimal(d['price'])

    # find the average buy price

    avgbuy = round(buyp / coinsbuy, 4)

    # print out the count of transactions, the coin we're looking at and the current market price.
    print("Last " + str(callLimit) + " Transactions")
    print(f"COIN: {coin}")
    print(f"Current: {str(cPrice['price'])}")
    print("  ")
    print("-----------------------------------")

    # find the profit and loss for all transactions.
    pl = sellp - buyp

    if pl < 0:
        # set the color to red if the P&L is negative.
        print(f"P/L: {Bcolors.FAIL}{pl}{Bcolors.ENDC}")
    else:
        # set the color to green is the P&L is positive.
        print(f"P/L: {Bcolors.OKGREEN}{pl}{Bcolors.ENDC}")

    if Decimal(coinPrice) - avgbuy < 0:
        # Set the color to red is the current price is lower than our average buy price.
        print(f"Price Delta: {Bcolors.FAIL}{Decimal(coinPrice) - avgbuy}{Bcolors.ENDC}")
    else:
        # set the color to green if the current price is higher than our average buy price.
        print(f"Price Delta: {Bcolors.OKGREEN}{Decimal(coinPrice) - avgbuy}{Bcolors.ENDC}")

    # Print the number of this coin you are holding in binance.
    print(f"Open Position: {round(Decimal(position['free']), 2)}")
    # Print the last price we bought for. LPP = Last Price Paid
    print(f"LPP: {lastbuy}")
    # Print out a dotted line and a blank line for formatting purposes.
    print("-----------------------------------")
    print(" ")
    # Print out the avg buy cost
    print(f"Coins Bought: {round(coinsbuy, 4)}")
    print(f"Cost total: {buyp}")
    print(f"Avg Buy Price: {Bcolors.OKBLUE}{avgbuy}{Bcolors.ENDC}")
    # Print out the avg sell cost
    print("  ")
    print(f"Coins Sold: {round(coinsells, 4)}")
    print(f"Price Total: {sellp}")
    print(f"Avg Sell Price: {round(sellp / coinsells, 4)}")


if __name__ == '__main__':
    calc(callLimit, coin)

