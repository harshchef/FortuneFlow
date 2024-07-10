from flask import Flask, request, jsonify
import csv
import json
import mysql.connector

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

                    # Insert data into users table
                    query = "INSERT INTO users (username, email, password, fullname, country_of_residence) " \
                            "VALUES (%s, %s, %s, %s, %s)"
                    values = (username, email, password, fullname, country_of_residence)
                    cursor.execute(query, values)

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

                    # Insert data into users table
                    query = "INSERT INTO users (username, email, password, fullname, country_of_residence) " \
                            "VALUES (%s, %s, %s, %s, %s)"
                    values = (username, email, password, fullname, country_of_residence)
                    cursor.execute(query, values)

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
