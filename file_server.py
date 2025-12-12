#!/usr/bin/env python3
"""
Simple HTTP file server for downloading TradePro Render deployment package
"""
import http.server
import socketserver
import os
import sys
from pathlib import Path

class FileDownloadHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/TradePro_Render_Deploy.tar.gz':
            file_path = Path('TradePro_Render_Deploy.tar.gz')
            if file_path.exists():
                self.send_response(200)
                self.send_header('Content-Type', 'application/gzip')
                self.send_header('Content-Disposition', 'attachment; filename="TradePro_Render_Deploy.tar.gz"')
                self.send_header('Content-Length', str(file_path.stat().st_size))
                self.end_headers()
                
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File not found")
        else:
            super().do_GET()

if __name__ == "__main__":
    PORT = 8000
    
    # Change to current directory
    os.chdir('/home/runner/workspace')
    
    with socketserver.TCPServer(("", PORT), FileDownloadHandler) as httpd:
        print(f"File server running at http://0.0.0.0:{PORT}/")
        print(f"Download link: http://0.0.0.0:{PORT}/TradePro_Render_Deploy.tar.gz")
        httpd.serve_forever()