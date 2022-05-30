from upbit import *
import pandas as pd
from datetime import datetime, timedelta
from ta.trend import SMAIndicator
from ta.momentum import RSIIndicator


def make_dataframe(market):
    now = datetime.now()
    before_200days = (now - timedelta(days=200)).strftime("%Y-%m-%d")
    first_day = (now - timedelta(days=291)).strftime("%Y-%m-%d")
    data = {"date": [], "open": [], "high": [],
            "low": [], "close": []}
    candles1 = get_candles_days_data(market, count=200)
    candles2 = get_candles_days_data(
        market, to=f"{before_200days} 09:00:00", count=92)

    for dic in candles1:
        candle_date = dic["candle_date_time_kst"].split('T')[0]
        data["date"].insert(0, candle_date)
        data["open"].insert(0, dic["opening_price"])
        data["high"].insert(0, dic["high_price"])
        data["low"].insert(0, dic["low_price"])
        data["close"].insert(0, dic["trade_price"])

    for dic in candles2:
        candle_date = dic["candle_date_time_kst"].split('T')[0]
        data["date"].insert(0, candle_date)
        data["open"].insert(0, dic["opening_price"])
        data["high"].insert(0, dic["high_price"])
        data["low"].insert(0, dic["low_price"])
        data["close"].insert(0, dic["trade_price"])

    df = pd.DataFrame(data)
    df.set_index('date', inplace=True)

    if df.index[0] != first_day:
        df = df[0:0]

    return df


def get_indicator(market):
    df = make_dataframe(market)

    if not df.empty:
        indicator_sma = SMAIndicator(close=df["close"], window=200)
        indicator_rsi = RSIIndicator(close=df["close"], window=2)

        df["sma"] = indicator_sma.sma_indicator()
        df["rsi"] = indicator_rsi.rsi()
        df = df.dropna()

    return df


def check_signal(market):
    open = False
    close = False
    ma200, rsi = get_indicator(market)
    ticker = get_ticker_data(market)
    if rsi != None:
        if rsi.iloc[0] > rsi.iloc[1] > rsi.iloc[2] and ma200 < ticker["trade_price"]:
            if rsi.iloc[0] <= 60 and rsi.iloc[3] <= 10:
                open = True

        if rsi.iloc[3] >= 70:
            close = True
    else:
        return None

    return open, close


# 90일 기준 backtesting
def backtesting_R3(market):
    check_sma = []
    data = {"date": [], "price": [], "profit": []}

    df = get_indicator(market)

    if not df.empty:
        sma = df["sma"]
        rsi = df["rsi"]

        buy_signal = False

        for i in range(93):
            if df["close"][i] <= sma[i] <= df["high"][i]:
                check_sma.append(sma[i])

        if check_sma != []:
            for i in range(2, 92):
                if buy_signal == False:
                    if (60 >= rsi[i-2]) > rsi[i-1] > (rsi[i] <= 10) and df["close"][i] <= sma[i] <= df["high"][i]:
                        buy_signal = True
                        data["date"].append(df.index[i])
                        data["price"].append(sma[i])
                else:
                    if rsi[i] >= 70:
                        buy_signal = False
                        data["date"].append(df.index[i])
                        data["price"].append(df["close"][i])
                        data["profit"].append(
                            data["price"][-1] - data["price"][-2])
                        data["profit"].append(
                            data["price"][-1] / data["price"][-2] * 100 - 100)

    if data["profit"] == []:
        data = {}

    df2 = pd.DataFrame(data)

    return df2
