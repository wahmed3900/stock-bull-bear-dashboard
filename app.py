from flask import Flask, jsonify, render_template_string
import yfinance as yf
import requests
from datetime import datetime, timedelta

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
        .joke-section { background: #0f3460; padding: 20px; margin: 20px 0; border-radius: 10px; border: 2px solid #e94560; }
        .joke-section h2 { color: #e94560; margin-top: 0; }
        .joke-text { font-size: 18px; line-height: 1.6; margin: 15px 0; font-style: italic; }
        .joke-punchline { color: #0f0; font-weight: bold; margin-top: 10px; }
        button { background: #e94560; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 5px; }
        button:hover { background: #ff6b9d; }
    </style>
</head>
<body>
    <h1>📈 30-Day Stock Bull/Bear Dashboard</h1>
    <button onclick="loadData()">Refresh Stocks</button>
    <div id="stocks">Loading...</div>
    
    <div class="joke-section">
        <h2>😂 Random Joke Generator</h2>
        <div class="joke-text" id="joke">Loading joke...</div>
        <button onclick="loadJoke()">Get Another Joke!</button>
    </div>
    
    <script>
        async function loadData() {
            try {
                const response = await fetch('/api/stocks');
                if (!response.ok) throw new Error('Failed to fetch stocks');
                const data = await response.json();
                const container = document.getElementById('stocks');
                
                // Build HTML as a string first (better performance)
                const html = data.map(stock => `
                    <div class="card">
                        <h2>${stock.ticker}</h2>
                        <div class="price">$${stock.price}</div>
                        <div class="${stock.momentum >= 0 ? 'bullish' : 'bearish'}">
                            ${stock.momentum >= 0 ? '+' : ''}${stock.momentum}%
                        </div>
                        <div>Prediction: $${stock.predicted}</div>
                        <div><b>${stock.signal}</b></div>
                    </div>
                `).join('');
                
                container.innerHTML = html;
            } catch (error) {
                document.getElementById('stocks').innerHTML = 
                    `<div style="color: #f00;">Error loading stocks: ${error.message}</div>`;
            }
        }
        
        async function loadJoke() {
            try {
                const jokeContainer = document.getElementById('joke');
                jokeContainer.textContent = 'Loading joke...';
                
                const response = await fetch('/api/joke');
                if (!response.ok) throw new Error('Failed to fetch joke');
                const data = await response.json();
                
                if (data.type === 'single') {
                    jokeContainer.innerHTML = `<div class="joke-text">${data.joke}</div>`;
                } else {
                    jokeContainer.innerHTML = `
                        <div class="joke-text">${data.setup}</div>
                        <div class="joke-punchline">${data.delivery}</div>
                    `;
                }
            } catch (error) {
                document.getElementById('joke').innerHTML = 
                    `<div style="color: #f00;">Error loading joke: ${error.message}</div>`;
            }
        }
        
        loadData();
        loadJoke();
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
            
            if len(df) >= 30:
                current = df['Close'].iloc[-1]
                old = df['Close'].iloc[-30]
                momentum = ((current - old) / old) * 100
                predicted = current * (1 + momentum / 100)
                
                results.append({
                    'ticker': ticker,
                    'price': round(float(current), 2),
                    'momentum': round(float(momentum), 2),
                    'predicted': round(float(predicted), 2),
                    'signal': '🟢 BULLISH' if momentum > 0 else '🔴 BEARISH'
                })
        except Exception as e:
            print(f"Error with {ticker}: {e}")
    
    results.sort(key=lambda x: x['momentum'], reverse=True)
    return jsonify(results)

@app.route('/api/joke')
def get_joke():
    """
    Fetch a random joke from JokeAPI
    API Docs: https://jokeapi.dev/
    """
    try:
        # JokeAPI endpoint - returns random jokes
        response = requests.get(
            'https://v2.jokeapi.dev/joke/Any',
            params={'format': 'json'},
            timeout=5
        )
        response.raise_for_status()
        
        joke_data = response.json()
        
        # Handle error responses from the API
        if joke_data.get('error'):
            return jsonify({
                'type': 'single',
                'joke': '😅 Could not fetch a joke right now. Try again later!'
            }), 200
        
        # Return the joke data
        return jsonify(joke_data), 200
        
    except requests.exceptions.Timeout:
        return jsonify({
            'type': 'single',
            'joke': '⏱️ Joke API timed out. Please try again!'
        }), 200
    except requests.exceptions.RequestException as e:
        print(f"Error fetching joke: {e}")
        return jsonify({
            'type': 'single',
            'joke': '🚨 Error connecting to joke service. Check your internet connection!'
        }), 200

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Stock Dashboard Starting...")
    print("="*50)
    print("\n✅ Server running at: http://localhost:5000")
    print("📌 Open this URL in your browser")
    print("="*50 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000)
