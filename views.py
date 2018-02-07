from flask import Flask, render_template, flash, redirect, request, url_for, session, logging
# from data import Articles
# from flaskext.mysql import MySQL
# from flask_mysqldb import MySQL
# from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
from app import app
from models.user_model import User
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
	#create cursor
	# cur = mysql.connection.cursor()

	#get Articles
	# result_todo = cur.execute("SELECT * FROM articles WHERE active=TRUE")
	# articles_todo = cur.fetchall()
    #
	# result_done = cur.execute("SELECT * FROM articles WHERE active=FALSE")
	# articles_done = cur.fetchall()
    #
	# if result_todo > 0 or result_done > 0:
	# 	return render_template('articles.html', articles_todo=articles_todo, articles_done = articles_done)
	# else:
	# 	msg = 'No Articles Found'
	# 	return render_template('articles.html', msg=msg)
    #
	# cur.close()

@app.route('/article/<string:id>/')
def article(id):

	article = Articles.query.filter(Articles.id == id).first()
	#create cursor
	# cur = mysql.connection.cursor()
    #
	# #get Articles
	# result = cur.execute("SELECT * FROM articles WHERE id=%s", [id])
    #
	# article = cur.fetchone()

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

		a_user = User(name, email, username, password) #fix
		db.session.add(user)
		db.session.commit()

		#create cursor
		# cur = mysql.connection.cursor()
        #
		# #execute query
		# cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))
        #
		# #commit to DB
		# mysql.connection.commit()
        #
		# #close connection
		# cur.close()

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

		#create cursor
		cur = mysql.connection.cursor()

		#get user by username
		result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

		if result > 0:
			# get stored hash
			data = cur.fetchone()
			password = data['password']

			if sha256_crypt.verify(password_candidate,password):
				# app.logger.info('PASSWORD MATCHED')
				#PASSED
				session['logged_in'] = True
				session['username'] = username

				flash('You are now logged in', 'success')
				return redirect(url_for('dashboard'))
			else:
				# app.logger.info('PASSWORD NOT MATCHED')
				error = 'Invalid login'
				return render_template('login.html',error=error)
			cur.close()
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
	#create cursor
	cur = mysql.connection.cursor()

	#get todo Articles
	result_todo = cur.execute("SELECT * FROM articles WHERE active=TRUE")
	articles_todo = cur.fetchall()

	#get todo Articles
	result_done = cur.execute("SELECT * FROM articles WHERE active=FALSE")
	articles_done = cur.fetchall()



	if result_todo > 0 or result_done > 0:
		return render_template('dashboard.html', articles_todo=articles_todo, articles_done=articles_done)
	else:
		msg = 'No Articles Found'
		return render_template('dashboard.html', msg=msg)

	cur.close()

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

		#create cursor
		cur = mysql.connection.cursor()

		#execute
		cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)", (title, body, session['username']))

		#commit to database
		mysql.connection.commit()

		#close connection
		cur.close()

		flash('Article Created', 'success')

		return redirect(url_for('dashboard'))

	return render_template('add_article.html', form=form)

#edit article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):

	# create cursor
	cur=mysql.connection.cursor()

	#get article by id
	result = cur.execute("SELECT * FROM articles WHERE id= %s", [id])

	article = cur.fetchone()

	#get form
	form = ArticleForm(request.form)

	#pupulate article form fields
	form.title.data = article['title']
	form.body.data = article['body']

	if request.method == 'POST' and form.validate():
		title = request.form['title']
		body = request.form['body']

		#create cursor
		cur = mysql.connection.cursor()

		#execute
		cur.execute("UPDATE articles SET title=%s, body=%s WHERE id = %s", (title, body, id))

		#commit to database
		mysql.connection.commit()

		#close connection
		cur.close()

		flash('Article Updated', 'success')

		return redirect(url_for('dashboard'))

	return render_template('edit_article.html', form=form)

#delete article
@app.route('/delete_article/<string:id>', methods = ['POST'])
@is_logged_in
def delete_article(id):
	#create cursor
	cur = mysql.connection.cursor()

	#execute
	# cur.execute("DELETE FROM articles WHERE id= %s", [id])
	cur.execute("UPDATE articles SET active=FALSE WHERE id=%s", (id))

	#commit
	mysql.connection.commit()

	#close connection
	cur.close()

	flash('Article Deleted', 'success')

	return redirect(url_for('dashboard'))

#delete article
@app.route('/reactivate_article/<string:id>', methods = ['POST'])
@is_logged_in
def reactivate_article(id):
	#create cursor
	cur = mysql.connection.cursor()

	#execute
	# cur.execute("DELETE FROM articles WHERE id= %s", [id])
	cur.execute("UPDATE articles SET active=TRUE WHERE id=%s", (id))

	#commit
	mysql.connection.commit()

	#close connection
	cur.close()

	flash('Article Reactivated', 'success')

	return redirect(url_for('dashboard'))

if __name__ == '__main__':
	app.run(debug=True)
