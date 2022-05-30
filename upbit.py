import logging
import requests
import asyncio
import json
from websockets import connect
import uuid

# Set logging level to DEBUG
logging.basicConfig(
    format='[%(levelname)s => %(filename)s:%(lineno)d][%(asctime)s]\n%(message)s',
    datefmt='%Y/%m/%d %H:%M:%S'
)

REST_API_url = 'https://api.upbit.com/v1/'
WEBSOCKET_url = 'wss://api.upbit.com/websocket/v1'


# REST API 요청
def REST_API(reqType, reqUrl, reqHeaders, reqParams):
    try:
        response = requests.request(
            reqType, REST_API_url+reqUrl, headers=reqHeaders, params=reqParams)

        return response.json()
    except:
        print("snapshot error")


# KRW 마켓 코드 조회
def get_krw_market():
    market_response = REST_API(
        'GET', 'market/all', {'Accept': 'application/json'}, {'isDetails': 'true'})

    krw = []
    for market in market_response:
        if market["market"].startswith("KRW"):
            krw.append(market["market"])
    krw.sort()

    return krw


# 시세 종목 조회 -> 마켓 코드 조회
# output: dictionary
# code = {market: [korean_name, english_name, market_warning], ...}
def get_market_data():
    market_response = REST_API(
        'GET', 'market/all', {'Accept': 'application/json'}, {'isDetails': 'true'})

    code = {}
    for data in market_response:
        code[data['market']] = [data['korean_name'],
                                data['english_name'], data['market_warning']]

    return code


# 시세 Ticker 조회 -> 현재가 정보
# input: market code
def get_ticker_data(market):
    ticker_response = REST_API(
        'GET', 'ticker', {'Accept': 'application/json'}, {'markets': market})[0]

    return ticker_response


# 시세 캔들 조회 -> 일(Day) 캔들
# input: market, to = None, count = 7, convertingPriceUnit = None
def get_candles_days_data(market, to=None, count=7, convertingPriceUnit=None):
    candles_days_response = REST_API(
        'GET', 'candles/days', {'Accept': 'application/json'}, {'market': market, 'to': to, 'count': count, 'convertingPriceUnit': convertingPriceUnit})

    return candles_days_response


# websocket 요청
# input: type, codes(list), stream_type("snapshot", "realtime")
async def websocket(type, codes, stream_type=None):
    async with connect(WEBSOCKET_url) as websocket:
        type_field = {"type": type, "codes": codes}

        if stream_type == "snapshot":
            type_field["isOnlySnapshot"] = True
        elif stream_type == "realtime":
            type_field["isOnlyRealtime"] = True

        data = [{"ticket": str(uuid.uuid4())}, type_field, {
            "format": "SIMPLE"}]
        await websocket.send(json.dumps(data))

        while True:
            recv_data = await websocket.recv()
            recv_data = recv_data.decode('utf8')
            result = json.loads(recv_data)

            return result


if __name__ == "__main__":
    asyncio.run(websocket("ticker", ["KRW-BTC"], "snapshot"))
