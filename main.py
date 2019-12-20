from flask import Flask, render_template, request, flash, redirect, url_for

from config import Config
from app.forms import LoginForm, RegistrationForm
from app.models import User, User_games, Games
from app import db, app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Post': User_games}

@app.route('/')
def redirect_home():
    return redirect(url_for("home"))


@app.route('/home')
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    games = Games.query.paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('home', page=games.next_num) \
        if games.has_next else None
    prev_url = url_for('home', page=games.prev_num) \
        if games.has_prev else None
    return render_template('index.html', games = games.items, url_next = next_url, url_prev = prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print("already authenticated")
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()  # SELECT * FROM users WHERE username = var
        if user is None or not user.check_password(form.password.data):
            print('Invalid username or password')
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("home"))
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
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        print('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)
