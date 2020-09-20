//-----Modal
// Get the modal
var modal = document.getElementById("myModal");

// Get the button that opens the modal
var btn = document.getElementById("Btn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("close")[0];

var timer;

// When the user clicks the button, open the modal 
btn.onclick = function() {
  // Stop any previous timers
  clearTimeout(timer);

  open_modal();

  // Automatically Timeout
  timer = setTimeout(close_modal, 20 * 1000); // 20 seconds
}

function open_modal(){
  modal.style.display = "block";
}

function close_modal(){
  modal.style.display = "none";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  // modal.style.display = "none";
  close_modal();
}

// For the Flash Modal
var flash_modal = document.getElementById("FlashModal");
var flash_control = setTimeout(show_flash, 0);


function show_flash(){
  flash_modal.style.display = "block";

  // Automatically Timeout
  setTimeout(hide_flash, 10 * 1000); // 10 seconds
}

function hide_flash(){
  flash_modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
// For both the flash modal and the payment modal
window.onclick = function(event) {
  if (event.target == modal) {
    close_modal();
  }

  hide_flash();
}