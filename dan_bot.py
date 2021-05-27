import config
import scout_data as sd
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from datetime import datetime
import time
import math

client = Client(config.API_KEY, config.API_SECRET, tld='us')

VERSION = 1.00


POSITION = False
COOLDOWN_SECONDS = 0
PURCHASE_PRICE = 0

def truncate(f, n):
    return math.floor(f * 10 ** n) / 10 ** n

def get_account_cash_balance():
    cash = client.get_asset_balance(asset='USD')['free']
    return cash

def get_coin_balance(coin):
    balance = client.get_asset_balance(asset=coin)['free']
    return balance

def buy_coin(coin):
    global POSITION
    global PURCHASE_PRICE
    global COOLDOWN_SECONDS

    PURCHASE_PRICE = sd.get_coin_price(coin)
    
    order = client.order_market_buy(
    symbol= coin + 'USD',
    quantity= truncate((get_account_cash_balance() / PURCHASE_PRICE), 5) - 0.1 )
    print(order)

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

    POSITION = False
    COOLDOWN_SECONDS = 10
    PURCHASE_PRICE = 0


def main():
    global POSITION
    global PURCHASE_PRICE
    global COOLDOWN_SECONDS

    while True:
        if COOLDOWN_SECONDS > 0:
            time.sleep(COOLDOWN_SECONDS)
            COOLDOWN_SECONDS = 0
            
        for coin in config.supported_coins:
            current_price = sd.get_coin_price(coin)
            print(current_price)
            print(datetime.now())

            if not POSITION and sd.is_coin_oversold(coin):
                # enter into a position
                print("Buying Coin :" + coin)
                print(datetime.now())
                print("Price:" + str(current_price))

                buy_coin(coin)

            if POSITION:
                # potential profit
                if sd.is_coin_overbought(coin):
                    print("Exiting Position")
                    print(datetime.now())
                    print("Purchase Price: " + str(PURCHASE_PRICE))
                    print("Exit Price:" + str(current_price))

                    sell_coin(coin)

                # stop loss
                if config.STOPLOSS_PERCENT != 0 and PURCHASE_PRICE * ((100.0 - config.STOPLOSS_PERCENT) / 100.0) >= current_price: 
                    print("Stoploss Triggered")
                    print(datetime.now())
                    print("Selling at: " + str(current_price))
                    print("Purchased at:" + str(PURCHASE_PRICE))
                    
                    sell_coin(coin)
                    COOLDOWN_SECONDS = config.COOLDOWN_SECONDS

        time.sleep(10.0)


if __name__ == "__main__":
    main()

