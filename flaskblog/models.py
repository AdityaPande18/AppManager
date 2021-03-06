from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	image_file = db.Column(db.String(20), nullable=False, default='M.jpg')
	password = db.Column(db.String(60), nullable=False)
	apps = db.relationship('App', backref='author', lazy=True)

	def __repr__(self):
		return f"User('{self.username}', '{self.apps}', '{self.image_file}')"


class App(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), unique=True, nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	status = db.Column(db.Boolean, default=False, nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

	def __repr__(self):
		return f"User('{self.name}', '{self.date_posted}', '{self.status}')"