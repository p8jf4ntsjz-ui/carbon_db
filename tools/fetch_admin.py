import os
import sys
# Ensure project root is on sys.path when running this script from tools/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run import app
from models import User

def main():
    with app.app_context():
        admin = User.query.filter_by(email='admin@opticrm.com').first()
        if not admin:
            print('No user found with email admin@opticrm.com')
            sys.exit(2)
        # Print a readable dict of the SQLAlchemy object (exclude internal state)
        data = {k: v for k, v in admin.__dict__.items() if k != '_sa_instance_state'}
        print(data)

if __name__ == '__main__':
    main()
