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
        for symbol in [coin.get('cmcTicker'), coin.get('symbolFront'), coin.get('symbol')]:
            if symbol:
                symbol_upper = symbol.upper()
                symbols.add(symbol_upper)
                if symbol_upper.startswith('$'):
                    symbols.add(symbol_upper[1:])

    # print(symbols)

    return symbols

@app.route('/evercodelab')
def evercodelab():
    cmc_coins = get_cmc_coins()
    ss_symbols = get_ss_symbols()

    result = []
    for coin in cmc_coins:
        symbol = coin['symbol'].upper()
        symbol_no_dollar = symbol[1:] if symbol.startswith('$') else symbol

        if symbol not in ss_symbols and symbol_no_dollar not in ss_symbols:
            volume_24h = 0
            quotes = coin.get('quotes', [])
            for quote in quotes:
                if quote.get('name') == 'USD':
                    volume_24h = quote.get('volume24h', 0)
                    break
            coin_url = f"https://coinmarketcap.com/currencies/{coin['slug']}/"
            result.append({'symbol': symbol, 'volume_24h': volume_24h, 'url': coin_url})

    result.sort(key=lambda x: x['volume_24h'], reverse=True)

    # print(len(result))

    template = '''
  <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CMC but not SimpleSwap</title>
    <meta name="description" content="Tokens listed on CMC but not available on SimpleSwap sorted by 24h vol">
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f7fa;
            color: #333;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            flex-direction: column;
        }
        
        .content {
            width: 100%;
            max-width: 1024px;
            margin-bottom: 20px;
            text-align: center;
            padding: 0 64px;
            box-sizing: border-box;
        }
        
        .table-container {
            width: 100%;
            max-width: 1024px;
            background-color: #fff;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
            overflow-x: auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            padding: 10px;
            text-align: left;
            border-bottom: 2px solid #ddd;
            position: sticky;
            top: 0;
        }
        
        td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        
        tr:hover {
            background-color: #f1f1f1;
        }
        
        td:nth-child(2) {
            text-align: right;
            font-weight: bold;
        }
        
        /* Styles for links */
        a {
            color: #007bff;
            text-decoration: none;
        }
        
        a:hover {
            color: #0056b3;
        }
        
        a:visited {
            color: #6c757d;
        }
        
        /* Responsive design for smaller screens */
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            
            .content, .table-container {
                margin-bottom: 15px;
            }
            
            th, td {
                padding: 8px;
                font-size: 14px;
            }
        }
        
        @media (max-width: 480px) {
            th, td {
                font-size: 12px;
                padding: 6px;
            }
            .content {
                padding: 0 16px;
            }
        }
    </style>
</head>
<body>
    <div class="content">
        <h1>CMC but not SimpleSwap</h1>
        <p>Tokens listed on CMC but not available on SimpleSwap sorted by 24h vol</p>
    </div>
    <div class="table-container">
        <table>
            <tr>
                <td>Coin</td>
                <td>Vol 24h</td>
            </tr>
            {% for coin in result %}
            <tr>
                <td><a href="{{ coin['url'] }}" target="_blank">{{ coin['symbol'] }}</a></td>
                <td>{{ "${:,.0f}".format(coin['volume_24h']) }}</td>
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