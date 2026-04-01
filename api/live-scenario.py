from http.server import BaseHTTPRequestHandler
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta


def get_et_now():
    utc_now = datetime.now(timezone.utc)
    year = utc_now.year
    mar1 = datetime(year, 3, 1, tzinfo=timezone.utc)
    dst_start = mar1 + timedelta(days=(6 - mar1.weekday()) % 7 + 7)
    dst_start = dst_start.replace(hour=7)
    nov1 = datetime(year, 11, 1, tzinfo=timezone.utc)
    dst_end = nov1 + timedelta(days=(6 - nov1.weekday()) % 7)
    dst_end = dst_end.replace(hour=6)
    if dst_start <= utc_now < dst_end:
        return utc_now + timedelta(hours=-4), "EDT"
    else:
        return utc_now + timedelta(hours=-5), "EST"


def is_market_open():
    et_now, tz_name = get_et_now()
    if et_now.weekday() >= 5:
        return False, "closed_weekend", et_now, tz_name
    market_open = et_now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = et_now.replace(hour=16, minute=0, second=0, microsecond=0)
    if et_now < market_open:
        return False, "closed_premarket", et_now, tz_name
    if et_now >= market_close:
        return False, "closed_afterhours", et_now, tz_name
    return True, "open", et_now, tz_name


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


def yahoo_fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def fetch_intraday(ticker, interval="5m", range_str="5d"):
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


def build_live_scenario(ticker):
    market_open, market_status, et_now, tz_name = is_market_open()
    try:
        intraday = fetch_intraday(ticker)
    except Exception as e:
        return {"error": f"Could not fetch data for {ticker}. ({e})"}
    if not intraday or len(intraday) < 30:
        return {"error": f"Not enough intraday data for {ticker}."}
    try:
        daily = fetch_daily(ticker)
    except:
        daily = []
    daily_closes = [c["c"] for c in daily]
    daily_sma50 = compute_sma(daily_closes, 50) if len(daily_closes) >= 50 else []
    daily_sma200 = compute_sma(daily_closes, 200) if len(daily_closes) >= 200 else []
    sma50_val = daily_sma50[-1] if daily_sma50 and daily_sma50[-1] is not None else None
    sma200_val = daily_sma200[-1] if daily_sma200 and daily_sma200[-1] is not None else None
    candle_offset = 12
    result_idx = len(intraday) - 1
    if not market_open:
        candle_offset = min(candle_offset, max(9, len(intraday) // 4))
    scenario_end_idx = len(intraday) - 1 - candle_offset
    if scenario_end_idx < 20:
        return {"error": f"Not enough candles for {ticker}."}
    scenario_candles = intraday[:scenario_end_idx + 1]
    scenario_price = scenario_candles[-1]["c"]
    result_price = intraday[result_idx]["c"]
    price_change = result_price - scenario_price
    pct_change = (price_change / scenario_price) * 100
    went_up = result_price > scenario_price
    intra_closes = [c["c"] for c in scenario_candles]
    rsi_values = compute_rsi(intra_closes, 14)
    rsi_val = rsi_values[-1] if rsi_values and rsi_values[-1] is not None else None
    macd_data = compute_macd(intra_closes)
    indicators = describe_indicators(intra_closes, rsi_val, macd_data, sma50_val, sma200_val, scenario_price)
    display_start = max(0, len(scenario_candles) - 60)
    display_candles = scenario_candles[display_start:]
    intra_sma20 = compute_sma(intra_closes, 20)
    intra_sma50 = compute_sma(intra_closes, 50)
    display_sma20 = intra_sma20[display_start:scenario_end_idx + 1]
    display_sma50 = intra_sma50[display_start:scenario_end_idx + 1]
    display_rsi = rsi_values[display_start:scenario_end_idx + 1]
    display_macd = {
        "macdLine": macd_data["macdLine"][display_start:scenario_end_idx + 1],
        "signalLine": macd_data["signalLine"][display_start:scenario_end_idx + 1],
        "histogram": macd_data["histogram"][display_start:scenario_end_idx + 1],
    }
    et_offset = timedelta(hours=-4) if tz_name == "EDT" else timedelta(hours=-5)
    scenario_ts = scenario_candles[-1]["t"]
    result_ts = intraday[result_idx]["t"]
    scenario_dt = datetime.fromtimestamp(scenario_ts, tz=timezone.utc) + et_offset
    result_dt = datetime.fromtimestamp(result_ts, tz=timezone.utc) + et_offset
    scenario_time = scenario_dt.strftime("%I:%M %p") + f" {tz_name}"
    result_time = result_dt.strftime("%I:%M %p") + f" {tz_name}"
    scenario_date = scenario_dt.strftime("%b %d, %Y")
    time_gap_min = round((result_ts - scenario_ts) / 60)
    market_info = {"isOpen": market_open, "status": market_status, "timezone": tz_name}
    if not market_open:
        if market_status == "closed_weekend":
            market_info["message"] = "Market is closed (weekend). Using last trading session data."
        elif market_status == "closed_premarket":
            market_info["message"] = f"Market opens at 9:30 AM {tz_name}. Using last trading session data."
        elif market_status == "closed_afterhours":
            market_info["message"] = f"Market closed at 4:00 PM {tz_name}. Using today's trading data."
    return {
        "ticker": ticker.upper(), "scenarioPrice": scenario_price, "resultPrice": result_price,
        "priceChange": round(price_change, 2), "pctChange": round(pct_change, 2),
        "correctAnswer": "up" if went_up else "down",
        "scenarioTime": scenario_time, "resultTime": result_time, "scenarioDate": scenario_date,
        "timeGapMin": time_gap_min, "indicators": indicators,
        "dailySma50": sma50_val, "dailySma200": sma200_val,
        "displayCandles": display_candles, "sma20": display_sma20, "sma50": display_sma50,
        "rsi": display_rsi, "macd": display_macd, "marketInfo": market_info,
    }


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        ticker = params.get("ticker", ["SPY"])[0]
        result = build_live_scenario(ticker)
        body = json.dumps(result).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)
