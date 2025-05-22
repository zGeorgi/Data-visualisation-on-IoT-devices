# Data-visualisation-on-IoT-devices
![image](https://github.com/user-attachments/assets/29f36eb0-3226-48cd-af24-8107d80eccbd)
Flowchart
Explanations:
1.	Start Elegoo UNO R3- start reading environmental data and send it to the dashboard
2.	Start the Custom Python Dashboard
a.	Thread 1: reads the incoming data and stores it in the shared dictionary
b.	Thread 2: send data to Power BI Service
c.	Thread 3: store sensor data in the database (table: sensor_data)
3.	Main program: update the incoming data on different visuals in the browser (with local server)
4.	Time logger: measure the execution of the callback functions in the main program and the response time from the Power BI service. It also stores the logs in the function_timings database table.
5.	Tableau: By manual refresh, retrieve data from the database and display it in visuals
6.	End: stopping the program
![image](https://github.com/user-attachments/assets/75500f1a-7e7e-4268-bb45-fa44a8034b4f)
![image](https://github.com/user-attachments/assets/3bc384b2-51b5-47c4-905f-3d382d462565)
