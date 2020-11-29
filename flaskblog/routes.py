from flask import render_template, url_for, flash, redirect, request, abort
import secrets
from PIL import Image
import os
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, AppForm
from flaskblog.models import User, App
from flaskblog import app, db, bcrypt, api
from flask_login import login_user, current_user, logout_user, login_required
from flask_restful import Resource, request


class TodoSimple(Resource):
    def get(self):
        name = request.args['name']
        app = App.query.filter_by(name=name).values('status')
        res = -1
        for i in app:
            res = i[0]
        if res == -1:
            return {'Status':'Not Registered'}
        elif res == 0:
            return {'Status':'Inactive'}
        else:
        	return {'Status':'Active'}

api.add_resource(TodoSimple, '/check_status')

@app.route("/")
@app.route("/home")
def home():
    app = App.query.all()
    return render_template('home.html', len= len(app),app=app)


@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)   

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/app/new", methods=['GET', 'POST'])
@login_required
def new_app():
    form = AppForm()
    if form.validate_on_submit():
        app = App(name=form.name.data, status=form.status.data, author=current_user)
        db.session.add(app)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_app.html', title='New App', form=form, legend='New App')

# @app.route("/post/<int:post_id>")
# @login_required
# def post(post_id):
#     post = Post.query.get_or_404(post_id)
#     return render_template('post.html', title=post.title, post=post )

@app.route("/app/update", methods=['POST'])
@login_required
def change_status():
    app_name = request.form['app_name']
    changed_status = "changed_status" in request.form

    print('-----------')
    print(changed_status)
    print('-----------')

    app = App.query.filter_by(name=app_name).update(dict(status=changed_status))
    db.session.commit()

    return redirect(url_for('home'))

@app.route("/app/delete_app", methods=['POST'])
@login_required
def delete_app():
    app_name = request.form['app_name']

    App.query.filter_by(name=app_name).delete()
    db.session.commit()

    return redirect(url_for('home'))

@app.errorhandler(404)
def error_404(error):
	return render_template('error_404.html')

@app.errorhandler(403)
def error_403(error):
	return render_template('error_403.html')

@app.errorhandler(500)
def error_500(error):
	return render_template('error_500.html')