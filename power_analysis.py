import time
import threading
import logging
import configparser
import numpy as np
import matplotlib.pyplot as plt
from data_transmitter import get_telemetry_data

# Initialize a logger to record power analysis results and errors
logging.basicConfig(filename="power_analysis.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load configuration from the "config.ini" file
config = configparser.ConfigParser()
config.read("config.ini")

# Define global variables for power analysis data and thread control
power_analysis_data = {
    "voltage": [],
    "current": [],
    "power": [],
    "efficiency": []
}
plot_update_flag = threading.Event()

# Define a lock for thread safety when accessing power analysis data
power_analysis_lock = threading.Lock()

# Function to perform power analysis on telemetry data
def perform_power_analysis():
    while not plot_update_flag.is_set():
        try:
            # Retrieve the latest telemetry data from the data_transmitter script
            telemetry_data = get_telemetry_data()

            # Extract voltage and current from telemetry data
            voltage = telemetry_data.get("voltage", 0.0)
            current = telemetry_data.get("current", 0.0)

            # Calculate power and efficiency
            power = voltage * current
            efficiency = (power / (voltage * current)) * 100 if current != 0 else 0.0

            # Update the power analysis data dictionary
            with power_analysis_lock:
                power_analysis_data["voltage"].append(voltage)
                power_analysis_data["current"].append(current)
                power_analysis_data["power"].append(power)
                power_analysis_data["efficiency"].append(efficiency)

            # Log the power analysis results
            logging.info(f"Power: {power} W, Efficiency: {efficiency:.2f}%")

            time.sleep(config.getfloat("power_analysis", "update_interval"))

        except Exception as e:
            logging.error(f"Failed to perform power analysis: {str(e)}")
            time.sleep(1)  # Wait for a short duration before retrying

# Function to continuously plot power analysis results
def plot_power_analysis():
    while not plot_update_flag.is_set():
        try:
            # Extract power analysis data for plotting
            with power_analysis_lock:
                voltages = np.array(power_analysis_data["voltage"])
                powers = np.array(power_analysis_data["power"])
                efficiencies = np.array(power_analysis_data["efficiency"])

            # Create subplots for power and efficiency
            fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(10, 8), sharex=True)

            # Plot power data
            axes[0].plot(voltages, powers, label="Power (W)", color="blue")
            axes[0].set_ylabel("Power (W)")
            axes[0].grid()

            # Plot efficiency data
            axes[1].plot(voltages, efficiencies, label="Efficiency (%)", color="green")
            axes[1].set_xlabel("Voltage (V)")
            axes[1].set_ylabel("Efficiency (%)")
            axes[1].grid()

            # Set the title and adjust layout
            fig.suptitle("Power Analysis Results")
            plt.tight_layout()

            # Show the plot
            plt.show()

            # Wait for the specified interval before updating the plot again
            plot_update_flag.wait(timeout=config.getfloat("power_analysis", "plot_update_interval"))

        except Exception as e:
            logging.error(f"Failed to plot power analysis results: {str(e)}")
            time.sleep(1)  # Wait for a short duration before retrying

# Function to gracefully stop the power analysis and plot threads
def stop_power_analysis():
    plot_update_flag.set()

if __name__ == "__main__":
    try:
        # Start the power analysis thread
        power_analysis_thread = threading.Thread(target=perform_power_analysis)
        power_analysis_thread.start()

        # Start the power analysis plot thread
        plot_thread = threading.Thread(target=plot_power_analysis)
        plot_thread.start()

        # Run the script for a specified duration (e.g., 30 seconds)
        time.sleep(config.getfloat("power_analysis", "run_duration"))

    except KeyboardInterrupt:
        print("Power analysis interrupted by user.")

    finally:
        # Stop the power analysis and plot threads gracefully
        stop_power_analysis()
