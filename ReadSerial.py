import serial
import time
import re

def read_serial_data(shared_data, port='COM3', baud_rate=9600):
    patterns = {
        'TEMP': re.compile(r"TEMP=(\d+(\.\d+)?)"),
        'HUM': re.compile(r"HUM=(\d+(\.\d+)?)"),
        'LIGHT': re.compile(r"LIGHT=(\d+)"),
        'SOUND': re.compile(r"SOUND=(\d+)"),
        'DIST': re.compile(r"DIST=(\d+)")
    }

    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        time.sleep(2)
        print(f"[Serial] Connected to {port}")

        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                line = line.replace(">>", "").strip()
               # print(f"[CLEANED] {line}")

                if match := patterns['TEMP'].search(line):
                    shared_data['temperature'] = float(match.group(1))
                    #print("[UPDATED] Temp =", shared_data['temperature'])

                elif match := patterns['HUM'].search(line):
                    shared_data['humidity'] = float(match.group(1))
                  #  print("[UPDATED] Hum =", shared_data['humidity'])

                elif match := patterns['LIGHT'].search(line):
                    shared_data['light'] = int(match.group(1))
                   # print("[UPDATED] Light =", shared_data['light'])

                elif match := patterns['SOUND'].search(line):
                    shared_data['sound_analog'] = int(match.group(1))
                   # print("[UPDATED] Sound =", shared_data['sound_analog'])

                elif match := patterns['DIST'].search(line):
                    shared_data['distance'] = int(match.group(1))
                    #print("[UPDATED] Distance =", shared_data['distance'])

            #time.sleep(0.3)

    except Exception as e:
        print("[Serial Error]", e)
