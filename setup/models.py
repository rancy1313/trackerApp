from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    # details for the post
    title = db.Column(db.String(30))
    text = db.Column(db.String(1000))
    image = db.Column(db.String(20))
    # a list that holds the categories of a post. Main use is to sort posts by category
    post_categories = db.Column(MutableList.as_mutable(PickleType), default=[])
    # a list with the name of the image files associated with the post.
    post_images = db.Column(MutableList.as_mutable(PickleType), default=[])
    # who can see the post
    post_privacy = db.Column(db.String(20))
    # customize the color of th post
    color = db.Column(db.String(20))
    # track posts by user
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # tag friends in photos to sort photos
    friends_tagged = db.Column(MutableList.as_mutable(PickleType), default=[])
    friends = db.relationship('Friend')

class Friend_request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    # status of the friend request
    status = db.Column(db.String(10))
    # name of the person getting the request
    receiver_name = db.Column(db.String(30))
    # picture of the person receiving the request
    receiver_profile_picture = db.Column(db.String(50))
    # name of sender
    sender_name = db.Column(db.String(30))
    # picture of the sender
    sender_profile_picture = db.Column(db.String(50))
    # id of user getting the request
    request_to_user_id = db.Column(db.Integer)
    # id of user sending the request
    request_from_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # does this friend have account
    account_status = db.Column(db.String(10))
    # user basic information
    ''' so if the friend does not have an account then you can create an instance of them. You will be able to manually
        enter information about that friend to keep track of them. '''
    first_name = db.Column(db.String(20))
    middle_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    gender = db.Column(db.String(20))
    birthday = db.Column(db.String(20))
    age = db.Column(db.Integer)
    # picture of friend
    profile_picture = db.Column(db.String(50))
    # this is the friends id
    friend_id = db.Column(db.Integer)
    # to link to the users id
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # to tag people in posts
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # account info for login
    email = db.Column(db.String(20), unique=True)
    # to search user's
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    # user basic information
    first_name = db.Column(db.String(20))
    middle_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    bio = db.Column(db.String(100))
    gender = db.Column(db.String(20))
    birthday = db.Column(db.String(20))
    profile_picture = db.Column(db.String(50))
    age = db.Column(db.Integer)
    # user can make posts
    posts = db.relationship('Post')
    # list of user's friends
    friends = db.relationship('Friend')
    # friends list of user's friends
    friends_list = db.Column(MutableList.as_mutable(PickleType), default=[])
    # list of user's friend requests
    friend_requests = db.relationship('Friend_request')
