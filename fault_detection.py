import time
import threading
import logging
import configparser
import smtplib
from email.mime.text import MIMEText
from data_transmitter import get_telemetry_data

# Initialize a logger to record fault detection results and errors
logging.basicConfig(filename="fault_detection.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load configuration from the "config.ini" file
config = configparser.ConfigParser()
config.read("config.ini")

# Function to perform fault detection on telemetry data
def perform_fault_detection():
    while True:
        try:
            # Retrieve the latest telemetry data from the data_transmitter script
            telemetry_data = get_telemetry_data()

            # Extract voltage, current, and temperature from telemetry data
            voltage = telemetry_data.get("voltage", 0.0)
            current = telemetry_data.get("current", 0.0)
            temperature = telemetry_data.get("temperature", 0.0)

            # Check for potential faults or anomalies in the telemetry data
            check_voltage_fault(voltage)
            check_current_fault(current)
            check_temperature_fault(temperature)

            time.sleep(config.getfloat("fault_detection", "update_interval"))

        except Exception as e:
            logging.error(f"Failed to perform fault detection: {str(e)}")
            time.sleep(1)  # Wait for a short duration before retrying

# Function to check for voltage faults
def check_voltage_fault(voltage):
    min_voltage = config.getfloat("fault_detection", "min_voltage")
    max_voltage = config.getfloat("fault_detection", "max_voltage")
    if voltage < min_voltage or voltage > max_voltage:
        logging.warning(f"Potential voltage fault detected: {voltage} V")
        send_email_notification(f"Potential voltage fault detected: {voltage} V")

# Function to check for current faults
def check_current_fault(current):
    min_current = config.getfloat("fault_detection", "min_current")
    max_current = config.getfloat("fault_detection", "max_current")
    if current < min_current or current > max_current:
        logging.warning(f"Potential current fault detected: {current} A")
        send_email_notification(f"Potential current fault detected: {current} A")

# Function to check for temperature faults
def check_temperature_fault(temperature):
    min_temperature = config.getfloat("fault_detection", "min_temperature")
    max_temperature = config.getfloat("fault_detection", "max_temperature")
    if temperature < min_temperature or temperature > max_temperature:
        logging.warning(f"Potential temperature fault detected: {temperature} °C")
        send_email_notification(f"Potential temperature fault detected: {temperature} °C")

# Function to send email notifications
def send_email_notification(message):
    try:
        sender_email = config.get("email_notification", "sender_email")
        receiver_email = config.get("email_notification", "receiver_email")
        smtp_server = config.get("email_notification", "smtp_server")
        smtp_port = config.getint("email_notification", "smtp_port")
        smtp_username = config.get("email_notification", "smtp_username")
        smtp_password = config.get("email_notification", "smtp_password")

        msg = MIMEText(message)
        msg['Subject'] = 'Drone Fault Detected'
        msg['From'] = sender_email
        msg['To'] = receiver_email

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, [receiver_email], msg.as_string())

        logging.info("Email notification sent.")

    except Exception as e:
        logging.error(f"Failed to send email notification: {str(e)}")

if __name__ == "__main__":
    # Start the fault detection thread
    fault_detection_thread = threading.Thread(target=perform_fault_detection)
    fault_detection_thread.start()
