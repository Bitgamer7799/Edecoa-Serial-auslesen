import binascii
import serial
import mysql.connector
import time

# Verbindung zur Datenbank herstellen
conn = mysql.connector.connect(
    host='SERVERIP',
    user='DATENBAMKUSER',
    password='DATENBANKPASSWORT',
    database='DATENBANK'
)

cursor = conn.cursor()


def crc16_xmodem(data: bytes) -> int:
    crc = 0x0000  # Initialwert
    for pos in data:
        crc ^= pos << 8
        for _ in range(8):
            if (crc & 0x8000) != 0:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
        crc &= 0xFFFF
    return crc

def calc_crc(command):
    crc = crc16_xmodem(command)
    crc_bytes = crc.to_bytes(2, 'big')
    crc = f"{crc:04X}".lower()
    crcb = crc[0] + crc[1]
    crca = crc[2] + crc[3]
    #print(f"CRC A: {crca}, CRC B: {crcb}")
    crc_bytes = bytes.fromhex(crcb + crca)
    full_command = command + crc_bytes + b'\r'
    return full_command


def sort_data(response):
    if response.startswith(b"("):
        response = response.split(b"(")
        response = response[1] #"(" am Anfang entfernen
        response = response.split(b" ") # Die einzelnen Parameter teilen

        ac_in_voltage = float(response[0].decode('utf-8'))
        ac_in_frequence = float(response[1].decode('utf-8'))
        ac_out_voltage = float(response[2].decode('utf-8'))
        ac_out_frequence = float(response[3].decode('utf-8'))
        apparent_power = float(response[4].decode('utf-8'))
        active_power = float(response[5].decode('utf-8'))
        load = float(response[6].decode('utf-8'))
        battery_voltage = float(response[8].decode('utf-8'))
        charging_current = float(response[9].decode('utf-8'))
        battery_remaining_capacity = float(response[10].decode('utf-8'))
        pv_in_current = float(response[12].decode('utf-8'))
        pv_in_voltage = float(response[13].decode('utf-8'))
        discharge_current = float(response[15].decode('utf-8'))

        return [ac_in_voltage, ac_in_frequence, ac_out_voltage, ac_out_frequence, apparent_power, active_power, load, battery_voltage, charging_current, battery_remaining_capacity, pv_in_current, pv_in_voltage, discharge_current]

try:
    print(f"Verbindung zum Wechselrichter wird über den PL2303 hergestellt.")
    ser = serial.Serial(
        'COM4', 2400, timeout=5,
        bytesize=serial.EIGHTBITS,  # 8 Datenbits
        parity=serial.PARITY_NONE,  # Keine Parität
        stopbits=serial.STOPBITS_ONE,  # 1 Stoppbit
    )

    while True:
        time.sleep(60)
        command = calc_crc(b"QPIGS")
        ser.write(command)

        response = ser.read(200)  # Liest bis zu 100 Bytes
        #print(f"Request: {command}, Answer: {response}")

        sql = """
            INSERT INTO solardaten (
                ac_in_voltage, 
                ac_in_frequence, 
                ac_out_voltage, 
                ac_out_frequence, 
                apparent_power, 
                active_power, 
                `load`, 
                battery_voltage, 
                charging_current, 
                battery_remaining_capacity, 
                pv_in_current, 
                pv_in_voltage, 
                discharge_current
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        data_list = sort_data(response)
        cursor.execute(sql, data_list)  # Führe das SQL-Insert-Statement aus
        conn.commit()  # Bestätige die Transaktion
        


        

except serial.SerialException as e:
    print(f"Fehler beim Öffnen der seriellen Verbindung: {e}")
except Exception as e:
    print(f"Ein unerwarteter Fehler ist aufgetreten: {e}")
except KeyboardInterrupt:
    print("Beenden durch Benutzer")
finally:
    cursor.close()
    conn.close()
