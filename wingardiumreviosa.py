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
        return subprocess.check_output(command, shell=True).decode().strip()

    host_info = {
        'timestamp': datetime.now().strftime("%Y%m%d%H%M%S"),
        'hostname': run_command('hostname'),
        'serial': run_command("grep -m 1 'Serial' /proc/cpuinfo | cut -d ':' -f2 | sed 's/^[ \t]*//'") or 'N/A',
        'model': run_command("cat /proc/device-tree/model"),
        # ... other commands
    }
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
