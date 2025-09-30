import os
from cli import cli_app

def main():
    port = "COM5"
    cli_app(port=port, measure_sht40=True, measure_oxygen=True)

if __name__ == "__main__":
    main()
