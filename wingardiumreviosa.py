#!/usr/bin/env python3
#
# wingardiumreviosa.py - Version 1.0 - 202401282245 - Update
#
import os
import socket
import traceback
import time
import logging
from datetime import datetime
import configparser
import subprocess
import pymysql
import shutil

def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['database']

# Constants
DEFAULT_DATA_SIZE_MB = 10000 # Default size of data to write/read
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
    try:
        conn = pymysql.connect(host=config['host'], port=int(config['port']), user=config['user'], password=config['password'])
        logging.info("Successfully connected to the database.")
        return conn
    except pymysql.MySQLError as e:
        logging.error(f"Error connecting to the database: {e}")
        raise

def check_and_create_database(cursor, hostname):
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {hostname}_wingardiumreviosa")
        logging.info(f"Database '{hostname}_wingardiumreviosa' checked/created successfully.")
    except pymysql.MySQLError as e:
        logging.error(f"Error creating database: {e}")
        raise

def check_and_create_hoststats_table(cursor, hostname):
    try:
        stats_table_query = f"""
        CREATE TABLE IF NOT EXISTS {hostname}_stats (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME,
            hostname VARCHAR(32),
            serial VARCHAR(64),
            model VARCHAR(128),
            proc_count INT(2),
            proc_model VARCHAR(64),
            disk_usage_root VARCHAR(128),
            total_ram INT(16),
            nic_mac VARCHAR(45),
            nic_ip VARCHAR(45)
        )"""
        cursor.execute(stats_table_query)
        logging.info(f"Table '{hostname}_stats' checked/created successfully.")

    except pymysql.MySQLError as e:
        logging.error(f"Error creating tables: {e}")
        raise

def insert_host_info(cursor, hostname, host_info):
    try:
        insert_query = f"INSERT INTO {hostname}_stats (timestamp, hostname, serial, model, proc_count, proc_model, disk_usage_root, total_ram, nic_mac, nic_ip) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, list(host_info.values()))
        logging.info("Host information inserted successfully.")
    except pymysql.MySQLError as e:
        logging.error(f"Error inserting host information: {e}")
        raise

def retrieve_last_host_info(cursor, hostname):
    try:
        cursor.execute(f"SELECT * FROM {hostname}_stats ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        if result:
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, result))
        return None
    except pymysql.MySQLError as e:
        logging.error(f"Error retrieving last host information: {e}")
        raise

def check_and_create_wrstats_table(cursor, hostname):
    try:
        stats_table_query = f"""
        CREATE TABLE IF NOT EXISTS {hostname}_wr_stats (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp DATETIME,
            default_data_size_mb INT(16),
            write_duration_secs DECIMAL(20,10),
            read_duration_secs DECIMAL(20,10)
        )"""
        cursor.execute(stats_table_query)
        logging.info(f"Table '{hostname}_wr_stats' checked/created successfully.")
    except pymysql.MySQLError as e:
        logging.error(f"Error creating 'wr_stats' table: {e}")
        raise

def get_available_space(path):
    """ Returns the available space in bytes at the given path. """
    total, used, free = shutil.disk_usage(path)
    return free

def insert_test_results(cursor, hostname, test_results):
    try:
        insert_query = f"INSERT INTO {hostname}_wr_stats (timestamp, default_data_size_mb, write_duration_secs, read_duration_secs) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, list(test_results.values()))
        logging.info("Test results inserted successfully.")
    except pymysql.MySQLError as e:
        logging.error(f"Error inserting test results: {e}")
        raise

def generate_data(size_mb):
    # Generates a string of alternating 0s and 1s of the specified size in MB.
    size_bytes = size_mb * 1024 * 1024
    return (DATA_PATTERN * (size_bytes // len(DATA_PATTERN)))[:size_bytes]

def write_data_to_file(file_path, size_mb, chunk_size_mb=10):
    # Writes data to the specified file path in chunks.
    try:
        size_bytes = size_mb * 1024 * 1024
        chunk_bytes = chunk_size_mb * 1024 * 1024
        data_pattern = DATA_PATTERN * (chunk_bytes // len(DATA_PATTERN))

        with open(file_path, 'w') as file:
            for _ in range(0, size_bytes, chunk_bytes):
                file.write(data_pattern)
        logging.info(f"Successfully wrote {size_mb}MB of data to {file_path}")
    except Exception as e:
        logging.error(f"Error writing data to file: {e}")

def read_data_from_file(file_path, chunk_size_mb=10):
    # Reads data from the specified file path in chunks.
    try:
        chunk_bytes = chunk_size_mb * 1024 * 1024
        with open(file_path, 'r') as file:
            while True:
                data_chunk = file.read(chunk_bytes)
                if not data_chunk:
                    break
                # Process the chunk (if needed)
        logging.info(f"Successfully read data from {file_path}")
    except Exception as e:
        logging.error(f"Error reading data from file: {e}")
        return None

def main():
    try:
        # Database Connection Setup
        db_config = read_config()
        db_connection = connect_to_database(db_config)
        cursor = db_connection.cursor()

        # Hostname for dynamic database/table naming
        hostname = socket.gethostname()

        # Database and Tables Setup
        check_and_create_database(cursor, hostname)
        db_connection.select_db(f"{hostname}_wingardiumreviosa")
        check_and_create_hoststats_table(cursor, hostname)
        check_and_create_wrstats_table(cursor, hostname)

        # Collect and Compare Host Information
        host_info = collect_host_info()
        last_host_info = retrieve_last_host_info(cursor, hostname)
        if not last_host_info or last_host_info['serial'] != host_info['serial']:
            insert_host_info(cursor, hostname, host_info)

        # Check Disk Space
        temp_file_path = f"/tmp/wingardiumreviosa-{datetime.now().strftime('%Y%m%d%H%M%S')}.tmp"
        required_space = DEFAULT_DATA_SIZE_MB * 1024 * 1024  # Convert MB to bytes
        available_space = get_available_space("/tmp")

        if available_space < required_space:
            logging.error(f"Not enough disk space. Required: {required_space} bytes, Available: {available_space} bytes")
            return  # Exit the function

        # Write and Read Test
        data_size = DEFAULT_DATA_SIZE_MB
        temp_file_path = f"/tmp/wingardiumreviosa-{datetime.now().strftime('%Y%m%d%H%M%S')}.tmp"

        # Write Data
        start_time = time.time()
        write_data_to_file(temp_file_path, data_size) 
        write_duration = time.time() - start_time

        # Read Data
        start_time = time.time()
        read_data = read_data_from_file(temp_file_path)
        read_duration = time.time() - start_time

        # Insert Test Results
        test_results = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'default_data_size_mb': data_size,
            'write_duration_secs': write_duration,
            'read_duration_secs': read_duration
        }
        insert_test_results(cursor, hostname, test_results)

        # Delete Temporary File
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logging.info(f"Deleted temporary file {temp_file_path}")

        # Commit Changes and Close Database Connection
        db_connection.commit()

    except Exception as e:
        logging.error(f"Error in main execution: {e}\n{traceback.format_exc()}")

    finally:
        if db_connection:
            cursor.close()
            db_connection.close()
            logging.info("Database connection closed.")

if __name__ == "__main__":
    main()
