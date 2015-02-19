import os

class BaseConfig(object): 
	SECRET_KEY = "kjdsbfkjgdf78sft"
	UPLOAD_FOLDER = 'static/uploads'

	# LOCAL
	#SQLALCHEMY_DATABASE_URI= 'sqlite:///monkeyDB.db'

	# Heroku
	# Database
	SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
	# S3 BUCKET
	S3_BUCKET = os.environ['S3_BUCKET']
	# S3 ACCESS_KEY
	AWS_ACCESS_KEY = os.environ['AWS_ACCESS_KEY']
	# S3 SECRET_KEY
	AWS_SECRET_KEY = os.environ['AWS_SECRET_KEY']
	