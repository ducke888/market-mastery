from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse


def yahoo_fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        query = params.get("q", [""])[0]
        results = []
        if len(query) >= 1:
            try:
                url = f"https://query2.finance.yahoo.com/v1/finance/search?q={urllib.parse.quote(query)}&quotesCount=8&newsCount=0"
                data = yahoo_fetch(url)
                for item in data.get("quotes", []):
                    if item.get("quoteType") in ("EQUITY", "ETF"):
                        results.append({
                            "ticker": item["symbol"],
                            "name": item.get("shortname", item.get("longname", item["symbol"]))
                        })
            except:
                pass
        body = json.dumps(results).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)
