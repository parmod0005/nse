import streamlit as st
from option_order import place_option_order

def broker_login_ui():
    broker_choice = st.selectbox("Select Broker", ["None", "Upstox", "Dhan", "Zerodha"])
    api_key = st.text_input("API Key")
    api_secret = st.text_input("API Secret", type="password")
    access_token = st.text_input("Access Token", help="Leave empty if using request_token (Zerodha only)")

    if broker_choice == "Zerodha":
        request_token = st.text_input("Zerodha Request Token")
        if st.button("Connect Zerodha"):
            from broker import ZerodhaBroker
            zb = ZerodhaBroker(api_key, api_secret)
            if request_token:
                access_token = zb.generate_session(request_token)
                st.success(f"Access Token: {access_token}")
                return zb
            else:
                st.warning("Enter request token after login from Zerodha login URL.")
        return None

    elif st.button("Connect"):
        if broker_choice == "Upstox":
            from broker import UpstoxBroker
            return UpstoxBroker(api_key, api_secret, access_token)
        elif broker_choice == "Dhan":
            from broker import DhanBroker
            return DhanBroker(api_key, access_token)
        else:
            st.warning("Select a valid broker.")
    return None

def signal_display_ui(signal):
    if signal == "BUY":
        st.markdown("### ✅ BUY Signal", unsafe_allow_html=True)
    elif signal == "SELL":
        st.markdown("### ❌ SELL Signal", unsafe_allow_html=True)
    else:
        st.markdown("### ⚠️ WAIT / NO TRADE")

def option_order_form(broker):
    st.sidebar.header("🛒 Option Trade")
    symbol = st.sidebar.selectbox("Symbol", ["NIFTY", "BANKNIFTY"])
    expiry = st.sidebar.text_input("Expiry (e.g. 25JUL)", value="25JUL")
    strike = st.sidebar.number_input("Strike Price", value=19700, step=50)
    option_type = st.sidebar.selectbox("Option Type", ["CE", "PE"])
    qty = st.sidebar.number_input("Quantity", value=50, step=25)
    sl_points = st.sidebar.number_input("Stop Loss (pts)", value=15)
    target_points = st.sidebar.number_input("Target (pts)", value=30)
    direction = st.sidebar.selectbox("Direction", ["BUY", "SELL"])

    if st.sidebar.button("🚀 Place Option Order"):
        from option_order import place_option_order
        response = place_option_order(broker, symbol, strike, option_type, expiry, qty, sl_points, target_points, direction)
        st.sidebar.success(f"Order Response: {response}")
        start_monitoring_exit(broker, response)

# Simulated SL/Target exit monitor (would use WebSocket LTP in full deployment)
import threading
import time

def start_monitoring_exit(broker, order_info):
    def monitor():
        symbol = order_info.get("symbol")
        entry_price = 100  # Assume dummy entry
        sl = order_info["sl"]
        target = order_info["target"]
        direction = "BUY" if "CE" in symbol else "SELL"
        while True:
            try:
                ltp = broker.get_positions()[0]["ltp"] if hasattr(broker, "get_positions") else entry_price
                if direction == "BUY":
                    if ltp >= entry_price + target:
                        st.sidebar.info("🎯 Target Hit. Exiting trade.")
                        break
                    elif ltp <= entry_price - sl:
                        st.sidebar.warning("🛑 SL Hit. Exiting trade.")
                        break
                else:
                    if ltp <= entry_price - target:
                        st.sidebar.info("🎯 Target Hit. Exiting trade.")
                        break
                    elif ltp >= entry_price + sl:
                        st.sidebar.warning("🛑 SL Hit. Exiting trade.")
                        break
            except Exception:
                pass
            time.sleep(5)

    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()