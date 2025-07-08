import streamlit as st
from ui import broker_login_ui, signal_display_ui, option_order_form
from strategy import signal_generator, get_exit_signal
from broker import BrokerHandler
from live_chart import display_live_chart
from option_chain import get_option_chain
from live_data import get_live_candles
from ws_listener import start_zerodha_ws, start_dhan_ws, start_upstox_ws
from datetime import datetime

st.set_page_config(page_title="Evritech AI AutoTrader", layout="wide")
st.title("📈 Evritech AI-Powered NSE/BSE Auto Trading Bot")

if "broker" not in st.session_state:
    st.session_state.broker = None
if "ltp" not in st.session_state:
    st.session_state.ltp = 0
if "signal" not in st.session_state:
    st.session_state.signal = "WAIT"
if "mtm" not in st.session_state:
    st.session_state.mtm = 0
if "order_ids" not in st.session_state:
    st.session_state.order_ids = {}

st.sidebar.header("🔑 Broker Login")
broker = broker_login_ui()

if broker:
    st.session_state.broker = broker
    st.sidebar.success("✅ Broker connected.")

    def on_tick(tick):
        st.session_state.ltp = tick["ltp"]
        st.session_state.signal = signal_generator("NIFTY")
        try:
            st.session_state.mtm = st.session_state.broker.get_mtm()
        except:
            st.session_state.mtm = 0

    try:
        if isinstance(broker, BrokerHandler):
            broker_name = type(broker).__name__
            if "Zerodha" in broker_name:
                start_zerodha_ws(broker.api_key, broker.access_token, 256265, on_tick)
            elif "Dhan" in broker_name:
                start_dhan_ws(broker.access_token, broker.client_id, "1330", on_tick)
            elif "Upstox" in broker_name:
                start_upstox_ws(broker.access_token, ["NSE_INDEX|Nifty 50"], on_tick)
    except Exception as e:
        st.warning(f"WebSocket error: {e}")

col1, col2, col3 = st.columns(3)
col1.metric("📊 LTP", st.session_state.ltp)
col2.metric("💸 Live MTM", st.session_state.mtm)
col3.metric("🚦 Signal", st.session_state.signal)

if st.session_state.ltp > 0 and st.session_state.signal in ["BUY", "SELL"]:
    entry_price = st.session_state.ltp - 10 if st.session_state.signal == "BUY" else st.session_state.ltp + 10
    exit_status = get_exit_signal(entry_price, st.session_state.ltp, st.session_state.signal)
    st.info(f"📉 Exit Status: {exit_status}")

st.subheader("📈 Live Candlestick Chart")
live_data = get_live_candles("Zerodha", "NIFTY")
display_live_chart(live_data)

st.subheader("📊 Option Chain Snapshot")
option_chain = get_option_chain("Zerodha", "NIFTY")
st.json(option_chain)

# Order Form
option_order_form(broker)

# Real-time Order Status UI
st.subheader("📦 Live Order Tracker")
if st.session_state.broker and hasattr(st.session_state.broker, "get_positions"):
    positions = st.session_state.broker.get_positions()
    if isinstance(positions, dict) and "data" in positions:
        st.write(positions["data"])
    elif isinstance(positions, list):
        st.write(positions)
    else:
        st.info("No active positions or order data available.")
else:
    st.warning("Broker does not support order tracking.")