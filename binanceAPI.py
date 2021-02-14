# This is a comment and does not run as code.
# these next two lines import libraries into the code so we can use the functions provided by them.
from binance.client import Client
from decimal import *
import sys
import json
import os

# Update your environmental variables with your Key and Secret for Binance API (read only permissions)
key = os.environ['BINKEY']
secret = os.environ['BINSEC']
client = Client(key, secret, {"verify": True, "timeout": 20})

# set the number of transactions to pull from Binance.
i = 0
try:
    # This is looking for the first value after the script name, these are called command line arguments (CLA).
    callLimit = sys.argv[1]
except IndexError:
    # If the CLA is missing, it will throw an error.
    # Here we're catching that error and prompting the user for the data we need.
    try:
        callLimit = int(input("Number of Transactions to get?: "))
    except ValueError:
        i += 1
        callLimit = int(input("You must enter a number of transactions: "))
        if i == 1:
            print("This is not really working out for me. Good bye.")
            exit()

# set the coin you want to pull transactions for.
try:
    # The second CLA is the trading pair name.
    coin = str(sys.argv[2])
except IndexError:
    # Again if it's not found in the CLAs, we'll ask for it in the following prompt.
    try:
        coin = str(input("Enter the trading pair you want to track: "))
    except ValueError:
        i += 1
        coin = str(input("A trading pair must be all capital letters, please enter your trading pair: "))
        if i > 1:
            print("Your lack of intellect surpasses my understanding. Good bye.")
            exit()



# This class sets the colors for output text
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# This makes the call to get your orders from binance history.
orders = client.get_all_orders(symbol=coin, limit=callLimit)
cPrice = client.get_symbol_ticker(symbol=coin)
coinPrice = cPrice['price']

###############
# DEBUG: Following lines print raw data from Binance, this is useful if you want to move the data
#        into excel to check math, or see the full list of data to add to this script. To use this feature, pass
#        "dump" in the 3rd CLA position.
try:
    if sys.argv[3] == 'dump':
        print(json.dumps(orders, indent=2))
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
for d in orders:
    # Get the executed qty from the binance data "d" for every buy and sell.
    # This is not being used yet.
    # TODO: Check if the buys+sells equal the total in totalCoins.
    totalCoins += Decimal(d['executedQty'])

    # Is this record a buy?
    if d['side'] == 'BUY' and d['status'] == 'FILLED':
        # Yes, this is a buy.
        # Add the Qty of coins to the coinsbuy variable.
        coinsbuy += Decimal(d['executedQty'])
        # Add the cost for all coins in this transaction to the buyp variable.
        buyp += Decimal(d['cummulativeQuoteQty'])

        # This will overwrite the variable 'lastbuy' with the buy price of each order. The value overwrites the variable
        # each time though the loop, leaving the value of the last price paid for the buy which is the latest buy.
        lastbuy = d['price']

        # Is this transaction a sell?
    elif d['side'] == 'SELL' and d['status'] == 'FILLED':
        # Yes, this is a sell.
        # Add the Qty of coins to the coinsells variable.
        coinsells += Decimal(d['executedQty'])
        # Add the price you got for this sale to the sellp variable.
        sellp += Decimal(d['cummulativeQuoteQty'])

# find the average buy price
avgbuy = round(buyp/coinsbuy, 4)

# print out the count of transactions, the coin we're looking at and the current market price.
print("Last " + str(callLimit) + " Transactions")
print(f"COIN: {coin}")
print(f"Current: {str(cPrice['price'])}")
print("  ")
print("-----------------------------------")

# find the profit and loss for all transactions.
pl = sellp-buyp

if pl < 0:
    # set the color to red if the P&L is negative.
    print(f"P/L: {bcolors.FAIL}{pl}{bcolors.ENDC}")
else:
    # set the color to green is the P&L is positive.
    print(f"P/L: {bcolors.OKGREEN}{pl}{bcolors.ENDC}")

if Decimal(coinPrice)-avgbuy < 0:
    # Set the color to red is the current price is lower than our average buy price.
    print(f"Price Delta: {bcolors.FAIL}{Decimal(coinPrice)-avgbuy}{bcolors.ENDC}")
else:
    # set the color to green if the current price is higher than our average buy price.
    print(f"Price Delta: {bcolors.OKGREEN}{Decimal(coinPrice)-avgbuy}{bcolors.ENDC}")

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
print(f"Avg Buy Price: {bcolors.OKBLUE}{avgbuy}{bcolors.ENDC}")
# Print out the avg sell cost
print("  ")
print(f"Coins Sold: {round(coinsells, 4)}")
print(f"Price Total: {sellp}")
print(f"Avg Sell Price: {round(sellp/coinsells, 4)}")