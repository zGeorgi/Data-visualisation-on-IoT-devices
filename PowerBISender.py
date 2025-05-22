import requests
import json
import time
from datetime import datetime, timezone
import mysql.connector

class PowerBISender:
    def __init__(self, url, shared_data):
        self.url = url
        self.shared_data = shared_data
        self.headers = {"Content-Type": "application/json"}

   
    def power_bi_post(self):
        while True:
            iso_time = datetime.now(timezone.utc).isoformat(timespec='milliseconds')
            payload = [{
                "Date": iso_time,
                "Humidity": self.shared_data.get("humidity", 0),
                "Distance": self.shared_data.get("distance", 0),
                "Photoresistor": self.shared_data.get("light", 0),  
                "Temperature": self.shared_data.get("temperature", 0),
                "Sound": self.shared_data.get("sound_analog", 0),
                "Request_time": str(iso_time)
            }] 

            start_time = time.time()
            try:
                print(json.dumps(payload, indent=2))

                response = requests.post(self.url, headers=self.headers, data=json.dumps(payload))
                elapsed_time = time.time() - start_time
                 # Store elapsed time in shared data
                self.shared_data['response_time'] = elapsed_time
                log_to_function_timings("power_bi_post", elapsed_time)

                print(f"[Power BI] Status: {response.status_code}, Time Taken: {elapsed_time} seconds")
            except Exception as e:
                print("[Power BI Error]", e)

            time.sleep(0.2)


def log_to_function_timings(function_name, elapsed_time):
    try:
        conn = mysql.connector.connect(
            host ="localhost",
            user ="root",
            password ="123456",
            database ="iot"
        )
        cursor = conn.cursor()
        query = "INSERT INTO function_timings (function_name, elapsed_time) VALUES (%s, %s)"
        cursor.execute(query, (function_name, elapsed_time))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("[MySQL Log Error]", e)
