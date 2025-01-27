from flask import Flask
from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv

load_dotenv() 

app = Flask(__name__)

app.config.update(
    DEBUG=os.getenv('FLASK_DEBUG', False),
    ENV=os.getenv('FLASK_ENV', 'production'),
    MONGO_URI=os.getenv('MONGODB_URI'),
    MONGO_DBNAME=os.getenv('MONGODB_DATABASE'),
    FLASK_HOST=os.getenv('FLASK_HOST', '0.0.0.0'),
    FLASK_PORT=os.getenv('FLASK_PORT', 5000)
)

# Initialize MongoDB
mongo = PyMongo(app, uri=app.config['MONGO_URI'])
app.db = mongo.cx[app.config['MONGO_DBNAME']]

# Import routes after app configuration
from routes.profiles import profiles_bp
app.register_blueprint(profiles_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(host=app.config['FLASK_HOST'], port=app.config['FLASK_PORT'])