import unittest
import datetime
import psycopg2
import os
import sys
# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../weather_project')))
# from weather_database import WeatherDatabase
from ..weather_project.weather_database import WeatherDatabase

class TestWeatherDatabase(unittest.TestCase):
    
    def setUp(self):
        self.db = WeatherDatabase()
        self.db.connect_database(database="testweather")
        self.db.create_tables()
    
    def tearDown(self):
        cur = self.db.conn.cursor()
        cur.execute("DROP TABLE response")
        cur.execute("DROP TABLE request")
        self.db.conn.commit()
        self.db.conn.close()
        
    def test_save_request_data(self):
        # Save a request for a city
        request_time = datetime.datetime.now().isoformat()
        request_id = self.db.save_request_data('London', request_time)
        
        # check that the request was saved successfully
        self.assertIsInstance(request_id, int)
        self.assertGreater(request_id, 0)

    def test_save_response_data(self):
        # save a response for a request
        request_time = datetime.datetime.now().isoformat()
        request_id = self.db.save_request_data('London', request_time)
        response_data = {'status': 200, 'temperature': 20.5}
        self.db.save_response_data(request_id, response_data)
        
        # check that the response was saved successfully
        cur = self.db.conn.cursor()
        cur.execute("SELECT data FROM response WHERE request_id = %s", (request_id,))
        result = cur.fetchone()[0]
        self.assertEqual(result, response_data)
        
    def test_get_request_count(self):
        # Insert some requests into the database
        request_time = datetime.datetime.now().isoformat()
        self.db.save_request_data('London', request_time)
        self.db.save_request_data('Paris', request_time)
        self.db.save_request_data('New York', request_time)
        
        count = self.db.get_request_count()
        
        # Check that the count is correct
        self.assertEqual(count, 3)

    def test_get_successful_request_count(self):
        # Insert some mixed responses into the database
        request_time = datetime.datetime.now().isoformat()
        request_id = self.db.save_request_data('London', request_time)
        response_data = {'status': 200, 'temperature': 20.5}
        self.db.save_response_data(request_id, response_data)
        request_id = self.db.save_request_data('Paris', request_time)
        response_data = {'status': 200, 'temperature': 18.2}
        self.db.save_response_data(request_id, response_data)
        request_id = self.db.save_request_data('New York', request_time)
        response_data = {'status': 404, 'message': 'City not found'}
        self.db.save_response_data(request_id, response_data)
        
        count = self.db.get_successful_request_count()
        
        # Check that the count is correct
        self.assertEqual(count, 2)
        
    def test_get_last_hour_requests(self):
        # Insert some requests into the database
        now = datetime.datetime.now()
        london_time = (now - datetime.timedelta(minutes=30))
        self.db.save_request_data('London', london_time.isoformat())
        paris_time = (now - datetime.timedelta(minutes=45))
        self.db.save_request_data('Paris', paris_time.isoformat())
        newyork_time = (now - datetime.timedelta(hours=2))
        self.db.save_request_data('New York', newyork_time.isoformat())
        
        results = [city for city, dt in self.db.get_last_hour_requests()]
        
        # Check that the results are correct
        self.assertEqual(len(results), 2)
        self.assertIn('London', results)
        self.assertIn('Paris', results)
        self.assertNotIn('New York', results)

    def test_get_city_request_count(self):
        # Insert some requests into the database
        request_time = datetime.datetime.now().isoformat()
        london1_id = self.db.save_request_data('London', request_time)
        paris_id = self.db.save_request_data('Paris', request_time)
        newyork_id = self.db.save_request_data('New York', request_time)
        london2_id = self.db.save_request_data('London', request_time)

        self.db.save_response_data(london1_id, {'status':200})
        self.db.save_response_data(paris_id, {'status':200})
        self.db.save_response_data(newyork_id, {'status':200})
        self.db.save_response_data(london2_id, {'status':200})
        
        results = self.db.get_city_request_count()
        
        # Check that the results are correct
        self.assertEqual(len(results), 3)
        self.assertIn(('London', 2), results)
        self.assertIn(('Paris', 1), results)
        self.assertIn(('New York', 1), results)
        
        
if __name__ == '__main__':
    unittest.main()