from flask import Flask
from routes.auth import auth_bp
app = Flask(__name__)
app.secret_key = 'secret_key_change_this_later'
app.register_blueprint(auth_bp)
@app.route('/')
def home():
    return "Home Page"
if __name__ == '__main__':
    app.run(debug=True)