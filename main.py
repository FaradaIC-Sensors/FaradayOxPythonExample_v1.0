import os
from cli import cli_app


APP_VERSION = "1.2"

def main():
    print(f"FaradayOxPythonExample v{APP_VERSION}")
    port = "COM5"
    cli_app(port=port, measure_sht40=True, measure_oxygen=True)

if __name__ == "__main__":
    main()
