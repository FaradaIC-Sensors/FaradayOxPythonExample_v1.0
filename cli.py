from module import Module
from connection import ping_module, send_frame
from client import build_registers_read_full_register_pageframe, build_registers_write_frame
from protocol import OPERATION_READ, OPERATION_WRITE, process_frame
import time
import csv
from pathlib import Path
from datetime import datetime


def cli_app(port: str = "COM5", *, measure_sht40: bool = True, measure_oxygen: bool = True):
    module = Module()

    # Wake device
    if not ping_module(port):
        print(f"ERROR: Could not ping module on {port}")
        return
    time.sleep(0.01)

    # 1. Perform SHT40 (temperature/humidity) measurement set (optional)
    if measure_sht40:
        module.control_start_sht40_measurement_set()
        addr, data = module.serialize_control()
        send_frame(port, build_registers_write_frame(addr, data), OPERATION_WRITE)
        time.sleep(0.05)  # brief wait for measurement
        if not request_and_log_registers(module, port, header="After SHT40 measurement"):
            print("ERROR: Failed to read/log registers after SHT40 measurement")
            return

    # 2. Perform oxygen (concentration) measurement set (optional)
    if measure_oxygen:
        module.control_start_measurement_set()
        addr, data = module.serialize_control()
        send_frame(port, build_registers_write_frame(addr, data), OPERATION_WRITE)
        time.sleep(0.25)  # longer wait if needed for gas measurement
        if not request_and_log_registers(module, port, header="After O2 measurement"):
            print("ERROR: Failed to read/log registers after O2 measurement")
            return


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


def request_and_log_registers(module, port, header=None) -> bool:
    status, frame = send_frame(port, build_registers_read_full_register_pageframe(), OPERATION_READ)
    if not status:
        print(f"ERROR: Read registers failed on {port} (no ACK/timeout)")
        return False
    frame_data = process_frame(frame)
    if not frame_data:
        op = frame[1] if frame and len(frame) >= 2 else None
        if op is None:
            print(f"ERROR: Invalid/empty response frame on {port}")
        else:
            print(f"ERROR: Invalid frame/CRC on {port} (op=0x{op:02X}, len={len(frame)})")
        return False
    if not module.deserialize(frame_data):
        print(f"ERROR: Failed to deserialize register page (payload len={len(frame_data)})")
        return False

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

    return True
