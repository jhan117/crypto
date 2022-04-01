import requests
import pandas as pd
import pyupbit


def get_open(ticker, currentPrice):
    openCheck = False
    df = pyupbit.get_ohlcv(ticker, count=600)  # 600 days

    # moving average 200
    window_ma = 200
    df['ma200'] = df["close"].rolling(window=window_ma).mean()
    ma200 = df['ma200'][-1]  # current ma200

    # RSI 2
    window_rsi = 2
    df['diff'] = df['close'].diff(1)
    df['gain'] = df['diff'].clip(lower=0).round(2)
    df['loss'] = df['diff'].clip(upper=0).abs().round(2)
    # initial avg
    df['avg_gain'] = df['gain'].rolling(
        window=window_rsi, min_periods=window_rsi).mean()[:window_rsi+1]
    df['avg_loss'] = df['loss'].rolling(
        window=window_rsi, min_periods=window_rsi).mean()[:window_rsi+1]
    # wms avg
    for i, row in enumerate(df['avg_gain'].iloc[window_rsi+1:]):
        df['avg_gain'].iloc[i + window_rsi + 1] =\
            (df['avg_gain'].iloc[i + window_rsi] *
             (window_rsi - 1) +
             df['gain'].iloc[i + window_rsi + 1])\
            / window_rsi
    for i, row in enumerate(df['avg_loss'].iloc[window_rsi+1:]):
        df['avg_loss'].iloc[i + window_rsi + 1] =\
            (df['avg_loss'].iloc[i + window_rsi] *
             (window_rsi - 1) +
             df['loss'].iloc[i + window_rsi + 1])\
            / window_rsi
    df['rs'] = df['avg_gain'] / df['avg_loss']
    df['rsi'] = 100 - (100 / (1.0 + df['rs']))
    rsi = df['rsi'][-4:]

    if rsi[0] > rsi[1] > rsi[2] and ma200 < currentPrice:
        if rsi[0] <= 60 and rsi[3] <= 10:
            openCheck = True

    return openCheck


def post_message(token, channel, text):
    response = requests.post("https://slack.com/api/chat.postMessage",
                             headers={"Authorization": "Bearer "+token},
                             data={"channel": channel, "text": text}
                             )


# ticker = "KRW-TRX"
tickers = pyupbit.get_tickers(fiat="KRW")

# slack API
myToken = "xoxb-3225469601255-3263838475088-VZRaGr2KX5Ixh535K2hm4Sq8"
channel_ID = "C0372227ML2"

post_message(myToken, channel_ID, "----Start----")

while True:
    try:
        for ticker in tickers:
            current = pyupbit.get_current_price(ticker)
            open = get_open(ticker, current)
            if open:
                post_message(myToken, channel_ID, ticker + "is open point")
    except:
        post_message(myToken, channel_ID, "----Stop----")
