import requests
import asyncio
import time
import websockets
import json


def calculate_a_coins(a_coins: float, b_coins: float, b_sell: float) -> float:
    k = a_coins * b_coins
    b_total = b_coins + b_sell
    a_total = k / b_total
    a_get = a_coins - a_total
    return a_get


def get_BCH_Price():
    uri = "https://api.coinbase.com/v2/prices/BCH-USD/spot"
    response = requests.get(uri)
    return float(response.json()['data']['amount'])


async def send_json_rpc_request(token_contract):
    uri = "wss://fex.cash:50005/"
    async with websockets.connect(uri) as websocket:
        request = {
            "method": "blockchain.address.listunspent",
            "params": ["bitcoincash:prcgkaynawe05erctyudxht5zpjl4sdd3v48ayjumd", "include_tokens"],
            "id": 1
        }
        while True:
            request_json = json.dumps(request)
            await websocket.send(request_json)
            response_json = await websocket.recv()
            response = json.loads(response_json)['result']
            for i in response:
                if str(i['token_data']['category']).lower() == token_contract.lower():
                    value = int(i['value']) / (10 ** 8)
                    amount = int(i['token_data']['amount']) / (10 ** 8)
                    now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    one_sheet = calculate_a_coins(value, amount, 1000)
                    print(
                        f'{now_time}  LP余额: {value:.2f} BCH = {value * get_BCH_Price():.2f} USD , 代币: {amount:.2f}  , 1000枚代币价值: {one_sheet:.4f} BCH = {one_sheet * get_BCH_Price():.2f} USD')
            await asyncio.sleep(10)


if __name__ == '__main__':
    token_contract = input('请输入代币合约地址: ')
    asyncio.get_event_loop().run_until_complete(send_json_rpc_request(token_contract))
