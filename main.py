from flask import Flask, render_template, request, flash, redirect, url_for, g

from config import Config
from app.forms import LoginForm, RegistrationForm, EditProfileForm, SearchForm
from app.models import User, User_games, Games
from app import db, app
from flask_login import current_user, login_user, logout_user, login_required
from datetime import datetime

from  sqlalchemy.sql.expression import func


@app.route('/')
def redirect_home():
    return redirect("/home")


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        g.search_form = SearchForm()


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    page = request.args.get('page', 1, type=int)
    games = Games.query.paginate(page, app.config['POSTS_PER_PAGE'], False)

    user_games_objects = User_games.query.filter_by(user_id=current_user.id).all()
    user_games = [it.game_id for it in user_games_objects]

    next_url = url_for('home', page=games.next_num) \
        if games.has_next else None
    prev_url = url_for('home', page=games.prev_num) \
        if games.has_prev else None
    games = games.items

    return render_template('index.html', games=games, ugames=user_games,
                           url_next=next_url, url_prev=prev_url, current_page=page,
                           search=g.search_form)


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


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    games = Games.query.join(User_games, Games.id == User_games.game_id).filter_by(user_id=user.id).all()
    return render_template('profile.html', user=user, games=games)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.description = form.description.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.description.data = current_user.description
    return render_template('edit_profile.html', form=form)


# ----------------------- Adding and removing favourite games ---------------------------
@app.route('/addgame')
@login_required
def addgame():
    game_id = request.args.get('id', -1, type=int)
    return_to = request.args.get('from', '/', type=str)
    page_num = request.args.get('page', '0', type=str)
    if game_id == 0:
        return redirect(return_to)
    if return_to == 'user':
        return_to += '/' + current_user.username
    if return_to == 'home':
        return_to += '?page=' + page_num
    added_game = User_games(user_id=current_user.id, game_id=game_id)
    db.session.add(added_game)
    db.session.commit()
    return redirect(return_to)


@app.route('/removegame')
@login_required
def removegame():
    game_id = request.args.get('id', 0, type=int)
    return_to = request.args.get('from', '/', type=str)
    page_num = request.args.get('page', '0', type=str)
    if game_id == 0:
        return redirect(url_for(return_to))
    if return_to == 'user':
        return_to += '/' + current_user.username
    if return_to == 'home':
        return_to += '?page=' + page_num
    game_to_remove = db.session.query(User_games).filter_by(user_id=current_user.id, game_id=game_id).first()
    db.session.delete(game_to_remove)
    db.session.commit()
    return redirect(return_to)


# ---------------------------------- Search ----------------------------------

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    by = request.args.get('by', 'invalid', type=str)
    search_value = request.args.get('value', '', type=str)

    if by == 'name':
        if search_value == '':
            search_result = "%{}%".format(g.search_form.search.data)
            search_value = g.search_form.search.data
        else:
            search_result = "%{}%".format(search_value)
        games = Games.query.filter(Games.name.like(search_result))
    elif by == 'new':
        games = Games.query.order_by(Games.released.desc())
    elif by == 'top':
        games = Games.query.order_by(Games.rating.desc())
    elif by == 'all':
        games = Games.query.order_by(func.rand())


    page = request.args.get('page', 1, type=int)
    games = games.paginate(page, app.config['POSTS_PER_PAGE'], False)

    user_games_objects = User_games.query.filter_by(user_id=current_user.id).all()
    user_games = [it.game_id for it in user_games_objects]

    next_url = url_for('search', by=by, value=search_value, page=games.next_num) \
        if games.has_next else None
    prev_url = url_for('search', by=by, value=search_value, page=games.prev_num) \
        if games.has_prev else None
    games = games.items

    return render_template('search.html', games=games, ugames=user_games,
                           url_next=next_url, url_prev=prev_url, current_page=page)
