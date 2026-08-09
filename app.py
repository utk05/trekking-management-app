from flask import Flask
from routes.auth import auth_bp
from routes.admin_routes import admin_bp
from routes.staff_routes import staff_bp
from routes.user_routes import user_bp
app = Flask(__name__)
app.secret_key = "dev-secret-key-change-later"
app.register_blueprint(user_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(staff_bp)   # ← this line was missing

@app.route('/')
def home():
    return "Home page"

if __name__ == "__main__":
    app.run(debug=True)