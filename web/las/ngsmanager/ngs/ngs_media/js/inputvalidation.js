function validate(evt) {
  var theEvent = evt || window.event;
  var key = theEvent.keyCode || theEvent.which;
  key = String.fromCharCode( key );
  var regex = /[0-9\b]|\./;
  if( !regex.test(key) ) {
	theEvent.returnValue = false;
	if(theEvent.preventDefault) theEvent.preventDefault();
  }
}

function validate2(evt) {
  var theEvent = evt || window.event;
  var key = theEvent.keyCode || theEvent.which;
  //sono le frecce a destra e a sinistra
  if((key==39)||(key==37)){
	  return;
  }
  key = String.fromCharCode( key ); 
  var regex = /[a-zA-Z0-9\b]|\(|\)|\_|\s|\-|\+|\.|\#|\,/;
  if( !regex.test(key) ) {
	theEvent.returnValue = false;
	if(theEvent.preventDefault) theEvent.preventDefault();
	alert("Unsupported character");
  }
}

function validate3(evt) {
  var theEvent = evt || window.event;
  var key = theEvent.keyCode || theEvent.which;
  key = String.fromCharCode( key );
  var regex = /[a-zA-Z0-9\b]/;
  if( !regex.test(key) ) {
	theEvent.returnValue = false;
	if(theEvent.preventDefault) theEvent.preventDefault();
  }
}

$('input,select').keypress(function(event) { return event.keyCode != 13; }); //disable enter key
	