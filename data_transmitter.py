import random
import time
import threading
import requests
import logging
import configparser

# Initialize a logger to record telemetry data and errors
logging.basicConfig(filename="telemetry.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load configuration from the "config.ini" file
config = configparser.ConfigParser()
config.read("config.ini")

# Define global variables for telemetry data
telemetry_data = {
    "voltage": 0.0,
    "current": 0.0,
    "temperature": 0.0
}

# Define a lock for thread safety when accessing telemetry data
telemetry_lock = threading.Lock()

# Function to continuously update telemetry data from the drone
def update_telemetry_data():
    global telemetry_data
    while True:
        try:
            # Simulate data retrieval from the drone (replace this with actual drone communication)
            voltage = round(random.uniform(config.getfloat("data_generation", "min_voltage"), config.getfloat("data_generation", "max_voltage")), 2)
            current = round(random.uniform(config.getfloat("data_generation", "min_current"), config.getfloat("data_generation", "max_current")), 2)
            temperature = round(random.uniform(config.getfloat("data_generation", "min_temperature"), config.getfloat("data_generation", "max_temperature")), 1)

            # Update the telemetry data dictionary
            with telemetry_lock:
                telemetry_data["voltage"] = voltage
                telemetry_data["current"] = current
                telemetry_data["temperature"] = temperature

            # Log the telemetry data
            logging.info(f"Voltage: {voltage} V, Current: {current} A, Temperature: {temperature} °C")

            time.sleep(config.getfloat("data_generation", "update_interval"))

        except Exception as e:
            logging.error(f"Failed to update telemetry data: {str(e)}")
            time.sleep(1)  # Wait for a short duration before retrying

# Function to get the latest telemetry data
def get_telemetry_data():
    global telemetry_data
    with telemetry_lock:
        return telemetry_data.copy()

# Function to start the telemetry data update thread
def start_telemetry_update_thread():
    telemetry_thread = threading.Thread(target=update_telemetry_data)
    telemetry_thread.start()

# Function to send telemetry data to a server
def send_telemetry_data(data):
    try:
        # Replace "http://your_server_url/telemetry" with the actual endpoint URL to your server
        response = requests.post(config.get("server", "endpoint"), json=data)

        # Check if the data was successfully transmitted (status code 200)
        if response.status_code == 200:
            print("Telemetry data transmitted successfully:", data)
        else:
            print("Failed to transmit telemetry data:", response.text)

    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to transmit telemetry data: {str(e)}")

# Function to continuously transmit telemetry data to a server
def transmit_telemetry_data():
    while True:
        telemetry_data = get_telemetry_data()
        send_telemetry_data(telemetry_data)
        time.sleep(config.getfloat("server", "transmission_interval"))

if __name__ == "__main__":
    start_telemetry_update_thread()
    transmit_telemetry_data()
