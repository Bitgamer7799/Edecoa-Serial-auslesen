import binascii
import serial

def crc16_xmodem(data: bytes) -> int:
    crc = 0x0000  # Initialwert
    for pos in data:
        crc ^= pos << 8
        for _ in range(8):
            if (crc & 0x8000) != 0:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
        crc &= 0xFFFF  # Sicherstellen, dass crc 16-bit bleibt
    return crc

def calc_crc(command):
    crc = crc16_xmodem(command)
    crc_bytes = crc.to_bytes(2, 'big')
    crc = f"{crc:04X}".lower()
    crcb = crc[0] + crc[1]
    crca = crc[2] + crc[3]
    print(f"CRC A: {crca}, CRC B: {crcb}")
    crc_bytes = bytes.fromhex(crcb + crca)
    full_command = command + crc_bytes + b'\r'
    return full_command



try:
    print(f"Verbindung zum Wechselrichter wird über den PL2303 hergestellt.")
    ser = serial.Serial(
        'COM4', 2400, timeout=5,
        bytesize=serial.EIGHTBITS,  # 8 Datenbits
        parity=serial.PARITY_NONE,  # Keine Parität
        stopbits=serial.STOPBITS_ONE,  # 1 Stoppbit
    )

    while True:
        command = calc_crc(b"QPIGS")
        ser.write(command)

        response = ser.read(200)  # Liest bis zu 100 Bytes
        
        if response.startswith(b"("):
            print(f"Request: {command}, Answer: {response}")
            print(response.split(b"'"))

except serial.SerialException as e:
    print(f"Fehler beim Öffnen der seriellen Verbindung: {e}")
except Exception as e:
    print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")



