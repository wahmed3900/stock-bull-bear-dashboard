from flask import Flask, jsonify, render_template_string
import yfinance as yf
import time
import os
import random
import requests

app = Flask(__name__)

# Joke API function
def get_random_joke():
    try:
        # Free joke API
        response = requests.get('https://official-joke-api.appspot.com/random_joke', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return f"{data['setup']} ... {data['punchline']}"
        else:
            return "Why do programmers prefer dark mode? Because light attracts bugs!"
    except:
        return "What do you call a bear with no teeth? A gummy bear!"

# HTML template with both stocks AND jokes
HTML = """
<!DOCTYPE html>
<html>
<head>
   <title>Stock Bull/Bear Dashboard + Jokes</title>
   <style>
       body { font-family: Arial; background: #1a1a2e; color: white; padding: 20px; }
       h1 { text-align: center; color: #00d4ff; }
       .container { display: flex; gap: 20px; flex-wrap: wrap; }
       .stocks-section { flex: 2; }
       .jokes-section { flex: 1; background: #16213e; padding: 20px; border-radius: 10px; height: fit-content; }
       .card { background: #16213e; padding: 15px; margin: 10px; border-radius: 10px; display: inline-block; width: 200px; }
       .bullish { color: #0f0; font-weight: bold; }
       .bearish { color: #f00; font-weight: bold; }
       .price { font-size: 24px; font-weight: bold; }
       button { background: #00d4ff; color: #1a1a2e; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; margin: 5px; }
       button:hover { background: #00b8d4; }
       .joke-box { background: #0f3460; padding: 20px; border-radius: 10px; margin-top: 20px; }
       .joke-text { font-size: 18px; line-height: 1.5; color: #00d4ff; }
       .refresh-btn { background: #ff6b6b; }
       .refresh-btn:hover { background: #ff5252; }
       .loading { text-align: center; padding: 20px; color: #888; }
   </style>
</head>
<body>
   <h1>📈 Stock Bull/Bear Dashboard + 😂 Daily Jokes</h1>
   
   <div class="container">
       <div class="stocks-section">
           <button onclick="loadStocks()">🔄 Refresh Stocks</button>
           <div id="stocks" class="loading">Loading stocks...</div>
       </div>
       
       <div class="jokes-section">
           <h2>😂 Random Joke</h2>
           <div class="joke-box">
               <div id="joke" class="joke-text">Loading joke...</div>
               <button onclick="loadJoke()" class="refresh-btn">🎲 New Joke</button>
           </div>
           <p style="font-size: 12px; color: #888; margin-top: 10px;">Powered by Official Joke API</p>
       </div>
   </div>
   
   <script>
       // Load stocks
       async function loadStocks() {
           try {
               const response = await fetch('/api/stocks');
               const data = await response.json();
               const container = document.getElementById('stocks');
               
               if (data.error) {
                   container.innerHTML = '<p>Error loading stocks. Please try again.</p>';
                   return;
               }
               
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
           } catch (error) {
               console.error('Error:', error);
               document.getElementById('stocks').innerHTML = '<p>Error loading stocks. Please refresh.</p>';
           }
       }
       
       // Load joke
       async function loadJoke() {
           try {
               const response = await fetch('/api/joke');
               const data = await response.json();
               document.getElementById('joke').innerHTML = data.joke;
           } catch (error) {
               document.getElementById('joke').innerHTML = 'Why do programmers prefer dark mode? Because light attracts bugs!';
           }
       }
       
       // Load everything on page load
       loadStocks();
       loadJoke();
       
       // Auto-refresh stocks every 30 seconds
       setInterval(loadStocks, 30000);
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
                
                # Convert Series to float
                if hasattr(current_series, 'item'):
                    current = float(current_series.item())
                else:
                    current = float(current_series)
                    
                if hasattr(old_series, 'item'):
                    old = float(old_series.item())
                else:
                    old = float(old_series)
                
                momentum = ((current - old) / old) * 100
                predicted = current * (1 + momentum / 100)
                
                results.append({
                    'ticker': ticker,
                    'price': round(current, 2),
                    'momentum': round(momentum, 2),
                    'predicted': round(predicted, 2),
                    'signal': '🟢 BULLISH' if momentum > 0 else '🔴 BEARISH'
                })
            
            time.sleep(0.3)  # Rate limit protection
            
        except Exception as e:
            print(f"Error with {ticker}: {e}")

    if not results:
        return jsonify([{'error': 'Unable to load stock data'}])
    
    results.sort(key=lambda x: x['momentum'], reverse=True)
    return jsonify(results)

@app.route('/api/joke')
def get_joke():
    joke = get_random_joke()
    return jsonify({'joke': joke})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
