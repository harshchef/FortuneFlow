from flask import Flask
from database import mydb
from routes.auth import auth_routes
from routes.main import main_routes

app = Flask(__name__)

# MySQL Connection
mydb = mydb  # Assuming mydb is already initialized in database.py

# Secret key for JWT (change this to a secure value)
app.config['SECRET_KEY'] = 'your_secret_key'

# Register blueprints
app.register_blueprint(auth_routes)
app.register_blueprint(main_routes)

if __name__ == '__main__':
    app.run(debug=True)
