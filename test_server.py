from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello! The server is working! 🚀"

if __name__ == '__main__':
    print("\n" + "="*50)
    print("TEST SERVER RUNNING")
    print("="*50)
    print("\nOpen your browser to: http://localhost:5000")
    print("="*50 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)