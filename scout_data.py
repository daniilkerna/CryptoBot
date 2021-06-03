import config
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from datetime import datetime
import numpy as np
from talib import RSI,BBANDS,SMA
import time
import csv


client = Client(config.API_KEY, config.API_SECRET, tld='us')

def get_latest_coin_price(coin):
    try:
        candles = client.get_klines(symbol=(coin + 'USD') , interval=Client.KLINE_INTERVAL_15MINUTE , limit=1)
        return float(candles[-1][4])
    except:
        return float(-1.0)

def get_latest_closing_price(coin):
    try:
        candles = client.get_klines(symbol=(coin + 'USD') , interval=Client.KLINE_INTERVAL_15MINUTE , limit=10)
        return float(candles[-2][4])
    except:
        return float(-1.0)

def get_coin_mov_avg(coin , period):
        try:
            candles = client.get_klines(symbol=(coin + 'USD') , interval=Client.KLINE_INTERVAL_15MINUTE , limit=period)
            candles = candles[:-1]
            closing_prices = np.array([float(x) for x in ([y[4] for y in candles])])
            mov_avg = SMA(closing_prices , timeperiod=period-1)
            return float(mov_avg[-1])
        except Exception as e:
            print(e)
            return float(-1.0)


def is_coin_oversold(coin , uptrend):
    candles = client.get_klines(symbol=(coin + 'USD') , interval=Client.KLINE_INTERVAL_15MINUTE , limit=150)
    candles = candles[:-1]
    closing_prices = np.array([float(x) for x in ([y[4] for y in candles])])
    rsi = RSI(closing_prices, timeperiod=config.RSI_TIME_PERIOD)[-1]

    if uptrend:
        if (rsi <= config.RSI_OVERSOLD_UPTREND):
            return True
    else:
        if (rsi <= config.RSI_OVERSOLD_DOWNTREND):
            return True

    return False

def is_coin_overbought(coin , uptrend):
    candles = client.get_klines(symbol=(coin + 'USD') , interval=Client.KLINE_INTERVAL_15MINUTE , limit=150)
    candles = candles[:-1]
    closing_prices = np.array([float(x) for x in ([y[4] for y in candles])])
    rsi = RSI(closing_prices, timeperiod=config.RSI_TIME_PERIOD)[-1]
    
    if uptrend:
        if (rsi >= config.RSI_OVERBOUGHT_UPTREND):
            return True
    else:
        if (rsi >= config.RSI_OVERBOUGHT_DOWNTREND):
            return True

    return False

def get_oversold_coins(coin_list):
    oversold_coins = []

    for coin in coin_list:
        if is_coin_oversold(coin , True):
            oversold_coins.append(coin)

    return oversold_coins


def main():

    LTCBALANCE = client.get_asset_balance(asset='LTC')['free']
    USDBALANCE = client.get_asset_balance(asset='USD')['free']

    print(LTCBALANCE)
    print(USDBALANCE)

    # candles  = client.get_historical_klines("LTCUSD", Client.KLINE_INTERVAL_15MINUTE, "1 Dec, 2019")

    # print(get_latest_coin_price('LTC'))
    # print(get_latest_closing_price('LTC'))
    print(get_coin_mov_avg('LTC' , 200))
    print(is_coin_overbought('LTC' , True))
    print(is_coin_overbought('LTC' , False))
    print(is_coin_oversold('LTC' , True))
    print(is_coin_oversold('LTC' , False))
    # print(get_coin_mov_avg('LTC' , 100))
    # print(get_coin_mov_avg('LTC' , 50))

    # csvfile = open('15minute_2020_LTC.csv' , 'w' , newline='')
    # candlestick_write = csv.writer(csvfile)

    # for candle in candles:
    #     candle[0] = candle[0] / 1000
    #     candlestick_write.writerow(candle)


if __name__ == "__main__":
    main()



