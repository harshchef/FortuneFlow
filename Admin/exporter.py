from flask import Flask, request, jsonify
import pandas as pd
import mysql.connector

app = Flask(__name__)

# MySQL Connection Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'yourpassword',
    'database': 'xxx4',  # Replace with your database name
    'auth_plugin': 'mysql_native_password'  # Specify the authentication plugin
}

def export_users(conn, filename):
    try:
        # Query to fetch data from users table
        query = "SELECT * FROM users"

        # Read SQL data into pandas DataFrame
        df = pd.read_sql(query, conn)

        # Export DataFrame to CSV
        df.to_csv(filename, index=False)

    except mysql.connector.Error as mysql_error:
        raise Exception(f"MySQL Error: {mysql_error}")

    except pd.errors.EmptyDataError as empty_data_error:
        raise Exception(f"No data retrieved from MySQL: {empty_data_error}")

    except Exception as e:
        raise Exception(f"Error exporting DataFrame to CSV: {str(e)}")

@app.route('/export', methods=['POST'])
def export_to_csv():
    try:
        data = request.json
        if not data or 'filename' not in data:
            return jsonify({'error': 'Missing or invalid JSON payload. Expected format: {"filename": "<file_path>"}'}), 400

        filename = data['filename']

        # Connect to MySQL
        conn = mysql.connector.connect(**db_config)

        # Export users table to CSV
        export_users(conn, filename)

        print(f"Data exported to {filename} successfully!")
        return jsonify({'message': f'Data exported to {filename} successfully!'})

    except mysql.connector.Error as mysql_error:
        return jsonify({'error': f"MySQL Error: {mysql_error}"}), 500

    except pd.errors.EmptyDataError as empty_data_error:
        return jsonify({'error': f"No data retrieved from MySQL: {empty_data_error}"}), 500

    except FileNotFoundError as file_not_found_error:
        return jsonify({'error': f"File not found: {file_not_found_error}"}), 500

    except Exception as e:
        return jsonify({'error': f"Error: {str(e)}"}), 500

    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

if __name__ == "__main__":
    app.run(debug=True)
