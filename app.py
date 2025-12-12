import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.INFO)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# configure the database - use SQLite as fallback for reliability
database_url = os.environ.get("DATABASE_URL")
use_sqlite = False

if database_url:
    # Test if PostgreSQL is available
    try:
        import psycopg2
        from urllib.parse import urlparse
        parsed = urlparse(database_url)
        test_conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port or 5432,
            user=parsed.username,
            password=parsed.password,
            dbname=parsed.path[1:],
            connect_timeout=5
        )
        test_conn.close()
        logging.info("PostgreSQL connection verified")
    except Exception as e:
        logging.warning(f"PostgreSQL unavailable, using SQLite: {e}")
        use_sqlite = True

if use_sqlite or not database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chart_analysis.db"
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {}
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

# initialize extensions
db.init_app(app)

with app.app_context():
    # Import models and routes
    import models  # noqa: F401
    import routes  # noqa: F401
    
    db.create_all()
    logging.info("Database initialized successfully")
