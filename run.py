import os
from __init__ import create_app, db
from models import User, Opportunity, Prediction, Notification, ActivityLog, Attachment

app = create_app(os.environ.get('FLASK_ENV', 'development'))


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db, 'User': User, 'Opportunity': Opportunity,
        'Prediction': Prediction, 'Notification': Notification,
        'ActivityLog': ActivityLog, 'Attachment': Attachment
    }


if __name__ == '__main__':
    app.run(
        host=os.environ.get('HOST', '0.0.0.0'),
        port=int(os.environ.get('PORT', 5000)),
        debug=os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    )