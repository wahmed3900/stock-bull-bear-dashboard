# Save as quick_test.py
import http.server
import socketserver

PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

print(f"\n✅ Server running at: http://localhost:{PORT}")
print("Open this URL in your browser\n")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()