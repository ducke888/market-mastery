#!/usr/bin/env python3
"""
Market Mastery Live Challenge Backend Server.

Uses Yahoo Finance for intraday candles (free, no API key needed)
and Finnhub for real-time quotes.

HOW THE TIMING WORKS:
=====================
Yahoo Finance provides 5-minute candles with ~15 min delay.
We use a 3-candle offset (15 min) to create the prediction window:

  Example at 3:15 PM real time:
  - Yahoo gives candles through ~3:00 PM (15 min delay)
  - We show user candles ending at 2:45 PM (the "scenario")
  - User predicts: "Will this stock go UP or DOWN?"
  - We instantly reveal: price at 3:00 PM (the "result")
  - The 2:45 -> 3:00 move is the answer

So the user is predicting a 15-minute move that ALREADY HAPPENED
but they don't know about yet. Instant feedback!

ENDPOINTS:
  GET /api/live-scenario?ticker=AAPL  - Full live scenario with chart data
  GET /api/popular-stocks             - List of popular tickers
  GET /api/search?q=apple             - Search for a stock
"""

import json
import urllib.request
import urllib.parse
import time
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from datetime import datetime, timezone, timedelta

FINNHUB_API_KEY = "d75vs9pr01qm4b7sd5agd75vs9pr01qm4b7sd5b0"

# US Eastern timezone offset (handles EST/EDT)
def get_et_now():
    """Get current time in US Eastern. Simple DST logic for US."""
    utc_now = datetime.now(timezone.utc)
    # US Eastern: UTC-5 (EST) or UTC-4 (EDT)
    # EDT: 2nd Sunday of March to 1st Sunday of November
    year = utc_now.year
    # 2nd Sunday of March
    mar1 = datetime(year, 3, 1, tzinfo=timezone.utc)
    dst_start = mar1 + timedelta(days=(6 - mar1.weekday()) % 7 + 7)  # 2nd Sunday
    dst_start = dst_start.replace(hour=7)  # 2am ET = 7am UTC
    # 1st Sunday of November
    nov1 = datetime(year, 11, 1, tzinfo=timezone.utc)
    dst_end = nov1 + timedelta(days=(6 - nov1.weekday()) % 7)  # 1st Sunday
    dst_end = dst_end.replace(hour=6)  # 2am ET = 6am UTC
    if dst_start <= utc_now < dst_end:
        return utc_now + timedelta(hours=-4), "EDT"
    else:
        return utc_now + timedelta(hours=-5), "EST"

def is_market_open():
    """Check if US stock market is currently open (9:30 AM - 4:00 PM ET, weekdays)."""
    et_now, tz_name = get_et_now()
    # Weekend check
    if et_now.weekday() >= 5:  # Saturday=5, Sunday=6
        return False, "closed_weekend", et_now, tz_name
    # Time check
    market_open = et_now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = et_now.replace(hour=16, minute=0, second=0, microsecond=0)
    if et_now < market_open:
        return False, "closed_premarket", et_now, tz_name
    if et_now >= market_close:
        return False, "closed_afterhours", et_now, tz_name
    return True, "open", et_now, tz_name

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


# ===== Technical Indicator Calculations =====

def compute_sma(closes, period):
    result = []
    for i in range(len(closes)):
        if i < period - 1:
            result.append(None)
        else:
            result.append(sum(closes[i - period + 1:i + 1]) / period)
    return result


def compute_rsi(closes, period=14):
    if len(closes) < period + 1:
        return [None] * len(closes)
    deltas = [closes[i] - closes[i-1] for i in range(1, len(closes))]
    gains = [max(d, 0) for d in deltas]
    losses = [abs(min(d, 0)) for d in deltas]
    result = [None] * period
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    if avg_loss == 0:
        result.append(100)
    else:
        result.append(100 - (100 / (1 + avg_gain / avg_loss)))
    for i in range(period, len(deltas)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        if avg_loss == 0:
            result.append(100)
        else:
            result.append(100 - (100 / (1 + avg_gain / avg_loss)))
    return result


def compute_ema(closes, period):
    if len(closes) < period:
        return [None] * len(closes)
    result = [None] * (period - 1)
    result.append(sum(closes[:period]) / period)
    mult = 2 / (period + 1)
    for i in range(period, len(closes)):
        result.append((closes[i] - result[-1]) * mult + result[-1])
    return result


def compute_macd(closes, fast=12, slow=26, signal=9):
    ema_fast = compute_ema(closes, fast)
    ema_slow = compute_ema(closes, slow)
    macd_line = []
    for i in range(len(closes)):
        if ema_fast[i] is not None and ema_slow[i] is not None:
            macd_line.append(ema_fast[i] - ema_slow[i])
        else:
            macd_line.append(None)
    valid_macd = [v for v in macd_line if v is not None]
    signal_line = [None] * len(closes)
    histogram = [None] * len(closes)
    if len(valid_macd) >= signal:
        first_valid = next(i for i, v in enumerate(macd_line) if v is not None)
        sma_start = sum(valid_macd[:signal]) / signal
        sig_idx = first_valid + signal - 1
        signal_line[sig_idx] = sma_start
        mult = 2 / (signal + 1)
        for i in range(sig_idx + 1, len(closes)):
            if macd_line[i] is not None and signal_line[i-1] is not None:
                signal_line[i] = (macd_line[i] - signal_line[i-1]) * mult + signal_line[i-1]
    for i in range(len(closes)):
        if macd_line[i] is not None and signal_line[i] is not None:
            histogram[i] = macd_line[i] - signal_line[i]
    return {"macdLine": macd_line, "signalLine": signal_line, "histogram": histogram}


def describe_indicators(closes, rsi_val, macd_data, sma50_val, sma200_val, price):
    indicators = {}
    if rsi_val is not None:
        rv = round(rsi_val, 1)
        if rsi_val > 70:
            indicators["rsi"] = {"value": rv, "label": "RSI (14)", "signal": "overbought", "desc": f"RSI at {rv}: overbought territory, above 70"}
        elif rsi_val < 30:
            indicators["rsi"] = {"value": rv, "label": "RSI (14)", "signal": "oversold", "desc": f"RSI at {rv}: oversold territory, below 30"}
        elif rsi_val > 50:
            indicators["rsi"] = {"value": rv, "label": "RSI (14)", "signal": "bullish", "desc": f"RSI at {rv}: bullish momentum, above 50"}
        else:
            indicators["rsi"] = {"value": rv, "label": "RSI (14)", "signal": "bearish", "desc": f"RSI at {rv}: bearish momentum, below 50"}

    ml = macd_data["macdLine"][-1]
    sl = macd_data["signalLine"][-1]
    if ml is not None and sl is not None:
        if ml > sl:
            indicators["macd"] = {"value": round(ml, 3), "label": "MACD (12,26,9)", "signal": "bullish", "desc": "MACD above signal line: bullish momentum"}
        else:
            indicators["macd"] = {"value": round(ml, 3), "label": "MACD (12,26,9)", "signal": "bearish", "desc": "MACD below signal line: bearish momentum"}

    if sma50_val and sma200_val:
        if sma50_val > sma200_val and price > sma50_val:
            indicators["sma"] = {"sma50": round(sma50_val, 2), "sma200": round(sma200_val, 2), "label": "50 & 200 SMA", "signal": "bullish", "desc": "Price above both SMAs, uptrend intact"}
        elif sma50_val < sma200_val and price < sma50_val:
            indicators["sma"] = {"sma50": round(sma50_val, 2), "sma200": round(sma200_val, 2), "label": "50 & 200 SMA", "signal": "bearish", "desc": "Price below both SMAs, downtrend intact"}
        elif price > sma200_val:
            indicators["sma"] = {"sma50": round(sma50_val, 2), "sma200": round(sma200_val, 2), "label": "50 & 200 SMA", "signal": "neutral-bullish", "desc": "Price above 200-SMA, long-term support holding"}
        else:
            indicators["sma"] = {"sma50": round(sma50_val, 2), "sma200": round(sma200_val, 2), "label": "50 & 200 SMA", "signal": "neutral-bearish", "desc": "Price below 200-SMA, long-term trend weakening"}
    return indicators


# ===== Yahoo Finance Data Fetching =====

def yahoo_fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def fetch_intraday(ticker, interval="5m", range_str="5d"):
    """Fetch intraday candles from Yahoo Finance."""
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(ticker)}?interval={interval}&range={range_str}"
    data = yahoo_fetch(url)
    result = data["chart"]["result"][0]
    ts = result["timestamp"]
    q = result["indicators"]["quote"][0]
    candles = []
    for i in range(len(ts)):
        o, h, l, c, v = q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i]
        if o is None or h is None or l is None or c is None:
            continue
        candles.append({"t": ts[i], "o": round(o, 2), "h": round(h, 2), "l": round(l, 2), "c": round(c, 2), "v": v or 0})
    return candles


def fetch_daily(ticker):
    """Fetch daily candles for SMA calculation (1 year)."""
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(ticker)}?interval=1d&range=1y"
    data = yahoo_fetch(url)
    result = data["chart"]["result"][0]
    ts = result["timestamp"]
    q = result["indicators"]["quote"][0]
    candles = []
    for i in range(len(ts)):
        o, h, l, c, v = q["open"][i], q["high"][i], q["low"][i], q["close"][i], q["volume"][i]
        if o is None or c is None:
            continue
        candles.append({"t": ts[i], "o": round(o, 2), "h": round(h or o, 2), "l": round(l or o, 2), "c": round(c, 2), "v": v or 0})
    return candles


def search_yahoo(query):
    """Search Yahoo Finance for tickers."""
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={urllib.parse.quote(query)}&quotesCount=8&newsCount=0"
    data = yahoo_fetch(url)
    results = []
    for item in data.get("quotes", []):
        if item.get("quoteType") in ("EQUITY", "ETF"):
            results.append({"ticker": item["symbol"], "name": item.get("shortname", item.get("longname", item["symbol"]))})
    return results


def build_live_scenario(ticker):
    """
    Build a live scenario for the given ticker.

    TIMING LOGIC (corrected):
    =========================
    Yahoo Finance provides 5-minute candles with ~15 min delay.
    We want to show the chart from 1 HOUR before real time, then reveal
    the most recent candle Yahoo has (which is ~15 min delayed).

    Example at 1:00 PM real time (ET):
    - Yahoo has data through ~12:45 PM (15 min delay)
    - We show user chart ending at ~12:00 PM (1 hour before real time)
    - That means we hide the last ~9 candles (45 min / 5 min each)
    - User predicts: UP or DOWN?
    - We reveal: most recent Yahoo price (~12:45 PM)
    - The move from 12:00 PM -> 12:45 PM is the answer

    MARKET CLOSED:
    When market is closed, we use the last available trading session data.
    The timing still works - we just note that data is from the last session.

    For indicators:
    - RSI(14) computed on 5-min candles (intraday momentum)
    - MACD(12,26,9) computed on 5-min candles
    - SMA(50,200) computed on DAILY candles (real support/resistance)
    """
    # Check market status
    market_open, market_status, et_now, tz_name = is_market_open()

    try:
        intraday = fetch_intraday(ticker)
    except Exception as e:
        return {"error": f"Could not fetch data for {ticker}. Market may be closed or ticker invalid. ({e})"}

    if not intraday or len(intraday) < 30:
        return {"error": f"Not enough intraday data for {ticker}. Market may be closed."}

    # Fetch daily data for SMA
    try:
        daily = fetch_daily(ticker)
    except:
        daily = []

    daily_closes = [c["c"] for c in daily]
    daily_sma50 = compute_sma(daily_closes, 50) if len(daily_closes) >= 50 else []
    daily_sma200 = compute_sma(daily_closes, 200) if len(daily_closes) >= 200 else []

    sma50_val = daily_sma50[-1] if daily_sma50 and daily_sma50[-1] is not None else None
    sma200_val = daily_sma200[-1] if daily_sma200 and daily_sma200[-1] is not None else None

    # TIMING: Find the right split point
    # We want scenario to end ~1 hour before real time
    # With 5-min candles, that's ~12 candles from the end
    # But we need at least a few candles gap for the result
    # Use 12 candle offset (1 hour), result = last candle Yahoo has
    candle_offset = 12  # 12 * 5min = 60min = 1 hour back from Yahoo's latest
    result_idx = len(intraday) - 1  # Most recent candle Yahoo has

    # If market is closed, we have fewer fresh candles, use smaller offset
    # but still ensure meaningful gap
    if not market_open:
        # Use at least 9 candle gap (45 min) for closed market
        candle_offset = min(candle_offset, max(9, len(intraday) // 4))

    scenario_end_idx = len(intraday) - 1 - candle_offset

    if scenario_end_idx < 20:
        return {"error": f"Not enough candles for {ticker}. Need more trading data."}

    scenario_candles = intraday[:scenario_end_idx + 1]
    scenario_price = scenario_candles[-1]["c"]
    result_price = intraday[result_idx]["c"]

    price_change = result_price - scenario_price
    pct_change = (price_change / scenario_price) * 100
    went_up = result_price > scenario_price

    # Compute indicators on intraday scenario candles
    intra_closes = [c["c"] for c in scenario_candles]
    rsi_values = compute_rsi(intra_closes, 14)
    rsi_val = rsi_values[-1] if rsi_values and rsi_values[-1] is not None else None

    macd_data = compute_macd(intra_closes)

    indicators = describe_indicators(intra_closes, rsi_val, macd_data, sma50_val, sma200_val, scenario_price)

    # Display candles for chart (last 60 of scenario)
    display_start = max(0, len(scenario_candles) - 60)
    display_candles = scenario_candles[display_start:]

    # Intraday SMA for chart (shorter periods for 5-min candles)
    intra_sma20 = compute_sma(intra_closes, 20)
    intra_sma50 = compute_sma(intra_closes, 50)
    display_sma20 = intra_sma20[display_start:scenario_end_idx + 1]
    display_sma50 = intra_sma50[display_start:scenario_end_idx + 1]

    # RSI for chart
    display_rsi = rsi_values[display_start:scenario_end_idx + 1]

    # MACD for chart
    display_macd = {
        "macdLine": macd_data["macdLine"][display_start:scenario_end_idx + 1],
        "signalLine": macd_data["signalLine"][display_start:scenario_end_idx + 1],
        "histogram": macd_data["histogram"][display_start:scenario_end_idx + 1],
    }

    # Format times in ET
    # Convert Unix timestamps to ET-aware times
    et_offset = timedelta(hours=-4) if tz_name == "EDT" else timedelta(hours=-5)
    scenario_ts = scenario_candles[-1]["t"]
    result_ts = intraday[result_idx]["t"]
    scenario_dt = datetime.fromtimestamp(scenario_ts, tz=timezone.utc) + et_offset
    result_dt = datetime.fromtimestamp(result_ts, tz=timezone.utc) + et_offset

    scenario_time = scenario_dt.strftime("%I:%M %p") + f" {tz_name}"
    result_time = result_dt.strftime("%I:%M %p") + f" {tz_name}"
    scenario_date = scenario_dt.strftime("%b %d, %Y")

    # Time gap in minutes between scenario and result
    time_gap_min = round((result_ts - scenario_ts) / 60)

    # Market status info
    market_info = {"isOpen": market_open, "status": market_status, "timezone": tz_name}
    if not market_open:
        if market_status == "closed_weekend":
            market_info["message"] = "Market is closed (weekend). Using last trading session data."
        elif market_status == "closed_premarket":
            market_info["message"] = f"Market opens at 9:30 AM {tz_name}. Using last trading session data."
        elif market_status == "closed_afterhours":
            market_info["message"] = f"Market closed at 4:00 PM {tz_name}. Using today's trading data."

    return {
        "ticker": ticker.upper(),
        "scenarioPrice": scenario_price,
        "resultPrice": result_price,
        "priceChange": round(price_change, 2),
        "pctChange": round(pct_change, 2),
        "correctAnswer": "up" if went_up else "down",
        "scenarioTime": scenario_time,
        "resultTime": result_time,
        "scenarioDate": scenario_date,
        "timeGapMin": time_gap_min,
        "indicators": indicators,
        "dailySma50": sma50_val,
        "dailySma200": sma200_val,
        "displayCandles": display_candles,
        "sma20": display_sma20,
        "sma50": display_sma50,
        "rsi": display_rsi,
        "macd": display_macd,
        "marketInfo": market_info,
    }


# ===== NEWS =====

def format_age(ts):
    try:
        from datetime import datetime, timezone
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


def fetch_news(ticker):
    try:
        url = (
            f"https://query2.finance.yahoo.com/v1/finance/search"
            f"?q={urllib.parse.quote(ticker)}&quotesCount=0&newsCount=8&enableNavLinks=false"
        )
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        results = []
        for item in data.get("news", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "source": item.get("publisher", ""),
                "age": format_age(item.get("providerPublishTime", 0))
            })
        return results
    except Exception as e:
        return []


# ===== HTTP Server =====

class MarketMasteryHandler(SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path.startswith("/api/"):
            self.handle_api()
        else:
            super().do_GET()

    def handle_api(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)

        try:
            if path == "/api/live-scenario":
                ticker = params.get("ticker", ["SPY"])[0]
                result = build_live_scenario(ticker)
                self.send_json(result)

            elif path == "/api/popular-stocks":
                self.send_json(POPULAR_STOCKS)

            elif path == "/api/search":
                query = params.get("q", [""])[0]
                if len(query) < 1:
                    self.send_json([])
                else:
                    results = search_yahoo(query)
                    self.send_json(results)

            elif path == "/api/news":
                ticker = params.get("ticker", ["SPY"])[0]
                results = fetch_news(ticker)
                self.send_json(results)

            else:
                self.send_json({"error": "Unknown endpoint"}, 404)

        except Exception as e:
            print(f"API Error: {e}")
            import traceback
            traceback.print_exc()
            self.send_json({"error": str(e)}, 500)

    def send_json(self, data, status=200):
        response = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", len(response))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, fmt, *args):
        msg = args[0] if args else ""
        if "/api/" in msg:
            print(f"  [API] {msg}")


def main():
    port = int(os.environ.get("PORT", 3456))
    server = HTTPServer(("", port), MarketMasteryHandler)
    print(f"\n  Market Mastery Live Server")
    print(f"  http://localhost:{port}")
    print(f"\n  API Endpoints:")
    print(f"    GET /api/live-scenario?ticker=NVDA")
    print(f"    GET /api/popular-stocks")
    print(f"    GET /api/search?q=apple")
    print(f"\n  Press Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
