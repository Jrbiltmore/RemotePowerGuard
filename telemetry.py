import random
import time
import threading
import logging
import numpy as np
import matplotlib.pyplot as plt

telemetry_data = {
    "voltage": 0.0,
    "current": 0.0,
    "temperature": 0.0
}

telemetry_lock = threading.Lock()
telemetry_logger = logging.getLogger("TelemetryDataLogger")
telemetry_logger.setLevel(logging.INFO)
telemetry_file_handler = logging.FileHandler("telemetry_data.log")
telemetry_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
telemetry_file_handler.setFormatter(telemetry_formatter)
telemetry_logger.addHandler(telemetry_file_handler)

def update_telemetry_data():
    global telemetry_data
    while True:
        voltage = round(random.uniform(10.0, 13.0), 2)
        current = round(random.uniform(1.5, 2.5), 2)
        temperature = round(random.uniform(25.0, 35.0), 1)
        with telemetry_lock:
            telemetry_data["voltage"] = voltage
            telemetry_data["current"] = current
            telemetry_data["temperature"] = temperature
        telemetry_logger.info(f"Voltage: {voltage} V, Current: {current} A, Temperature: {temperature} °C")
        time.sleep(0.5)

def get_telemetry_data():
    global telemetry_data
    with telemetry_lock:
        return telemetry_data.copy()

def start_telemetry_update_thread():
    telemetry_thread = threading.Thread(target=update_telemetry_data)
    telemetry_thread.start()

def voltage_filter(key, value):
    return 10.5 <= value <= 12.5

def temperature_filter(key, value):
    return value > 30.0

def handle_telemetry_event(event_callback):
    event = random.choice(["voltage_change", "temperature_change"])
    if event == "voltage_change":
        voltage = round(random.uniform(10.0, 13.0), 2)
        event_callback(event, voltage)
    elif event == "temperature_change":
        temperature = round(random.uniform(25.0, 35.0), 1)
        event_callback(event, temperature)

def start_telemetry_event_handler_thread(event_callback):
    event_handler_thread = threading.Thread(target=telemetry_event_handler, args=(event_callback,))
    event_handler_thread.start()

def telemetry_event_handler(event_callback):
    while True:
        handle_telemetry_event(event_callback)
        time.sleep(5)

def perform_power_analysis(telemetry_data):
    voltage = telemetry_data.get("voltage", 0.0)
    current = telemetry_data.get("current", 0.0)
    power = voltage * current
    efficiency = (power / (voltage * current)) * 100 if current != 0 else 0.0
    power_analysis_results = {
        "voltage": voltage,
        "current": current,
        "power": power,
        "efficiency": efficiency
    }
    return power_analysis_results

def display_power_analysis_results(power_analysis_results):
    if power_analysis_results:
        # Assuming you have labels or text fields to display the results
        voltage_label.setText(f"Voltage: {power_analysis_results['voltage']} V")
        current_label.setText(f"Current: {power_analysis_results['current']} A")
        power_label.setText(f"Power: {power_analysis_results['power']} W")
        efficiency_label.setText(f"Efficiency: {power_analysis_results['efficiency']} %")
    else:
        voltage_label.setText("Voltage: N/A")
        current_label.setText("Current: N/A")
        power_label.setText("Power: N/A")
        efficiency_label.setText("Efficiency: N/A")

def plot_telemetry_data():
    telemetry_data = get_telemetry_data()
    time_stamps = [time.time()]
    voltages = [telemetry_data.get("voltage", 0.0)]
    currents = [telemetry_data.get("current", 0.0)]
    temperatures = [telemetry_data.get("temperature", 0.0)]
    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(10, 8), sharex=True)
    axes[0].plot(time_stamps, voltages, label="Voltage (V)", color="blue")
    axes[0].set_ylabel("Voltage (V)")
    axes[1].plot(time_stamps, currents, label="Current (A)", color="green")
    axes[1].set_ylabel("Current (A)")
    axes[2].plot(time_stamps, temperatures, label="Temperature (°C)", color="red")
    axes[2].set_ylabel("Temperature (°C)")
    axes[-1].set_xlabel("Time")
    fig.suptitle("Telemetry Data Over Time")
    for ax in axes:
        ax.legend()
        ax.grid()
    plt.show()

def log_telemetry_data(telemetry_data):
    try:
        with open("telemetry_data.csv", "a") as file:
            timestamp = time.time()
            voltage = telemetry_data.get("voltage", 0.0)
            current = telemetry_data.get("current", 0.0)
            temperature = telemetry_data.get("temperature", 0.0)
            file.write(f"{timestamp},{voltage},{current},{temperature}\n")

    except Exception as e:
        logging.error(f"Failed to log telemetry data: {str(e)}")

def visualize_telemetry_data():
    try:
        with open("telemetry_data.csv", "r") as file:
            data = np.loadtxt(file, delimiter=",", skiprows=1)
            timestamps = data[:, 0]
            voltages = data[:, 1]
            currents = data[:, 2]
            temperatures = data[:, 3]
            plt.figure(figsize=(12, 6))
            plt.subplot(3, 1, 1)
            plt.plot(timestamps, voltages, label="Voltage (V)")
            plt.xlabel("Timestamp")
            plt.ylabel("Voltage (V)")
            plt.legend()
            plt.subplot(3, 1, 2)
            plt.plot(timestamps, currents, label="Current (A)")
            plt.xlabel("Timestamp")
            plt.ylabel("Current (A)")
            plt.legend()
            plt.subplot(3, 1, 3)
            plt.plot(timestamps, temperatures, label="Temperature (°C)")
            plt.xlabel("Timestamp")
            plt.ylabel("Temperature (°C)")
            plt.legend()
            plt.tight_layout()
            plt.show()

    except Exception as e:
        logging.error(f"Failed to visualize telemetry data: {str(e)}")

if __name__ == "__main__":
    start_telemetry_update_thread()
    start_telemetry_event_handler_thread(handle_telemetry_event)

    while True:
        try:
            telemetry_data = get_telemetry_data()
            power_analysis_results = perform_power_analysis(telemetry_data)
            display_power_analysis_results(power_analysis_results)
            log_telemetry_data(telemetry_data)
            time.sleep(5)

        except KeyboardInterrupt:
            logging.info("Power analysis interrupted by user.")
            break

        except Exception as e:
            logging.error(f"Failed to perform power analysis: {str(e)}")
            display_error("An error occurred while performing power analysis.")
            time.sleep(1)

    stop_telemetry_update_thread()
    visualize_telemetry_data()
