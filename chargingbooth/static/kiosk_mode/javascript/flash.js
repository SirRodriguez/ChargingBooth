// --- Variables

var flash_fade = setTimeout(flash_fade_out, 5000);

// --- Functions

function flash_fade_out(){

$(document).ready(function(){
	$("flash").ready(function(){
		$("main").fadeOut(5000, "swing");
		});
	});
}