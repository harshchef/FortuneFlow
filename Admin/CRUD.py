from flask import Flask, request, jsonify
import mysql.connector
import jwt
from functools import wraps
import bcrypt
from database import get_db_connection

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

def admin_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            token = token.split()[1]  # Assuming "Bearer <token>"
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['admin_id']
        except IndexError:
            return jsonify({'error': 'Bearer token malformed'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401

        # Add logic to check if the user is an admin
        mydb = get_db_connection()
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM admin WHERE admin_id = %s", (current_user_id,))
        admin = cursor.fetchone()
        cursor.close()
        mydb.close()

        if not admin:
            return jsonify({'error': 'Unauthorized access'}), 401

        return f(current_user_id, *args, **kwargs)

    return decorated

# API for admin login
@app.route('/admin/login', methods=['POST'])
def login_admin():
    try:
        email = request.json['email']
        password = request.json['password']
        
        # Check if admin exists in the database and credentials are correct
        mydb = get_db_connection()
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
        admin = cursor.fetchone()
        cursor.close()
        mydb.close()
        
        if admin and bcrypt.checkpw(password.encode('utf-8'), admin[3].encode('utf-8')):  # Assuming password is in the 4th column
            # Generate JWT token for admin
            token = jwt.encode({'admin_id': admin[0]}, app.config['SECRET_KEY'], algorithm='HS256')
            return jsonify({'token': token}), 200
        else:
            return jsonify({'error': 'Invalid credentials'}), 401

    except mysql.connector.Error as err:
        return jsonify({'error': f"MySQL Error: {err}"}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint to change admin password
@app.route('/admin/change_admin_password/<int:admin_id>', methods=['POST'])
@admin_token_required
def change_password(current_user_id, admin_id):
    current_password = request.json.get('current_password')
    new_password = request.json.get('new_password')

    mydb = get_db_connection()
    cur = mydb.cursor()
    cur.execute("SELECT * FROM admin WHERE admin_id = %s", (admin_id,))
    admin = cur.fetchone()

    if not admin:
        cur.close()
        mydb.close()
        return jsonify({'error': 'Admin not found'}), 404

    # Verify current password
    if not bcrypt.checkpw(current_password.encode('utf-8'), admin[3].encode('utf-8')):  # Assuming 'password' is the fourth column
        cur.close()
        mydb.close()
        return jsonify({'error': 'Incorrect current password'}), 401

    # Hash the new password
    hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

    # Update admin's password in the database
    cur.execute("UPDATE admin SET password = %s WHERE admin_id = %s", (hashed_new_password.decode('utf-8'), admin_id))
    mydb.commit()
    cur.close()
    mydb.close()

    return jsonify({'message': 'Password changed successfully'}), 200

# Endpoint to create a new user
@app.route('/admin/create_user', methods=['POST'])
@admin_token_required
def create_user(current_user_id):
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        fullname = data.get('fullname')
        country_of_residence = data.get('country_of_residence')

        # Check if username or email already exists
        mydb = get_db_connection()
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            mydb.close()
            return jsonify({'error': 'User with the same username or email already exists'}), 400

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Inserting a new user into the database
        sql = "INSERT INTO users (username, email, password, fullname, country_of_residence) VALUES (%s, %s, %s, %s, %s)"
        values = (username, email, hashed_password.decode('utf-8'), fullname, country_of_residence)
        cursor.execute(sql, values)
        mydb.commit()

        # Fetch the auto-generated user_id
        new_user_id = cursor.lastrowid

        cursor.close()
        mydb.close()

        return jsonify({'message': 'User created successfully', 'user_id': new_user_id}), 201

    except mysql.connector.Error as err:
        return jsonify({'error': f"MySQL Error: {err}"}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Updating a user with the help of their user_id
@app.route('/admin/update_user/<int:user_id>', methods=['PUT'])
@admin_token_required
def update_user(current_user_id, user_id):
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        fullname = data.get('fullname')
        country_of_residence = data.get('country_of_residence')

        mydb = get_db_connection()
        cursor = mydb.cursor()

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Updating the user in the database
        cursor.execute(
            "UPDATE users SET username = %s, password = %s, email = %s, fullname = %s, country_of_residence = %s WHERE user_id = %s",
            (username, hashed_password.decode('utf-8'), email, fullname, country_of_residence, user_id)
        )
        mydb.commit()
        cursor.close()
        mydb.close()

        return jsonify({'message': f'User with ID {user_id} updated successfully'}), 200

    except mysql.connector.Error as err:
        return jsonify({'error': f"MySQL Error: {err}"}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Deleting a user with the help of their user_id
@app.route('/admin/delete_user/<int:user_id>', methods=['DELETE'])
@admin_token_required
def delete_user(current_user_id, user_id):
    try:
        mydb = get_db_connection()
        cursor = mydb.cursor()

        # Checking if the particular user exists in the db or not
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            cursor.close()
            mydb.close()
            return jsonify({'error': f'User with ID {user_id} not found'}), 404

        # Delete the user from the db as it is present
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        mydb.commit()
        cursor.close()
        mydb.close()

        return jsonify({'message': f'User with ID {user_id} deleted successfully'}), 200

    except mysql.connector.Error as err:
        return jsonify({'error': f"MySQL Error: {err}"}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
