# dashboard.py
import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import plotly.graph_objs as go
from threading import Thread
from ReadSerial import read_serial_data
import time
from threading import Thread
from PowerBISender import PowerBISender
from mysql_logger import MySQLLogger
from ElapsedTimeLogger import ElapsedTimeLogger

# instance of the logger
logger = ElapsedTimeLogger('localhost', 'root', '123456', 'iot')

# Shared dictionary for sensor values
shared_data = {
    'temperature': 0,
    'humidity': 0,
    'light': 0,
    'sound_analog': 0,
    'distance': 0
}

# Start the serial sensor reading in a background thread
reader_thread = Thread(target=read_serial_data, args=(shared_data,), daemon=True)
reader_thread.start()

# SET the url like a SYSTEM variable or in another File- SHOULD NOT BE SUBMITTED IN THE DOCUMENT!!!!
power_bi_url = "https://api.powerbi.com/beta/f0033efe-d82e-4c5f-a712-3a3948bb453e/daXE"
# background thread sends a POST to Power BI
powerbi = PowerBISender(power_bi_url, shared_data)
power_bi_thread = Thread(target=powerbi.power_bi_post, daemon=True)
power_bi_thread.start()

# MySQL Logger thread stores data in the DB
mysql_logger = MySQLLogger(shared_data)
mysql_thread = Thread(target=mysql_logger.run, daemon=True)
mysql_thread.start()



#  Dash app
app = dash.Dash(__name__)
app.title = "IoT Sensors Dashboard" 

# Global variables 
temperature_values = []
humidity_values = []
timestamps = []
light_values = []
light_timestamps = []

# HTML Layout with CSS
app.layout = html.Div([ 
    html.H1("IoT Sensor Dashboard", style={'textAlign': 'center'}),

    dcc.Interval(id='interval', interval=200, n_intervals=0),

    html.Div([
        dcc.Graph(id='temperature', style={'width': '50%', 'height': '300px'}),
        dcc.Graph(id='humidity', style={'width': '50%', 'height': '300px'})
    ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around'}),

    html.Div([
        dcc.Graph(id='light', style={'width': '50%', 'height': '300px'}),
        dcc.Graph(id='sound', style={'width': '50%', 'height': '300px'})
    ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around'}),

    html.Div([
    html.Div(
        dcc.Graph(id='light-gauge', style={'width': '100%', 'height': '300px'}),
        style={'flex': '1', 'minWidth': '300px', 'maxWidth': '600px', 'padding': '10px'}
    ),
    html.Div(
        dcc.Graph(id='distance', style={'width': '100%', 'height': '300px'}),
        style={'flex': '1', 'minWidth': '300px', 'maxWidth': '600px', 'padding': '10px'}
    )
], style={
    'display': 'flex',
    'flexWrap': 'wrap',
    'justifyContent': 'center'
})

])

# Callback to update graphs
@app.callback(Output('light-gauge', 'figure'),[Input('interval', 'n_intervals')])
@logger.log_function_time  # Apply the decorator
def update_light_gauge_graph(n):
    light = shared_data.get("light", 0)
    light_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=light,
        title={"text": "Light Intensity"},
        gauge={"axis": {"range": [0, 1023]}}
    ))
    return light_gauge

@app.callback(Output('distance', 'figure'),[Input('interval', 'n_intervals')])
@logger.log_function_time  # Apply the decorator
def update_distance_graph(n):
    dist = shared_data.get("distance", 0)
    # Distance gauge
    dist_fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=dist,
        title={"text": "Distance (cm)"},
        gauge={"axis": {"range": [2, 400]}}
    ))
    return dist_fig

@app.callback(Output('sound', 'figure'),[Input('interval', 'n_intervals')])
@logger.log_function_time  
def update_sound_graph(n):
    sound = shared_data.get("sound_analog", 0)
    sound_fig = go.Figure(go.Bar(
        x=["Sound"],
        y=[sound],
        marker_color="mediumvioletred"
    ))
    sound_fig.update_layout(
        title="Sound Level (Analog)",
        yaxis_title="Value",
        yaxis=dict(range=[0, 1023])
    )
    return sound_fig


@app.callback(Output('light', 'figure'),[Input('interval', 'n_intervals')])
@logger.log_function_time  
def update_light_graph(n):
     #  light history tracking
    light = shared_data.get("light", 0)
    light_values.append(light)
    light_timestamps.append(n)

# Limit history to last 100  reading
    if len(light_values) > 100:
        light_values.pop(0)
        light_timestamps.pop(0)

     # Light line chart
    light_fig = go.Figure()
    light_fig.add_trace(go.Scatter(
        x=light_timestamps,
        y=light_values,
        mode='lines+markers',
        name='Light Intensity',
        line=dict(color='gold')
    ))

    light_fig.update_layout(
        title="Real-Time Light Intensity",
        xaxis_title="Time (s)",
        yaxis_title="Intensity",
        yaxis=dict(range=[0, 1023]),
        xaxis=dict(range=[max(0, n-100), n])  # Shows only the last 100 readings
    )
    return light_fig


@app.callback(
    [Output('temperature', 'figure'), Output('humidity', 'figure')],
    [Input('interval', 'n_intervals')]
)
@logger.log_function_time
def update_temp_humidity_graph(n):

    temp = shared_data.get("temperature", 0)
    hum = shared_data.get("humidity", 0)
    # Track temperature history
    temperature_values.append(temp)
    humidity_values.append(hum)
    timestamps.append(n)

    # Limit to last 100 readings
    if len(temperature_values) > 100:
        temperature_values.pop(0)
        humidity_values.pop(0)
        timestamps.pop(0)
    
    # Temperature and Humidity in one chart with two axis
    temp_fig = go.Figure()

    # Temperature left Y-axis
    temp_fig.add_trace(go.Scatter(
        x=timestamps,
        y=temperature_values,
        mode='lines+markers',
        name='Temperature (°C)',
        line=dict(color='red'),
        yaxis='y1'
    ))

    # Humidity right Y-axis
    temp_fig.add_trace(go.Scatter(
        x=timestamps,
        y=humidity_values,
        mode='lines+markers',
        name='Humidity (%)',
        line=dict(color='blue'),
        yaxis='y2'
    ))

    # Layout with two y-axes
    temp_fig.update_layout(
        title="Temperature and Humidity Over Time",
        xaxis=dict(title="Time in seconds"),\
        yaxis=dict(
            title=dict(text="Temperature (°C)", font=dict(color='red')),
            range=[0, 50],
            tickfont=dict(color='red')
        ),
        yaxis2=dict(
            title=dict(text="Humidity (%)", font=dict(color='blue')),
            range=[0, 100],
            tickfont=dict(color='blue'),
            overlaying='y',
            side='right'
        ),
        legend=dict(x=0.01, y=0.99)
    )

    # Humidity bar + comfort zone
    hum_fig = go.Figure()

    #Humidity Bar
    hum_fig.add_trace(go.Bar(
        x=["Humidity"],
        y=[hum],
        name="Humidity",
        marker_color="blue"
    ))

    # Temperature Bar
    hum_fig.add_trace(go.Bar(
        x=["Temperature"],
        y=[temp],
        name="Temperature",
        marker_color="red"
    ))

    # Comfort zone for Humidity
    hum_fig.add_shape(
        type="rect",
        x0=-0.5,
        x1=0.5,
        y0=30,
        y1=60,
        fillcolor="LightSkyBlue",
        opacity=0.3,
        line_width=0
    )

    # Layout
    hum_fig.update_layout(
        title="Humidity and Temperature Levels",
        yaxis_title="Value",
        yaxis=dict(range=[0, max(100, temp + 10)]),  
        barmode='group',
        legend=dict(x=0.8, y=1.1)
    )   

    return temp_fig, hum_fig, 


# Run the app
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
    
