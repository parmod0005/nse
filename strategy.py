import yfinance as yf
import pandas as pd

trailing_sl_points = 10
target_points = 50

def signal_generator(symbol):
    df = yf.download(f"{symbol}.NS", period="5d", interval="5m")
    if df.empty:
        return "WAIT"
    df["EMA20"] = df["Close"].ewm(span=20, adjust=False).mean()
    df["RSI"] = compute_rsi(df["Close"])
    df["MACD"], df["MACD_Signal"] = compute_macd(df["Close"])

    last_row = df.iloc[-1]
    if last_row["MACD"] > last_row["MACD_Signal"] and last_row["RSI"] > 55 and last_row["Close"] > last_row["EMA20"]:
        return "BUY"
    elif last_row["MACD"] < last_row["MACD_Signal"] and last_row["RSI"] < 45 and last_row["Close"] < last_row["EMA20"]:
        return "SELL"
    else:
        return "WAIT"

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def compute_macd(series):
    exp1 = series.ewm(span=12, adjust=False).mean()
    exp2 = series.ewm(span=26, adjust=False).mean()
    macd = exp1 - exp2
    signal = macd.ewm(span=9, adjust=False).mean()
    return macd, signal

def get_exit_signal(entry_price, current_price, direction):
    if direction == "BUY":
        sl_trigger = entry_price - trailing_sl_points
        target_trigger = entry_price + target_points
        if current_price <= sl_trigger:
            return "SL HIT"
        elif current_price >= target_trigger:
            return "TARGET HIT"
    elif direction == "SELL":
        sl_trigger = entry_price + trailing_sl_points
        target_trigger = entry_price - target_points
        if current_price >= sl_trigger:
            return "SL HIT"
        elif current_price <= target_trigger:
            return "TARGET HIT"
    return "HOLD"