# coding:utf-8
# !/usr/bin/python

from flask import Flask, render_template, redirect, \
    url_for, request, session, flash

from flask.ext.sqlalchemy import SQLAlchemy

import boto
from boto.s3.key import Key
import cStringIO
import os
import sys
import logging


app = Flask(__name__)

db = SQLAlchemy(app)

from models import *

app.config.from_object(os.environ['APP_SETTINGS'])

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)


@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        return redirect(url_for('friendList'))


@app.route('/friendList<int:page>', methods=['GET', 'POST'])
@app.route('/friends')
def friendList(page=1):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        userID = session['user_id']
        userList = (
            users.query
            .join(friendships, users.id == friendships.user_id)
            .add_columns(users.id, users.userName)
            .add_columns(friendships.user_id, friendships.friend_id)
            .filter(friendships.friend_id == userID)
            .paginate(page, 6, False)
        )
        bestFriend = (
            users.query
            .join(bestFriends, users.id == bestFriends.user_id)
            .add_columns(users.id, users.userName, bestFriends.best_friend_id)
            .filter(bestFriends.best_friend_id == userID)
        )
        flash('"Friends"')
        return render_template(
            'friends.html', userList=userList, bestFriend=bestFriend)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userCheck = request.form['username']
        userCheck2 = request.form['password']
        user = (
            users.query
            .filter_by(
                userName=userCheck,
                userPass=userCheck2)
            .first()
        )
        if user:
            session['logged_in'] = True
            session['user_id'] = user.id
            session['user_pass'] = user.userPass
            return redirect(url_for('friendList'))
        else:
            flash('"You have to Login"')
            return render_template('login.html')
    else:
        flash('"Login"')
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('"You have logged out"')
    return render_template('login.html')


@app.route('/allList<int:page><int:sort>', methods=['GET', 'POST'])
@app.route('/users')
def allList(page=1, sort=1):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        user_bf = db.aliased(users, name='user_bf')
        if sort == 1:
            test = users.userName
        if sort == 2:
            test = user_bf.userName
        if sort == 3:
            test = db.func.count(friendships.user_id).desc()
        userList = (
            users.query
            .add_column(db.func.count(friendships.user_id).label("total"))
            .add_column(user_bf.id.label("best_friend"))
            .add_column(user_bf.userName.label("best_friend_name"))
            .outerjoin(friendships, users.id == friendships.user_id)
            .outerjoin(user_bf, users.best_friend)
            .group_by(users.id, user_bf.id)
            .order_by(test)
            .paginate(page, 6, False)
        )
        flash('"Users"')
        return render_template('users.html', userList=userList, sort=sort)


@app.route('/profile<profileId>')
def profile(profileId):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        profileID = profileId
        bestFriend = (
            users.query
            .join(bestFriends, users.id == bestFriends.user_id)
            .add_columns(users.id, users.userName, bestFriends.best_friend_id)
            .filter(bestFriends.best_friend_id == profileID)
        )
        userList = users.query.filter_by(id=profileID)
        flash('"Profile"')
        return render_template(
            'profile.html', userList=userList,
            bestFriend=bestFriend, profileID=profileID)


@app.route('/myProfile')
def myProfile():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        profileID = session['user_id']
        userList = users.query.filter_by(id=profileID).all()
        flash('"My Profile"')
        return render_template('myProfile.html', userList=userList)


@app.route('/addFriend/<userToAdd>')
def addFriend(userToAdd):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        # get loged in user id
        profileID = session['user_id']
        # check friendship doesnt exist to avoid duplication
        frienshipCheck = friendships.query.filter_by(
            user_id=profileID, friend_id=userToAdd).first()
        if frienshipCheck:
            flash('"Friendship exists"')
            return redirect(url_for('friendList'))
        frienshipCheck2 = friendships.query.filter_by(
            user_id=userToAdd, friend_id=profileID).first()
        if frienshipCheck2:
            flash('"Friendship exists"')
            return redirect(url_for('friendList'))
        else:
            newFriend = friendships(
                profileID, userToAdd)
            db.session.add(newFriend)
            newFriend2 = friendships(
                userToAdd, profileID)
            db.session.add(newFriend2)
            db.session.commit()
            flash('"Friendship Created"')
            return redirect(url_for('friendList'))


@app.route('/removeFriend/<userToRemove>')
def removeFriend(userToRemove):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        profileID = session['user_id']
        # remove friendship
        oldFriend = (
            friendships.query
            .filter_by(
                user_id=userToRemove,
                friend_id=profileID)
            .first()
        )
        if oldFriend:
            db.session.delete(oldFriend)
            db.session.commit()
        oldFriend2 = (
            friendships.query
            .filter_by(
                user_id=profileID,
                friend_id=userToRemove)
            .first()
        )
        if oldFriend2:
            db.session.delete(oldFriend2)
            db.session.commit()
        # remove BFF if exists
        oldBFFCheck = (
            bestFriends.query
            .filter_by(
                user_id=userToRemove,
                best_friend_id=profileID)
            .first()
        )
        if oldBFFCheck:
            db.session.delete(oldBFFCheck)
            db.session.commit()
        oldBFFCheck = (
            bestFriends.query
            .filter_by(
                user_id=profileID,
                best_friend_id=userToRemove)
            .first()
        )
        if oldBFFCheck:
            db.session.delete(oldBFFCheck)
            db.session.commit()
        flash('"Friendship removed"')
        return redirect(url_for('friendList'))


@app.route('/addBestFriend/<userToRequest>')
def addBestFriend(userToRequest):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        profileID = session['user_id']
        # remove existing BFF of requester
        oldBFFCheck = (
            bestFriends.query
            .filter_by(best_friend_id=profileID)
            .first()
        )
        if oldBFFCheck:
            db.session.delete(oldBFFCheck)
            db.session.commit()
        oldBFFCheck = (
            bestFriends.query
            .filter_by(user_id=profileID)
            .first()
        )
        if oldBFFCheck:
            db.session.delete(oldBFFCheck)
            db.session.commit()
        # of requested
        oldBFFCheck = (
            bestFriends.query
            .filter_by(best_friend_id=userToRequest)
            .first()
        )
        if oldBFFCheck:
            db.session.delete(oldBFFCheck)
            db.session.commit()
        oldBFFCheck = (
            bestFriends.query
            .filter_by(user_id=userToRequest)
            .first()
        )
        if oldBFFCheck:
            db.session.delete(oldBFFCheck)
            db.session.commit()
        # add the new Bestfriend
        newBFF = bestFriends(profileID, userToRequest)
        db.session.add(newBFF)
        db.session.commit()
        newBFF2 = bestFriends(userToRequest, profileID)
        db.session.add(newBFF2)
        db.session.commit()
        flash('"Best Friend Created"')
        return redirect(url_for('friendList'))


def allowed_file(filename):
    ALLOWED_EXTENSIONS = set(['jpg'])
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/register')
def register():
    if session.get('logged_in'):
        return redirect(url_for('friendList'))
    else:
        flash('"Register"')
        return render_template('register.html')


@app.route('/registering', methods=['GET', 'POST'])
def registering():
    if request.method == 'POST':
        userCheck = request.form['username']
        userCheck2 = request.form['email']
        userCheck3 = request.form['password']
        userCheck4 = request.form['passwordCheck']
        userCheck5 = request.form['phone']
        if userCheck == "":
            flash('"Username required"')
            return render_template('register.html')
        userName = users.query.filter_by(userName=userCheck).first()
        if userName:
            flash('"Username Taken'"")
            return render_template('register.html')
        if userCheck2 == "":
            flash('"Email required"')
            return render_template('register.html')
        if userCheck5 == "":
            flash('"Phone required"')
            return render_template('register.html')
        if userCheck3 == "":
            flash('"Password required"')
            return render_template('register.html')
        if userCheck4 == "":
            flash('"Confirm password"')
        if userCheck3 == userCheck4:
            file = request.files['file']
            if file and allowed_file(file.filename):
                    newUser = users(userCheck, userCheck2, userCheck5, userCheck3)
                    db.session.add(newUser)
                    db.session.commit()
                    userName = users.query.filter_by(
                        userName=userCheck, userPass=userCheck3).first()
                    session['logged_in'] = True
                    session['user_id'] = userName.id
                    # image part
                    filename = str(userName.id)
                    # S3_BUCKET, AWS_ACCESS_KEY & AWS_SECRET_KEY = HEROKU envar from config.py
                    conn = boto.connect_s3(
                        app.config['AWS_ACCESS_KEY'],
                        app.config['AWS_SECRET_KEY']
                    )
                    bucket = conn.get_bucket(app.config['S3_BUCKET'])
                    key = '%s.jpg' % filename
                    k = Key(bucket)
                    k.key = key
                    buff = cStringIO.StringIO()
                    buff.write(file.read())
                    buff.seek(0)
                    k.set_contents_from_file(buff)
                    flash('"Registered Successfully"')
                    return redirect(url_for('friendList'))
            else:
                flash('"Add an image (.jpg)"')
                return render_template('register.html')
        else:
            flash('"Retype passwords"')
            return render_template('register.html')
        
    else:
        return render_template('register.html')


@app.route('/deleteAccount')
def deleteAccount():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        # target
        userToDelete = session['user_id']
        # Friendships
        oldAccountFriendships1 = friendships.query.filter_by(
            user_id=userToDelete).all()
        for row in oldAccountFriendships1:
            db.session.delete(row)
            db.session.commit()
        oldAccountFriendships2 = friendships.query.filter_by(
            friend_id=userToDelete).all()
        for row in oldAccountFriendships2:
            db.session.delete(row)
            db.session.commit()
        # BFF
        oldBFFCheck = (
            bestFriends.query
            .filter_by(best_friend_id=userToDelete)
            .first()
        )
        if oldBFFCheck:
            db.session.delete(oldBFFCheck)
            db.session.commit()
        oldBFFCheck = (
            bestFriends.query
            .filter_by(user_id=userToDelete)
            .first()
        )
        if oldBFFCheck:
            db.session.delete(oldBFFCheck)
            db.session.commit()
        # delete user    
        oldAccountUser = users.query.filter_by(id=userToDelete).first()
        db.session.delete(oldAccountUser)
        db.session.commit()

        filename = str(userToDelete) + '.jpg'
        bucket.delete_key(filename)
        flash('"Account deleted"')
        return redirect(url_for('logout'))


@app.route('/editAccount')
def editAccount():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        profileID = session['user_id']
        userList = users.query.filter_by(id=profileID).all()
        flash('"Edit profile"')
        return render_template('edit.html', userList=userList)


@app.route('/saveEditAccount', methods=['GET', 'POST'])
def saveEditAccount():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        if request.method == 'POST':
            userCheck1 = request.form['userName']
            userCheck2 = request.form['userEmail']
            userCheck3 = request.form['userPhone']
            userCheck4 = request.form['userPassA']
            userCheck5 = request.form['userPassB']
            profileID = session['user_id']
            if userCheck1 == "":
                        flash('"Username required"')
                        return redirect(url_for('editAccount'))
            newUser = users.query.filter_by(userName=userCheck1).first()
            if newUser:
                if newUser.id != profileID:
                    flash('"Username Taken"')
                    return redirect(url_for('editAccount'))
                else:
                    if userCheck2 == "":
                        flash('"Email required"')
                        return redirect(url_for('editAccount'))
                    if userCheck3 == "":
                        flash('"Phone required"')
                        return redirect(url_for('editAccount'))
                    if userCheck4 == "":
                        flash('"Password required"')
                        return redirect(url_for('editAccount'))
                    if userCheck5 == "":
                        flash('"Confirm password"')
                        return redirect(url_for('editAccount'))
                    file = request.files['file']
                    if file and allowed_file(file.filename):
                        if userCheck4 == userCheck5:
                            newUser = users.query.get(profileID)
                            newUser.userName = userCheck1
                            newUser.userEmail = userCheck2
                            newUser.userPhone = userCheck3
                            newUser.userPass = userCheck4
                            db.session.commit()
                            filename = str(profileID)
                            # S3_BUCKET, AWS_ACCESS_KEY & AWS_SECRET_KEY = HEROKU envar from config.py
                            conn = boto.connect_s3(
                                app.config['AWS_ACCESS_KEY'], 
                                app.config['AWS_SECRET_KEY']
                            )
                            bucket = conn.get_bucket(app.config['S3_BUCKET'])
                            bucket.delete_key(filename + '.jpg')    
                            key = '%s.jpg' % filename
                            k = Key(bucket)
                            k.key = key
                            buff = cStringIO.StringIO()
                            buff.write(file.read())
                            buff.seek(0)
                            k.set_contents_from_file(buff)
                            flash('"Saved"')
                            return redirect(url_for('myProfile'))
                        else:
                            flash('"Retype passwords"')
                        return redirect(url_for('editAccount'))
                    else:
                        flash('"Image has to be .jpg format"')
                        return redirect(url_for('editAccount'))
            else:
                if userCheck2 == "":
                    flash('"Email required"')
                    return redirect(url_for('editAccount'))
                if userCheck3 == "":
                    flash('"Phone required"')
                    return redirect(url_for('editAccount'))
                if userCheck4 == "":
                    flash('"Password required"')
                    return redirect(url_for('editAccount'))
                if userCheck5 == "":
                    flash('"Confirm password"')
                    return redirect(url_for('editAccount'))
                file = request.files['file']
                if file and allowed_file(file.filename):
                    if userCheck4 == userCheck5:
                        newUser = users.query.get(profileID)
                        newUser.userName = userCheck1
                        newUser.userEmail = userCheck2
                        newUser.userPhone = userCheck3
                        newUser.userPass = userCheck4
                        db.session.commit()
                        filename = str(profileID)
                        # S3_BUCKET, AWS_ACCESS_KEY & AWS_SECRET_KEY = HEROKU envar from config.py
                        conn = boto.connect_s3(
                            app.config['AWS_ACCESS_KEY'], 
                            app.config['AWS_SECRET_KEY']
                        )
                        bucket = conn.get_bucket(app.config['S3_BUCKET'])
                        bucket.delete_key(filename + '.jpg')
                        key = '%s.jpg' % filename
                        k = Key(bucket)
                        k.key = key
                        buff = cStringIO.StringIO()
                        buff.write(file.read())
                        buff.seek(0)
                        k.set_contents_from_file(buff)
                        flash('"Saved"')
                        return redirect(url_for('myProfile'))
                    else:
                        flash('"Retype passwords"')
                        return redirect(url_for('editAccount'))
                else:
                    flash('"Add an image (.jpg)"')
                    return redirect(url_for('editAccount'))
        else:
            return render_template('myProfile.html')

if __name__ == '__main__':
    app.run()