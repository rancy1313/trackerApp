let slideIndex = 1;
// used for the dots next to the image. Depending on which one is clicked will determine the current slide
function currentSlide(n, post_id) {
    // calls show slides with post id and the index
    showSlides(slideIndex = n, post_id);
}
// takes a post id and index
function showSlides(n, post_id) {
    let i;
    let slides = document.getElementsByClassName("post_images" + post_id);
    let dots = document.getElementsByClassName("dot " + post_id);
    if (n > slides.length) {slideIndex = 1}
    if (n < 1) {slideIndex = slides.length}
    for (i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }
    for (i = 0; i < dots.length; i++) {
        dots[i].className = dots[i].className.replace(" active", "");
    }
    slides[slideIndex-1].style.display = "block";
    dots[slideIndex-1].className += " active";
}
// used to load all posts' images. Takes a list of ids and sets their slide index all to one after the page is done
// being loaded. If all the posts' images index are not set to 1, then they do not display properly.
function loadSlides(lst) {
    for (i=0; i < lst.length; i++){
        showSlides(1, lst[i])
    }
}
// js for collapsible sections on the user home pages
var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", function() {
        this.classList.toggle("active");
        var content = this.nextElementSibling;
        if (content.style.display === "block") {
            content.style.display = "none";
        } else {
            content.style.display = "block";
        }
  });
}
// takes a section by id filter friends and then loops through the tags with class filter users and uses a search
// function to see if text is in the tags. If text is found in the tag then the section is shown, else it is hidden.
// this is used to filter through friends.
$("#filter_friends").keyup(function() {
    // Retrieve the searched friend name and set count to 0
    var filter = $(this).val(),
    count = 0;
    // loop through the tags
    $('#user_friends .filter_users').each(function() {
        // tags that do not have the text need to be hidden
        if ($(this).text().search(new RegExp(filter, "i")) < 0) {
            $(this).hide();
            // show what matches and increase count by 1
        } else {
            $(this).show();
            count++;
        }
    });
});

// some js to check the length of an input field to amke sure the input text is long enough
function lengthCheck(text, id) {
    // create tags for the warnings id_tag
    var tag = id + '_tag';
    // if text less than 2 then turn background red
    if (text.length < 2 && id != 'middle_name') {
        document.getElementById(id).style.backgroundColor="#fce7e6";
    } else if (text.length < 1 && id == 'middle_name') {
        // middle names not required, so field turns white if input field empty
        document.getElementById(id).style.backgroundColor="white";
        document.getElementById(tag).style.display = "none";
    } else {
        // else turn background green
        document.getElementById(id).style.backgroundColor="#d5f7dd";
        document.getElementById(tag).style.display = "none";
    }
    // if not allowed chars are in the input text then turn the background red
    var tmp = '!@#$%^&*()<>"';
    for (let c = 0; c < tmp.length; c++){
        if (text.indexOf(tmp[c]) > -1) {
            document.getElementById(id).style.backgroundColor="#fce7e6";
            // format for warning
            document.getElementById(tag).style.display = "block";
            document.getElementById(tag).innerHTML = 'Char not allowed: ' + tmp[c];
            document.getElementById(tag).style.backgroundColor="#fce7e6";
            document.getElementById(tag).style.padding="20px";
            document.getElementById(tag).style.border="ridge";
        }
    }
}
/* checks usernames to see if they are already taken and if so then the background turns red.(usernames are case
   sensitive, so ranch13 and RANCH13 are usernames that can be taken at the same time. Don't know if that is good
   or not, so I am gonna just leave a note about it) */
function usernameCheck(text, id, list_of_usernames) {
    // if less than 2 red
    if (text.length < 2) {
        document.getElementById(id).style.backgroundColor="#fce7e6";
    } else {
        // else green
        document.getElementById(id).style.backgroundColor="#d5f7dd";
    }
    // if username is in the list_of_usernames then red because username is taken already
    if (list_of_usernames.indexOf(text) > -1) {
            document.getElementById(id).style.backgroundColor="#fce7e6";
            // format for warning
            document.getElementById('warning').style.display = "block";
            document.getElementById('warning').innerHTML = 'USERNAME TAKEN ALREADY.';
            document.getElementById('warning').style.backgroundColor="#fce7e6";
            document.getElementById('warning').style.padding="20px";
            document.getElementById('warning').style.border="ridge";
        } else {
            document.getElementById('warning').style.display = "none";
        }
    // tmp is string of banned chars
    var tmp = '!@#$%^&*()<>"';
    // loop checks if banned chars are in text
    for (let c = 0; c < tmp.length; c++){
        if (text.indexOf(tmp[c]) > -1) {
            document.getElementById(id).style.backgroundColor="#fce7e6";
            // format for warning
            document.getElementById('warning').style.display = "block";
            document.getElementById('warning').innerHTML = 'Char not allowed: ' + tmp[c];
            document.getElementById('warning').style.backgroundColor="#fce7e6";
            document.getElementById('warning').style.padding="20px";
            document.getElementById('warning').style.border="ridge";
        }
    }
}
// js functions for formatting the password fields
function password_check(password1, password2, id) {
    // red for both fields if passwords do not match each other
    if (password1 != password2) {
        document.getElementById('password1').style.backgroundColor="#fce7e6";
        document.getElementById('password2').style.backgroundColor="#fce7e6";
        // format for warning passwords not matching
        document.getElementById('password_warning').style.display = "block";
        document.getElementById('password_warning').innerHTML = 'Passwords do not match.';
        document.getElementById('password_warning').style.backgroundColor="#fce7e6";
        document.getElementById('password_warning').style.padding="20px";
        document.getElementById('password_warning').style.border="ridge";
    } else if ((password1 == password2) && (password1 != '' && password2 != '')) {
        // if passwords match each other then green. However, if both passwords are empty strings then they match but
        // do not meet requirements
        document.getElementById('password1').style.backgroundColor="#d5f7dd";
        document.getElementById('password2').style.backgroundColor="#d5f7dd";
        // hide warning
        document.getElementById('password_warning').style.display = "none";
    } else if (password1 == '' && password2 == ''){
        // if both passwords are empty strings then make fields red because they do not pass requirements
        document.getElementById('password1').style.backgroundColor="#fce7e6";
        document.getElementById('password2').style.backgroundColor="#fce7e6";
        // warning letting user know password fields are empty
        document.getElementById('password_warning').innerHTML = 'Password field empty.';
    }
    if (password1.length < 7 && password2.length < 7) {
        // if both passwords' length are less than 7, then field is red because requirements not met
        document.getElementById('password1').style.backgroundColor="#fce7e6";
        document.getElementById('password2').style.backgroundColor="#fce7e6";
        document.getElementById('password_warning').style.display = "block";
        document.getElementById('password_warning').innerHTML = 'Passwords are too short.';
        document.getElementById('password_warning').style.backgroundColor="#fce7e6";
        document.getElementById('password_warning').style.padding="20px";
        document.getElementById('password_warning').style.border="ridge";
    }
}