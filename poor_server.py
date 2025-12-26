from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.request


class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):
        from urllib.parse import urlparse, parse_qs

        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)


        print(f"[GET]{self.path}")

        routes = {
            "/": self.handle_index,
            "/json": self.handle_json,
            "/health": self.handle_health,
            "/weather": lambda: self.handle_weather(query),
        }
        handler = routes.get(path)

        if handler:
            handler()
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
    def handle_weather(self, query: dict):
        city = query.get("city", [None])[0]

        if not city:
            self.send_response(400)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()

            data = {
                "success": False,
                "error": "Missing required query parameter: city",
                "example": "/weather?city=Almaty"
            }
            self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
            return
        cities = {
            "Almaty": (43.25, 76.95),
            "Astana": (51.16, 71.47),
        }
        coords = cities.get(city)

        if not coords:
            self.send_response(404)
            self.send_header("Content-Type", "application/json; charset-8")
            self.end_headers()

            data = {
                "success": False,
                "error": f"Unknown city: {city}"
            }
            self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
            return
        lat, lon = coords

        url = (
            "http://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}&current_weather=true"
        )

        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                raw = response.read().decode("utf-8")
                api_data = json.loads(raw)

                weather = api_data.get("current_weather", {})

        except Exception as e:
            self.send_response(502)
            self.send_header("Content_Type", "application/json; charset=utf-8")
            self.end_headers()

            data = {
                "success": False,
                "error": "Weather service unavailable",
                "details": str(e)
            }
            self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))
            return

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()

        data = {
            "success": True,
            "city": city,
            "temperature": weather.get("temperature"),
            "windspeed": weather.get("windspeed")
        }

        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))

        self.send_response(200, "OK")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()

        data = {
            "success":True,
            "city": city,
            "weather": {
                "temp_c": 0,
                "condition": "stub"
            }
        }
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))

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
