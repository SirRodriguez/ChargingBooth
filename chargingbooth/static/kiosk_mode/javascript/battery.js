//-----Battery
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