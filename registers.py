from enum import IntEnum


class Registers(IntEnum):
    """Minimal register map containing only fields needed by the slimmed client."""
    # Version / control / status
    REG_MAP_VER_LSB = 0x00
    REG_MAP_VER_MSB = 0x01
    REG_FIRMWARE_VER_LSB = 0x02
    REG_FIRMWARE_VER_MSB = 0x03
    REG_CONTROL = 0x04
    REG_STATUS = 0x06  # original address preserved (0x05 was reserved)
    # Float32 sensor values
    REG_CONCENTRATION_LLSB = 0x08
    REG_CONCENTRATION_LMSB = 0x09
    REG_CONCENTRATION_MLSB = 0x0A
    REG_CONCENTRATION_MMSB = 0x0B
    REG_TEMPERATURE_LLSB = 0x0C
    REG_TEMPERATURE_LMSB = 0x0D
    REG_TEMPERATURE_MLSB = 0x0E
    REG_TEMPERATURE_MMSB = 0x0F
    REG_HUMIDITY_LLSB = 0x10
    REG_HUMIDITY_LMSB = 0x11
    REG_HUMIDITY_MLSB = 0x12
    REG_HUMIDITY_MMSB = 0x13
    # Device ID (u32) lives at high addresses; keep originals so hardware protocol still works
    REG_DEVICE_ID_LLSB = 0x7C
    REG_DEVICE_ID_LMSB = 0x7D
    REG_DEVICE_ID_MLSB = 0x7E
    REG_DEVICE_ID_MMSB = 0x7F
    # Keep overall page size constant (device may still send 256 bytes); we only parse what we define
    REG_LAST = 256


REGISTERS_PAGE_SIZE = Registers.REG_LAST  # still 256 bytes for full-page reads

