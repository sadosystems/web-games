from application import app, db

def reset_database():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        
        # Create all tables
        db.create_all()

        print("Database has been reset.")

if __name__ == '__main__':
    confirm = input("Are you sure you want to reset the database? This cannot be undone. Type 'yes' to confirm: ")
    if confirm.lower() == 'yes':
        reset_database()
    else:
        print("Database reset cancelled.")
