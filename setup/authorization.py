from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from .import db
from flask_login import login_user, login_required, logout_user, current_user
import os
import json
import random
# for image uploading
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
authorization = Blueprint('authorization', __name__)

@authorization.route('/login', methods=['GET', 'POST'])
def login():
    # this function renders login.html if method == get and logs in user if method == post
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # .first() returns first result but should only be one
        user = User.query.filter_by(email=email).first()

        # checks to see if the user exists by checking if the password entered matches the db password
        # it is also hashed in the db
        # if password does not match db password then user can't log in to that account
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category="success")
                # makes it so user doesn't have to log in everytime
                login_user(user, remember=True)
                return redirect(url_for('features.user_home'))
            else:
                flash('Incorrect password, try again.', category="error")
        else:
            flash('Email does not exist.', category="error")
    return render_template("login.html", user=current_user)


# can't access this route unless user is logged in
# just logs out user and redirects to login page
@authorization.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('authorization.login'))


@authorization.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    tmp_users = User.query.all()
    # this list of usernames is used in the javascript to let user's that are trying to create an account know if a
    # username is taken
    list_of_usernames = []
    for user in tmp_users:
        list_of_usernames.append(user.username)
    # renders sign up page if get method and creates user row if a post method
    if request.method == 'POST':
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        last_name = request.form.get('last_name')
        bio = request.form.get('bio')
        gender = request.form.get('gender')
        birthday = request.form.get('birthday')
        username = request.form.get('username')
        email = request.form.get('email')
        # iterate through all form variables to check for special chars
        tmp_lst = [first_name, middle_name, last_name, username, bio, gender]
        # all special chars minus @ and . because it is needed to make an email
        # loop make sures no special characters are in and if it is then refreshes page
        # i allowed for some special chars like ) , - _ : ; for smiley faces :)
        special_chars = '`~$%^&*(=+|[]{}<>\"\\/'
        for char in special_chars:
            for form_var in tmp_lst:
                # @ and . are allowed in email but nothing else
                if (form_var != email) and ('@' in form_var):
                    flash('@ or . only allowed in email', category="error")
                    return redirect(url_for('authorization.sign_up'))
                # checks every other char
                if char in form_var:
                    tmp = 'No special chars allowed in ' + form_var
                    flash(tmp, category="error")
                    return redirect(url_for('authorization.sign_up'))

        # umm might need more password restrictions
        # I will consider making better password restriction in the future
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        # fetch user to see if the email is already in use
        # can't have two users with same email
        # these are some slight restrictions for the users email/password
        user = User.query.filter_by(email=email).first()
        if user:
            flash('This email already exists.', category="error")
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category="error")
        elif len(first_name) < 2 or len(last_name) < 2 or len(gender) < 2:
            flash('First name, last name, and gender must be greater than 1 character.', category="error")
        elif password1 != password2:
            flash('Passwords don\'t match.', category="error")
        elif len(password1) < 1:
            flash('Password must be greater than 0 characters', category="error")
        else:
            # create path for image storing
            target = os.path.join(APP_ROOT, 'images/')
            # if path doesn't exist create it
            if not os.path.isdir(target):
                os.mkdir(target)
            # getting submitted image to store in image folder
            for file in request.files.getlist('file'):
                if file.filename == "":
                    # if user didn't submit a profile picture, then a temporary fake picture is used
                    filename = 'tmp_picture.png'
                else:
                    # the file name will be called after the user's email because every user has a unique email
                    filename = email + '.jpg'
                    destination = "/".join([target, filename])
                    file.save(destination)
            # add the user
            # if user passes restrictions then their account is created
            # redirects to login page for user to login/ could be changed to redirect to user homepage
            new_user = User(email=email, first_name=first_name, middle_name=middle_name, last_name=last_name, bio=bio,
                            gender=gender, birthday=birthday, profile_picture=filename, username=username,
                            password=generate_password_hash(password1, method="sha256"))
            db.session.add(new_user)
            db.session.commit()
            #login_user(user, remember=True)
            flash('Account created!!! You can login now!!', category="success")
            return redirect(url_for('authorization.login'))
    return render_template("sign_up.html", user=current_user, list_of_usernames=list_of_usernames)

