import http.server
import socketserver
import http.client
import json
import sys

socketserver.TCPServer.allow_reuse_address = True
IP = "localhost"
PORT = 8000

TOKEN = sys.argv[1]

class Genius_Client():
    def get_singer(self, choice):
        headers = {"Authorization": "Bearer " + TOKEN }

        conn = http.client.HTTPSConnection("api.genius.com")
        url = "/search?q=" + choice
        conn.request("GET", url , None, headers)
        r1 = conn.getresponse()
        print(r1.status, r1.reason)
        res_raw = r1.read().decode("utf-8")
        conn.close()

        singer = json.loads(res_raw)
        return singer
    def get_id(self, singer):
        try:
            for i in singer['response']['hits']:
                id = str(i['result']['primary_artist']['id'])
                break
        except KeyError:
            with open("not_found.html") as f:
                message = f.read()
            self.wfile.write(bytes(message, "utf8"))

        return id
    def get_url(self, id):
        headers = {"Authorization": "Bearer " + TOKEN}

        conn = http.client.HTTPSConnection("api.genius.com")
        url = "/artists/" + id + "/songs?per_page=30&page=1"
        conn.request("GET", url, None, headers)
        r1 = conn.getresponse()
        print(r1.status, r1.reason)
        res_raw = r1.read().decode("utf-8")
        conn.close()
        data = json.loads(res_raw)
        return data

client = Genius_Client()

class Genius_Parser():
    def get_data(self,data):
        list = []
        try:
            list = data['response']['songs']
        except KeyError:
            with open("not_found.html") as f:
                message = f.read()
            self.wfile.write(bytes(message, "utf8"))

        return list

parser = Genius_Parser()

class Genius_HTML():
    def write_data(self, list):
        with open('songs.html', 'w') as f:
            f.write ("<!doctype html>" + "<html>" + "<body>" + "<ul>")
            for song in list:
                f.write("<li>")
                if song['header_image_thumbnail_url'].find('default cover'):
                    f.write("<img align='left' height='50' width='50' src=' " + song['header_image_thumbnail_url'] + "'>")
                else:
                    f.write('(Album photo not found)')
                f.write("<a href='" + song['url'] + "'>" + "<h2>" + song['title'] + "</h2></a></li>")
            f.write ("</ul>" + "</body>" + "</html>")

        with open('songs.html', 'r') as f:
            file = f.read()
        return file

HTML = Genius_HTML()

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
                choice = self.path.split("=")[1]
                singer = client.get_singer(choice)
                id = client.get_id(singer)
                data = client.get_url(id)
                list = parser.get_data(data)
                file = HTML.write_data(list)
                self.wfile.write(bytes(file, "utf8"))

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
