#!/usr/bin/env python3
#
# wingardiumreviosa.py - Version 1.0 - 202401281915 - Update
#
import os
import time
import logging
from datetime import datetime
import configparser
import subprocess
import pymysql

def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['database']

# Constants
DEFAULT_DATA_SIZE_MB = 1  # Default size of data to write/read
DATA_PATTERN = "01"  # Data pattern to write (alternating 0s and 1s)
LOG_FILE_NAME = "wingardiumreviosa-" + datetime.now().strftime("%Y%m%d%H%M%S") + ".log"

# Configure logging
logging.basicConfig(filename=LOG_FILE_NAME, level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s')

def collect_host_info():
    def run_command(command):
        try:
            result = subprocess.check_output(command, shell=True).decode().strip()
            logging.info(f"Command '{command}' executed successfully.")
            return result
        except subprocess.CalledProcessError as e:
            logging.error(f"Command '{command}' failed to execute: {e}")
            return None

    serial = run_command("grep -m 1 'Serial' /proc/cpuinfo | cut -d ':' -f2 | sed 's/^[ \t]*//'")
    if not serial:
        serial = 'N/A'
        logging.info("Serial number not found, set to 'N/A'.")

    proc_model = run_command("grep -m 1 'model name' /proc/cpuinfo | cut -d ':' -f2 | sed 's/^[ \t]*//'")
    if not proc_model:
        proc_model = run_command("grep -m 1 'Revision' /proc/cpuinfo | cut -d ':' -f2 | sed 's/^[ \t]*//'")
        if not proc_model:
            proc_model = 'N/A'
            logging.info("Processor model not found, set to 'N/A'.")

    disk_usage_root = run_command("df -ah | grep '\/$'")
    if not disk_usage_root:
        disk_usage_root = 'N/A'
        logging.info("Disk usage for root not found, set to 'N/A'.")

    nic_mac = run_command("ip link show $(ip route show default | awk '/default/ {print $5}') | awk '/ether/ {print $2}'")
    if not nic_mac:
        nic_mac = 'N/A'
        logging.info("NIC MAC address not found, set to 'N/A'.")

    nic_ip = run_command("ip -4 addr show $(ip route show default | awk '/default/ {print $5}') | grep -oP '(?<=inet\s)\d+(\.\d+){3}'")
    if not nic_ip:
        nic_ip = 'N/A'
        logging.info("NIC IP address not found, set to 'N/A'.")

    host_info = {
        'timestamp': datetime.now().strftime("%Y%m%d%H%M%S"),
        'hostname': run_command('hostname'),
        'serial': serial,
        'model': run_command("cat /proc/device-tree/model") or 'N/A',
        'proc_count': int(run_command("grep -c ^processor /proc/cpuinfo") or 0),
        'proc_model': proc_model,
        'disk_usage_root': disk_usage_root,
        'total_ram': run_command("free | grep Mem: | awk '{print $2}'") or '0',
        'nic_mac': nic_mac,
        'nic_ip': nic_ip,
    }

    logging.info(f"Collected host information: {host_info}")
    return host_info

def connect_to_database(config):
    return pymysql.connect(host=config['host'], user=config['user'], password=config['password'])

def check_and_create_database(cursor):
    cursor.execute("CREATE DATABASE IF NOT EXISTS {hostname}_wingardiumreviosa")

def check_and_create_tables(cursor):
    cursor.execute("CREATE TABLE IF NOT EXISTS {hostname}_stats (id INT AUTO_INCREMENT PRIMARY KEY, ...)")
    cursor.execute("CREATE TABLE IF NOT EXISTS wr_stats (id INT AUTO_INCREMENT PRIMARY KEY, ...)")

def insert_host_info(cursor, host_info):
    insert_query = "INSERT INTO {hostname}_stats (timestamp, hostname, ...) VALUES (%s, %s, ...)"
    cursor.execute(insert_query, list(host_info.values()))

def retrieve_last_host_info(cursor):
    cursor.execute("SELECT * FROM {hostname}_stats ORDER BY id DESC LIMIT 1")
    return cursor.fetchone()

def insert_test_results(cursor, test_results):
    insert_query = "INSERT INTO wr_stats (timestamp, default_data_size_mb, ...) VALUES (%s, %s, ...)"
    cursor.execute(insert_query, list(test_results.values()))

def generate_data(size_mb):
    # Generates a string of alternating 0s and 1s of the specified size in MB.
    size_bytes = size_mb * 1024 * 1024
    return (DATA_PATTERN * (size_bytes // len(DATA_PATTERN)))[:size_bytes]

def write_data_to_file(data, file_path):
    # Writes the provided data to the specified file path.
    try:
        with open(file_path, 'w') as file:
            file.write(data)
        logging.info(f"Successfully wrote data to {file_path}")
    except Exception as e:
        logging.error(f"Error writing data to file: {e}")

def read_data_from_file(file_path):
    # Reads data from the specified file path.
    try:
        with open(file_path, 'r') as file:
            data = file.read()
        logging.info(f"Successfully read data from {file_path}")
        return data
    except Exception as e:
        logging.error(f"Error reading data from file: {e}")
        return None

def main():
    # Main function to execute the write and read speed test.
    try:
        data_size = DEFAULT_DATA_SIZE_MB
        data = generate_data(data_size)

        # Generate file path
        temp_file_path = f"/tmp/wingardiumreviosa-{datetime.now().strftime('%Y%m%d%H%M%S')}.tmp"

        # Write data to file
        start_time = time.time()
        write_data_to_file(data, temp_file_path)
        write_duration = time.time() - start_time
        logging.info(f"Write duration for {data_size}MB: {write_duration} seconds")

        # Read data from file
        start_time = time.time()
        read_data = read_data_from_file(temp_file_path)
        read_duration = time.time() - start_time
        logging.info(f"Read duration for {data_size}MB: {read_duration} seconds")

    except Exception as e:
        logging.error(f"Error in main execution: {e}")

if __name__ == "__main__":
    main()
