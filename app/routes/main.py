from flask import Blueprint, request, jsonify
import jwt
import bcrypt
from database import mydb
from utils import token_required
from utils import get_exchange_rate
import mysql.connector

main_routes = Blueprint('main_routes', __name__)

@main_routes.route('/transfer', methods=['POST'])
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

@main_routes.route('/deleteuser/<int:user_id>', methods=['DELETE'])
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

@main_routes.route('/deposit', methods=['POST'])
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

@main_routes.route('/withdraw', methods=['POST'])
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
