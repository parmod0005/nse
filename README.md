# Evritech AI AutoTrading Bot (NSE/BSE)

## Features:
- Real-time technical indicator strategy (RSI, MACD, EMA)
- ML model placeholder for LSTM/XGBoost prediction
- Broker UI: Dhan & Upstox API integration
- Streamlit dashboard for live signals and trading
- Modular, extendable, and Windows executable ready

## How to Run:
```bash
pip install -r requirements.txt
streamlit run main.py
```

## To Convert into EXE:
```bash
pyinstaller --onefile --noconsole launcher.py
```