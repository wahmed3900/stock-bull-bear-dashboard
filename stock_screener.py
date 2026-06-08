import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

print("="*60)
print("30-Day Stock Bull/Bear Screener")
print("="*60)

# List of stocks to analyze
stocks = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'TSLA', 'AMZN', 'JPM', 'JNJ']
results = []

for ticker in stocks:
    try:
        print(f"\nAnalyzing {ticker}...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=120)
        
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)
        
        if df.empty or len(df) < 30:
            print(f"   No data for {ticker}")
            continue
        
        current_price = df['Close'].iloc[-1]
        ma30 = df['Close'].rolling(window=30).mean().iloc[-1]
        price_30d_ago = df['Close'].iloc[-30]
        momentum = ((current_price - price_30d_ago) / price_30d_ago) * 100
        
        # Determine signal
        if current_price > ma30 and momentum > 5:
            signal = "🚀 STRONG BULLISH"
        elif current_price > ma30 and momentum > 0:
            signal = "🟢 BULLISH"
        elif current_price < ma30 and momentum < -5:
            signal = "💀 STRONG BEARISH"
        elif current_price < ma30:
            signal = "🔴 BEARISH"
        else:
            signal = "⚪ NEUTRAL"
        
        predicted_price = current_price * (1 + momentum / 100)
        
        results.append({
            'Ticker': ticker,
            'Current_Price': round(current_price, 2),
            'Predicted_30d': round(predicted_price, 2),
            'Expected_Return_%': round(momentum, 2),
            'Signal': signal,
            'MA30': round(ma30, 2)
        })
        
        print(f"   ✓ {ticker}: {momentum:+.2f}% - {signal}")
        
    except Exception as e:
        print(f"   ✗ {ticker}: Error")

# Display results
print("\n" + "="*80)
print("STOCK RANKING BY 30-DAY BULLISH/BEARISH POTENTIAL")
print("="*80)

if results:
    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values('Expected_Return_%', ascending=False)
    
    print(df_results[['Ticker', 'Current_Price', 'Predicted_30d', 'Expected_Return_%', 'Signal']].to_string(index=False))
    
    # Save to CSV
    filename = f'stock_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    df_results.to_csv(filename, index=False)
    print(f"\n📁 Results saved to: {filename}")
    
    # Summary
    bullish = len(df_results[df_results['Expected_Return_%'] > 0])
    bearish = len(df_results[df_results['Expected_Return_%'] < 0])
    print(f"\n📊 Summary: {bullish} Bullish | {bearish} Bearish")
else:
    print("No results to display")

print("\n" + "="*60)
print("Analysis Complete!")
print("="*60)
