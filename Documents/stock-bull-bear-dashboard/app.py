from flask import Flask, jsonify, render_template_string
import yfinance as yf
import time

app = Flask(__name__)

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
    </style>
</head>
<body>
    <h1>📈 30-Day Stock Bull/Bear Dashboard</h1>
    <button onclick="loadData()">Refresh</button>
    <div id="stocks">Loading...</div>
    
    <script>
        async function loadData() {
            const response = await fetch('/api/stocks');
            const data = await response.json();
            const container = document.getElementById('stocks');
            container.innerHTML = '';
            
            data.forEach(stock => {
                container.innerHTML += `
                    <div class="card">
                        <h2>${stock.ticker}</h2>
                        <div class="price">$${stock.price}</div>
                        <div class="${stock.momentum >= 0 ? 'bullish' : 'bearish'}">
                            ${stock.momentum >= 0 ? '+' : ''}${stock.momentum}%
                        </div>
                        <div>Prediction: $${stock.predicted}</div>
                        <div><b>${stock.signal}</b></div>
                    </div>
                `;
            });
        }
        loadData();
        setInterval(loadData, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/api/stocks')
def get_stocks():
    stocks = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA', 'META']
    results = []
    
    for ticker in stocks:
        try:
            df = yf.download(ticker, period='60d', progress=False)
            
            if df is not None and len(df) >= 30:
                current_series = df['Close'].iloc[-1]
                old_series = df['Close'].iloc[-30]
                
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
            
            time.sleep(0.5)
        except Exception as e:
            print(f"Error with {ticker}: {e}")
    
    if not results:
        return jsonify([{'ticker': 'Error', 'price': 0, 'momentum': 0, 'predicted': 0, 'signal': 'Unable to load data'}])
    
    results.sort(key=lambda x: x['momentum'], reverse=True)
    return jsonify(results)

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Stock Dashboard Starting...")
    print("="*50)
    print("\n✅ Server running at: http://localhost:5000")
    print("📌 Open this URL in your browser")
    print("="*50 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000)