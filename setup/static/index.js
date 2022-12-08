let slideIndex = 1;

function currentSlide(n, post_id) {
    showSlides(slideIndex = n, post_id);
}

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

function loadSlides(lst) {
    for (i=0; i < lst.length; i++){
        showSlides(1, lst[i])
    }
}

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


$("#filter_friends").keyup(function() {
      // Retrieve the input field text and reset the count to zero
      var filter = $(this).val(),
        count = 0;
      // Loop through the comment list
      /*$('#user_friends .filter_users').each(function() {*/
      $('#user_friends .filter_users').each(function() {
        // If the list item does not contain the text phrase fade it out
        if ($(this).text().search(new RegExp(filter, "i")) < 0) {
          $(this).hide();  // MY CHANGE
          // Show the list item if the phrase matches and increase the count by 1
        } else {
          $(this).show(); // MY CHANGE
          count++;
        }
      });
    });


function lengthCheck(text, id) {
    if (text.length < 2) {
        document.getElementById(id).style.backgroundColor="#fce7e6";
    } else {
        document.getElementById(id).style.backgroundColor="#d5f7dd";
    }
    var tmp = '!@#$%^&*()<>"';
    for (let c = 0; c < tmp.length; c++){
        if (text.indexOf(tmp[c]) > -1) {
            document.getElementById(id).style.backgroundColor="#fce7e6";
        }
    }
}
/* make usernames not be case sensitive */
function usernameCheck(text, id, list_of_usernames) {
    if (text.length < 2) {
        document.getElementById(id).style.backgroundColor="#fce7e6";
    } else {
        document.getElementById(id).style.backgroundColor="#d5f7dd";
    }
    if (list_of_usernames.indexOf(text) > -1) {
            document.getElementById(id).style.backgroundColor="#fce7e6";
        }
    var tmp = '!@#$%^&*()<>"';
    for (let c = 0; c < tmp.length; c++){
        if (text.indexOf(tmp[c]) > -1) {
            document.getElementById(id).style.backgroundColor="#fce7e6";
        }
    }
}

