# MySQLLogger.py
import mysql.connector
from datetime import datetime
import time

class MySQLLogger:
    def __init__(self, shared_data, interval=1):
        self.shared_data = shared_data
        self.interval = interval

    def run(self):
        while True:
            try:
                conn = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="123456",  
                    database="iot"
                )
                cursor = conn.cursor()

                query = """
                    INSERT INTO sensor_data (timestamp, temperature, humidity, light, sound, distance)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                data = (
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    float(self.shared_data.get('temperature', 0)),
                    float(self.shared_data.get('humidity', 0)),
                    int(self.shared_data.get('light', 0)),
                    int(self.shared_data.get('sound_analog', 0)),
                    int(self.shared_data.get('distance', 0)),
                )
                cursor.execute(query, data)
                conn.commit()
                conn.close()
                print("MySQL row inserted.")
            except Exception as e:
                print(f"MySQL insert failed: {e}")

            time.sleep(self.interval)


                
