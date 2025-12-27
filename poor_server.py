from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import urllib.request

# ❌ ВОПРОС 2 (частично 40%): Нет exit кодов для определения успешности выполнения скрипта
# TODO: Добавить sys.exit(0) при успехе, sys.exit(1) при ошибке
# TODO: Нет обработки исключений на уровне main для корректного завершения

# ❌ ВОПРОС 1 (частично 30%): Показан только print() и wfile.write()
# TODO: Добавить примеры других способов вывода: f-строки, format(), %, logging, sys.stdout.write()

# ❌ ВОПРОС 6 (0%): Endpoint /download полностью отсутствует!
# TODO: Реализовать /download с headers: Content-Disposition: attachment; filename="file.txt"


class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):
        from urllib.parse import urlparse, parse_qs

        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)


        # ✅ ВОПРОС 1: Пример вывода через print(), но не хватает других способов
        # TODO: Показать также: sys.stdout.write(), logging.info(), format(), % formatting
        print(f"[GET]{self.path}")

        routes = {
            "/": self.handle_index,
            "/json": self.handle_json,
            "/health": self.handle_health,
            "/weather": lambda: self.handle_weather(query),
            # ❌ БАГ: Отсутствует "/download": self.handle_download - ВОПРОС 6 не выполнен!
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
        # ✅ ВОПРОС 3: Изменение кода ответа - send_response(200) ✓
        # ✅ ВОПРОС 4: Возврат JSON в браузере - правильный Content-Type и json.dumps() ✓
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()

        data = {
             "success": True,  # ✅ ВОПРОС 2: Частично - есть флаг success, но нет exit кодов
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
        # ✅ ВОПРОС 3: Демонстрация разных кодов: 400, 404, 502, 200 ✓
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
            # 🐛 БАГ: Опечатка "charset-8" должно быть "charset=utf-8"
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
            # 🐛 БАГ: "Content_Type" с underscore! Должно быть "Content-Type" с дефисом
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

        # 🐛🐛🐛 КРИТИЧЕСКИЙ БАГ: Повторная отправка response после уже завершенного!
        # Headers уже были отправлены выше (строка 136 + 149), это вызовет ошибку!
        # Этот код НИКОГДА не выполнится корректно - надо удалить весь блок ниже
        self.send_response(200, "OK")  # ✅ ВОПРОС 5: Пример Reason Phrase ("OK")
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
        # ✅ ВОПРОС 5: Изменение Reason Phrase - второй параметр "Not Found" ✓
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
    # 🐛 БАГ: Порт 8080, но в задании требуется 8899!
    server = HTTPServer (('localhost',8080), MyServer)
    # 🐛 БАГ: Опечатка в URL - пропущен слэш "http:/localhost" → "http://localhost"
    print("Сервер запущен: http:/localhost:8080")
    server.serve_forever()
    # ❌ ВОПРОС 2: Нет обработки KeyboardInterrupt и sys.exit(0) для корректного завершения

# ============================================================================
# ИТОГОВАЯ ОЦЕНКА: 45/100
# ============================================================================
# ✅ Полностью выполнено (100%):
#    - Вопрос 3: Изменение кода ответа (200, 400, 404, 502)
#    - Вопрос 4: Возврат JSON в браузере
#    - Вопрос 5: Изменение Reason Phrase
#
# ⚠️  Частично выполнено:
#    - Вопрос 1 (30%): Способы вывода строки - только print() и wfile.write()
#    - Вопрос 2 (40%): Определение успешности - есть try-except и JSON success, но нет exit кодов
#
# ❌ Не выполнено:
#    - Вопрос 6 (0%): Endpoint /download полностью отсутствует
#
# 🐛 Критические баги:
#    1. Двойная отправка response в handle_weather (строки 164-179) - СЛОМАЕТ СЕРВЕР
#    2. Опечатка "charset-8" вместо "charset=utf-8" (строка 114)
#    3. Опечатка "Content_Type" вместо "Content-Type" (строка 140)
#    4. Опечатка в URL "http:/localhost" (строка 201)
#    5. Неверный порт 8080 вместо 8899 (строка 199)
# ============================================================================
