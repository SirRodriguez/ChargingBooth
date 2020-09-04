// --- Variables

var slideIndex = 0;
var timeout_seconds = 20;
var slides = setTimeout(nextSlide, 0);

// --- Functions

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