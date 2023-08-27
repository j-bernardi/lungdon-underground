from flask import Flask, Response
from http.server import BaseHTTPRequestHandler

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"

# def app_handler(environ, start_response):
#     return app(environ, start_response)
# 
# class handler(BaseHTTPRequestHandler):
#     def do_GET(self):
#         self.send_response(200)
#         self.send_header('Content-type','text/plain')
#         self.end_headers()
# 
#         message = "Hello, World!"
#         self.wfile.write(message.encode())
#         return

