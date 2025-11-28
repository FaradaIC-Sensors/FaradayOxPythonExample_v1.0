import os
from cli import cli_app
from fast_cli import cli_app as fast_cli_app

def main():
    port = "COM13"
    fast_cli_app(port=port, measure_sht40=False, measure_oxygen=True)

if __name__ == "__main__":
    main()
