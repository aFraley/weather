### Weather
## Description
This is a command line tool to fetch weather data from NOAA API, based on your configured location, and display it to your command line. 
## Installation
1. Clone to a directory of your choice
2. Create a virtual env and install dependencies
3. Create a `config.ini` file based on `config.ini.example`
4. Add shabang like `#!/my-venv-python-with-deps` to top of file
5. Run `chmod +x weather.py` to make it executable for your user
6. Add `weather=/path-to-weather.py` to .alias file
## Usage
- `weather` displays the current temperature.
- `weather --today-forecast` displays current temperature and today's forecast briefing
- `weather --verbose` displays current temperature and verbose extended forecast
- `weather --brief` displays current temperature and brief extended forecast