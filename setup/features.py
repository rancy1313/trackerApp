from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, send_from_directory
from flask_login import login_required, current_user
from .models import User, Friend, Friend_request, Post
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

@features.route('/user-home', methods=['GET', 'POST'])
@login_required
def user_home():
    #friend_request_for_current_user = Friend_request.query.filter_by(request_to_user_id=current_user.id).all()
    """ this loop is used to update friend info when ever the user goes to their homepage. Since the friend objects
    are stored in a list, they don't get updated if there are changes made outside the loop. For example, if one of the
    user's friends updates their profile, then that change will not be updated om the friend object inside
    the current user's friends list. So this loop goes through the current user's friends list and reasigns each friend
    in there with the updated info by id. """
    all_requests = db.session.query(Friend_request).order_by(Friend_request.id.desc()).all()
    list_of_user_friends = []
    for index, friend in enumerate(current_user.friends_list):
        tmp_user = User.query.filter_by(id=friend.id).first()
        current_user.friends_list[index] = tmp_user
        list_of_user_friends.append(tmp_user)
    db.session.commit()

    print("check: ", list_of_user_friends)
    return render_template("home.html", user=current_user, all_requests=all_requests, list_of_user_friends=list_of_user_friends)


"""@features.route('/search-friend', methods=['GET', 'POST'])
@login_required
def search_friend():
    # search is done by email because all emails are unique
    # could replace search by email with a username variable or by first name
    # retrieve email from form
    email = request.form.get('email')
    # search db for user with that email
    friend = User.query.filter_by(email=email).first()
    # fixes bug were wrong friend is displaying. It is just getting a random friend so set friend
    # to None if email is none
    if email is None:
        friend = None
    if request.method == "POST":
        # stop people from adding themselves
        if current_user.email == email:
            flash('Not allowed to search yourself', category="error")
            # set friend to None so None type is passed to search friend page
            friend = None
        elif friend:
            flash('Friend found', category="success")
        else:
            flash('Error. Friend not found', category="error")
    return render_template("search_friend.html", user=current_user, friend=friend)"""


@features.route('/search-friends', methods=['GET', 'POST'])
@login_required
def search_friends():
    # search is done by email because all emails are unique
    # could replace search by email with a username variable or by first name
    # retrieve email from form
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


@features.route('/search-friend/send-friend-request/<int:user_id>', methods=['GET', 'POST'])
@login_required
def send_friend_request(user_id):
    # find friend by User id
    friend = User.query.filter_by(id=user_id).first()
    # check if already friends by looping through current user's friends and comparing friend ids
    for tmp_friend in current_user.friends:
        if tmp_friend.friend_id == friend.id:
            flash('Error. Already friends.', category="error")
            return redirect(url_for('features.search_friends'))

    # only one friend request to a person can be made until.
    # The person has to wait until the last request was cancelled
    for tmp_request in current_user.friend_requests:
        if tmp_request.request_to_user_id == user_id:
            flash('Error. There is already a pending friend request to this person.', category="error")
            return redirect(url_for('features.search_friends'))

    if request.method == 'POST':
        # save the profile picture of the receiver so that the sender can see who they see the request to
        filename_receiver = friend.profile_picture
        # save the profile picture of the sender so the receiver can see who sent the request
        filename_sender = current_user.profile_picture
        # if not already friends then send request
        tmp_receiver_name = friend.first_name + " " + friend.middle_name + " " + friend.last_name
        tmp_sender_name = current_user.first_name + " " + current_user.middle_name + " " + current_user.last_name
        tmp_request = Friend_request(status="PENDING", receiver_name=tmp_receiver_name, sender_name=tmp_sender_name,
                                     request_to_user_id=user_id, request_from_user_id=current_user.id,
                                     receiver_profile_picture=filename_receiver, sender_profile_picture=filename_sender)
        db.session.add(tmp_request)
        db.session.commit()
        flash('Request Sent.', category="success")
        return redirect(url_for('features.search_friends'))

@features.route('/user-home/accept-friend-request/<int:request_id>', methods=['GET', 'POST'])
@login_required
def accept_friend_request(request_id):
    # search friend request by id to delete
    tmp_request = Friend_request.query.filter_by(id=request_id).first()
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
        """# first we have to add the sender of the request to the current user's friend list
        tmp_friend = Friend()
        tmp_friend.account_status = 'True'
        tmp_friend.friend_id = tmp_request.request_from_user_id
        tmp_friend.user_id = current_user.id
        tmp_friend.first_name = tmp_user.first_name
        tmp_friend.middle_name = tmp_user.middle_name
        tmp_friend.last_name = tmp_user.last_name
        tmp_friend.birthday = tmp_user.birthday
        tmp_friend.gender = tmp_user.gender
        tmp_friend.profile_picture = tmp_user.profile_picture
        db.session.add(tmp_friend)
        db.session.commit()
        # now we have to add the current user to the friend list of the sender
        tmp_friend = Friend()
        tmp_friend.account_status = 'True'
        tmp_friend.friend_id = current_user.id
        tmp_friend.user_id = tmp_request.request_from_user_id
        tmp_friend.first_name = current_user.first_name
        tmp_friend.middle_name = current_user.middle_name
        tmp_friend.last_name = current_user.last_name
        tmp_friend.birthday = current_user.birthday
        tmp_friend.gender = current_user.gender
        tmp_friend.profile_picture = current_user.profile_picture
        db.session.add(tmp_friend)
        db.session.commit()"""
        # now we have to delete the friend request because it was accepted
        db.session.delete(tmp_request)
        db.session.commit()
        flash('Friend added', category="success")
        return redirect(url_for('features.user_home'))
    else:
        flash('Error.', category="error")
        return redirect(url_for('features.user_home'))

"""@features.route('/search-friend/add-friend/<int:user_id>', methods=['GET', 'POST'])
@login_required
def add_friend(user_id):
    # find friend by id
    friend = User.query.filter_by(id=user_id).first()
    xxx = db.session.query(User).order_by(User.id.desc()).all()
    for tmpx in xxx:
        print("Testing ids: ", tmpx.id)
    for tmp in current_user.friends:
        print(tmp.friend_id, friend.id)
    # check if already friends by looping through current user's friends and comparing friend ids
    for tmp_friend in current_user.friends:
        if tmp_friend.friend_id == friend.id:
            flash('Error. Already friends.', category="error")
            return redirect(url_for('features.search_friend'))
    if request.method == 'POST':
        # if not already friends then add friend and
        tmp_friend = Friend()
        tmp_friend.account_status = 'True'
        tmp_friend.friend_id = user_id
        tmp_friend.user_id = current_user.id
        tmp_friend.first_name = friend.first_name
        tmp_friend.middle_name = friend.middle_name
        tmp_friend.last_name = friend.last_name
        tmp_friend.birthday = friend.birthday
        tmp_friend.gender = friend.gender
        tmp_friend.profile_picture = friend.email + '.jpg'
        db.session.add(tmp_friend)
        db.session.commit()
        flash('Friend added', category="success")
        return redirect(url_for('features.search_friend'))"""


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
        #return redirect(url_for('features.view_friend_profile'), friend_id=friend_id)
    elif friend.username is None:
        current_user.friends_list.remove(friend)
        db.session.delete(friend)
        db.session.commit()
        flash('Friend Creation deleted.', category="success")
        return redirect(url_for('features.user_home'))
    else:
        flash('Error.', category="error")
        return redirect(url_for('features.user_home'))
        #return redirect(url_for('features.view_friend_profile'), friend_id=friend_id)
    """# there are two friend links because when someone accepts a friend request, they both need to be added to each
    # other's friends list. Thus, that requires two links to do, so we have to delete both links
    friend_link1 = Friend.query.filter_by(friend_id=friend_id).first()
    friend_link2 = Friend.query.filter_by(friend_id=current_user.id).filter_by(user_id=friend_link1.friend_id).first()
    # if friend exist then delete and redirect to home
    if friend_link1 and friend_link1:
        db.session.delete(friend_link1)
        db.session.commit()
        db.session.delete(friend_link2)
        db.session.commit()
        flash('Friend removed', category="success")
        return redirect(url_for('features.user_home'))
    else:
        flash('Error.', category="error")
        return redirect(url_for('features.user_home'))"""


"""@features.route('/user-home/remove-friend/<int:friend_id>', methods=['GET', 'POST'])
@login_required
def remove_friend(friend_id):
    # there are two friend links because when someone accepts a friend request, they both need to be added to each
    # other's friends list. Thus, that requires two links to do, so we have to delete both links
    friend_link1 = Friend.query.filter_by(id=friend_id).first()
    friend_link2 = Friend.query.filter_by(friend_id=current_user.id).filter_by(user_id=friend_link1.friend_id).first()
    print("hey test1", friend_link1)
    print("hey test2", friend_link2)
    # if friend exist then delete and redirect to home
    if friend_link1 and friend_link1:
        db.session.delete(friend_link1)
        db.session.commit()
        db.session.delete(friend_link2)
        db.session.commit()
        flash('Friend removed', category="success")
        return redirect(url_for('features.user_home'))
    else:
        flash('Error.', category="error")
        return redirect(url_for('features.user_home'))"""


@features.route('/user-home/cancel-friend-request/<int:request_id>', methods=['GET', 'POST'])
@login_required
def cancel_friend_request(request_id):
    # search friend request by id to delete
    tmp_request = Friend_request.query.filter_by(id=request_id).first()
    # if request exist then delete and redirect to home
    if tmp_request:
        db.session.delete(tmp_request)
        db.session.commit()
        flash('Request cancelled', category="success")
        return redirect(url_for('features.user_home'))
    else:
        flash('Error.', category="error")
        return redirect(url_for('features.user_home'))


@features.route('/user-home/view-friend-profile/<int:friend_id>', methods=['GET', 'POST'])
@login_required
def view_friend_profile(friend_id):
    # search friend by id to view profile
    """friend = Friend.query.filter_by(id=friend_id).first()
    friend = User.query.filter_by(id=friend.friend_id).first()"""
    friend = User.query.filter_by(id=friend_id).first()
    return render_template('friend_page.html', friend=friend, user=current_user)


@features.route('/view-friend-profile/add_friend_from_friend/<int:user_id>/<int:curr_page_user_id>',
                methods=['GET', 'POST'])
@login_required
def add_friend_from_friend(user_id, curr_page_user_id):
    # search friend by id to delete
    #friend = Friend.query.filter_by(id=friend_id).first()
    """# check if the friend and the current user are the same person
    if friend.friend_id == current_user.id:
        flash('Can\'t add yourself', category="error")
        # get the id of the current friend's page you're on to reload page
        friend = User.query.filter_by(id=curr_page_user_id).first()
        return render_template('friend_page.html', friend=friend, user=current_user)"""

    """# check through current users and compare friend_id to see if user is already friends
    for tmp_friend in current_user.friends:
        if tmp_friend.friend_id == friend.friend_id:
            flash('Error. Already friends.', category="error")
            # get the id of the current friend's page you're on to reload page
            friend = User.query.filter_by(id=curr_page_user_id).first()
            return render_template('friend_page.html', friend=friend, user=current_user)"""

    if request.method == 'POST':
        # else add friend
        """tmp_friend = Friend()
        tmp_friend.account_status = 'True'
        tmp_friend.friend_id = friend.friend_id
        tmp_friend.user_id = current_user.id
        tmp_friend.first_name = friend.first_name
        tmp_friend.middle_name = friend.middle_name
        tmp_friend.last_name = friend.last_name
        tmp_friend.birthday = friend.birthday
        tmp_friend.gender = friend.gender
        db.session.add(tmp_friend)
        db.session.commit()"""
        # only one friend request to a person can be made until.
        # The person has to wait until the last request was cancelled
        for tmp_request in current_user.friend_requests:
            if tmp_request.request_to_user_id == user_id:
                flash('Error. There is already a pending friend request to this person.', category="error")
                return redirect(url_for('features.view_friend_profile', friend_id=curr_page_user_id))

        if request.method == 'POST':
            tmp_user = User.query.filter_by(id=user_id).first()
            filename_receiver = tmp_user.email + '.jpg'
            filename_sender = current_user.email + '.jpg'
            # if not already friends then send request
            tmp_receiver_name = tmp_user.first_name + " " + tmp_user.middle_name + " " + tmp_user.last_name
            tmp_sender_name = current_user.first_name + " " + current_user.middle_name + " " + current_user.last_name
            tmp_request = Friend_request(status="PENDING", receiver_name=tmp_receiver_name, sender_name=tmp_sender_name,
                                         request_to_user_id=user_id, request_from_user_id=current_user.id,
                                         receiver_profile_picture=filename_receiver,
                                         sender_profile_picture=filename_sender)
            db.session.add(tmp_request)
            db.session.commit()
        flash('Friend request sent test', category="success")
        return redirect(url_for('features.view_friend_profile', friend_id=curr_page_user_id))
    # print(friend.first_name)
    # return render_template("home.html", user=current_user)

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
        picture = request.files.getlist('file')
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
        user_being_edited.first_name = first_name
        user_being_edited.middle_name = middle_name
        user_being_edited.last_name = last_name
        # if birthday == "" then no new date was selected to change birthday
        # so if birthday != "" then user selected a date to change birthday
        if birthday != "":
            user_being_edited.birthday = birthday
        user_being_edited.gender = gender
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
        """# create an empty list to collect ids from the tagged friends
        ids = []
        for friend_id in tag_friend_id:
            # each element is a string. The names and id are separated by a space, so split by space and return a list
            # of friend_id = [first_name, middle_name, last_name, friend_id]
            # then append to the ids list the last element which is the friend_id
            friend_id = friend_id.split(' ')
            ids.append(friend_id[-1])"""
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


@features.route('/delete-post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    # get post by id and delete then refresh to home page
    post = Post.query.filter_by(id=post_id).first()
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', category="success")
    return redirect(url_for('features.user_home'))

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
        post.title = title
        post.text = text
        post.post_privacy = post_privacy
        if color != '#000000':
            post.color = color
        db.session.commit()
    return render_template('edit_post.html', user=current_user, post=post)

@features.route('/edit-post/remove-post-image/<int:post_id>', methods=['GET', 'POST'])
@login_required
def remove_post_image(post_id):
    post = Post.query.filter_by(id=post_id).first()
    image_name = request.form.get('image_name')
    if image_name not in post.post_images:
        flash('Image may have been wrongly deleted!!', category="error")
        return render_template('edit_post.html', user=current_user, post=post)
    post.post_images.remove(image_name)
    db.session.commit()
    return render_template('edit_post.html', user=current_user, post=post)


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
        print("last user id: ", tmp_user.id)
        # create the friend object to save user submitted info
        friend = User()
        friend.first_name = first_name
        friend.middle_name = middle_name
        friend.last_name = last_name
        friend.gender = gender
        friend.birthday = birthday
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

@features.route('/filter-posts', methods=['GET', 'POST'])
def filter_posts():
    filtered_posts = []
    filtered_users = []
    if request.method == 'POST':
        # get the friends from user if user is filtering posts by friends
        filter_friends = request.form.getlist('filter_friends')
        # copy of filtered friends to check if there are posts were friends have not been tagged yet
        tmp_filtered_friends = filter_friends[:]
        # get keyword from user if user is filtering posts by keyword
        key_word = request.form.get('key_word')
        # a boolean to check if the key word was found
        # this is used in case if user is searching by friends and keyword. If posts were found, but no posts were found
        # with the keyword then an error message is posted alerting the user that no posts with the keyword were found
        was_key_word_found = False
        # loop through all of user's posts
        for post in current_user.posts:
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
    return render_template('filter_posts.html', user=current_user, filtered_posts=filtered_posts, filtered_users=filtered_users)

