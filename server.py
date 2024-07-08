from flask import Flask, request, jsonify
import mysql.connector
import requests

app = Flask(__name__)

# MySQL Connection
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Harsh98321234@",
    database="xxx"
)

# Function to fetch real-time exchange rate from ExchangeRate-API
def get_exchange_rate(base_currency, target_currency):
    url = f'https://v6.exchangerate-api.com/v6/c34eb65e8181fda34335eed1/latest/{base_currency}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['conversion_rates'].get(target_currency)
    else:
        return None

@app.route('/transfer', methods=['POST'])
def transfer_money():
    try:
        # Extract data from request
        sender_id = request.json['sender_id']
        receiver_id = request.json['receiver_id']
        amount = float(request.json['amount'])
        sender_currency = request.json['sender_currency']
        receiver_currency = request.json['receiver_currency']

        # Check if sender_id and receiver_id exist in users table
        cursor = mydb.cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_id IN (%s, %s)", (sender_id, receiver_id))
        rows = cursor.fetchall()

        if len(rows) != 2:  # Assuming sender_id and receiver_id must both exist
            return jsonify({'error': 'Sender or Receiver not found'}), 404

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


if __name__ == '__main__':
    app.run(debug=True)
