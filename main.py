from flask import Flask, render_template, request, flash, redirect, url_for

from config import Config
from app.forms import LoginForm, RegistrationForm
from app.models import Users, User_game
from app import db, app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': Users, 'Post': User_game}

@app.route('/')
@login_required
def home():

    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print("already authenticated")
        return redirect("/")
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()  # SELECT * FROM users WHERE username = var
        if user is None or not user.check_password(form.password.data):
            print('Invalid username or password')
            return redirect("/")
        login_user(user, remember=form.remember_me.data)
        return redirect("/")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        print('Already logged in')
        return redirect("/")
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Users(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        print('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)
