import json
import os
import re
from flask import jsonify
import secrets
import hashlib
from cryptography.fernet import Fernet

key = Fernet.generate_key()
cipher_suite = Fernet(key)

def encrypt_data(data):
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data):
    return cipher_suite.decrypt(encrypted_data.encode()).decode()

def load_json_file(filename):
    if not os.path.isfile(filename):
        with open(filename, 'w') as f:
            json.dump({}, f)
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("Data in file is not a dictionary.")
            return data
    except json.JSONDecodeError as e:
        return handle_error(f"JSONDecodeError: {e}")
    except Exception as e:
        return handle_error(f"Exception: {e}")

def save_json_file(filename, data):
    if not isinstance(data, dict):
        return handle_error("Data must be a dictionary.")
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        return handle_error(f"Exception: {e}")

def parse_duration(duration_str):
    patterns = {
        'd': 1,
        'h': 1 / 24,
        'm': 1 / 1440
    }

    match = re.match(r'^(\d+)([d|h|m])$', duration_str)
    if not match:
        raise ValueError("Invalid duration format")

    value, unit = match.groups()
    value = int(value)

    if unit not in patterns:
        raise ValueError("Unsupported time unit")

    return value * patterns[unit]

def generate_secure_key(format_string='XXXX-XXXX-XXXX'):
    return ''.join(secrets.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') if char == 'X' else char for char in format_string)

def hash_api_key(api_key):
    return hashlib.sha256(api_key.encode()).hexdigest()

def handle_error(message, status_code=400):
    return jsonify({'error': message}), status_code
