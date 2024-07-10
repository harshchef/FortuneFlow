from flask import Blueprint, request, jsonify, current_app as app  # Import current_app as app
import jwt
import bcrypt
from database import mydb
from utils import token_required
import mysql.connector
auth_routes = Blueprint('auth_routes', __name__)

@auth_routes.route('/register', methods=['POST'])
def register_user():
    try:
        # Parsing JSON data
        username = request.json['username']
        email = request.json['email']
        fullname = request.json['fullname']
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
            INSERT INTO users (username, email, password, fullname, country_of_residence) 
            VALUES (%s, %s, %s, %s, %s)
        """
        user_data = (username, email, hashed_password, fullname, country_of_residence)
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

@auth_routes.route('/login', methods=['POST'])
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
            token = jwt.encode({'user_id': user[0]}, app.config['SECRET_KEY'], algorithm='HS256')  # Use app.config['SECRET_KEY']
            return jsonify({'token': token}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401
    
    except mysql.connector.Error as err:
        return jsonify({'error': f"MySQL Error: {err}"}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
