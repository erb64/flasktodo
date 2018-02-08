from app import db

class Articles(db.Model):
    __tablename__= 'articles'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    author = db.Column(db.String(100))
    body = db.Column(db.Text)
    create_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), default=db.func.current_timestamp)
    active = db.Column(db.Boolean())

    def __repr__(self):
        return '<User %r>' % self.title

    def __str__(self):
        return self.title

    def __init__(self, title, author, body):
        self.title = title
        self.author = author
        self.body = body
