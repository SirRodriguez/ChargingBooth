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

function make_time_string(hour, minute, second){
  return ( hour > 9 ? hour.toString() : "0" + hour.toString() ) + ":"
          + ( minute > 9 ? minute.toString() : "0" + minute.toString() ) + ":"
          + ( second > 9 ? second.toString() : "0" + second.toString() );
}

function count_sessions(){
  var session_time_remains = document.getElementsByClassName("time_remaining");

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