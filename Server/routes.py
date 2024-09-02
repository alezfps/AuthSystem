from flask import request, jsonify, Blueprint
from utils import load_json_file, save_json_file, generate_secure_key, parse_duration, hash_api_key
from datetime import datetime, timedelta
import os
routes = Blueprint('routes', __name__)

KEYS_FILE = 'keys.json'
PRODUCTS_FILE = 'products.json'

API_KEY_HASHED = hash_api_key(os.getenv('API_KEY'))

def validate_api_key(api_key):
    return hash_api_key(api_key) == API_KEY_HASHED

@routes.before_app_request
def before_request():
    if request.endpoint == 'routes.claim_key':
        return
    api_key = request.headers.get('X-API-KEY')
    if not api_key or not validate_api_key(api_key):
        return jsonify({'error': 'Unauthorized'}), 401

@routes.route('/claim_key', methods=['POST'])
def claim_key():
    try:
        data = request.json

        if not data:
            return jsonify({'error': 'No JSON data received'}), 400

        key = data.get('key')
        hwid = data.get('hwid')
        if not key or not hwid:
            return jsonify({'error': 'Key and HWID are required'}), 400

        ip = request.remote_addr
        keys_data = load_json_file(KEYS_FILE)

        if key not in keys_data:
            return jsonify({'error': 'Invalid key'}), 400

        key_entry = keys_data[key]

        if key_entry['hwid'] and key_entry['hwid'] != hwid:
            return jsonify({'error': 'HWID mismatch'}), 403

        if key_entry['claim_date']:
            claim_date = datetime.fromisoformat(key_entry['claim_date'])
            if datetime.now() > claim_date + timedelta(days=key_entry['duration']):
                return jsonify({'error': 'Key expired'}), 403
        else:
            key_entry['claim_date'] = datetime.now().isoformat()

        # Update HWID if it's None or if it matches the provided HWID
        if key_entry['hwid'] is None or key_entry['hwid'] == hwid:
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

    except Exception as e:
        # Log the exception for debugging purposes
        return jsonify({'error': 'Internal Server Error'}), 500

@routes.route('/create_key', methods=['POST'])
def create_key():
    try:
        data = request.json

        key = str(generate_secure_key())
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

@routes.route('/delete_key', methods=['POST'])
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

@routes.route('/reset_hwid', methods=['POST'])
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

@routes.route('/create_product', methods=['POST'])
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

@routes.route('/delete_product', methods=['POST'])
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