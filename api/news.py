from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta


def yahoo_fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    })
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


def format_age(ts):
    try:
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        diff = datetime.now(timezone.utc) - dt
        h = int(diff.total_seconds() / 3600)
        if h < 1:
            return f"{int(diff.total_seconds()/60)}m ago"
        elif h < 24:
            return f"{h}h ago"
        else:
            return f"{diff.days}d ago"
    except:
        return ""


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        ticker = params.get("ticker", ["SPY"])[0]
        results = []
        try:
            url = (
                f"https://query2.finance.yahoo.com/v1/finance/search"
                f"?q={urllib.parse.quote(ticker)}&quotesCount=0&newsCount=8&enableNavLinks=false"
            )
            data = yahoo_fetch(url)
            for item in data.get("news", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "source": item.get("publisher", ""),
                    "age": format_age(item.get("providerPublishTime", 0))
                })
        except Exception as e:
            pass

        body = json.dumps(results).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)
