from flask import Flask, render_template, send_from_directory
from .config import Config
from .extensions import db
from .routes.trip_routes import trip_bp

def create_app():
    app = Flask(__name__, static_folder="../static")
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(trip_bp)
    
    @app.route('/')
    def index():
        return render_template('index.html')

    return app