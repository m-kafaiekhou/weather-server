import requests
import json
import sys
import os
import getpass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../menu')))
from models import generate_menu_from_dict
from weather_server import logger
import config as C


def see_weather():
    promt: str = "Enter a city name: "
    while True:
        city = input(promt)
        promt = "Enter a new city name: "
        response = get_weather(city)

        if response.get('status') == 200:
            print_weather(response)
            input("Press any key...")
            return start_client()
        else:
            print("could not get data due to :", response["status"])

    
def request_count():
    url = f'{C.ADMIN_URL}request_count'
    response = requests.get(url).json()
    print("Total count: ", response['count'])


def success_request():
    url = f'{C.ADMIN_URL}successful_request_count'
    response = requests.get(url).json()
    print("Total success count: ", response['count'])


def last_hour_count():
    url = f'{C.ADMIN_URL}last_hour_requests'
    response = requests.get(url).json()

    for city, date in response['requests']:
        print(city, date)


def city_count():
    url = f'{C.ADMIN_URL}city_request_count'
    response = requests.get(url).json()
    print(response)
    for city, count in response['requests']:
        print(count, ' requests for ', city)


def admin_menu():
    menu_obj = generate_menu_from_dict(admin_dict)
    menu_obj()
    

def login_as_admin():
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    data = {'username': username, 'password': password}

    response = requests.post(f'{C.ADMIN_URL}signin', json=json.dumps(data))

    if response.json()['auth']:
        logger.info("admin logged in")
        admin_menu()


def get_weather(city:str) -> dict:
    """
    Gets data from the server for a given city

    Args: city(str): Name of the city you want the data for

    Returns: dict: a dictionary containing temp, feels like temp, last updated  Info for the city
    """

    url = f'{C.WEATHER_URL}{city}'
    response = requests.get(url).json()
    return response


def print_weather(weather: dict) -> None:
    """
    Prints the weather info from a given dictionary

    Args: weather(dict): a dictionary containing temp, feels like temp, last updated  Info for the city

    Returns: None
    """

    temp = weather['temp']
    feels_like = weather['feels_like_temp']
    last_update = weather['last_update']
    print("Temperature: ", temp)
    print("Feels like: ", feels_like)
    print("Last updated: ", last_update)


admin_dict = {
    'name':'Weather API',
    'children':[
        {
            'name': 'See request count',
            'action': request_count,
        },
        {
            'name': 'See successful requests',
            'action': success_request
        },
        {
            'name': 'See city request count',
            'action': city_count
        },
        {
            'name': 'See last hour requests',
            'action': last_hour_count
        }]}


main_menu_dict = {
    'name':'Weather API',
    'children':[
        {
            'name':'see weather',
            'action': see_weather
        },
        {
            'name': 'Login as admin',
            'action': login_as_admin
        }]}
    



def start_client():
    """
    Start the weather client command-line interface.
    """
    
    main_menu = generate_menu_from_dict(main_menu_dict)
    main_menu()
    


if __name__ == "__main__":
    start_client()
    