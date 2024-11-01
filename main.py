from flask import Flask, render_template_string
import requests

app = Flask(__name__)

def get_cmc_coins():
    url = 'https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listing?start=1&limit=1500&sortBy=market_cap&sortType=desc&convert=USD,BTC,ETH&cryptoType=all&tagType=all&audited=false&aux=ath,atl,high24h,low24h,num_market_pairs,cmc_rank,date_added,max_supply,circulating_supply,total_supply,volume_7d,volume_30d,self_reported_circulating_supply,self_reported_market_cap'
    response = requests.get(url)
    data = response.json()
    return data['data']['cryptoCurrencyList']


def get_ss_symbols():
    url = 'https://simpleswap.io/api/v3/currencies?fixed=false&includeDisabled=false'
    data = requests.get(url).json()
    symbols = set()

    for coin in data:
        symbol = coin.get('cmcTicker')
        if symbol:
            symbols.add(symbol.upper())

        symbol_front = coin.get('symbolFront')
        if symbol_front:
            symbols.add(symbol_front.upper())

        symb = coin.get('symbol')
        if symb:
            symbols.add(symb.upper())

    return symbols

@app.route('/evercodelab')
def evercodelab():
    cmc_coins = get_cmc_coins()
    ss_symbols = get_ss_symbols()

    result = []
    for coin in cmc_coins:
        symbol = coin['symbol'].upper()
        if symbol not in ss_symbols:
            volume_24h = 0
            quotes = coin.get('quotes', [])
            for quote in quotes:
                if quote.get('name') == 'USD':
                    volume_24h = quote.get('volume24h', 0)
                    break
            result.append({'symbol': symbol, 'volume_24h': volume_24h})

    result.sort(key=lambda x: x['volume_24h'], reverse=True)
    print(len(result))
    template = '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>CMC but not SimpleSwap </title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f7fa; color: #333; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: flex-start; min-height: 100vh; }
            .table-container { width: 100%; max-width: 800px; background-color: #fff; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); border-radius: 8px; overflow-x: auto; }
            table { width: 100%; border-collapse: collapse; }
            th { background-color: #4CAF50; color: white; font-weight: bold; padding: 10px; text-align: left; border-bottom: 2px solid #ddd; position: sticky; top: 0; }
            td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            tr:hover { background-color: #f1f1f1; }
            td:nth-child(2) { text-align: right; font-weight: bold; }
            h2 { text-align: center; margin-top: 10px; color: #333; }
        </style>
    </head>
    <body>
        <div class="table-container">
            <table>
            <tr>
                    <td>Coin</td>
                    <td>Vol 24h</td>
                </tr>
                {% for coin in result %}
                <tr>
                    <td>{{ coin['symbol'] }}</td>
                    <td>{{ "${:,.2f}".format(coin['volume_24h']) }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    '''
    return render_template_string(template, result=result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)