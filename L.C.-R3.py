import pyupbit
import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('TOKEN')


def get_rsi(ticker):
    df = pyupbit.get_ohlcv(ticker, count=600)  # 600 days

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

    return df['rsi'][-4:]


def get_open(ticker, currentPrice):
    openCheck = False
    df = pyupbit.get_ohlcv(ticker, count=600)  # 600 days

    # moving average 200
    window_ma = 200
    df['ma200'] = df["close"].rolling(window=window_ma).mean()
    ma200 = df['ma200'][-1]  # current ma200

    rsi = get_rsi(ticker)

    if rsi[0] > rsi[1] > rsi[2] and ma200 < currentPrice:
        if rsi[0] <= 60 and rsi[3] <= 10:
            openCheck = True

    return openCheck


def get_close(ticker):
    closeCheck = False
    rsi = get_rsi(ticker)

    if rsi[3] > 70:
        closeCheck = True

    return closeCheck


tickers = pyupbit.get_tickers(fiat="KRW")
activity = discord.Game(name="Trading Crypto")
bot = commands.Bot(command_prefix='!', activity=activity,
                   status=discord.Status.online)
openList = []


@bot.event
async def on_ready():
    print('Logged on as {0}!'.format(bot.user))
    channel = bot.get_channel(959384498213122090)

    await channel.send("Hi! I started trading.")

    while True:
        try:
            for ticker in tickers:
                current = pyupbit.get_current_price(ticker)
                open = get_open(ticker, current)
                close = get_close(ticker)
                if open:
                    buy = True
                    await channel.send(ticker + " is open!")
                elif close and buy:
                    await channel.send(ticker + " is close!")
        except:
            print("It ended unexpectedly")

bot.run(token)
