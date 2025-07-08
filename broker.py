import requests
import json

class BrokerHandler:
    def place_order(self, direction, symbol="NSE:RELIANCE", qty=1, order_type="MARKET"):
        raise NotImplementedError

    def get_positions(self):
        raise NotImplementedError

    def get_mtm(self):
        raise NotImplementedError

# -------------------------
# Upstox Real API Handler
# -------------------------
class UpstoxBroker(BrokerHandler):
    def __init__(self, api_key, api_secret, access_token, redirect_uri="https://example.com"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.base_url = "https://api.upstox.com/v2"

    def place_order(self, direction, symbol="NSE:RELIANCE", qty=1, order_type="MARKET"):
        side = "BUY" if direction == "BUY" else "SELL"
        url = f"{self.base_url}/order/place"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }
        payload = {
            "quantity": qty,
            "product": "I",
            "validity": "DAY",
            "price": 0,
            "tag": "evritech-bot",
            "instrument_token": symbol,
            "order_type": order_type,
            "transaction_type": side,
            "disclosed_quantity": 0,
            "trigger_price": 0
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()

    def get_positions(self):
        url = f"{self.base_url}/portfolio/positions"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        response = requests.get(url, headers=headers)
        return response.json()

    def get_mtm(self):
        data = self.get_positions()
        if "data" in data:
            mtm = sum(float(p.get("unrealized_mark_to_market", 0)) for p in data["data"])
            return mtm
        return 0

# -------------------------
# Dhan Real API Handler
# -------------------------
class DhanBroker(BrokerHandler):
    def __init__(self, client_id, access_token):
        self.client_id = client_id
        self.access_token = access_token
        self.base_url = "https://api.dhan.co"

    def place_order(self, direction, symbol="RELIANCE", qty=1, order_type="MARKET"):
        side = "BUY" if direction == "BUY" else "SELL"
        url = f"{self.base_url}/orders"
        headers = {
            "Content-Type": "application/json",
            "access-token": self.access_token,
            "client-id": self.client_id
        }
        payload = {
            "securityId": symbol,
            "quantity": qty,
            "orderType": order_type,
            "transactionType": side,
            "exchangeSegment": "NSE_EQ",
            "productType": "INTRADAY",
            "price": 0,
            "afterMarketOrder": False,
            "amoTime": "OPEN",
            "validity": "DAY"
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()

    def get_positions(self):
        url = f"{self.base_url}/positions"
        headers = {
            "access-token": self.access_token,
            "client-id": self.client_id
        }
        response = requests.get(url, headers=headers)
        return response.json()

    def get_mtm(self):
        data = self.get_positions()
        if "data" in data:
            mtm = sum(float(p.get("mtm", 0)) for p in data["data"])
            return mtm
        return 0# -------------------------
# Zerodha Kite Connect API Handler
# -------------------------
from kiteconnect import KiteConnect

class ZerodhaBroker(BrokerHandler):
    def __init__(self, api_key, api_secret, access_token=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.kite = KiteConnect(api_key=api_key)
        if access_token:
            self.kite.set_access_token(access_token)

    def generate_session(self, request_token):
        data = self.kite.generate_session(request_token, api_secret=self.api_secret)
        self.access_token = data["access_token"]
        self.kite.set_access_token(self.access_token)
        return self.access_token

    def place_order(self, direction, symbol="RELIANCE", qty=1, order_type="MARKET"):
        side = "BUY" if direction == "BUY" else "SELL"
        return self.kite.place_order(
            variety=self.kite.VARIETY_REGULAR,
            exchange=self.kite.EXCHANGE_NSE,
            tradingsymbol=symbol,
            transaction_type=side,
            quantity=qty,
            order_type=order_type,
            product=self.kite.PRODUCT_MIS
        )

    def get_positions(self):
        return self.kite.positions()

    def get_mtm(self):
        positions = self.kite.positions()
        mtm = 0
        if "day" in positions:
            for p in positions["day"]:
                mtm += p.get("pnl", 0)
        return mtm