from apps import create_app, db
from apps.models import User

def seed_admin():
    app = create_app()
    with app.app_context():
        admin_username = 'emokids'
        admin_email = 'emokids@gmail.com'
        admin_password = '1234567890'
        
        # Check if the admin user already exists
        if not User.query.filter_by(username=admin_username).first():
            admin_user = User(
                username=admin_username,
                email=admin_email,
                role='admin'
            )
            admin_user.set_password(admin_password)
            
            db.session.add(admin_user)
            db.session.commit()
            
            print("Admin user created")
        else:
            print("Admin user already exists")

if __name__ == '__main__':
    seed_admin()
