import struct
from registers import Registers, REGISTERS_PAGE_SIZE


class Module:
    def __init__(self):
        # Required simple byte fields
        self.register_map_ver_minor = 0
        self.register_map_ver_major = 0
        self.status = 0
        self.control = 0
        self.firmware_ver_minor = 0
        self.firmware_ver_major = 0
        # Float (32-bit) sensor values
        self._concentration = 0.0
        self._temperature = 0.0
        self._humidity = 0.0
        # Device id (u32)
        self.module_id = 0

    def __str__(self):
        fields = [
            ("Module ID", self.module_id),
            ("Register Map Version", f"{self.register_map_ver_major}.{self.register_map_ver_minor}"),
            ("Firmware Version", f"{self.firmware_ver_major}.{self.firmware_ver_minor}"),
            ("Status", f"0x{self.status:02X}"),
            ("Control", f"0x{self.control:02X}"),
            ("Concentration", f"{self.concentration:.6f}"),
            ("Temperature", f"{self.temperature:.6f}"),
            ("Humidity", f"{self.humidity:.6f}"),
        ]
        w = max(len(n) for n, _ in fields)
        return "\n".join(f"{n:<{w}} : {v}" for n, v in fields)

    # ------------- 32-bit float quantization & properties -------------
    @staticmethod
    def _as_f32(value):
        """Quantize a Python float to IEEE-754 single precision and return that value."""
        try:
            f = float(0.0 if value is None else value)
        except Exception:
            f = 0.0
        return struct.unpack('<f', struct.pack('<f', f))[0]

    def _get_concentration(self): return self._concentration
    def _set_concentration(self, v): self._concentration = self._as_f32(v)
    concentration = property(_get_concentration, _set_concentration)

    def _get_temperature(self): return self._temperature
    def _set_temperature(self, v): self._temperature = self._as_f32(v)
    temperature = property(_get_temperature, _set_temperature)

    def _get_humidity(self): return self._humidity
    def _set_humidity(self, v): self._humidity = self._as_f32(v)
    humidity = property(_get_humidity, _set_humidity)

    # Removed other properties (pressure, gain, zero_offset, calibration values etc.)

    # --------------------- Helpers ---------------------
    @staticmethod
    def _u16(data, lo, hi):
        return data[lo] | (data[hi] << 8)

    @staticmethod
    def _u32(data, b0, b1, b2, b3):
        return data[b0] | (data[b1] << 8) | (data[b2] << 16) | (data[b3] << 24)

    @staticmethod
    def _f32(data, b0, b1, b2, b3):
        return struct.unpack("<f", bytes([data[b0], data[b1], data[b2], data[b3]]))[0]

    # ------------------ Public API --------------------
    def deserialize(self, data):
        if len(data) < REGISTERS_PAGE_SIZE:
            return False
        self.register_map_ver_minor = data[Registers.REG_MAP_VER_LSB]
        self.register_map_ver_major = data[Registers.REG_MAP_VER_MSB]
        self.control = data[Registers.REG_CONTROL]
        self.status = data[Registers.REG_STATUS]
        self.firmware_ver_minor = data[Registers.REG_FIRMWARE_VER_LSB]
        self.firmware_ver_major = data[Registers.REG_FIRMWARE_VER_MSB]
        self.concentration = self._f32(
            data,
            Registers.REG_CONCENTRATION_LLSB,
            Registers.REG_CONCENTRATION_LMSB,
            Registers.REG_CONCENTRATION_MLSB,
            Registers.REG_CONCENTRATION_MMSB,
        )
        self.temperature = self._f32(
            data,
            Registers.REG_TEMPERATURE_LLSB,
            Registers.REG_TEMPERATURE_LMSB,
            Registers.REG_TEMPERATURE_MLSB,
            Registers.REG_TEMPERATURE_MMSB,
        )
        self.humidity = self._f32(
            data,
            Registers.REG_HUMIDITY_LLSB,
            Registers.REG_HUMIDITY_LMSB,
            Registers.REG_HUMIDITY_MLSB,
            Registers.REG_HUMIDITY_MMSB,
        )
        self.module_id = self._u32(
            data,
            Registers.REG_DEVICE_ID_LLSB,
            Registers.REG_DEVICE_ID_LMSB,
            Registers.REG_DEVICE_ID_MLSB,
            Registers.REG_DEVICE_ID_MMSB,
        )
        return True

    # Removed serialization/control helpers not needed for simple read-only client
    # ---- Minimal control helpers (reintroduced for measurement sequencing) ----
    def serialize_control(self):
        """Return address & single-byte control payload."""
        return Registers.REG_CONTROL, [int(self.control) & 0xFF]

    def control_start_measurement_set(self):
        self.control = 0x01  # oxygen measurement sequence

    def control_start_sht40_measurement_set(self):
        self.control = 0x02  # temperature/humidity measurement sequence

    def control_store_settings_to_flash(self):
        self.control = 0x04  # optional retained for compatibility
