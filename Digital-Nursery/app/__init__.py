from flask import Flask

# Factory function to create Flask app

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key_here'

    # Import and register blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)

    return app
