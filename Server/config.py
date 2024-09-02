import os
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

API_KEY = os.getenv('API_KEY')  # Config in .env

def init_rate_limiter(app):
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["10 per minute"]
    )
    return limiter
