import time
import random

def place_option_order(broker, symbol, strike, option_type, expiry, qty, sl_points, target_points, direction="BUY"):
    # Simulated entry + SL + Target order
    base_symbol = f"{symbol}{expiry}{int(strike)}{option_type}"
    order_ids = {}

    # Entry Order
    entry = broker.place_order(direction, symbol=base_symbol, qty=qty)
    entry_id = entry.get("order_id", f"entry_{random.randint(1000,9999)}")
    order_ids["entry"] = entry_id

    # Assume LTP from positions or static (mock)
    ltp = 100  # Simulated entry price
    sl_price = ltp - sl_points if direction == "BUY" else ltp + sl_points
    tgt_price = ltp + target_points if direction == "BUY" else ltp - target_points

    # Target Order
    target_order = {
        "transaction_type": "SELL" if direction == "BUY" else "BUY",
        "order_type": "LIMIT",
        "price": tgt_price,
        "qty": qty
    }
    target = broker.place_order(target_order["transaction_type"], symbol=base_symbol, qty=qty)
    order_ids["target"] = target.get("order_id", f"tgt_{random.randint(1000,9999)}")

    # SL Order
    sl_order = {
        "transaction_type": "SELL" if direction == "BUY" else "BUY",
        "order_type": "SL-M",
        "trigger_price": sl_price,
        "qty": qty
    }
    sl = broker.place_order(sl_order["transaction_type"], symbol=base_symbol, qty=qty)
    order_ids["sl"] = sl.get("order_id", f"sl_{random.randint(1000,9999)}")

    return {
        "status": "success",
        "symbol": base_symbol,
        "entry": entry,
        "target_order": target,
        "sl_order": sl,
        "order_ids": order_ids,
        "message": "Bracket orders placed"
    }

def cancel_order(broker, order_id):
    try:
        return broker.cancel_order(order_id)
    except Exception as e:
        return {"error": str(e)}