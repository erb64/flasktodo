from flask import Flask, render_template, flash, redirect, request, url_for, session, logging
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from app import app, db
from models.user_model import Users
from models.article_model import Articles


@app.route('/')
def index():
	return render_template('home.html')

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/articles')
def articles():
	articles_todo = Articles.query.filter(Articles.active == True).all()
	articles_done = Articles.query.filter(Articles.active == False).all()

	if(articles_todo and articles_done):
		return render_template('articles.html', articles_todo=articles_todo, articles_done = articles_done)
	else:
		msg = 'No Articles Found'
		return render_template('articles.html', msg=msg)

@app.route('/article/<string:id>/')
def article(id):

	article = Articles.query.filter(Articles.id == id).first()

	return render_template('article.html', article=article)

class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	username = StringField('Username', [validators.Length(min=4, max=25)])
	email = StringField('Email', [validators.Length(min=6, max=50)])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Passwords do not match'),
	])
	confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))

		user = Users(name, email, username, password)
		db.session.add(user)
		db.session.commit()

		flash('You are now registered and can log in', 'success')

		return redirect(url_for('login'))
	return render_template('register.html', form=form)

#user login
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		#get form fields
		username = request.form['username']
		password_candidate = request.form['password']

		user = Users.query.filter(Users.username == username).first()

		if(user):
			password = user.password

			if sha256_crypt.verify(password_candidate,password):
				session['logged_in'] = True
				session['username'] = username

				flash('You are now logged in', 'success')
				return redirect(url_for('dashboard'))
		else:
			error = 'Username not found'
			# app.logger.info('NO USER')
			return render_template('login.html',error=error)

	return render_template('login.html')

# check if user logged in
def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unathorized, Please login', 'danger')
			return redirect(url_for('login'))
	return wrap

#logout
@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash('You are now logged out', 'success')
	return redirect(url_for('login'))

@app.route('/dashboard')
@is_logged_in
def dashboard():
	articles_todo = Articles.query.filter(Articles.active == True).all()
	articles_done = Articles.query.filter(Articles.active == False).all()

	if(articles_todo and articles_done):
		return render_template('dashboard.html', articles_todo=articles_todo, articles_done = articles_done)
	else:
		msg = 'No Articles Found'
		return render_template('dashboard.html', msg=msg)

class ArticleForm(Form):
	title = StringField('Title', [validators.Length(min=1, max=200)])
	body = TextAreaField('Body', [validators.Length(min=30)])

@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
	form = ArticleForm(request.form)
	if request.method == 'POST' and form.validate():
		title = form.title.data
		body = form.body.data
		author = session['username']

		article = Articles(title, author, body)
		db.session.add(article)
		db.session.commit()

		flash('Article Created', 'success')

		return redirect(url_for('dashboard'))

	return render_template('add_article.html', form=form)

#edit article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):

	article = Articles.query.filter(Articles.id == id).first()

	#get form
	form = ArticleForm(request.form)

	#pupulate article form fields
	form.title.data = article['title']
	form.body.data = article['body']

	if request.method == 'POST' and form.validate():
		title = request.form['title']
		body = request.form['body']

		article = Articles.query.filter_by(id=id).update(dict(title=title))
		article = Articles.query.filter_by(id=id).update(dict(body=body))
		db.session.commit()

		flash('Article Updated', 'success')

		return redirect(url_for('dashboard'))

	return render_template('edit_article.html', form=form)

# Complete article
@app.route('/delete_article/<string:id>', methods = ['POST'])
@is_logged_in
def delete_article(id):

	article = Articles.query.filter_by(id=id).update(dict(active=False))
	db.session.commit()

	flash('Task Completed', 'success')

	return redirect(url_for('dashboard'))

# Reactivate article
@app.route('/reactivate_article/<string:id>', methods = ['POST'])
@is_logged_in
def reactivate_article(id):

	article = Articles.query.filter_by(id=id).update(dict(active=True))
	db.session.commit()

	flash('Task Reactivated', 'success')

	return redirect(url_for('dashboard'))

if __name__ == '__main__':
	app.secret_key = 'super secret key'
	app.run(debug=True)
