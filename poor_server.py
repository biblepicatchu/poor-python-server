from http.server import BaseHTTPRequestHandler, HTTPServer
import json


class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):
        print(f"[GET]{self.path}")

        if self.path == "/":
            self.handle_index()
        elif self.path == "/json":
            self.handle_json()
        elif self.path == "/health":
            self.handle_health()
        else:
            self.handle_404()


    def handle_index(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        html = """
            <html>
            <body>
                <h1>Привет!</h1>
                <p>Главная страница моего сервера</p>
            </body>
            </html>
            """

        self.wfile.write(html.encode("utf-8"))


    def handle_json(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()

        data = {
             "success": True,
             "message": "Это JSON ответ",
             "path": self.path
                   }

        self.wfile.write(
               json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
           )
    def handle_health(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()

        data = {
            "status": "ok"
        }

        self.wfile.write(
            json.dumps(data).encode("utf-8")
        )

    def handle_404(self):
        self.send_response(404, "Not Found")
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        html = """
            <html>
            <body>
                 <h1>404 Not Found</h1>
                 <p>Запрошенный ресурс не существует</p>
            </body>
            </html>
            """

        self.wfile.write(html.encode("utf-8"))
if __name__ == "__main__":
    server = HTTPServer (('localhost',8080), MyServer)
    print("Сервер запущен: http:/localhost:8080")
    server.serve_forever()
