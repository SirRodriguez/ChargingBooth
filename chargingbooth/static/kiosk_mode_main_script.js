// --- Variables

// Slideshow
var slideIndex = 0;
var timeout_seconds = 20;
var slides = setTimeout(nextSlide, 0);

// Session Counter
var sessions = setTimeout(count_sessions, 0);


// --- Functions

// Slideshow
function plusSlides(n) {
  showSlides(slideIndex += n, false);
}

function currentSlide(n) {
  showSlides(slideIndex = n, false);
}

function nextSlide(){
  showSlides(slideIndex += 1, true);
}

function showSlides(n, timeout) {
  var i;
  var slides = document.getElementsByClassName("mySlides");
  var dots = document.getElementsByClassName("dot");
  if (n > slides.length) {
    slideIndex = 1
  }    
  if (n < 1) {
    slideIndex = slides.length
  }
  for (i = 0; i < slides.length; i++) {
      slides[i].style.display = "none";  
  }
  for (i = 0; i < dots.length; i++) {
      dots[i].className = dots[i].className.replace(" active", "");
  }
  slides[slideIndex-1].style.display = "block";  
  dots[slideIndex-1].className += " active";

  if(timeout == true){
    setTimeout(nextSlide, timeout_seconds * 1000);
  }
}

// Sessions

// Returns True if there are sessions running, false othersiwse
// Only works when there is only one session allowed at a time!
function sessions_active(){
  var session_time_remains = document.getElementsByClassName("time_remaining");


  if( session_time_remains.length > 0 ){
    // Check if the sessions on screen have completed
    if( session_time_remains[0].innerHTML == "<mark><b>Session Completed!</b></mark>" ){
      return false;

    // If they are not completed
    }else{
      return true;
    }

  }else{
    return false;
  }
}

function make_time_string(hour, minute, second){
  return ( hour > 9 ? hour.toString() : "0" + hour.toString() ) + ":"
          + ( minute > 9 ? minute.toString() : "0" + minute.toString() ) + ":"
          + ( second > 9 ? second.toString() : "0" + second.toString() );
}

function count_sessions(){
  var session_time_remains = document.getElementsByClassName("time_remaining");

  // -- This is to only allow one session at a time.
  // Check here if there are any sessions available
  // If there is, then block click to start session
  // Else, Make it visable and allow the user to start a session
  var start_sess_btn = document.getElementById("Btn");
  var sess_in_prog = document.getElementById("progBtn");

  if(sessions_active()){
    // Block the Click To Start a Session
    start_sess_btn.style.display = "none";
    sess_in_prog.style.display = "block";
  }else{
    // Show the Click To Start A Session
    start_sess_btn.style.display = "block";
    sess_in_prog.style.display = "none";
  }

  var i;
  for(i = 0; i < session_time_remains.length; i++){
    // subtract seconds from it at a time
    var time_string = session_time_remains[i].innerHTML;
    var time = time_string.split(":");
    var hour = parseInt(time[0]);
    var min = parseInt(time[1]);
    var sec = parseInt(time[2]);

    if(sec > 0){
      sec -= 1;

      session_time_remains[i].innerHTML = make_time_string(hour, min, sec);

    }else if(min > 0){
      min -= 1;
      sec = 59;

      session_time_remains[i].innerHTML = make_time_string(hour, min, sec);

    }else if(hour > 0){
      hour -= 1;
      min = 59;
      sec = 59;

      session_time_remains[i].innerHTML = make_time_string(hour, min, sec);

    }else{
      
      session_time_remains[i].innerHTML = "<mark><b>Session Completed!</b></mark>"
    }

  }


  setTimeout(count_sessions, 1000);

}


// For the Flash Info
  var flash_fade = setTimeout(flash_fade_out, 5000);

  function flash_fade_out(){

    $(document).ready(function(){
      $("flash").ready(function(){
        $("main").fadeOut(5000, "swing");
      });
    });
  }

  // For the Modal

  // Get the modal
  var modal = document.getElementById("myModal");

  // Get the button that opens the modal
  var btn = document.getElementById("Btn");

  // Get the <span> element that closes the modal
  var span = document.getElementsByClassName("close")[0];

  // When the user clicks the button, open the modal 
  btn.onclick = function() {
    modal.style.display = "block";
  }

  // When the user clicks on <span> (x), close the modal
  span.onclick = function() {
    modal.style.display = "none";
  }

  // When the user clicks anywhere outside of the modal, close it
  window.onclick = function(event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  }


  // Confirm button inside modal
  var conf = document.getElementById("confim")

  // When the button is Pressed
  conf.onclick = function(){
    // Make a session and start payment
    modal.style.display = "none"

  }


  // For the Flash Modal
  var flash_modal = document.getElementById("FlashModal");
  var flash_control = setTimeout(show_flash, 0);


  function show_flash(){
    flash_modal.style.display = "block";

    // Automatically Timeout
    setTimeout(hide_flash, 10000); // 5 seconds
  }

  function hide_flash(){
    flash_modal.style.display = "none";
  }

  // When the user clicks anywhere outside of the modal, close it
  window.onclick = function(event) {
    hide_flash();
  }


function chargebattery() {
  // Check to see if the session is still active
  // Otherwise, Pause the battery motion

  if(sessions_active()){
    var a;
    a = document.getElementById("battery");
    a.innerHTML = "&#xf244;";

    setTimeout(function () {
        a.innerHTML = "&#xf243;";
      }, 1000);

    setTimeout(function () {
        a.innerHTML = "&#xf242;";
      }, 2000);

    setTimeout(function () {
        a.innerHTML = "&#xf241;";
      }, 3000);

    setTimeout(function () {
        a.innerHTML = "&#xf240;";
      }, 4000);
  }

  setTimeout(chargebattery, 5000);
}

chargebattery();