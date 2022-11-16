from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # account info for login
    email = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    # user basic information
    first_name = db.Column(db.String(20))
    mid_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    gender = db.Column(db.String(20))
    birthday = db.Column(db.String(20))
    age = db.Column(db.Integer)
    # user can make posts
    posts = db.relationship('Posts')
    # list of user's friends
    friends = db.relationship('Friend')


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    # details for the post
    title = db.Column(db.String(30))
    image = db.Column(db.String(20))
    text = db.Column(db.String(1000))
    # post type to sort post
    post_type = db.Column(db)
    # customize the color of th post
    color = db.Column(db.String(20))
    # track posts by user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # tag friends in photos to sort photos
    friends = db.relationship('Friend')

class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # does this friend have account
    account_status = db.Column(db.String(10))
    # user basic information
    ''' so if the friend does not have an account then you can create an instance of them. You will be able to manually
        enter information about that friend to keep track of them. '''
    first_name = db.Column(db.String(20))
    mid_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    gender = db.Column(db.String(20))
    birthday = db.Column(db.String(20))
    age = db.Column(db.Integer)
    # to be friends with people with accounts
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # to tag people in posts
    post_id = db.Column(db.Integer, db.ForeignKey('user.id'))
