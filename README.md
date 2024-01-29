
# Wingardium Reviosa

This repository contains the `wingardiumreviosa.py` script, a Python tool designed for performance testing on Debian Linux systems, specifically targeting Raspberry Pi 4 and 5, as well as potentially other Debian-based systems.

## Overview

`wingardiumreviosa.py` is a Python 3 program that tests the read and write speeds of a system by writing and reading a large amount of data to and from a temporary file. The script is developed using SOLID programming principles, utilizes the `logging` library for output, and is compatible with Python 3.11.2.

## Features

- **Flexible Data Size Configuration**: Default test data size is set to 5 GB. Users can adjust the `DEFAULT_DATA_SIZE_MB` constant in the script to change the amount of data used for read/write tests.
- **Enhanced Logging**: Detailed logging of operations, including success and error messages, is implemented using Python's `logging` module.
- **Robust Error Handling**: Comprehensive error handling ensures reliability and stability during testing.
- **Host Information Collection**: Gathers and logs detailed host system information, including CPU, memory, and network details.
- **Database Integration**: Stores test results and host information in a MariaDB database, enabling persistent tracking across multiple hosts.
- **Efficient Data Generation**: Utilizes a pattern-based approach to generate test data efficiently.

## Usage

To run the script, execute it in a Python 3.11.2 environment:
```
python wingardiumreviosa.py
```

The script creates a temporary file in the `/tmp` directory and a log file with the naming pattern `wingardiumreviosa-YYMMDDhhmmss.log` in the running directory.

## Customization

Modify the `DEFAULT_DATA_SIZE_MB` constant in the script to alter the data size for the read/write tests.

## Version

- Script Version: 1.0
- Last Updated: 202401282245

## Author

This script was created as part of a collaborative effort with guidance and specifications provided by a user and implemented by an OpenAI assistant.

## License

This project is open-sourced under the MIT License. See the LICENSE file for more details.
