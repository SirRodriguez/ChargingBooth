//-----Modal
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