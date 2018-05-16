import http.server
import socketserver
import http.client
import json
import sys

socketserver.TCPServer.allow_reuse_address = True
IP = "localhost"
PORT = 8000

api_token = sys.argv[1]

class Client():
    def get_url(self,choice):
        headers = {"Authorization": "Bearer " + self.api_token}

        conn = http.client.HTTPSConnection("api.genius.com")
        url =
        conn.request("GET", url , None, headers)
        print('amoaver', url)
        r1 = conn.getresponse()
        print(r1.status, r1.reason)
        res_raw = r1.read().decode("utf-8")
        conn.close()

        search = json.loads(res_raw)
        return search



class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        try:
            if self.path == "/":
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                with open("genius.html", "r") as f:
                    menu = f.read()
                    self.wfile.write(bytes(menu, "utf8"))
            elif "searchSongs" in self.path:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                print(self.path)
                Client().get_url()

        except KeyError:
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            with open("error.html", "r") as f:
                file = f.read()
            self.wfile.write(bytes(file, "utf8"))

        return

Handler.api_token = sys.argv[1]

httpd = socketserver.TCPServer(("", PORT), Handler)
print("serving at port", PORT)
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass
httpd.server_close()
