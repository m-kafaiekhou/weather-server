import unittest
from unittest.mock import patch 
import requests
import sys
import os
# inserts the weather_project dir to path so we can import it
# normal packaging(__init__.py) did not work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../weather_project')))
from weather_server import get_city_weather



class TestGetWeather(unittest.TestCase):
    def test_city_exists(self):
        city:str = "Tehran"

        response:dict = get_city_weather(city_name=city)
        
        self.assertIsInstance(response, dict)
        self.assertEqual(response["status"], 200)
        self.assertIn('temp', response)
        self.assertIn('feels_like_temp', response)
        self.assertIn('last_update', response)

    def test_city_not_exists(self):
        city:str = "this city does not exist"
        response = get_city_weather(city_name=city)

        self.assertIsInstance(response, dict)
        self.assertIn('status', response)
        self.assertEqual(response["status"], 404)
        self.assertNotIn('temp', response)
        self.assertNotIn('feels_like_temp', response)
        self.assertNotIn('last_update', response)

    # def test_get_city_weather_timeout(self):
    #     """
    #     This test case ensures that the function handles connection timeouts correctly.
    #     """
    #     city_name = 'Tehran'
    #     with patch('requests.get') as mock_get:
    #         mock_get.side_effect = requests.exceptions.Timeout
    #         with self.assertRaises(requests.exceptions.Timeout):
    #             get_city_weather(city_name)
            

if __name__ == "__main__":
    unittest.main()


