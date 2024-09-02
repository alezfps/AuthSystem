from flask import Flask
from config import init_rate_limiter
from routes import routes
from waitress import serve

app = Flask(__name__)
limiter = init_rate_limiter(app)
app.register_blueprint(routes)

if __name__ == '__main__':
    serve(app, host='0.0.0.0', port='5000') # Replace "serve" with "app.run" for development
