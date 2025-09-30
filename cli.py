from module import Module
from connection import ping_module, send_frame
from client import build_registers_read_full_register_pageframe, build_registers_write_frame
from protocol import OPERATION_READ, OPERATION_WRITE, process_frame
import time
import csv
from pathlib import Path
from datetime import datetime


def cli_app(port: str = "COM5"):
    module = Module()

    # Wake device
    ping_module(port)
    time.sleep(0.01)

    # 1. Perform SHT40 (temperature/humidity) measurement set
    module.control_start_sht40_measurement_set()
    addr, data = module.serialize_control()
    send_frame(port, build_registers_write_frame(addr, data), OPERATION_WRITE)
    time.sleep(0.05)  # brief wait for measurement
    request_and_log_registers(module, port, header="After SHT40 measurement")

    # 2. Perform oxygen (concentration) measurement set
    module.control_start_measurement_set()
    addr, data = module.serialize_control()
    send_frame(port, build_registers_write_frame(addr, data), OPERATION_WRITE)
    time.sleep(0.25)  # longer wait if needed for gas measurement
    request_and_log_registers(module, port, header="After O2 measurement")


def _log_file_path():
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    return logs_dir / f"{date_str}.csv"


def _ensure_log_header(path: Path):
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "module_id",
                "register_map_version",
                "firmware_version",
                "status",
                "control",
                "concentration",
                "temperature",
                "humidity",
            ])


def request_and_log_registers(module, port, header=None):
    status, frame = send_frame(port, build_registers_read_full_register_pageframe(), OPERATION_READ)
    if not status:
        return
    frame_data = process_frame(frame)
    if not frame_data:
        return
    if not module.deserialize(frame_data):
        return

    if header:
        print(f"\n=== {header} ===")
    print(module)

    # Logging
    path = _log_file_path()
    _ensure_log_header(path)
    ts = datetime.now().isoformat(timespec="seconds")
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            ts,
            module.module_id,
            f"{module.register_map_ver_major}.{module.register_map_ver_minor}",
            f"{module.firmware_ver_major}.{module.firmware_ver_minor}",
            f"0x{module.status:02X}",
            f"0x{module.control:02X}",
            f"{module.concentration:.6f}",
            f"{module.temperature:.6f}",
            f"{module.humidity:.6f}",
        ])
