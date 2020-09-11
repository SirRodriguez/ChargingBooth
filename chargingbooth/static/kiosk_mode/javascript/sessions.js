//-----Sessions
var sessions = setTimeout(count_sessions, 1000);


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