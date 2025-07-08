import pandas as pd
import plotly.graph_objects as go
import streamlit as st

def display_live_chart(candle_data):
    if not candle_data or "data" not in candle_data:
        st.warning("No candle data available.")
        return

    df = pd.DataFrame(candle_data["data"])
    df["datetime"] = pd.to_datetime(df["datetime"])

    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df["datetime"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Price"
    ))

    fig.update_layout(
        title=f"Live Chart: {candle_data.get('symbol', 'NSE')}",
        xaxis_title="Time",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)