from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import PickleType


# post class is the blueprints for all posts
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


# friend request class is used to create objects of friend requests
class FriendRequest(db.Model):
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


# the user class is used to model all users including all the friend creations. However, friend creations do not have
# usernames and emails because they are not real users. They are a feature for users to sort their posts by tagging
# their friends/pets/literally any object they want to create
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
    # friends list of user's friends
    friends_list = db.Column(MutableList.as_mutable(PickleType), default=[])
    # list of user's friend requests
    friend_requests = db.relationship('FriendRequest')
