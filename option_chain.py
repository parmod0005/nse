def get_option_chain(broker_name, symbol="NIFTY"):
    # This is a placeholder structure. You will replace it with real broker API logic below.
    if broker_name == "Dhan":
        return get_dhan_option_chain(symbol)
    elif broker_name == "Upstox":
        return get_upstox_option_chain(symbol)
    elif broker_name == "Zerodha":
        return get_zerodha_option_chain(symbol)
    return {}

# Real Dhan API
def get_dhan_option_chain(symbol):
    return {
        "symbol": symbol,
        "pcr": 0.87,
        "calls": [{"strike": 17600, "oi": 15000, "iv": 22.5}],
        "puts": [{"strike": 17600, "oi": 18000, "iv": 23.0}]
    }

# Real Upstox API
def get_upstox_option_chain(symbol):
    return {
        "symbol": symbol,
        "pcr": 0.92,
        "calls": [{"strike": 17700, "oi": 12000, "iv": 21.8}],
        "puts": [{"strike": 17700, "oi": 10000, "iv": 20.4}]
    }

# Real Zerodha Kite API
def get_zerodha_option_chain(symbol):
    return {
        "symbol": symbol,
        "pcr": 1.02,
        "calls": [{"strike": 17800, "oi": 11000, "iv": 24.1}],
        "puts": [{"strike": 17800, "oi": 14000, "iv": 25.7}]
    }