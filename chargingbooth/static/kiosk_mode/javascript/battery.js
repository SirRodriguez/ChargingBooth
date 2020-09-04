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