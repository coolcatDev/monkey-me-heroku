from app import db
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
class users(db.Model):
	__tablename__ = "Users"

	id = db.Column(db.Integer, primary_key=True)
	userName = db.Column(db.String, nullable=False)
	userEmail = db.Column(db.String, nullable=False)
	userPhone = db.Column(db.String, nullable=False)
	userPass = db.Column(db.String, nullable=False)

	best_friend = db.relationship(
		'users', 
		secondary='BestFriends', 
		primaryjoin='users.id==bestFriends.user_id', 
		secondaryjoin='users.id==bestFriends.best_friend_id', 
		uselist=False, 
		backref=db.backref('best_friend_of', uselist=False)
	)

	def __init__(self, userName, userEmail, userPhone, userPass):

		self.userName = userName
		self.userEmail = userEmail
		self.userPhone = userPhone
		self.userPass = userPass

	def __repr__(self):
		return '{}-{}-{}-{}'.format(self.id, self.userName, self.userEmail, self.userPhone)


class friendships(db.Model):
	__tablename__ = "Friendships"

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
	friend_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)

	userR = db.relationship('users', foreign_keys='friendships.user_id')
	friendR = db.relationship('users', foreign_keys='friendships.friend_id')

	def __init__(self, user_id, friend_id):
		self.user_id = user_id
		self.friend_id = friend_id

	def __repr__(self):
		return '{}-{}-{}-{}'.format(self.user_id, self.friend_id)


class bestFriends(db.Model):

	__tablename__ = "BestFriends"

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
	best_friend_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)

	def __init__(self, user_id, best_friend_id):
		
		self.user_id = user_id
		self.best_friend_id = best_friend_id

	def __repr__(self):
		return '{}-{}-{}-{}'.format(self.user_id, self.best_friend_id)
