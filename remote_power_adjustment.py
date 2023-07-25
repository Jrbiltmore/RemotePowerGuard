# remote_power_adjustment.py
import time
import threading
import logging
import configparser
import random
import requests
from urllib3.exceptions import NewConnectionError

# Initialize a logger for recording power adjustments and errors
logging.basicConfig(filename="power_adjustment.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Function to load configuration from the "config.ini" file
def load_configuration():
    config = configparser.ConfigParser()
    config.read("config.ini")

    # Define global variable for power settings
    power_settings = {
        "voltage": config.getfloat("default_power_settings", "voltage"),
        "current": config.getfloat("default_power_settings", "current")
    }

    # Define global variables for power range, adjustment interval, and telemetry power reserve
    power_range = {
        "min_voltage": config.getfloat("power_range", "min_voltage"),
        "max_voltage": config.getfloat("power_range", "max_voltage"),
        "min_current": config.getfloat("power_range", "min_current"),
        "max_current": config.getfloat("power_range", "max_current")
    }

    adjustment_interval = config.getfloat("power_adjustment", "adjustment_interval")
    telemetry_power_reserve = config.getfloat("power_adjustment", "telemetry_power_reserve")

    return power_settings, power_range, adjustment_interval, telemetry_power_reserve

# Function to adjust the drone's power settings using HTTP request
def adjust_power_http(voltage, current):
    global power_settings
    logging.info(f"Adjusting power settings: Voltage={voltage} V, Current={current} A")

    # Replace the URL and API endpoint with the actual API endpoint of the drone's control system
    api_url = "https://drone-control-api.example.com/adjust_power"
    payload = {
        "voltage": voltage,
        "current": current
    }

    try:
        response = requests.post(api_url, json=payload)

        if response.status_code == 200:
            power_settings["voltage"] = voltage
            power_settings["current"] = current
            logging.info("Power settings adjusted successfully.")
        else:
            logging.error(f"Failed to adjust power settings. Status code: {response.status_code}")

    except (requests.exceptions.RequestException, NewConnectionError) as e:
        logging.error(f"Failed to make the HTTP request: {str(e)}")

# Function to reserve power for telemetry transmission and combat mode
def reserve_power(telemetry_distance, combat_mode=False):
    global power_settings, telemetry_power_reserve

    # Calculate the power required for telemetry transmission
    min_voltage_telemetry = power_settings["voltage"] - telemetry_power_reserve
    min_current_telemetry = power_settings["current"] - telemetry_power_reserve

    # Calculate the power required to reach within 1 kilometer of the origination in combat mode
    if combat_mode:
        combat_mode_power_reserve = 1.5  # Adjust this value based on combat mode requirements
        min_voltage_combat_mode = power_settings["voltage"] - combat_mode_power_reserve
        min_current_combat_mode = power_settings["current"] - combat_mode_power_reserve

        # Check if there's enough power for both telemetry and combat mode
        if min_voltage_combat_mode >= power_range["min_voltage"] and min_current_combat_mode >= power_range["min_current"]:
            power_settings["voltage"] = min_voltage_combat_mode
            power_settings["current"] = min_current_combat_mode
        else:
            logging.warning("Not enough power for both telemetry and combat mode.")
            # Use only the reserve power for telemetry transmission
            power_settings["voltage"] = min(min_voltage_telemetry, power_range["max_voltage"])
            power_settings["current"] = min(min_current_telemetry, power_range["max_current"])
    else:
        # Use only the reserve power for telemetry transmission
        power_settings["voltage"] = min(min_voltage_telemetry, power_range["max_voltage"])
        power_settings["current"] = min(min_current_telemetry, power_range["max_current"])

    # Ensure that power settings stay within the specified power range
    power_settings["voltage"] = max(power_range["min_voltage"], power_settings["voltage"])
    power_settings["current"] = max(power_range["min_current"], power_settings["current"])

# Function to simulate remote power adjustment commands
def simulate_remote_power_adjustment(power_range, adjustment_interval, stop_event):
    while not stop_event.is_set():
        try:
            # Simulate random power adjustment commands
            voltage = round(random.uniform(power_range["min_voltage"], power_range["max_voltage"]), 2)
            current = round(random.uniform(power_range["min_current"], power_range["max_current"]), 2)

            # Reserve power for telemetry transmission
            reserve_power(telemetry_distance=0.5, combat_mode=True)

            # Send power adjustment command to the drone via HTTP request
            adjust_power_http(power_settings["voltage"], power_settings["current"])

            time.sleep(adjustment_interval)

        except Exception as e:
            logging.error(f"Failed to adjust power settings: {str(e)}")
            time.sleep(1)  # Wait for a short duration before retrying

if __name__ == "__main__":
    # Load configuration from the "config.ini" file
    power_settings, power_range, adjustment_interval, telemetry_power_reserve = load_configuration()

    # Start the remote power adjustment thread
    stop_event = threading.Event()
    remote_power_adjustment_thread = threading.Thread(target=simulate_remote_power_adjustment, args=(power_range, adjustment_interval, stop_event))
    remote_power_adjustment_thread.start()

    try:
        # Simulate a user interface to stop the power adjustment simulation
        while True:
            user_input = input("Enter 'stop' to stop the power adjustment simulation: ")
            if user_input.lower() == "stop":
                stop_event.set()
                break
            else:
                print("Invalid input. Please enter 'stop' to stop the simulation.")

    except KeyboardInterrupt:
        stop_event.set()
        logging.info("Power adjustment simulation interrupted by the user.")
