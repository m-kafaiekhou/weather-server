import requests
import datetime
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
#local import
from weather_database import WeatherDatabase as wd
import config as C
from logger import Logger


db = wd()
db.connect_database()
db.create_tables()


logger = Logger()


class weatherHandler(BaseHTTPRequestHandler):
    """
    A request handler for an HTTP server that provides weather information for a given city.

    Attributes:
        city (str): The name of the city to get weather information for.

    Methods:
        set_header(status_code=200): Sets the HTTP response headers for the current request.
        do_GET(): Handles GET requests by returning the weather information for the configured city.
        do_POST(): Handles POST requests by setting the configured city to the value in the request body.
    """

    def set_header(self, status_code: int=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()


    def do_GET(self):
        self.set_header()
        if self.path.startswith("/admin/") and self.command == "GET":
            if self.path == "/admin/request_count":
                self.reqest_count()

            elif self.path == "/admin/successful_request_count":
                self.successful_request_count()

            elif self.path == "/admin/last_hour_requests":
                self.last_hour_requests()
            
            elif self.path == "/admin/city_request_count":
                self.city_request_count()

            else:
                logger.warning("wrong url for admin panel!")
                self.set_header(404)
                self.wfile.write(json.dumps({'error': 'Not Found'}).encode())

        elif self.path.startswith("/weather/"):
            self.city_weather()
            
        else:
            logger.warning("wrong url for weather")
            self.set_header(404)
            self.wfile.write(json.dumps({'error': 'Not Found'}).encode())


    def do_POST(self):

        if self.path.startswith("/admin/signin") and self.command == "POST":
            logger.info("admin login attempt")
            self.admin_signin()
            
        else:
            logger.warning("post request with wrong url")
            self.set_header(404)
            self.wfile.write(json.dumps({'error': 'Not Found'}).encode())
            

    def admin_signin(self):
        data = self.rfile.read(int(self.headers.get('Content-Length')))
        rdata = eval(json.loads(data.decode()))
        auth = self.admin_authenticator(rdata['username'], rdata['password'])
        self.set_header(201)
        self.wfile.write(json.dumps(auth).encode())

    def city_weather(self):
        city = self.path[9:].replace("/", "")
        time:str = datetime.datetime.now().isoformat()
        request_id = db.save_request_data(city, time)
        response = get_city_weather(city)
        db.save_response_data(request_id, response)
        self.wfile.write(json.dumps(response).encode())

    def reqest_count(self):
        count = db.get_request_count()
        data = {'count':count}
        self.wfile.write(json.dumps(data).encode())

    def successful_request_count(self):
        count = db.get_successful_request_count()
        data = {'count':count}
        self.wfile.write(json.dumps(data).encode())

    def last_hour_requests(self):
        data = db.get_last_hour_requests()
        data = {'requests':data}
        self.wfile.write(json.dumps(data).encode())

    def city_request_count(self):
        data = db.get_city_request_count()
        data = {'requests':data}
        self.wfile.write(json.dumps(data).encode())

    @classmethod
    def admin_authenticator(cls, username: str, password: str) -> bool:
        __password = db.get_admin_pass(username)
        if password == __password:
            return {'auth': True}
        return {'auth': False}



def get_city_weather(city_name: str) -> dict:
    """
    Retrieve weather data from an external API for a given city.

    Args:
    - city_name (str): The name of the city to retrieve weather data for.

    Returns:
    - dict: A dictionary containing weather information for the city, including temperature, feels like temperature, and last updated time.
    """

    url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={C.API_KEY}&units={C.API_UNIT}'

    try:
        response = requests.get(url, timeout=8)
        response.raise_for_status()
        weather_info = response.json()

        main = weather_info.get('main', None)
        if main:

            temp = float(main['temp'])                                     
            feels_like_temp = float(main['feels_like'])
            last_updated = datetime.datetime.fromtimestamp(weather_info["dt"]).strftime('%Y-%m-%d %H:%M:%S')

            weather = {'temp': temp, 'feels_like_temp': feels_like_temp, 'last_update': last_updated, 'status': response.status_code}
        else:
            weather = {'status': response.status_code}
        return weather
    except requests.exceptions.HTTPError as exc:
        logger.error(f"HTTPError: {exc}")
        exc_message = {"status": exc.response.status_code}
        response.close()
        return exc_message
    except requests.exceptions.Timeout:
        logger.error("Timeout: 408")
        exc_message = {"status": 408}
        return exc_message



def start_server() -> None:
    """
    Start the weather server.
    """
   
    server_address = ('localhost', 8000)
    with HTTPServer(server_address, weatherHandler) as server:
        print('Server running at http://localhost:8000/')
        logger.info("server running")
        server.serve_forever()


if __name__ == "__main__":
    try:
        start_server()
        logger.info("server running")
    except:
        logger.error("server shutdown due to an exception")
    