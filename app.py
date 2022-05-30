import sys

from flask_socketio import SocketIO
from appfile import create_app, db
from config import get_current_config

app = create_app(get_current_config())
socketio = SocketIO(app)

def create_db():
    db.init_app(app)
    db.create_all()

#routes sorted by when they are rendered
if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'database':
        create_db()
    app.run(debug=True)