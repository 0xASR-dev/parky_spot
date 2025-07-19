from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from app.config import Config




app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

from app import routes, models, sockets


with app.app_context():
    db.create_all()
    print("Database initialized successfully!")