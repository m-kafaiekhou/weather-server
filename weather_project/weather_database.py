import psycopg2
from typing import List, Tuple
import datetime as dt
import json
import config as C


def singleton(cls):
    instances = {}
    def wrapper(*args, **kwargs):
        if cls not in instances:
          instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return wrapper

@singleton
class WeatherDatabase:
    def __init__(self):
        """
        Initialize a new WeatherDatabase instance.
        """
        self.conn = None

    def connect_database(self, database=C.DATABASE, user=C.USER, password=C.PASSWORD, host=C.HOST, port=C.PORT):
        self.conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

    def create_tables(self):
        try:
            cur = self.conn.cursor()
            # CREATE TABLES
            cur.execute("""CREATE TABLE IF NOT EXISTS request (
                        id BIGSERIAL PRIMARY KEY, city VARCHAR(80) DEFAULT LOWER(NULL),
                        dt TIMESTAMP DEFAULT NOW())""")
            
            cur.execute("""CREATE TABLE IF NOT EXISTS response (
                        id BIGSERIAL PRIMARY KEY, request_id BIGINT NOT NULL,
                        data JSON, dt TIMESTAMP DEFAULT NOW(),
                        FOREIGN KEY (request_id) REFERENCES request(id))""")
            self.conn.commit()
            cur.close()
        except AttributeError:
            print("Please connect to a database first")
        

    def save_request_data(self, city_name: str, request_time: str) -> int:
        """
        Save request data for a city to the database.

        Args:
        - city_name (str): The name of the city to save request data for.
        - request_time (str): The time the request was made, in ISO format.

        Returns:
        - int: request_id
        """
        
        cur = self.conn.cursor()
        # converts a ISO format dt string into timestamp
        cur.execute("""INSERT INTO request (city, dt) 
                    VALUES (%s, %s)
                    RETURNING id""",
                    (city_name, request_time,))
        
        request_id = cur.fetchone()[0] 
        cur.close()
        self.conn.commit()

        return request_id
        

    def save_response_data(self, request_id: int, response_data: dict) -> None:
        """
        Save response data for a city to the database.

        Args:
        - city_name (str): The name of the city to save response data for.
        - response_data (dict): A dictionary containing weather information for the city, including temperature, feels like temperature, and last updated time.

        Returns:
        - None
        """

        cur = self.conn.cursor()
        cur.execute("""INSERT INTO response (request_id, data) 
                    VALUES (%s, %s)
                    RETURNING id""",
                    (request_id, json.dumps(response_data),))
        cur.close()
        self.conn.commit()


    def get_request_count(self) -> int:
        """
        Get the total number of requests made to the server.

        Returns:
        - int: The total number of requests made to the server.
        """

        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM request")

        count = cur.fetchone()[0]
        self.conn.commit()
        cur.close()

        return count


    def get_successful_request_count(self) -> int:
        """
        Get the total number of successful requests made to the server.

        Returns:
        - int: The total number of successful requests made to the server.
        """
        
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM response WHERE CAST(data->>'status' AS INTEGER) = 200")

        count = cur.fetchone()[0]
        self.conn.commit()
        cur.close()

        return count


    def get_last_hour_requests(self) -> List[Tuple[str, str]]:
        """
        Get a list of requests made in the last hour.

        Returns:
        - List[Tuple[str, str]]: A list of tuples containing the name of the city and the time the request was made, in ISO format.
        """

        cur = self.conn.cursor()
        last_hour = dt.datetime.now() - dt.timedelta(hours=1)
        cur.execute("SELECT city, TO_CHAR(dt, 'YYYY-MM-DD HH24:MM:SS') FROM request WHERE dt >= %s", (last_hour,))

        results = cur.fetchall()
        self.conn.commit()
        cur.close()

        return results


    def get_city_request_count(self) -> List[Tuple[str, int]]:
        """
        Get a count of requests made for each city.

        Returns:
        - List[Tuple[str, int]]: A list of tuples containing the name of the city and the number of requests made for that city.
        """
        cur = self.conn.cursor()
        cur.execute("""SELECT request.city, COUNT(*) FROM request 
                       JOIN response ON response.request_id = request.id 
                       WHERE CAST(data->>'status' AS INTEGER) = 200 
                       GROUP BY request.city""")

        result = cur.fetchall()
        print(result)
        self.conn.commit()
        cur.close()

        return result


    def get_admin_pass(self, username: str='admin') -> str:
        """
        Retrieves password for the useradmin from database

        Args:
        username: str - Default set to 'admin'

        Returns: 
        password: str
        """
        cur = self.conn.cursor()
        cur.execute("SELECT password FROM admin WHERE username = %s", (username,))
        password = cur.fetchone() 
        self.conn.commit()
        cur.close()

        if password:
            password = password[0]
        return password


    def close_conn(self) -> None:
        self.conn.close()

    def __enter__(self):
        return self
    
    def __exit__(self, *args, **kwargs) -> None:
        self.conn.close()


if __name__ == "__main__":
    db = WeatherDatabase()