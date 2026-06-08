from flask import Flask, jsonify, render_template_string
from datetime import datetime, timedelta
import yfinance as yf
import time

app = Flask(__name__)

# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================
STOCK_TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA', 'META']
ANALYSIS_PERIOD_DAYS = 60
MOMENTUM_LOOKBACK_DAYS = 30
API_CALL_DELAY_SECONDS = 0.5
CACHE_DURATION_SECONDS = 60
REFRESH_INTERVAL_MS = 30000  # 30 seconds

# Cache storage
_stock_cache = {'data': None, 'timestamp': None}

# HTML template
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Stock Bull/Bear Dashboard</title>
    <style>
        body { font-family: Arial; background: #1a1a2e; color: white; padding: 20px; }
        .card { background: #16213e; padding: 15px; margin: 10px; border-radius: 10px; display: inline-block; width: 200px; }
        .bullish { color: #0f0; }
        .bearish { color: #f00; }
        .price { font-size: 24px; font-weight: bold; }
        .error-message { background: #8b0000; padding: 15px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>📈 30-Day Stock Bull/Bear Dashboard</h1>
    <button onclick="loadData()">Refresh</button>
    <div id="stocks">Loading...</div>
    
    <script>
        async function loadData() {
            try {
                const response = await fetch('/api/stocks');
                const data = await response.json();
                const container = document.getElementById('stocks');
                
                if (!data || data.length === 0) {
                    container.innerHTML = '<div class="error-message">Unable to load stock data. Try refreshing.</div>';
                    return;
                }
                
                // Use proper DOM manipulation instead of innerHTML +=
                container.innerHTML = '';
                
                data.forEach(stock => {
                    const card = document.createElement('div');
                    card.className = 'card';
                    card.innerHTML = `
                        <h2>${stock.ticker}</h2>
                        <div class="price">$${stock.price}</div>
                        <div class="${stock.momentum >= 0 ? 'bullish' : 'bearish'}">
                            ${stock.momentum >= 0 ? '+' : ''}${stock.momentum}%
                        </div>
                        <div>Prediction: $${stock.predicted}</div>
                        <div><b>${stock.signal}</b></div>
                    `;
                    container.appendChild(card);
                });
            } catch (error) {
                console.error('Error loading data:', error);
                document.getElementById('stocks').innerHTML = 
                    '<div class="error-message">⚠️ Error fetching stock data. Check console.</div>';
            }
        }
        
        loadData();
        setInterval(loadData, """ + str(REFRESH_INTERVAL_MS) + """);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api/stocks')
def get_stocks():
    """
    Fetch and analyze stock data with caching.
    Returns cached data if fresh, otherwise fetches from yfinance.
    """
    global _stock_cache
    now = datetime.now()
    
    # Return cached data if still fresh
    if (_stock_cache['data'] is not None and 
        _stock_cache['timestamp'] is not None and
        now - _stock_cache['timestamp'] < timedelta(seconds=CACHE_DURATION_SECONDS)):
        return jsonify(_stock_cache['data'])
    
    # Fetch fresh data
    results = []
    
    for ticker in STOCK_TICKERS:
        try:
            df = yf.download(ticker, period=f'{ANALYSIS_PERIOD_DAYS}d', progress=False)
            
            if df is not None and len(df) >= MOMENTUM_LOOKBACK_DAYS:
                current_series = df['Close'].iloc[-1]
                old_series = df['Close'].iloc[-MOMENTUM_LOOKBACK_DAYS]
                
                current = float(current_series.item() if hasattr(current_series, 'item') else current_series)
                old = float(old_series.item() if hasattr(old_series, 'item') else old_series)
                
                momentum = ((current - old) / old) * 100
                predicted = current * (1 + momentum / 100)
                
                results.append({
                    'ticker': ticker,
                    'price': round(current, 2),
                    'momentum': round(momentum, 2),
                    'predicted': round(predicted, 2),
                    'signal': '🟢 BULLISH' if momentum > 0 else '🔴 BEARISH'
                })
            
            time.sleep(API_CALL_DELAY_SECONDS)
        except Exception as e:
            print(f"Error with {ticker}: {e}")
    
    # Sort by momentum (highest first)
    results.sort(key=lambda x: x['momentum'], reverse=True)
    
    # Cache the results
    _stock_cache['data'] = results
    _stock_cache['timestamp'] = now
    
    return jsonify(results)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Stock Dashboard Starting...")
    print("="*50)
    print("\n✅ Server running at: http://localhost:5000")
    print("📌 Open this URL in your browser")
    print("="*50 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000)
