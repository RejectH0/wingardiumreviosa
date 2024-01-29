#!/usr/bin/env python3
#
# wingardiumreviosa.py - Version 0.1 - 202401281700 - Creation
#
import os
import time
import logging
from datetime import datetime

# Constants
DEFAULT_DATA_SIZE_MB = 1  # Default size of data to write/read
DATA_PATTERN = "01"  # Data pattern to write (alternating 0s and 1s)
LOG_FILE_NAME = "wingardiumreviosa-" + datetime.now().strftime("%Y%m%d%H%M%S") + ".log"

# Configure logging
logging.basicConfig(filename=LOG_FILE_NAME, level=logging.INFO,
                    format='%(asctime)s %(levelname)s:%(message)s')

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
