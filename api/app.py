from flask import Flask, request, render_template
from http.server import BaseHTTPRequestHandler
from urllib import parse

app = Flask(__name__, template_folder='templates')
print("XYZ")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        option = request.form.get('option')
        minutes = request.form.get('minutes')
        
        if option == '1':
            result = int(minutes) * 2
        elif option == '2':
            result = int(minutes) * 3
        elif option == '3':
            result = int(minutes) * 4
        else:
            result = "Invalid option"

        return render_template("index.html", result=result)

    return render_template("index.html")

def app_handler(environ, start_response):
    return app(environ, start_response)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

        message = app_handler
        self.wfile.write(message.encode())
        return

@app.route('/about')
def about():
    return 'About'

