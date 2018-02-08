from app import db
from datetime import datetime

class Users(db.Model):
    __tablename__= 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    username = db.Column(db.String(30))
    password = db.Column(db.String(100))
    register_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), default=db.func.current_timestamp)
    # register_date = db.Column(db.TIMESTAMP, default=db.func.current_timestamp)

    def __repr__(self):
        return '<User %r>' % self.username

    def __str__(self):
        return self.username

    def __init__(self, name, email, username, password):
        self.name = name
        self.email = email
        self.username = username
        self.password = password
        self.register_date = datetime.now()
