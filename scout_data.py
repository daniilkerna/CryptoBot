import config
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from datetime import datetime
import numpy as np
from talib import RSI,BBANDS
import time
import csv


client = Client(config.API_KEY, config.API_SECRET, tld='us')

def get_coin_price(coin):
    try:
        candles = client.get_klines(symbol=(coin + 'USD') , interval=Client.KLINE_INTERVAL_15MINUTE , limit=1)
        return float(candles[-1][4])
    except:
        return float(-1)

def is_coin_oversold(coin):
    candles = client.get_klines(symbol=(coin + 'USD') , interval=Client.KLINE_INTERVAL_15MINUTE , limit=150)
    candles = candles[:-1]
    closing_prices = np.array([float(x) for x in ([y[4] for y in candles])])
    rsi = RSI(closing_prices, timeperiod=config.RSI_TIME_PERIOD)[-1]

    if (rsi <= config.RSI_OVERSOLD):
        return True

    return False

def is_coin_overbought(coin):
    candles = client.get_klines(symbol=(coin + 'USD') , interval=Client.KLINE_INTERVAL_15MINUTE , limit=150)
    candles = candles[:-1]
    closing_prices = np.array([float(x) for x in ([y[4] for y in candles])])
    rsi = RSI(closing_prices, timeperiod=config.RSI_TIME_PERIOD)[-1]
    
    if (rsi >= config.RSI_OVERBOUGHT):
        return True

    return False

def get_oversold_coins(coin_list):
    oversold_coins = []

    for coin in coin_list:
        if is_coin_oversold(coin):
            oversold_coins.append(coin)

    return oversold_coins


def main():

    print(get_oversold_coins(config.supported_coins))
    LTCBALANCE = client.get_asset_balance(asset='LTC')['free']
    USDBALANCE = client.get_asset_balance(asset='USD')['free']

    print(LTCBALANCE)
    print(USDBALANCE)

    # candles = client.get_historical_klines("LTCUSD", Client.KLINE_INTERVAL_15MINUTE, "1 Jan, 2020")

    # print(len(candles))
    # print(candles[-1])
    # csvfile = open('15minute_2020_LTC.csv' , 'w' , newline='')
    # candlestick_write = csv.writer(csvfile)

    # for candle in candles:
    #     candle[0] = candle[0] / 1000
    #     candlestick_write.writerow(candle)


if __name__ == "__main__":
    main()



