# hello.py
# https://lungdon-underground.vercel.app/api/hello.py
from http.server import BaseHTTPRequestHandler
from urllib import parse

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        message = "Hello, Vercel! Edited"
        self.wfile.write(message.encode())
        return

