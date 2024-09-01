import requests
import json

API_BASE_URL = 'http://localhost:5000'  # Replace with your Server IP
API_KEY = 'example1337'  # Replace with your API Key

def get_headers():
    return {'X-API-KEY': API_KEY, 'Content-Type': 'application/json'}

def handle_response(response):
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=4))
    else:
        print(f"Error: {response.status_code} - {response.text}")

def create_key(product_id, duration):
    url = f'{API_BASE_URL}/create_key'
    data = {'product_id': product_id, 'duration': duration}
    response = requests.post(url, headers=get_headers(), json=data)
    handle_response(response)

def delete_key(key):
    url = f'{API_BASE_URL}/delete_key'
    data = {'key': key}
    response = requests.post(url, headers=get_headers(), json=data)
    handle_response(response)
def reset_hwid(key):
    url = f'{API_BASE_URL}/reset_hwid'
    data = {'key': key}
    response = requests.post(url, headers=get_headers(), json=data)
    handle_response(response)

def create_product(name):
    url = f'{API_BASE_URL}/create_product'
    data = {'name': name}
    response = requests.post(url, headers=get_headers(), json=data)
    handle_response(response)

def delete_product(name):
    url = f'{API_BASE_URL}/delete_product'
    data = {'name': name}
    response = requests.post(url, headers=get_headers(), json=data)
    handle_response(response)
def show_help():
    print("Commands:")
    print("  key <create|delete|claim|reset> - Manage keys")
    print("    create <product_id> <duration> - Create a new key")
    print("    delete <key> - Delete an existing key")
    print("    reset <key> - Reset HWID for a key")
    print("  product <create|delete> - Manage products")
    print("    create <name> - Create a new product")
    print("    delete <name> - Delete a product")
    print("  help - Show help message")
    print("  exit - Exit")

def main():
    show_help()

    while True:
        try:
            command = input("cli_tool> ").strip()
            if command == 'exit':
                break

            if command == 'help':
                show_help()
                continue

            parts = command.split()
            main_command = parts[0]
            sub_command = parts[1]

            if main_command == 'key':
                if sub_command == 'create':
                    if len(parts) != 4:
                        print("Usage: key create <product_id> <duration>")
                        continue
                    _, _, product_id, duration = parts
                    create_key(product_id, duration)
                elif sub_command == 'delete':
                    if len(parts) != 3:
                        print("Usage: key delete <key>")
                        continue
                    _, _, key = parts
                    delete_key(key)
                elif sub_command == 'reset':
                    if len(parts) != 3:
                        print("Usage: key reset <key>")
                        continue
                    _, _, key = parts
                    reset_hwid(key)
                else:
                    print("Unknown subcommand. Type 'help' for a list of commands.")

            elif main_command == 'product':
                if sub_command == 'create':
                    if len(parts) != 3:
                        print("Usage: product create <name>")
                        continue
                    _, _, name = parts
                    create_product(name)
                elif sub_command == 'delete':
                    if len(parts) != 3:
                        print("Usage: product delete <name>")
                        continue
                    _, _, name = parts
                    delete_product(name)
                else:
                    print("Unknown subcommand. Type 'help' for a list of commands.")

            else:
                print("Unknown command. Type 'help' for a list of commands.")

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
