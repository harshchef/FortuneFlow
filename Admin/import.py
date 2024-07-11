

from flask import Flask, request, jsonify
import csv
import json
import mysql.connector
import bcrypt
 
app = Flask(__name__)
 
# MySQL Connection Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Harsh98321234@',
    'database': 'xxx4', # Replace with your database name
    'auth_plugin': 'mysql_native_password'  # Specify the authentication plugin
}
 
@app.route('/import', methods=['GET'])
def import_users():
    # Get JSON input
    data = request.json
    if not data or 'type' not in data or 'path' not in data:
        return jsonify({'error': 'Missing or invalid JSON payload. Expected format: {"type": "csv" or "json", "path": "<file_path>"}'}), 400
 
    file_type = data['type']
    filename = data['path']
 
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
 
        if file_type == 'csv':
            # Read data from CSV and insert into MySQL
            with open(filename, 'r') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    username = row['username']
                    email = row['email']
                    password = row['password']
                    fullname = row['fullname']
                    country_of_residence = row['country_of_residence']
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                   
                    # Insert data into users table
                    query = "INSERT INTO users (username, email, password, fullname, country_of_residence) " \
                            "VALUES (%s, %s, %s, %s, %s)"
                    values = (username, email, hashed_password, fullname, country_of_residence)
                    cursor.execute(query, values)
                   
                    user_id = cursor.lastrowid  # Get the inserted user's ID
 
                    # Insert data into accounts table
                    account_query = "INSERT INTO accounts (user_id, balance) VALUES (%s, %s)"
                    account_values = (user_id, 0.00)  # Initialize balance to 0
                    cursor.execute(account_query, account_values)
 
        elif file_type == 'json':
            # Read data from JSON and insert into MySQL
            with open(filename, 'r') as file:
                json_data = json.load(file)
                for entry in json_data:
                    username = entry['username']
                    email = entry['email']
                    password = entry['password']
                    fullname = entry['fullname']
                    country_of_residence = entry['country_of_residence']
                    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                   
                    # Insert data into users table
                    query = "INSERT INTO users (username, email, password, fullname, country_of_residence) " \
                            "VALUES (%s, %s, %s, %s, %s)"
                    values = (username, email, hashed_password, fullname, country_of_residence)
                    cursor.execute(query, values)
                   
                    user_id = cursor.lastrowid  # Get the inserted user's ID
 
                    # Insert data into accounts table
                    account_query = "INSERT INTO accounts (user_id, balance) VALUES (%s, %s)"
                    account_values = (user_id, 0.00)  # Initialize balance to 0
                    cursor.execute(account_query, account_values)
 
        else:
            return jsonify({'error': 'Unsupported file type. Supported types are "csv" and "json".'}), 400
 
        conn.commit()
        return jsonify({'message': 'Data inserted successfully!'})
 
    except mysql.connector.Error as err:
        return jsonify({'error': f"MySQL Error: {err}"}), 500
 
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
 
if __name__ == '__main__':
    app.run(debug=True)
 