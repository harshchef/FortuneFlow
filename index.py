from flask import Flask, request, jsonify
import mysql.connector
import requests
import jwt
import bcrypt
from functools import wraps

app = Flask(__name__)

# MySQL Connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Harsh98321234@",
    database="xxx4"
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
        fullname=request.json['fullname']
        password = request.json['password']
        country_of_residence = request.json['country_of_residence']
        
        # Check if username already exists
        cursor = mydb.cursor()
        cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            cursor.close()
            return jsonify({'error': 'Username already exists'}), 400

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Insert user into the database
        insert_query = """
            INSERT INTO users (username, email, password,fullname, country_of_residence) 
            VALUES (%s, %s, %s, %s,%s)
        """
        user_data = (username, email, hashed_password,fullname, country_of_residence)
        cursor.execute(insert_query, user_data)
        user_id = cursor.lastrowid  # Get the inserted user's ID

        # Initialize account balance
        insert_balance_query = "INSERT INTO accounts (user_id, balance) VALUES (%s, %s)"
        cursor.execute(insert_balance_query, (user_id, 0))  # Initialize with a balance of 0

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
        email = request.json.get('email')
        password = request.json.get('password')
        
        # Check if user exists in the database and credentials are correct
        cursor = mydb.cursor()
        query = "SELECT * FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        cursor.close()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):  # user[3] is the password column
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
        receiver_id = request.json['receiver_id']
        amount = float(request.json['amount'])
        sender_currency = request.json['sender_currency']
        receiver_currency = request.json['receiver_currency']

        # Check if sender_id exists in users table (assuming receiver_id will be checked via frontend or another endpoint)
        cursor = mydb.cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (current_user_id,))
        sender_exists = cursor.fetchone()

        if not sender_exists:
            cursor.close()
            return jsonify({'error': 'Sender not found'}), 404

        # Check sender's balance
        cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (current_user_id,))
        sender_balance = cursor.fetchone()
        
        if not sender_balance or sender_balance[0] < amount:
            cursor.close()
            return jsonify({'error': 'Insufficient balance'}), 400

        # Fetch exchange rate
        exchange_rate = get_exchange_rate(sender_currency, receiver_currency)
        
        if exchange_rate is None:
            cursor.close()
            return jsonify({'error': 'Failed to fetch exchange rate'}), 500

        # Perform currency conversion
        converted_amount = amount * exchange_rate

        # Update transaction in database
        insert_query = """
            INSERT INTO transactions 
            (sender_id, receiver_id, amount, sender_currency, receiver_currency, exchange_rate, converted_amount) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        transaction_data = (current_user_id, receiver_id, amount, sender_currency, receiver_currency, exchange_rate, converted_amount)
        cursor.execute(insert_query, transaction_data)

        # Update sender's and receiver's balance
        update_sender_balance_query = "UPDATE accounts SET balance = balance - %s WHERE user_id = %s"
        cursor.execute(update_sender_balance_query, (amount, current_user_id))

        update_receiver_balance_query = "UPDATE accounts SET balance = balance + %s WHERE user_id = %s"
        cursor.execute(update_receiver_balance_query, (converted_amount, receiver_id))

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

@app.route('/deleteuser/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        # Establish MySQL connection
        cursor = mydb.cursor()

        # Check if the particular user exists in the database
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            cursor.close()
            return jsonify({'error': f'User with ID {user_id} not found'}), 404

        # Delete transactions associated with the user
        delete_transactions_query = "DELETE FROM transactions WHERE sender_id = %s OR receiver_id = %s"
        cursor.execute(delete_transactions_query, (user_id, user_id))
        mydb.commit()

        # Delete the user from the database
        delete_user_query = "DELETE FROM users WHERE user_id = %s"
        cursor.execute(delete_user_query, (user_id,))
        mydb.commit()

        cursor.close()

        return jsonify({'message': f'User with ID {user_id} deleted successfully'}), 200

    except mysql.connector.Error as err:
        return jsonify({'error': f"MySQL Error: {err}"}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/deposit', methods=['POST'])
@token_required
def deposit(current_user_id):
    try:
        amount = float(request.json['amount'])
        
        if amount <= 0:
            return jsonify({'error': 'Deposit amount must be positive'}), 400
        
        cursor = mydb.cursor()
        
        # Update user balance
        update_balance_query = "UPDATE accounts SET balance = balance + %s WHERE user_id = %s"
        cursor.execute(update_balance_query, (amount, current_user_id))
        
        mydb.commit()
        cursor.close()
        
        return jsonify({'message': 'Deposit successful', 'amount': amount}), 200
    
    except mysql.connector.Error as err:
        return jsonify({'error': f"MySQL Error: {err}"}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/withdraw', methods=['POST'])
@token_required
def withdraw(current_user_id):
    try:
        amount = float(request.json['amount'])
        
        if amount <= 0:
            return jsonify({'error': 'Withdrawal amount must be positive'}), 400
        
        cursor = mydb.cursor()
        
        # Check if user has sufficient balance
        cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (current_user_id,))
        user_balance = cursor.fetchone()
        
        if not user_balance or user_balance[0] < amount:
            cursor.close()
            return jsonify({'error': 'Insufficient balance'}), 400
        
        # Update user balance
        update_balance_query = "UPDATE accounts SET balance = balance - %s WHERE user_id = %s"
        cursor.execute(update_balance_query, (amount, current_user_id))
        
        mydb.commit()
        cursor.close()
        
        return jsonify({'message': 'Withdrawal successful', 'amount': amount}), 200
    
    except mysql.connector.Error as err:
        return jsonify({'error': f"MySQL Error: {err}"}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
