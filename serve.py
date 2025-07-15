#!/usr/bin/env python3
"""
Simple HTTP server for testing HTML locally
Usage: python serve.py [port]
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

def get_available_port(start_port=8000):
    """Find an available port starting from start_port"""
    port = start_port
    while True:
        try:
            with socketserver.TCPServer(("", port), None) as s:
                return port
        except OSError:
            port += 1
            if port > 9000:
                raise RuntimeError("No available ports found")

def main():
    # Change to the directory containing index.html
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Get port from command line or use default
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    
    try:
        # Try to use the specified port
        Handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"Serving at http://localhost:{port}")
            print(f"Directory: {os.getcwd()}")
            print("Press Ctrl+C to stop the server")
            httpd.serve_forever()
    except OSError as e:
        if "Address already in use" in str(e):
            new_port = get_available_port(port + 1)
            print(f"Port {port} is in use, trying port {new_port}")
            with socketserver.TCPServer(("", new_port), Handler) as httpd:
                print(f"Serving at http://localhost:{new_port}")
                print("Press Ctrl+C to stop the server")
                httpd.serve_forever()
        else:
            raise

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nServer stopped.")