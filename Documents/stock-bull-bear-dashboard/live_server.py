from flask import Flask, render_template_string, jsonify
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# List of stocks to monitor
STOCKS = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'TSLA', 'AMZN', 'JPM', 'JNJ', 'WMT']

def analyze_stock(ticker):
    """Analyze a single stock - NO TENSORFLOW NEEDED"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=120)
        
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)
        
        if df.empty or len(df) < 30:
            return None
        
        current_price = df['Close'].iloc[-1]
        ma30 = df['Close'].rolling(window=30).mean().iloc[-1]
        price_30d_ago = df['Close'].iloc[-30]
        momentum = ((current_price - price_30d_ago) / price_30d_ago) * 100
        
        # Determine signal
        if current_price > ma30 and momentum > 5:
            signal = "STRONG BULLISH"
            emoji = "🚀"
            color = "#00ff00"
        elif current_price > ma30 and momentum > 0:
            signal = "BULLISH"
            emoji = "🟢"
            color = "#90ff90"
        elif current_price < ma30 and momentum < -5:
            signal = "STRONG BEARISH"
            emoji = "💀"
            color = "#ff0000"
        elif current_price < ma30:
            signal = "BEARISH"
            emoji = "🔴"
            color = "#ff6666"
        else:
            signal = "NEUTRAL"
            emoji = "⚪"
            color = "#ffff00"
        
        predicted_price = current_price * (1 + momentum / 100)
        
        # Get company name
        try:
            info = stock.info
            name = info.get('longName', ticker)[:25]
        except:
            name = ticker
        
        return {
            'ticker': ticker,
            'name': name,
            'current_price': round(current_price, 2),
            'momentum': round(momentum, 2),
            'predicted_price': round(predicted_price, 2),
            'signal': signal,
            'emoji': emoji,
            'color': color,
            'ma30': round(ma30, 2)
        }
    except Exception as e:
        print(f"Error analyzing {ticker}: {e}")
        return None

# Beautiful HTML Dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>30-Day Stock Bull/Bear Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        h1 {
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .subtitle {
            text-align: center;
            color: #aaa;
            margin-bottom: 30px;
        }
        
        .stats {
            display: flex;
            justify-content: space-around;
            background: rgba(255,255,255,0.1);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .stat {
            text-align: center;
        }
        
        .stat-value {
            font-size: 32px;
            font-weight: bold;
        }
        
        .stat-label {
            font-size: 12px;
            color: #aaa;
        }
        
        .refresh-bar {
            text-align: right;
            color: #aaa;
            font-size: 12px;
            margin-bottom: 20px;
        }
        
        .stock-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }
        
        .card {
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            transition: transform 0.3s, box-shadow 0.3s;
            border-left: 4px solid;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .ticker {
            font-size: 24px;
            font-weight: bold;
        }
        
        .signal-badge {
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            background: rgba(0,0,0,0.5);
        }
        
        .price {
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }
        
        .momentum {
            font-size: 18px;
            margin-bottom: 15px;
        }
        
        .positive { color: #00ff00; }
        .negative { color: #ff4444; }
        
        .details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid rgba(255,255,255,0.2);
        }
        
        .detail-label {
            font-size: 11px;
            color: #aaa;
        }
        
        .detail-value {
            font-weight: bold;
        }
        
        .prediction {
            background: rgba(0,0,0,0.3);
            padding: 10px;
            border-radius: 8px;
            margin-top: 15px;
            text-align: center;
            font-size: 14px;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .updating {
            animation: pulse 1s ease-in-out;
        }
        
        @media (max-width: 768px) {
            .stock-grid { grid-template-columns: 1fr; }
            .stats { flex-direction: column; gap: 15px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📈 30-Day Stock Bull/Bear Dashboard</h1>
        <div class="subtitle">Real-time analysis based on 30-day momentum & moving averages</div>
        
        <div class="stats" id="stats">
            <div class="stat">
                <div class="stat-value" id="totalStocks">-</div>
                <div class="stat-label">Total Stocks</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="bullishCount" style="color: #00ff00">-</div>
                <div class="stat-label">Bullish</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="bearishCount" style="color: #ff4444">-</div>
                <div class="stat-label">Bearish</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="bestStock">-</div>
                <div class="stat-label">Best Performer</div>
            </div>
        </div>
        
        <div class="refresh-bar">
            Last updated: <span id="lastUpdate">--:--:--</span>
            <span id="updateIndicator"></span>
        </div>
        
        <div class="stock-grid" id="stockGrid">
            <div style="text-align: center; grid-column: 1/-1;">Loading stock data...</div>
        </div>
    </div>
    
    <script>
        async function fetchData() {
            const indicator = document.getElementById('updateIndicator');
            indicator.innerHTML = ' 🔄 Updating...';
            
            try {
                const response = await fetch('/api/stocks');
                const data = await response.json();
                updateDashboard(data);
                indicator.innerHTML = ' ✅ Live';
                setTimeout(() => { indicator.innerHTML = ''; }, 2000);
            } catch (error) {
                console.error('Error:', error);
                indicator.innerHTML = ' ❌ Error';
            }
        }
        
        function updateDashboard(data) {
            document.getElementById('totalStocks').textContent = data.total;
            document.getElementById('bullishCount').textContent = data.bullish;
            document.getElementById('bearishCount').textContent = data.bearish;
            document.getElementById('bestStock').textContent = data.best_performer;
            document.getElementById('lastUpdate').textContent = data.last_update;
            
            const grid = document.getElementById('stockGrid');
            grid.innerHTML = '';
            
            data.stocks.forEach(stock => {
                const card = document.createElement('div');
                card.className = 'card';
                card.style.borderLeftColor = stock.color;
                card.innerHTML = `
                    <div class="card-header">
                        <span class="ticker">${stock.emoji} ${stock.ticker}</span>
                        <span class="signal-badge" style="color: ${stock.color}">${stock.signal}</span>
                    </div>
                    <div class="price">$${stock.current_price}</div>
                    <div class="momentum ${stock.momentum >= 0 ? 'positive' : 'negative'}">
                        ${stock.momentum >= 0 ? '+' : ''}${stock.momentum}% (30-day momentum)
                    </div>
                    <div class="details">
                        <div>
                            <div class="detail-label">Company</div>
                            <div class="detail-value">${stock.name}</div>
                        </div>
                        <div>
                            <div class="detail-label">30-Day MA</div>
                            <div class="detail-value">$${stock.ma30}</div>
                        </div>
                    </div>
                    <div class="prediction">
                        📊 30-Day Prediction: <strong>$${stock.predicted_price}</strong>
                        ${stock.momentum >= 0 ? '↑' : '↓'} ${Math.abs(stock.momentum).toFixed(1)}%
                    </div>
                `;
                grid.appendChild(card);
            });
        }
        
        fetchData();
        setInterval(fetchData, 15000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/stocks')
def get_stocks():
    results = []
    bullish = bearish = 0
    
    for ticker in STOCKS:
        data = analyze_stock(ticker)
        if data:
            results.append(data)
            if 'BULLISH' in data['signal']:
                bullish += 1
            elif 'BEARISH' in data['signal']:
                bearish += 1
    
    # Sort by momentum (best first)
    results.sort(key=lambda x: x['momentum'], reverse=True)
    
    best = results[0] if results else None
    
    return jsonify({
        'stocks': results,
        'total': len(results),
        'bullish': bullish,
        'bearish': bearish,
        'best_performer': f"{best['ticker']} (+{best['momentum']:.1f}%)" if best else '-',
        'last_update': datetime.now().strftime('%H:%M:%S')
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 LIVE STOCK BULL/BEAR DASHBOARD")
    print("="*60)
    print("\n✅ No TensorFlow required - works with Python 3.14!")
    print("\n📊 Testing connection...")
    
    # Test one stock
    test = analyze_stock('AAPL')
    if test:
        print(f"   ✓ AAPL: {test['signal']} ({test['momentum']:+.1f}%)")
    else:
        print("   ⚠️ Please install yfinance: pip install yfinance")
    
    print("\n🌐 Starting web server...")
    print("📌 Open your browser and go to: http://localhost:5000")
    print("\n⏹️  Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000)