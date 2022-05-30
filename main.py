from upbit import *
from LC_R3 import *

from datetime import datetime
import time

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!', case_insensitive=True)


@bot.event
async def on_ready():
    print(f'{bot.user} successfully logged in!')


@bot.command(aliases=["clean", "청소"], help="!clean or 청소")
async def clear(ctx):
    await ctx.channel.purge()


@bot.command(aliases=["code", "코드"], help='!code or 코드 (name = 비트코인, Bitcoin, bitcoin, ...)')
async def market_code(ctx, name):
    market = get_market_data()
    market_code = []

    for key, value in market.items():
        if value[0] == name or value[1] == name or value[1].lower() == name:
            market_code.append(key)
            if value[2] == 'NONE':
                warning = False
            else:
                warning = True

    if not warning:
        await ctx.channel.send(f"{name}의 마켓 코드는 `{', '.join(market_code)}`입니다.")
    else:
        await ctx.channel.send(f"{name}의 마켓 코드는 `{', '.join(market_code)}`입니다.\n그러나 이 종목은 유의 종목이니 투자에 유의하세요.")


@bot.command(aliases=list(get_market_data().keys()), help='!market_code_name = KRW-BTC, USDT-BTC, ...')
async def info(ctx):
    market_data = get_market_data()
    ticker_data = get_ticker_data(ctx.invoked_with)

    # 마켓 코드
    code = ticker_data['market']

    # 웹소켓 조회
    websocket_data = await websocket("ticker", [code], "snapshot")

    # 마켓 코드 조회
    market_kr_name = market_data[code][0]
    market_en_name = market_data[code][1]
    desc = f"{code}"
    if market_data[code][2] == "CAUTION":
        desc = f"{code} `유의`"

    # 현재가 정보
    high_price = format(round(ticker_data['high_price']), ',')
    low_price = format(round(ticker_data['low_price']), ',')
    prev_closing_price = format(round(ticker_data['prev_closing_price']), ',')
    high_rate = (ticker_data['high_price'] /
                 ticker_data['prev_closing_price'] - 1) * 100
    low_rate = (1 - ticker_data['low_price'] /
                ticker_data['prev_closing_price']) * 100

    trade_price = format(round(ticker_data['trade_price']), ',')

    signed_change_rate = ticker_data['signed_change_rate'] * 100
    signed_change_price = ticker_data['signed_change_price']
    if ticker_data['change_price'] < 100:
        signed_change_price = f'{signed_change_price:.2f}'
    else:
        signed_change_price = format(round(signed_change_price), ',')
    if ticker_data['change'] == 'RISE':
        message_color = 0xFF0000
        value = f"```ansi\n\u001b[{0};{31}m+{signed_change_rate:.2f}\u0025\n+{signed_change_price}\n```"
    elif ticker_data['change'] == 'FALL':
        message_color = 0x0000FF
        value = f"```ansi\n\u001b[{0};{34}m{signed_change_rate:.2f}\u0025\n{signed_change_price}\n```"
    else:
        message_color = 0x000000
        value = f"```ansi\n{signed_change_rate:.2f}\u0025\n{signed_change_price}\n```"

    acc_trade_price_24h = format(
        round(ticker_data['acc_trade_price_24h'] / 1000000), ',')

    timestamp = ticker_data['timestamp'] / 1000
    format_time = datetime.fromtimestamp(
        int(timestamp)).strftime('%Y-%m-%d %H:%M:%S')

    # 체결 강도
    volume_power = websocket_data['abv'] / websocket_data['aav'] * 100

    # embed message
    info_embed = discord.Embed(
        color=message_color, title=f"{market_kr_name} ({market_en_name})의 시세", description=desc)

    info_embed.add_field(name='현재가', value=f"```ansi\n{trade_price}\n```")
    info_embed.add_field(
        name='전일대비', value=value)
    info_embed.add_field(
        name='거래대금', value=f'```ansi\n{acc_trade_price_24h}백만\n```')
    info_embed.add_field(
        name="체결 강도", value=f"```ansi\n+{volume_power:.2f}%\n```", inline=False)
    info_embed.add_field(
        name="전일 종가", value=f"```ansi\n{prev_closing_price}\n```")
    info_embed.add_field(
        name="당일 고가", value=f"```ansi\n\u001b[{0};{31}m{high_price}\n+{high_rate:.2f}%```")
    info_embed.add_field(
        name="당일 저가", value=f"```ansi\n\u001b[{0};{34}m{low_price}\n-{low_rate:.2f}%```")
    info_embed.set_footer(text=format_time)

    await ctx.channel.send(embed=info_embed)


@bot.command(aliases=["전략", "strategy"], help="!strategy or 전략")
async def strategies(ctx):
    message = ""

    strategies = ["R3", "ATR 채널 돌파", "추세 강도", "HLHB", "내부 막대 추세"]

    for strategy in strategies:
        message += f"- {strategy}\n"

    await ctx.channel.send(message)


@bot.command(aliases=["백테스팅"])
async def backtesting(ctx, strategy, market="all"):
    if strategy == "R3":
        if market == "all":
            await ctx.channel.send("---Start---")
            for code in get_krw_market():
                market_text = get_market_data()[code][0]
                if make_dataframe(code).empty:
                    await ctx.channel.send(f"{market_text}은(는) 데이터가 충분하지 않습니다")
                else:
                    result = backtesting_R3(code)
                    if result.empty:
                        await ctx.channel.send(f"{market_text}은(는) 조건에 맞는 경우가 없습니다")
                    else:
                        # message_embed =
                        await ctx.channel.send(result)

                time.sleep(0.1)
            await ctx.channel.send("---End---")
        else:
            result = backtesting_R3(market)
            if result == None:
                await ctx.channel.send("최근 90일동안 백테스팅 해봤지만 진입할 포지션을 찾지 못했습니다.")
            else:
                await ctx.channel.send(result)


# bot.run(os.environ['TOKEN'])
