#!/Users/alan/dev/weather_getter/venv/bin/python
import argparse
import configparser
from datetime import datetime
import pathlib

import bs4
import requests


MODULE_PATH = pathlib.Path(__file__).parent

def extract_current_temperature(dom):
    return dom.find('data', attrs={'type': 'current observations'}).find('temperature').find('value').text


def extract_today_forecast(dom):
    return dom.find('data', attrs={'type': 'forecast'}).find('parameters').find('wordedforecast').find('text').text


def extract_time_period(dom):
    return dom.find('data', attrs={'type': 'forecast'}).find('time-layout').find('start-valid-time', attrs={'period-name': 'Today'})


def print_current_temperature(temperature):
    print(f'\nCurrent Temperature: {temperature}°F\n')


def print_today_forecast(forecast):
    print(forecast, end='\n\n')


def print_time_period(time_period):
    print(time_period['period-name'])


def setup_configuration():
    config = configparser.ConfigParser()
    config.read(f'{MODULE_PATH.absolute()}/config.ini')

    return config


def fetch_data():
    """Fetches data from NOAA API"""
    config = setup_configuration()
    LAT = config['location']['latitude']
    LON = config['location']['longitude']
    LANG = config['location']['language']
    URL = f'https://forecast.weather.gov/MapClick.php?lat={LAT}&lon={LON}&unit=0&lg={LANG}&FcstType=dwml'

    return requests.get(URL)

def main():
    response = fetch_data()
    dom = bs4.BeautifulSoup(response.content, features='html.parser')
    current_temperature = extract_current_temperature(dom)

    print_current_temperature(current_temperature)

    parser = argparse.ArgumentParser(
        prog='weather',
        description='CL tool to fetch and display weather data based on your configured lat and lon coordinates.'
    )
    parser.add_argument('--today-forecast', action='store_true', default=False, help='Extract and display today\'s forecast')

    args = parser.parse_args()

    if args.today_forecast:
        time_period = extract_time_period(dom)
        today_forecast = extract_today_forecast(dom)
        print_time_period(time_period)
        print_today_forecast(today_forecast)


if __name__ == "__main__":
    main()