from flask import Flask, request, jsonify
import mysql.connector
import bcrypt
from database import get_db_connection
app = Flask(__name__)



# Endpoint to register a new admin
@app.route('/admin/register', methods=['POST'])
def register_admin():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')

    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    mydb = get_db_connection()
    cursor = mydb.cursor()

    try:
        # Check if admin already exists
        cursor.execute("SELECT * FROM admin WHERE email = %s", (email,))
        existing_admin = cursor.fetchone()

        if existing_admin:
            cursor.close()
            mydb.close()
            return jsonify({'error': 'Admin with the same email already exists'}), 400

        # Insert into admin table
        sql = "INSERT INTO admin (name, email, password, full_name) VALUES (%s, %s, %s, %s)"
        values = (name, email, hashed_password, full_name)
        cursor.execute(sql, values)
        mydb.commit()

        cursor.close()
        mydb.close()
        return jsonify({'message': 'Admin registered successfully'}), 201

    except mysql.connector.Error as err:
        print(f"Error registering admin: {err}")
        mydb.rollback()
        cursor.close()
        mydb.close()
        return jsonify({'error': 'Failed to register admin'}), 500

if __name__ == '__main__':
    app.run(debug=True)
