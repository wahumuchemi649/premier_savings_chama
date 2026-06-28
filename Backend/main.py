from datetime import timedelta
from flask import Flask, jsonify
from sqlalchemy import func
from Admin.models import Financial_Periods, Members
from Config import SessionLocal, Base, engine
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from Admin.routes import Admin_bp

app = Flask(__name__)

# CORS must come before blueprint registration
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True, allow_headers=["Content-Type", "Authorization"])

app.config['JWT_SECRET_KEY'] = 'premier_savings_chama'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)
jwt = JWTManager(app)

app.register_blueprint(Admin_bp, url_prefix="/Chama")

def database_init():
    print("Initializing the database...")
    db = SessionLocal()
    try:
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully.")
    except Exception as e:
        print(f"An error occurred during database initialization: {e}")
    db.close()

    # auto-create first period if none exists
    db = SessionLocal()
    existing = db.query(Financial_Periods).first()
    if not existing:
            earliest = db.query(func.min(Members.date_joined)).scalar()
            if earliest:
                first_period = Financial_Periods(
                    period_start=earliest,
                    status='open'
                )
                db.add(first_period)
                db.commit()
                print("First financial period created automatically.")
    db.close()

database_init()
if __name__ == "__main__":
    app.run(debug=True)