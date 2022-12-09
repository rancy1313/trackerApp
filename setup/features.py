from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from .models import User, FriendRequest, Post
from . import db
import os

# for image uploading
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
features = Blueprint('features', __name__)
# create path for image storing
target = os.path.join(APP_ROOT, 'images/')
# if path doesn't exist create it
if not os.path.isdir(target):
    os.mkdir(target)


# this function just returns a specific image based on the name from the directory
@features.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory('images', filename)


# th user home functions is used anytime the user needs to be directed back to their homepage.
@features.route('/user-home', methods=['GET', 'POST'])
@login_required
def user_home():
    """ this loop is used to update friend info when ever the user goes to their homepage. Since the friend objects
    are stored in a list, they don't get updated if there are changes made outside the loop. For example, if one of the
    user's friends updates their profile, then that change will not be updated om the friend object inside
    the current user's friends list. So this loop goes through the current user's friends list and reasigns each friend
    in there with the updated info by id. """
    all_requests = db.session.query(FriendRequest).order_by(FriendRequest.id.desc()).all()
    list_of_user_friends = []
    for index, friend in enumerate(current_user.friends_list):
        tmp_user = User.query.filter_by(id=friend.id).first()
        current_user.friends_list[index] = tmp_user
        list_of_user_friends.append(tmp_user)
    db.session.commit()
    return render_template("home.html", user=current_user, all_requests=all_requests,
                           list_of_user_friends=list_of_user_friends)


# the search friends function is used to search for and send friend requests. It takes a username entered by the user
# and returns users that match that username. There are restrictions such as not being able to search yourself.
@features.route('/search-friends', methods=['GET', 'POST'])
@login_required
def search_friends():
    # search is done by username because all usernames are unique
    # retrieve username from form
    username = request.form.get('username')
    # search db for user with that email
    friend = User.query.filter_by(username=username).first()
    # fixes bug were wrong friend is displaying. It is just getting a random friend so set friend
    # to None if email is none
    if username is None:
        friend = None
    if request.method == "POST":
        # stop people from adding themselves
        if current_user.username == username:
            flash('Not allowed to search yourself', category="error")
            # set friend to None so None type is passed to search friend page
            friend = None
        elif friend:
            flash('Friend found', category="success")
        else:
            flash('Error. Friend not found', category="error")
    return render_template("search_friend.html", user=current_user, friend=friend)


#  After searching for a friend. The user can send a friend request. It will be sent to the user's friend, and if they
#  accept, then both users will be each other's friends. Only one friend request can be sent at a time. If the friend
#  declines the friend request then the user can send another one.
@features.route('/search-friend/send-friend-request/<int:user_id>', methods=['GET', 'POST'])
@login_required
def send_friend_request(user_id):
    # find friend by User id
    friend = User.query.filter_by(id=user_id).first()
    # if friend is in current user friends list then they are already friends
    if friend in current_user.friends_list:
        flash('Error. Already friends.', category="error")
        return redirect(url_for('features.search_friends'))
    # only one friend request to a person can be made until.
    # The person has to wait until the last request was cancelled
    for tmp_request in current_user.friend_requests:
        if tmp_request.request_to_user_id == user_id:
            flash('Error. There is already a pending friend request to this person.', category="error")
            return redirect(url_for('features.search_friends'))
    # check friend's friend requests and if they sent the user one already then current user cannot send one to the
    # friend. They have to accept/decline the one sent from the friend.
    for tmp_request in friend.friend_requests:
        if tmp_request.request_from_user_id == user_id:
            flash('Error. There is already a pending friend request from this person.', category="error")
            return redirect(url_for('features.search_friends'))
    # if post request then proceed to send friend request
    if request.method == 'POST':
        # save the profile picture of the receiver so that the sender can see who they see the request to
        filename_receiver = friend.profile_picture
        # save the profile picture of the sender so the receiver can see who sent the request
        filename_sender = current_user.profile_picture
        # if not already friends then send request
        # save names of the receiver
        tmp_receiver_name = friend.first_name + " " + friend.middle_name + " " + friend.last_name
        # save name of the sender
        tmp_sender_name = current_user.first_name + " " + current_user.middle_name + " " + current_user.last_name
        tmp_request = FriendRequest(status="PENDING", receiver_name=tmp_receiver_name, sender_name=tmp_sender_name,
                                    request_to_user_id=user_id, request_from_user_id=current_user.id,
                                    receiver_profile_picture=filename_receiver, sender_profile_picture=filename_sender)
        db.session.add(tmp_request)
        db.session.commit()
        flash('Request Sent.', category="success")
        return redirect(url_for('features.search_friends'))


# If a user is sent a friend request then they can accept it and then become friends with the sender.
@features.route('/user-home/accept-friend-request/<int:request_id>', methods=['GET', 'POST'])
@login_required
def accept_friend_request(request_id):
    # search friend request by id to delete
    tmp_request = FriendRequest.query.filter_by(id=request_id).first()
    # get the information from the person who sent the request
    tmp_user = User.query.filter_by(id=tmp_request.request_from_user_id).first()
    # if request exist then delete and redirect to home
    if tmp_request:
        # you can't directly add current_user to friends list because for some reason counts it as none type
        # ,so I am setting tmp_curr to current user
        tmp_curr = User.query.filter_by(id=current_user.id).first()
        # add each user to each other's friends list
        tmp_user.friends_list.append(tmp_curr)
        current_user.friends_list.append(tmp_user)
        db.session.commit()
        # now we have to delete the friend request because it was accepted
        db.session.delete(tmp_request)
        db.session.commit()
        flash('Friend added', category="success")
        return redirect(url_for('features.user_home'))
    else:
        flash('Error.', category="error")
        return redirect(url_for('features.user_home'))


# If a user wishes to remove a friend from their friend list then they can remove them when viewing that person's page
@features.route('/user-home/view-friend-profile/remove-friend/<int:friend_id>', methods=['GET', 'POST'])
@login_required
def remove_friend(friend_id):
    # find friend that the user is trying to delete by id
    friend = User.query.filter_by(id=friend_id).first()
    # simple test to make sure user and friend are in each other's friend's list. Probably unnecessary.
    if friend in current_user.friends_list and current_user in friend.friends_list:
        current_user.friends_list.remove(friend)
        friend.friends_list.remove(current_user)
        db.session.commit()
        flash('Friend removed', category="success")
        return redirect(url_for('features.user_home'))
        # return redirect(url_for('features.view_friend_profile'), friend_id=friend_id)
    elif friend.username is None:
        current_user.friends_list.remove(friend)
        db.session.delete(friend)
        db.session.commit()
        flash('Friend Creation deleted.', category="success")
        return redirect(url_for('features.user_home'))
    else:
        flash('Error.', category="error")
        return redirect(url_for('features.user_home'))


# If a user gets a friend request from someone they do not want to be friends with, then they can cancel that person's
# friend request.
@features.route('/user-home/cancel-friend-request/<int:request_id>', methods=['GET', 'POST'])
@login_required
def cancel_friend_request(request_id):
    # search friend request by id to delete
    tmp_request = FriendRequest.query.filter_by(id=request_id).first()
    # if request exist then delete and redirect to home
    if tmp_request:
        db.session.delete(tmp_request)
        db.session.commit()
        flash('Request cancelled', category="success")
        return redirect(url_for('features.user_home'))
    else:
        flash('Error.', category="error")
        return redirect(url_for('features.user_home'))


#  The user can view anyone's profile if the button is available. Usually available from looking at friends lists
@features.route('/user-home/view-friend-profile/<int:friend_id>', methods=['GET', 'POST'])
@login_required
def view_friend_profile(friend_id):
    # search friend by id to view profile
    friend = User.query.filter_by(id=friend_id).first()
    friends_of_friend = []
    for x in friend.friends_list:
        tmp_user = User.query.filter_by(id=x.id).first()
        friends_of_friend.append(tmp_user)
    #friends_of_friend = friend.friends_list
    return render_template('friend_page.html', friend=friend, user=current_user, friends_of_friend=friends_of_friend)


# this is to send friend requests when either viewing someone's page that is not your friend or when sending a friend
# request to a user from a friends friend list
@features.route('/view-friend-profile/add_friend_from_friend/<int:user_id>/<int:curr_page_user_id>',
                methods=['GET', 'POST'])
@login_required
def add_friend_from_friend(user_id, curr_page_user_id):
    if request.method == 'POST':
        # only one friend request to a person can be made until.
        # The person has to wait until the last request was cancelled
        for tmp_request in current_user.friend_requests:
            if tmp_request.request_to_user_id == user_id:
                flash('Error. There is already a pending friend request to this person.', category="error")
                return redirect(url_for('features.view_friend_profile', friend_id=curr_page_user_id))
        tmp_user = User.query.filter_by(id=user_id).first()
        # check friend's friend requests and if they sent the user one already then current user cannot send one to the
        # friend. They have to accept/decline the one sent from the friend.
        for tmp_request in tmp_user.friend_requests:
            if tmp_request.request_from_user_id == user_id:
                flash('Error. There is already a pending friend request from this person.', category="error")
                return redirect(url_for('features.search_friends'))
        # this is here for a just in case but add friend button shouldn't show for friends you're already friends with
        if tmp_user in current_user.friends_list:
            flash('Error. You are already friends with this user.', category="error")
            return redirect(url_for('features.view_friend_profile', friend_id=curr_page_user_id))
        # save the receiver's profile picture
        filename_receiver = tmp_user.profile_picture
        # save the sender's profile picture
        filename_sender = current_user.profile_picture
        # save the receiver's name
        tmp_receiver_name = tmp_user.first_name + " " + tmp_user.middle_name + " " + tmp_user.last_name
        # save the sender's name
        tmp_sender_name = current_user.first_name + " " + current_user.middle_name + " " + current_user.last_name
        # if not already friends then send request
        tmp_request = FriendRequest(status="PENDING", receiver_name=tmp_receiver_name, sender_name=tmp_sender_name,
                                    request_to_user_id=user_id, request_from_user_id=current_user.id,
                                    receiver_profile_picture=filename_receiver,
                                    sender_profile_picture=filename_sender)
        db.session.add(tmp_request)
        db.session.commit()
        flash('Friend request sent test', category="success")
        return redirect(url_for('features.view_friend_profile', friend_id=curr_page_user_id))


# all users can edit their profile. The only thing that cannot be changed yet is a user's username and email
@features.route('/edit-profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_profile(user_id):
    user_being_edited = User.query.filter_by(id=user_id).first()
    if request.method == "POST":
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        last_name = request.form.get('last_name')
        birthday = request.form.get('birthday')
        gender = request.form.get('gender')
        bio = request.form.get('bio')
        picture = request.files.getlist('file')
        # iterate through all form variables to check for special chars
        tmp_lst = [first_name, middle_name, last_name, bio, gender]
        # all special chars minus @ and . because it is needed to make an email
        # loop make sures no special characters are in and if it is then refreshes page
        # i allowed for some special chars like ) , - _ : ; for smiley faces :)
        special_chars = '`@~$%^&*(=+|[]{}<>\"\\/'
        for char in special_chars:
            for form_var in tmp_lst:
                # checks every other char
                if char in form_var:
                    tmp = 'No special chars allowed in: ' + form_var
                    flash(tmp, category="error")
                    return redirect(url_for('features.edit_profile', user_id=user_id))
        # if picture == "" then the that means the user did not submit a new image in the form.
        # Therefore, if picture != "" then the user is trying to submit a new photo
        if picture[0].filename != "":
            if user_being_edited.email is None:
                # created from a user do not have emails so their profile pictures are name after their user id
                picture[0].filename = str(user_being_edited.id) + '.jpg'
            else:
                # make the pictures name the user's email because that is how photos are retrieved
                picture[0].filename = user_being_edited.email + '.jpg'
            destination = "/".join([target, picture[0].filename])
            picture[0].save(destination)
            user_being_edited.profile_picture = picture[0].filename
        # set all the user's values to the new values
        user_being_edited.first_name = first_name
        user_being_edited.middle_name = middle_name
        user_being_edited.last_name = last_name
        # if birthday == "" then no new date was selected to change birthday
        # so if birthday != "" then user selected a date to change birthday
        if birthday != "":
            user_being_edited.birthday = birthday
        user_being_edited.gender = gender
        user_being_edited.bio = bio
        db.session.commit()
        """ there is an issue when you update a user's info. It won't update in the friends list. For example, if a user
        updates their profiles name, gender and birthday, it will not show the updated info in the home pages of the
        user's friends. In this case here, when you update a created friend, it won't show the updated info in the 
        user's home page, so to fix it i remove the outdated list object and just re add it. This fixes this problem"""
        if user_being_edited != current_user:
            for friend in current_user.friends_list:
                if user_being_edited == friend:
                    # we have to save the index of the created friend, so we can insert it back to where it was in the
                    # list. This is trivial, and it can just be appended to the back of the list but since friends are
                    # displayed from oldest to newest, it might be helpful to just insert it back to were it is
                    # supposed to be in the list.
                    index = current_user.friends_list.index(friend)
                    current_user.friends_list.remove(friend)
                    current_user.friends_list.insert(index, user_being_edited)
                    break
        db.session.commit()
    return render_template('edit_profile.html', user=current_user, user_being_edited=user_being_edited)


# all users can create posts with images or without images. they also have the ability to tag any friend they want in
# the post, change the color of the post, and edit the post privacy of who can view the post.
@features.route('/create-post', methods=['GET', 'POST'])
@login_required
def create_post():
    # if request.method == 'POST' then create a post otherwise just render template
    if request.method == 'POST':
        # retrieve post details from form
        title = request.form.get('title')
        text = request.form.get('text')
        color = request.form.get('color')
        post_privacy = request.form.get('post_privacy')
        # list of tagged friends from user
        tag_friends_id = request.form.getlist('tagged_friends')
        # create post object to save details. excluding image
        # the images associated with the post are named after the post's id,
        # but id is created after being added to session
        tmp_post = Post(title=title, text=text, color=color, post_privacy=post_privacy, user_id=current_user.id)
        db.session.add(tmp_post)
        db.session.commit()
        # append tagged users to the post tagged list
        for friend_id in tag_friends_id:
            tmp_user = User.query.filter_by(id=friend_id).first()
            tmp_post.friends_tagged.append(tmp_user)
        db.session.commit()
        # save images from post
        for file in request.files.getlist('file'):
            if file.filename != "":
                # save to the image directory with the name of the file
                destination = "/".join([target, file.filename])
                file.save(destination)
                # append to the post's images by file name
                tmp_post.post_images.append(file.filename)
        db.session.commit()
        flash('Post created.', category="success")
        return redirect(url_for('features.user_home'))
    return render_template('create_post.html', user=current_user)


# users can delete any post they want
@features.route('/delete-post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    # get post by id and delete then refresh to home page
    post = Post.query.filter_by(id=post_id).first()
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', category="success")
    return redirect(url_for('features.user_home'))


# all posts can be edited and the changes will be saved. Any part of the post can be edited.
@features.route('/edit-post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    # get the post the user is trying to edit by id to display in edit post html
    post = Post.query.filter_by(id=post_id).first()
    if request.method == "POST":
        # get form details from user
        title = request.form.get('title')
        text = request.form.get('text')
        color = request.form.get('color')
        post_privacy = request.form.get('post_privacy')
        tag_friends_id = request.form.getlist('tagged_friends')
        # clear the list so that the friends tagged list of the post can be reassigned to the changes
        # if the user didn't make any changes then it is ok to clear and reassign because the previous tagged friends
        # options were preselected when they are brought to the edit page, so nothing will change. will just reassign
        # old values
        post.friends_tagged.clear()
        # append tagged users to the post tagged list
        for friend_id in tag_friends_id:
            tmp_user = User.query.filter_by(id=friend_id).first()
            post.friends_tagged.append(tmp_user)
        # save new images from post
        for file in request.files.getlist('file'):
            if file.filename != "":
                # save to the image directory with the name of the file
                destination = "/".join([target, file.filename])
                file.save(destination)
                # append to the post's images by file name
                post.post_images.append(file.filename)
        # save the new value to the post's variables
        post.title = title
        post.text = text
        post.post_privacy = post_privacy
        if color != '#000000':
            post.color = color
        db.session.commit()
    return render_template('edit_post.html', user=current_user, post=post)


# when editing a post, the user can remove any image they want one by one. There could be a multi delete feature in
# the future.
@features.route('/edit-post/remove-post-image/<int:post_id>', methods=['GET', 'POST'])
@login_required
def remove_post_image(post_id):
    # get post by id
    post = Post.query.filter_by(id=post_id).first()
    # then get the image name from the hidden p tag that contains the image's name
    # there is a for loop that makes a hidden p tag with the name of each image and depending on which delete button
    # get pressed, that p tag's info will get fetched from this function for deletion
    image_name = request.form.get('image_name')
    # there is an error when reloading the page after deleting an image, so this is here to make sure that the function
    # doesn't try to delete an image that has already been deleted
    if image_name not in post.post_images:
        flash('Image may have been wrongly deleted!!', category="error")
        return render_template('edit_post.html', user=current_user, post=post)
    post.post_images.remove(image_name)
    db.session.commit()
    return render_template('edit_post.html', user=current_user, post=post)


# this feature is for the user to create a fake account that is only accessible themselves in order to tag tht account
# in the user's posts. The user can use this feature to create accounts of anything such as their pet for example. Then
# the user can tag their dog/friend/any entity they want in posts and sort the posts later if they ever want to find
# it again.
@features.route('/create-friend', methods=['GET', 'POST'])
def create_friend():
    if request.method == "POST":
        first_name = request.form.get('first_name')
        middle_name = request.form.get('middle_name')
        last_name = request.form.get('last_name')
        gender = request.form.get('gender')
        birthday = request.form.get('birthday')
        tmp_user = db.session.query(User).order_by(User.id.desc()).first()
        """ Typically,the profile pictures of the users are named after their email because that value is set to unique
         and my function to retrieve photos from the images folder does it by name. Therefore, all the images have to 
         have a unique name, and each user object has the name of the image associated with it(profile picture) saved in
         its profile picture variable. The issue here is that friend objects do not have an email, so I decided to name 
         it after its object id, so that every image for the friend objects have profile pictures with unique names. 
         However, you can only get an id for a new object after adding it to the session and committing it, but it then 
         loses its state. As a result, I cannot change the profile_picture variable after committing because it won't 
         , but I can only do it after committing because the profile_picture var here are name after the object's id 
         which isn't created until after committing. As a solution, I just get the id of the last user object created 
         and add 1 to it because the new object ids just increment by 1. This fixes my issues. """
        # create the friend object to save user submitted info
        friend = User()
        friend.first_name = first_name
        friend.middle_name = middle_name
        friend.last_name = last_name
        friend.gender = gender
        friend.birthday = birthday
        # get the creation's profile picture
        tmp_file = request.files.getlist('file')
        if tmp_file[0].filename == '':
            friend.profile_picture = 'tmp_picture.jpg'
        else:
            friend.profile_picture = str(tmp_user.id + 1) + '.jpg'
        db.session.add(friend)
        # get current user by query filter to avoid technical errors
        tmp_current_user = User.query.filter_by(id=current_user.id).first()
        tmp_current_user.friends_list.append(friend)
        db.session.commit()
        if tmp_file[0].filename != '':
            # getting submitted image to store in image folder
            for file in request.files.getlist('file'):
                # the file name will be called after the friend object id
                filename = str(friend.id) + '.jpg'
                destination = "/".join([target, filename])
                file.save(destination)
        flash('Friend created.', category="success")
    return render_template('create_friend.html', user=current_user)


# the user can filter all their posts by the tagged friends, key word in the post's text, and by the post's privacy type
# When a keyword is used to filter, the filtered posts will bold that word everytime it shows up in its text(easier for
# the user to find the keyword in the text)
# You can now sort through friends posts too, but the user cannot edit friend's posts or filter through friend's private
# posts.
@features.route('/filter-posts/<int:user_id>', methods=['GET', 'POST'])
def filter_posts(user_id):
    filtered_posts = []
    filtered_users = []
    tmp_current_user = User.query.filter_by(id=user_id).first()
    if request.method == 'POST':
        # get the friends from user if user is filtering posts by friends
        filter_friends = request.form.getlist('filter_friends')
        # copy of filtered friends to check if there are posts were friends have not been tagged yet
        tmp_filtered_friends = filter_friends[:]
        # get posts status types to filter through all th posts
        post_status = request.form.getlist('post_status')
        # get keyword from user if user is filtering posts by keyword
        key_word = request.form.get('key_word')
        # a boolean to check if the key word was found
        # this is used in case if user is searching by friends and keyword. If posts were found, but no posts were found
        # with the keyword then an error message is posted alerting the user that no posts with the keyword were found
        was_key_word_found = False
        # loop through all of user's posts
        for post in tmp_current_user.posts:
            # loop through all of user's friends to check if they are in the tagged friend of the post
            for user in filter_friends:
                tmp_user = User.query.filter_by(id=user).first()
                # first case: check if user is in the post's tagged friends
                # second case: make sure you do not add a post more than once in the filtered posts list because then
                # it will display the post twice.
                if (tmp_user in post.friends_tagged) and (post not in filtered_posts):
                    # append post to the filtered list to pass to html and display
                    filtered_posts.append(post)
                    # make sure not to try to remove a user that has already been removed
                    if user in tmp_filtered_friends:
                        tmp_filtered_friends.remove(user)
                    if tmp_user not in filtered_users:
                        filtered_users.append(tmp_user)
            # first case: check if key word is in the text of the post
            # second case: make sure the keyword is not an empty string. this occurs when the user is trying to search
            # friends only. Else, many unwanted posts will get added to the filtered list and displayed
            # third case: make sure the post isn't added to the filtered list more than once, or it will be displayed
            # twice
            if (key_word in post.text) and (key_word != '') and (post not in filtered_posts):
                filtered_posts.append(post)
                # replace the keyword with itself surrounded by html b tag so that it can be bolded when the returned
                # to the html and easy for the user to spot in the post's text. We do not commit to session here because
                # do not want to save these changes. We only want the keywords bolded for the current search
                post.text = post.text.replace(key_word, '<b>' + key_word + '</b>')
                # set was_key_word_found to let the user know that there is at least one post with the keyword
                was_key_word_found = True
            if (post_status is not None) and (post not in filtered_posts):
                if post.post_privacy in post_status:
                    filtered_posts.append(post)
        # if the length of filtered posts is zero, then return an error message that no posts were found.
        if (len(filtered_posts) == 0) or (key_word != '') and (was_key_word_found is False):
            # first error is that no posts were found with the entered keyword
            message = 'No posts found with keyword: ' + key_word + '.'
            flash(message, category="error")
        # if tmp_filtered_friends does not zero, then that means there is a friend that has not been tagged in a post
        if len(tmp_filtered_friends) != 0:
            # second error is that no posts were found with the friends the user was trying to find
            message = 'No posts found with: '
            for user in tmp_filtered_friends:
                # get user by id, so that their name can be added to the error message
                tmp_user = User.query.filter_by(id=user).first()
                # checks which user we are on in the list to format the message string.
                if filter_friends.index(user) != len(filter_friends) - 1:
                    # this is for comma
                    message = message + tmp_user.first_name + ', '
                else:
                    # this is for the last user in the list to end with a period
                    message = message + tmp_user.first_name + '.'
            flash(message, category="error")
        # if post were found
        if len(filtered_posts) != 0:
            flash('Post(s) found.')
    return render_template('filter_posts.html', user=current_user, tmp_user=tmp_current_user,
                           filtered_posts=filtered_posts, filtered_users=filtered_users)
