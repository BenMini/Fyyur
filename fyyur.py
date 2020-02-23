from app import app, db
from app.models import Artist, Venue, Show


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Artist': Artist, 'Venue': Venue, 'Show': Show}
