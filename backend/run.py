from app import create_app, db
import os
app = create_app()
with app.app_context():
    db.drop_all()  # Delete all tables
    db.create_all()  # Create new tables with corrected schema
    print("Database reset successfully!")
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)