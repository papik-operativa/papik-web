import http.server, os, sys
os.chdir(os.path.dirname(os.path.abspath(__file__)))
port = int(os.environ.get('PORT', 9123))
print(f'Serving from {os.getcwd()} on port {port}')
http.server.test(HandlerClass=http.server.SimpleHTTPRequestHandler, port=port)
