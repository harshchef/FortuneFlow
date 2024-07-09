from flask import Flask, request, jsonify
import mysql.connector
import requests
import jwt
from functools import wraps
 
app = Flask(__name__)
 
# MySQL Connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Harsh98321234@",
    database="xxx"
)
 
# Secret key for JWT (change this to a secure value)
app.config['SECRET_KEY'] = 'your_secret_key'
 
# Function to fetch real-time exchange rate from ExchangeRate-API
def get_exchange_rate(base_currency, target_currency):
    url = f'https://v6.exchangerate-api.com/v6/c34eb65e8181fda34335eed1/latest/{base_currency}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['conversion_rates'].get(target_currency)
    else:
        return None
 
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
 
@app.route('/register', methods=['POST'])
def register_user():
    try:
        username = request.json['username']
        email = request.json['email']
        password = request.json['password']
        country_of_residence = request.json['country_of_residence']
       
        # Insert user into the database
        cursor = mydb.cursor()
        insert_query = """
            INSERT INTO users (username, email, password, country_of_residence)
            VALUES (%s, %s, %s, %s)
        """
        user_data = (username, email, password, country_of_residence)
        cursor.execute(insert_query, user_data)
        mydb.commit()
        cursor.close()
       
        return jsonify({'message': 'User registered successfully'}), 201
   
    except mysql.connector.Error as err:
        return jsonify({'error': f"MySQL Error: {err}"}), 500
   
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 
@app.route('/login', methods=['POST'])
def login_user():
    try:
        email = request.json['email']
        password = request.json['password']
       
        # Check if user exists in the database and credentials are correct
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()
       
        if user:
            # Generate JWT token
            token = jwt.encode({'user_id': user[0]}, app.config['SECRET_KEY'], algorithm='HS256')
            return jsonify({'token': token}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
   
    except mysql.connector.Error as err:
        return jsonify({'error': f"MySQL Error: {err}"}), 500
   
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 
@app.route('/transfer', methods=['POST'])
@token_required
def transfer_money(current_user_id):
    try:
        # Extract data from request
        sender_id = current_user_id
        receiver_id = request.json['receiver_id']
        amount = float(request.json['amount'])
        sender_currency = request.json['sender_currency']
        receiver_currency = request.json['receiver_currency']
 
        # Check if sender_id exists in users table (assuming receiver_id will be checked via frontend or another endpoint)
        cursor = mydb.cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (sender_id,))
        sender_exists = cursor.fetchone()
 
        if not sender_exists:
            return jsonify({'error': 'Sender not found'}), 404
 
        # Fetch exchange rate
        exchange_rate = get_exchange_rate(sender_currency, receiver_currency)
       
        if exchange_rate is None:
            return jsonify({'error': 'Failed to fetch exchange rate'}), 500
 
        # Perform currency conversion
        converted_amount = amount * exchange_rate
 
        # Update transaction in database
        insert_query = """
            INSERT INTO transactions
            (sender_id, receiver_id, amount, sender_currency, receiver_currency, exchange_rate, converted_amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        transaction_data = (sender_id, receiver_id, amount, sender_currency, receiver_currency, exchange_rate, converted_amount)
        cursor.execute(insert_query, transaction_data)
        mydb.commit()
        cursor.close()
 
        # Prepare response
        response_data = {
            'message': 'Transfer successful',
            'amount': converted_amount,
            'exchange_rate': exchange_rate
        }
 
        return jsonify(response_data), 200
   
    except mysql.connector.Error as err:
        return jsonify({'error': f"MySQL Error: {err}"}), 500
 
    except Exception as e:
        return jsonify({'error': str(e)}), 500
   
 
# Function to get transaction details by transaction_id
def get_transaction(transaction_id):
    try:
        cursor = mydb.cursor(dictionary=True)
        sql = "SELECT * FROM transactions WHERE transaction_id = %s"
        cursor.execute(sql, (transaction_id,))
        transaction = cursor.fetchone()
 
        if transaction:
            return transaction
        else:
            return None
    except mysql.connector.Error as err:
        print(f"Error getting transaction: {err}")
        return None
    finally:
        cursor.close()
 
# API endpoint to retrieve transaction details by transaction_id
@app.route('/transfer', methods=['GET'])
@token_required
def get_transaction_details(current_user_id):
    try:
        # Extract transaction_id from JSON request
        transaction_id = request.json.get('transaction_id')
 
        if not transaction_id:
            return jsonify({'error': 'Transaction ID is required in JSON format'}), 400
 
        # Retrieve transaction details
        transaction = get_transaction(transaction_id)
 
        if transaction:
            return jsonify(transaction), 200
        else:
            return jsonify({'error': f"Transaction with ID {transaction_id} not found"}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
 
 
 
 
 
   
 
if __name__ == '__main__':
    app.run(debug=True)
 