import threading

# -----------------------------
# Zerodha WebSocket (KiteTicker)
# -----------------------------
def start_zerodha_ws(api_key, access_token, instrument_token, callback):
    from kiteconnect import KiteTicker

    kws = KiteTicker(api_key, access_token)

    def on_ticks(ws, ticks):
        for tick in ticks:
            callback({
                "symbol": tick.get("instrument_token"),
                "ltp": tick.get("last_price"),
                "volume": tick.get("volume_traded"),
                "timestamp": tick.get("timestamp")
            })

    def on_connect(ws, response):
        ws.subscribe([instrument_token])

    def on_error(ws, code, reason):
        print("Zerodha WebSocket Error:", reason)

    kws.on_ticks = on_ticks
    kws.on_connect = on_connect
    kws.on_error = on_error

    thread = threading.Thread(target=kws.connect, daemon=True)
    thread.start()


# -----------------------------
# Dhan WebSocket
# -----------------------------
def start_dhan_ws(access_token, client_id, instrument, callback):
    import websocket
    import json

    def on_message(ws, message):
        data = json.loads(message)
        callback({
            "symbol": data.get("securityId"),
            "ltp": data.get("lastTradedPrice"),
            "volume": data.get("volume"),
            "timestamp": data.get("lastTradedTime")
        })

    def on_open(ws):
        subscribe_msg = {
            "correlationID": "abc123",
            "action": "subscribe",
            "params": {
                "mode": "FULL",
                "instruments": [instrument]
            }
        }
        ws.send(json.dumps(subscribe_msg))

    url = "wss://streamapi.dhan.co/quotes"
    headers = {
        "access-token": access_token,
        "client-id": client_id
    }

    ws = websocket.WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
        header=headers
    )

    thread = threading.Thread(target=ws.run_forever, daemon=True)
    thread.start()


# -----------------------------
# Upstox WebSocket
# -----------------------------
def start_upstox_ws(access_token, instrument_keys, callback):
    import websocket
    import json

    def on_message(ws, message):
        data = json.loads(message)
        for token in instrument_keys:
            if token in data.get("data", {}):
                tick = data["data"][token]
                callback({
                    "symbol": token,
                    "ltp": tick.get("ltp"),
                    "volume": tick.get("volume"),
                    "timestamp": tick.get("last_traded_time")
                })

    def on_open(ws):
        subscribe_message = {
            "guid": "abc123",
            "method": "sub",
            "data": {
                "mode": "full",
                "instrumentKeys": instrument_keys
            }
        }
        ws.send(json.dumps(subscribe_message))

    ws = websocket.WebSocketApp(
        "wss://api.upstox.com/v2/feed/market-data",
        on_open=on_open,
        on_message=on_message,
        header={"Authorization": f"Bearer {access_token}"}
    )

    thread = threading.Thread(target=ws.run_forever, daemon=True)
    thread.start()