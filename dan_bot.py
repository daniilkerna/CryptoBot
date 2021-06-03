import config
import scout_data as sd
from binance import Client
from datetime import datetime
import time
import math

client = Client(config.API_KEY, config.API_SECRET, tld='us')

VERSION = 1.01


POSITION = False
COOLDOWN_SECONDS = 0
PURCHASE_PRICE = 0
UPTREND = False

def truncate(f, n):
    return math.floor(f * 10 ** n) / 10 ** n

def get_account_cash_balance():
    cash = client.get_asset_balance(asset='USD')['free']
    return float(cash)

def get_coin_balance(coin):
    balance = client.get_asset_balance(asset=coin)['free']
    return float(balance)

def buy_coin(coin):
    global POSITION
    global PURCHASE_PRICE
    global COOLDOWN_SECONDS

    PURCHASE_PRICE = sd.get_latest_coin_price(coin)
    
    order = client.order_market_buy(
    symbol= coin + 'USD',
    quantity= truncate((get_account_cash_balance() / PURCHASE_PRICE), 5) - 0.1 )
    print(order)

    try:
        file_object = open('log.txt', 'a')
        file_object.write("\n\n")
        file_object.write('Purchase')
        file_object.write("\n")
        file_object.write(str(datetime.now()))
        file_object.write("\n")
        file_object.write(str(order))
        file_object.write("\n")
        file_object.close()

    finally:
        POSITION = True
        COOLDOWN_SECONDS = 10


def sell_coin(coin):
    global POSITION
    global COOLDOWN_SECONDS
    global PURCHASE_PRICE

    order = client.order_market_sell(
    symbol= coin + 'USD',
    quantity= truncate(get_coin_balance(coin) , 5))    
    print(order)

    try:
        file_object = open('log.txt', 'a')
        file_object.write("\n\n")
        file_object.write('Sell Order')
        file_object.write("\n")
        file_object.write(str(datetime.now()))
        file_object.write("\n")
        file_object.write(str(order))
        file_object.close()

    finally:
        POSITION = False
        COOLDOWN_SECONDS = 10
        PURCHASE_PRICE = 0

def set_uptrend(coin):
    global UPTREND
    old_uptrend = UPTREND
    closing_price = sd.get_latest_closing_price(coin)
    mov_avg = sd.get_coin_mov_avg(coin , config.TREND_MA)
    # print(closing_price , mov_avg , UPTREND)
    if closing_price == -1.0 or mov_avg == -1.0 :
        return

    if closing_price >= mov_avg:
        UPTREND = True
    else:
        UPTREND = False

    if old_uptrend != UPTREND:
        try:
            file_object = open('log.txt', 'a')
            file_object.write("\n")
            file_object.write('New Trend Detected. Uptrend is now:' + str(UPTREND) + "\n")
            file_object.write(str(datetime.now()))
            file_object.write("\n")
            file_object.close()
        finally:
            print("New Trend Detected")
            print("Uptrend is now: " + str(UPTREND))
            print(datetime.now())

def main():
    global POSITION
    global PURCHASE_PRICE
    global COOLDOWN_SECONDS
    global UPTREND

    while True:
        try:
            if COOLDOWN_SECONDS > 0:
                time.sleep(COOLDOWN_SECONDS)
                COOLDOWN_SECONDS = 0
                
            for coin in config.supported_coins:
                current_price = sd.get_latest_coin_price(coin)
                time.sleep(0.5)
                closing_price = sd.get_latest_closing_price(coin)
                if (current_price == -1.0 or closing_price == -1.0):
                    continue

                set_uptrend(coin)

                if not POSITION and sd.is_coin_oversold(coin , UPTREND):
                    # enter into a position
                    print("Buying Coin :" + coin)
                    print(datetime.now())
                    print("Price:" + str(current_price))

                    buy_coin(coin)

                if POSITION:
                    # potential profit
                    if sd.is_coin_overbought(coin , UPTREND):
                        print("Exiting Position")
                        print(datetime.now())
                        print("Purchase Price: " + str(PURCHASE_PRICE))
                        print("Exit Price:" + str(current_price))

                        sell_coin(coin)

                    # stop loss
                    if config.STOPLOSS_PERCENT != 0 and PURCHASE_PRICE * ((100.0 - config.STOPLOSS_PERCENT) / 100.0) >= closing_price: 
                        try:
                            file_object = open('log.txt', 'a')
                            file_object.write("\n")
                            file_object.write('Stoploss Triggered')
                            file_object.write(str(datetime.now()))
                            file_object.close()
                        finally:
                            print("Stoploss Triggered")
                            print(datetime.now())
                            print("Selling at: " + str(current_price))
                            print("Purchased at:" + str(PURCHASE_PRICE))
                        
                        sell_coin(coin)
                        COOLDOWN_SECONDS = config.COOLDOWN_SECONDS
        except Exception as e:
            print("Exception Occured")
            print(str(e))

        time.sleep(30.0)


if __name__ == "__main__":
    main()

