# Flask API Auth System

## Description

This project is a Flask-based REST API for managing product keys and associated products. The API allows for creating, deleting, claiming, and resetting product keys, as well as managing products. It includes endpoints for both key and product management, protected by an API key for security.

## Features

- **Key Management**
- **Product Management**
- **API Key Protection**

## Installation

### Requirements

- Python 3.6+
- Flask
- Other dependencies listed in `requirements.txt`

## API Endpoints

### Authentication

- **Header:** `X-API-KEY: API_KEY`

### Key Management

- **Create Key**

    - **Endpoint:** `/create_key`
    - **Method:** `POST`

- **Delete Key**

    - **Endpoint:** `/delete_key`
    - **Method:** `POST`

- **Claim Key**

    - **Endpoint:** `/claim_key`
    - **Method:** `POST`

- **Reset HWID**

    - **Endpoint:** `/reset_hwid`
    - **Method:** `POST`

### Product Management

- **Create Product**

    - **Endpoint:** `/create_product`
    - **Method:** `POST`

- **Delete Product**

    - **Endpoint:** `/delete_product`
    - **Method:** `POST`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
