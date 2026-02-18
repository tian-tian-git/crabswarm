#!/usr/bin/env python3
"""
Simple tunnel to expose Lobster to public
Usage: python3 tunnel.py
"""

import http.server
import socketserver
import urllib.request
import threading
import sys

LOCAL_PORT = 3000
TUNNEL_PORT = 8080

class TunnelHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request('GET')
    
    def do_POST(self):
        self.proxy_request('POST')
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
    
    def proxy_request(self, method):
        try:
            url = f'http://127.0.0.1:{LOCAL_PORT}{self.path}'
            
            headers = {}
            for key, value in self.headers.items():
                if key.lower() not in ['host', 'content-length']:
                    headers[key] = value
            
            req = urllib.request.Request(
                url,
                headers=headers,
                method=method
            )
            
            if method == 'POST':
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                req.data = body
            
            with urllib.request.urlopen(req, timeout=30) as response:
                self.send_response(response.status)
                for key, value in response.headers.items():
                    if key.lower() not in ['transfer-encoding', 'content-encoding']:
                        self.send_header(key, value)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(response.read())
                
        except Exception as e:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(f'{{"error": "{str(e)}"}}'.encode())
    
    def log_message(self, format, *args):
        print(f"[TUNNEL] {self.address_string()} - {format % args}")

def main():
    with socketserver.TCPServer(("0.0.0.0", TUNNEL_PORT), TunnelHandler) as httpd:
        print(f"🦞 Lobster Tunnel running on port {TUNNEL_PORT}")
        print(f"Forwarding to localhost:{LOCAL_PORT}")
        print(f"Try: http://YOUR_SERVER_IP:{TUNNEL_PORT}")
        httpd.serve_forever()

if __name__ == '__main__':
    main()
