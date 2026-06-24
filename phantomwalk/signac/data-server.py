#!/usr/bin/env python3

# Taken from https://pythonbasics.org/webserver/

from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import os

hostName = "localhost"
serverPort = 8888

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # URLs should be formatted as localhost:8888/<var1>-<var2>
        variables = self.path[1:].split("-")
        status = os.system(f"python compile_graph.py {' '.join(variables)}")
        if status != 0:
            self.send_response(400)
            return

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(f"time-plots/{self.path}.html", 'rb') as ret_file:
            self.wfile.write(ret_file.read())

if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
