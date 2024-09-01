from flask import Flask, request, jsonify
import json
import random
import string
from datetime import datetime, timedelta
import os
import re

app = Flask(__name__)

PRODUCTS_FILE = 'products.json'
KEYS_FILE = 'keys.json'
API_KEYS = 'example1337' # Enter your API Key
KEY_FORMAT = 'XXXX-XXXX-XXXX'

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
        raise ValueError(f"JSONDecodeError occurred in load_json_file: {e}")
    except Exception as e:
        raise Exception(f"Exception occurred in load_json_file: {e}")

def save_json_file(filename, data):
    if not isinstance(data, dict):
        raise ValueError("Data must be a dictionary.")
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        raise Exception(f"Exception occurred in save_json_file: {e}")

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

def generate_key(format_string=KEY_FORMAT):
    def random_char():
        return random.choice(string.ascii_uppercase + string.digits)

    key = ''.join(random_char() if char == 'X' else char for char in format_string)
    return key

def validate_api_key(api_key):
    return api_key == API_KEYS

@app.before_request
def before_request():
    if request.endpoint == 'claim_key':
        return
    api_key = request.headers.get('X-API-KEY')
    if not api_key or not validate_api_key(api_key):
        return jsonify({'error': 'Unauthorized'}), 401

@app.route('/claim_key', methods=['POST'])
def claim_key():
    data = request.json
    key = data.get('key')
    hwid = data.get('hwid')
    ip = request.remote_addr

    keys_data = load_json_file(KEYS_FILE)

    if key not in keys_data:
        return jsonify({'Error': 'Invalid key'}), 400

    key_entry = keys_data[key]

    if key_entry['hwid'] and key_entry['hwid'] != hwid:
        return jsonify({'Error': 'HWID mismatch'}), 403

    if key_entry['claim_date']:
        claim_date = datetime.fromisoformat(key_entry['claim_date'])
        if datetime.now() > claim_date + timedelta(days=key_entry['duration']):
            return jsonify({'Error': 'Key expired'}), 403
    else:
        key_entry['claim_date'] = datetime.now().isoformat()
        key_entry['hwid'] = hwid
        key_entry['ip'] = ip
        save_json_file(KEYS_FILE, keys_data)

    product_id = key_entry['product_id']
    products_data = load_json_file(PRODUCTS_FILE)
    product_name = products_data.get(product_id, {}).get('name', 'Unknown')

    return jsonify({
        'key': key,
        'product': product_name,
        'expires_at': (datetime.fromisoformat(key_entry['claim_date']) + timedelta(days=key_entry['duration'])).isoformat()
    })

@app.route('/create_key', methods=['POST'])
def create_key():
    try:
        data = request.json

        key = str(generate_key())
        product_id = data.get('product_id')
        duration_str = data.get('duration')

        if not product_id or not duration_str:
            raise ValueError("Product ID and duration are required")

        try:
            duration_days = parse_duration(duration_str)
        except ValueError as e:
            return jsonify({'error': 'Invalid duration format'}), 400

        keys_data = load_json_file(KEYS_FILE)
        products_data = load_json_file(PRODUCTS_FILE)

        if product_id not in [p['id'] for p in products_data.values()]:
            return jsonify({'error': 'Invalid product ID'}), 400

        keys_data[key] = {
            'product_id': product_id,
            'hwid': None,
            'ip': None,
            'claim_date': None,
            'duration': duration_days
        }

        save_json_file(KEYS_FILE, keys_data)

        return jsonify({'key': key})
    except ValueError as e:
        return jsonify({'error': 'Bad Request'}), 400
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/delete_key', methods=['POST'])
def delete_key():
    try:
        data = request.json
        key = data.get('key')

        if not key:
            raise ValueError("Key is required")

        keys_data = load_json_file(KEYS_FILE)

        if key not in keys_data:
            return jsonify({'error': 'Key not found'}), 404

        del keys_data[key]
        save_json_file(KEYS_FILE, keys_data)

        return jsonify({'message': 'Key deleted successfully'})
    except ValueError as e:
        return jsonify({'error': 'Bad Request'}), 400
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/reset_hwid', methods=['POST'])
def reset_hwid():
    data = request.json
    key = data.get('key')

    if not key:
        return jsonify({'error': 'Invalid key'}), 400

    keys_data = load_json_file(KEYS_FILE)

    if key not in keys_data:
        return jsonify({'error': 'Invalid key'}), 400

    keys_data[key]['hwid'] = None
    save_json_file(KEYS_FILE, keys_data)

    return jsonify({'message': 'HWID reset'})

@app.route('/create_product', methods=['POST'])
def create_product():
    try:
        data = request.json
        name = data.get('name')

        if not name or not isinstance(name, str):
            return jsonify({'error': 'Invalid product name'}), 400

        products_data = load_json_file(PRODUCTS_FILE)
        if name in products_data:
            return jsonify({'error': 'Product already exists'}), 400

        products_data[name] = {
            'id': name,
            'name': name
        }

        save_json_file(PRODUCTS_FILE, products_data)
        return jsonify({'product_id': name})

    except ValueError as e:
        return jsonify({'error': 'Bad Request'}), 400
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

@app.route('/delete_product', methods=['POST'])
def delete_product():
    try:
        data = request.json
        name = data.get('name')

        if not name:
            return jsonify({'error': 'Product name is required'}), 400

        products_data = load_json_file(PRODUCTS_FILE)

        if name not in products_data:
            return jsonify({'error': 'Product not found'}), 404

        del products_data[name]
        save_json_file(PRODUCTS_FILE, products_data)

        return jsonify({'message': 'Product deleted successfully'})
    except ValueError as e:
        return jsonify({'error': 'Bad Request'}), 400
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
