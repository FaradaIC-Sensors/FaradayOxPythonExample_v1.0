# FaradayOxPythonExample

## Dependencies

Uses Python3.

To install dependencies run ```pip install -r requirements.txt```.

## How to use

1. Set the COM Port in main.py to the one to which module is connected
2. Run ```python main.py```
3. When only testing things up, it's advisable to set ```cli_app(port=port, measure_sht40=True, measure_oxygen=False)```.
To only trigger the sht40 sensor humidity and temperature sensor.
4. When performing oxygen measurements ```cli_app(port=port, measure_sht40=False, measure_oxygen=False)```.
To trigger oxygen measurement, under the hood the sht40 measurement will still be performed and appropriate registers will be set.