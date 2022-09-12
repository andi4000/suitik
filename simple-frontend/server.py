#!/usr/bin/env python3
# simple http server with SSL support
# for devel use only
import os
import http.server
import ssl

if not os.path.exists("./server.pem"):
    os.system("openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes")

print("==> Accepting HTTPS connection at port 4443..")
httpd = http.server.HTTPServer(("0.0.0.0", 4443), http.server.SimpleHTTPRequestHandler)
httpd.socket = ssl.wrap_socket(httpd.socket, certfile="./server.pem", server_side=True)
httpd.serve_forever()
