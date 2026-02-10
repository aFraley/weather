### Weather
## Description
This is a command line tool to fetch weather data from NOAA API, based on your configured location, and display it to your command line.
![](demo.gif)
## Installation
1. Install [pipx](https://pipx.pypa.io/) if you don't have it:
   ```
   brew install pipx
   pipx ensurepath
   ```
2. Install weather:
   ```
   pipx install git+https://github.com/aFraley/weather.git
   ```
3. Create your config file:
   ```
   mkdir -p ~/.config/weather
   ```
   Create `~/.config/weather/config.ini` with your latitude and longitude:
   ```ini
   [location]
   latitude=47.6062
   longitude=-122.3321
   ```
## Usage
- `weather` displays the current temperature.
- `weather --today-forecast` displays current temperature and today's forecast briefing
- `weather --verbose` displays current temperature and verbose extended forecast
- `weather --brief` displays current temperature and brief extended forecast