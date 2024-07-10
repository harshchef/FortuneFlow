from functools import wraps
from flask import request, jsonify, current_app as app
import jwt
import requests
# Middleware function to check for JWT token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            data = jwt.decode(token.split()[1], app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user_id, *args, **kwargs)

    return decorated

# Function to fetch real-time exchange rate from ExchangeRate-API
def get_exchange_rate(base_currency, target_currency):
    url = f'https://v6.exchangerate-api.com/v6/c34eb65e8181fda34335eed1/latest/{base_currency}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['conversion_rates'].get(target_currency)
    else:
        return None
