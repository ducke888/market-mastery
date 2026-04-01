from http.server import BaseHTTPRequestHandler
import json

POPULAR_STOCKS = [
    {"ticker": "AAPL", "name": "Apple Inc."},
    {"ticker": "MSFT", "name": "Microsoft Corp."},
    {"ticker": "NVDA", "name": "NVIDIA Corp."},
    {"ticker": "TSLA", "name": "Tesla Inc."},
    {"ticker": "GOOGL", "name": "Alphabet Inc."},
    {"ticker": "AMZN", "name": "Amazon.com Inc."},
    {"ticker": "META", "name": "Meta Platforms"},
    {"ticker": "SPY", "name": "S&P 500 ETF"},
    {"ticker": "QQQ", "name": "Nasdaq 100 ETF"},
    {"ticker": "AMD", "name": "Advanced Micro Devices"},
    {"ticker": "JPM", "name": "JPMorgan Chase"},
    {"ticker": "NFLX", "name": "Netflix Inc."},
    {"ticker": "DIS", "name": "Walt Disney Co."},
    {"ticker": "BA", "name": "Boeing Co."},
    {"ticker": "V", "name": "Visa Inc."},
    {"ticker": "XOM", "name": "Exxon Mobil"},
    {"ticker": "COIN", "name": "Coinbase Global"},
    {"ticker": "UBER", "name": "Uber Technologies"},
    {"ticker": "SHOP", "name": "Shopify Inc."},
    {"ticker": "PLTR", "name": "Palantir Technologies"},
]


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps(POPULAR_STOCKS).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)
