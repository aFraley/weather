#!/usr/bin/env python3
import argparse
import configparser
import pathlib
import sys

import requests
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

MODULE_PATH = pathlib.Path(__file__).parent
HEADERS = {"User-Agent": "(weather-cli, github.com/aFraley/weather)"}

console = Console()


def fetch_points(lat, lon):
    """Fetch metadata for a lat/lon point from the NWS API."""
    url = f"https://api.weather.gov/points/{lat},{lon}"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    props = resp.json()["properties"]
    return props["forecast"], props["observationStations"]


def degrees_to_compass(deg):
    """Convert wind direction in degrees to an 8-point compass abbreviation."""
    if deg is None:
        return None
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = round(deg / 45) % 8
    return directions[idx]


def fetch_current_observations(stations_url):
    """Fetch current observations from the nearest observation station."""
    resp = requests.get(stations_url, headers=HEADERS)
    resp.raise_for_status()
    station = resp.json()["features"][0]["id"]

    obs_resp = requests.get(f"{station}/observations/latest", headers=HEADERS)
    obs_resp.raise_for_status()
    props = obs_resp.json()["properties"]

    def val(key):
        obj = props.get(key)
        return obj["value"] if isinstance(obj, dict) else None

    def c_to_f(v):
        return round(v * 9 / 5 + 32) if v is not None else None

    def kmh_to_mph(v):
        return round(v * 0.621371) if v is not None else None

    humidity_raw = val("relativeHumidity")

    return {
        "temperature": c_to_f(val("temperature")),
        "humidity": round(humidity_raw) if humidity_raw is not None else None,
        "wind_speed": kmh_to_mph(val("windSpeed")),
        "wind_direction": degrees_to_compass(val("windDirection")),
        "wind_gust": kmh_to_mph(val("windGust")),
        "dewpoint": c_to_f(val("dewpoint")),
        "conditions": props.get("textDescription") or None,
    }


def fetch_forecast(forecast_url):
    """Fetch forecast periods from the NWS API."""
    resp = requests.get(forecast_url, headers=HEADERS)
    resp.raise_for_status()
    return resp.json()["properties"]["periods"]


def display_current_conditions(obs):
    """Display current conditions in a styled Rich panel."""
    if all(v is None for v in obs.values()):
        console.print(Panel("[yellow]Current conditions unavailable[/yellow]"))
        return

    text = Text()

    if obs["conditions"] is not None:
        text.append(f"{obs['conditions']}\n", style="bold white")

    if obs["temperature"] is not None or obs["dewpoint"] is not None:
        if obs["temperature"] is not None:
            text.append(f"{obs['temperature']}°F", style="bold white")
        if obs["dewpoint"] is not None:
            if obs["temperature"] is not None:
                text.append("  ", style="white")
            text.append(f"(Dewpoint: {obs['dewpoint']}°F)", style="dim")
        text.append("\n")

    if obs["humidity"] is not None:
        text.append(f"Humidity: {obs['humidity']}%\n", style="white")

    if obs["wind_speed"] is not None or obs["wind_direction"] is not None:
        parts = ["Wind:"]
        if obs["wind_direction"] is not None:
            parts.append(obs["wind_direction"])
        if obs["wind_speed"] is not None:
            parts.append(f"{obs['wind_speed']} mph")
        wind_str = " ".join(parts)
        if obs["wind_gust"] is not None:
            wind_str += f", gusts {obs['wind_gust']} mph"
        text.append(wind_str + "\n", style="white")

    # Remove trailing newline
    text.rstrip()

    console.print(Panel(text, title="Current Conditions", border_style="cyan"))


def display_forecast(periods):
    """Display forecast periods with Rich styling."""
    for period in periods:
        name = period["name"]
        detail = period["detailedForecast"]
        console.print(f"\n[bold cyan]{name}[/bold cyan]")
        console.print(Panel(detail))


def setup_configuration():
    config = configparser.ConfigParser()
    config.read(f"{MODULE_PATH.absolute()}/config.ini")
    return config


def main():
    parser = argparse.ArgumentParser(
        prog="weather",
        description="CL tool to fetch and display weather data based on your configured lat and lon coordinates.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=False,
        help="Extract and display verbose forecast",
    )
    parser.add_argument(
        "-t", "--today-forecast", action="store_true", default=False,
        help="Extract and display today's forecast",
    )
    parser.add_argument(
        "-b", "--brief", action="store_true", default=False,
        help="Extract and display today and tonight's forecast",
    )

    args = parser.parse_args()

    try:
        config = setup_configuration()
        lat = config["location"]["latitude"]
        lon = config["location"]["longitude"]

        forecast_url, stations_url = fetch_points(lat, lon)
        obs = fetch_current_observations(stations_url)
        display_current_conditions(obs)

        if args.verbose:
            periods = fetch_forecast(forecast_url)
            display_forecast(periods)
        elif args.brief:
            periods = fetch_forecast(forecast_url)
            display_forecast(periods[:2])
        elif args.today_forecast:
            periods = fetch_forecast(forecast_url)
            display_forecast(periods[:1])

    except requests.ConnectionError:
        console.print("[red]Error: Unable to connect to the weather service.[/red]")
        sys.exit(1)
    except requests.HTTPError as e:
        console.print(f"[red]Error: Weather API returned {e.response.status_code}.[/red]")
        sys.exit(1)
    except (KeyError, IndexError):
        console.print("[red]Error: Unexpected response from weather API.[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
