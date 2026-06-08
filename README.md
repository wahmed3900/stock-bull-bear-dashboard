# 30-Day Stock Bull/Bear Prediction Dashboard

A real-time Flask dashboard that predicts whether selected stocks will be bullish or bearish over the next 30 days using 30-day momentum and moving average analysis.

## 🚀 Features

- Real-time stock analysis using Yahoo Finance
- 30-day momentum comparison and 30-day moving average
- Color-coded bullish/bearish signals
- Estimated 30-day price prediction
- Auto-refresh every 15 seconds
- Responsive dashboard UI for desktop and mobile

## 📊 Stock Coverage

- AAPL (Apple)
- MSFT (Microsoft)
- GOOGL (Google)
- NVDA (NVIDIA)
- TSLA (Tesla)
- META (Meta)
- AMZN (Amazon)
- JPM (JPMorgan)
- JNJ (Johnson & Johnson)
- WMT (Walmart)

## 🛠️ Tech Stack

- Backend: Python, Flask
- Data Source: yFinance API
- Data Processing: Pandas
- Frontend: HTML, CSS, JavaScript

## 📦 Installation

```bash
cd "c:\Users\waqas\Documents\30 day stock trend website guide"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## ▶️ Run the Dashboard

```bash
python live_server.py
```

Then open `http://localhost:5000` in your browser.

## 📁 Files

- `live_server.py` - main Flask dashboard application
- `app.py` - simple stock dashboard example
- `live_stock_dashboard.py` - alternate dashboard implementation

## 💡 Notes

- If you run into a `yfinance` or `pandas` import error, make sure your virtual environment is activated.
- The dashboard fetches up to 120 days of historical price data to compute momentum and moving averages.
