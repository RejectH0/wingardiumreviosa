
# Wingardium Reviosa

This repository contains the `wingardiumreviosa.py` script, a Python tool designed for performance testing on Debian Linux systems, specifically targeting Raspberry Pi 4 and 5, as well as potentially other Debian-based systems. 

## Overview

`wingardiumreviosa.py` is a Python 3 program that tests the read and write speeds of a system by writing and reading a large amount of data to and from a temporary file. The script is developed using SOLID programming principles, utilizes the `logging` library for output, and is compatible with Python 3.11.2.

## Features

- **Data Size Flexibility**: Default test data size is set to 1 MB, but the script is designed to be easily adjustable for testing with larger data sizes (100MB, 1GB, 100GB).
- **Logging**: Detailed logging of operations, including success and error messages, is implemented using Python's `logging` module.
- **Error Handling**: Robust error handling is incorporated throughout the script, ensuring reliability and stability during testing.

## Usage

To run the script, simply execute it in a Python 3.11.2 environment:
```
python wingardiumreviosa.py
```

The script generates a temporary file in the `/tmp` directory and a log file with a name pattern `wingardiumreviosa-YYMMDDhhmmss.log` in the script's running directory.

## Customization

You can modify the `DEFAULT_DATA_SIZE_MB` constant in the script to change the amount of data used for the read/write tests.

## Version

- Script Version: 0.1
- Last Updated: 202401281700

## Author

This script was created as part of a collaborative effort with guidance and specifications provided by a user and implemented by an OpenAI assistant.

## License

This project is open-sourced under the MIT License. See the LICENSE file for more details.
