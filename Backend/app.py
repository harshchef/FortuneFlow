from flask import Flask
from routes.auth import auth_bp
from routes.transfer import transfer_bp

app = Flask(__name__)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(transfer_bp)

if __name__ == '__main__':
    app.run(debug=True)
