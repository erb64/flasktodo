from flask import Flask, render_template, flash, redirect, request, url_for, session, logging
# from data import Articles
# from flaskext.mysql import MySQL
# from flask_mysqldb import MySQL
# from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

# Config MySQL
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = '123456'
# app.config['MYSQL_DB'] = 'myflaskapp'
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init MYSQL
# mysql = MySQL(app)

# init SQLAlchemy
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/myflaskapp.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456@localhost/myflaskapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
app.config['DEBUG'] = True

db = SQLAlchemy(app)

def init_db():
	from models.user_model import Users
	from models.article_model import Articles
	db.create_all()

@app.before_first_request
def startup_setup():
	init_db()
# Articles = Articles()
