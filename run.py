# run.py
from app import create_app
from app.extensions import db

app = create_app()

# Create DB tables if not exist (simple dev approach)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run()
