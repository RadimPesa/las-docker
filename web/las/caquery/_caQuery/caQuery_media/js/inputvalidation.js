function validate(evt) {
    var theEvent = evt || window.event;
    var key = theEvent.keyCode || theEvent.which;
    if (key == 9) { // don't prevent tab from causing to move to next field
        ;
    } else {
        key = String.fromCharCode( key );
        var regex = /[0-9\b]|\.|\,/;
        if( !regex.test(key) ) {
    	   theEvent.returnValue = false;
    	   if(theEvent.preventDefault) theEvent.preventDefault();
        }
    }
}

function validate2(evt) {
    var theEvent = evt || window.event;
    var key = theEvent.keyCode || theEvent.which;
    if (key == 9) { // don't prevent tab from causing to move to next field
        ;
    } else if (key == 13) {
        ;
    } else {
        key = String.fromCharCode( key );
        var regex = /[a-zA-Z0-9\b]|\.|\,|\:|\_|\s|\;|\-/;
        if( !regex.test(key) ) {
            theEvent.returnValue = false;
            if(theEvent.preventDefault) theEvent.preventDefault();
        }
    }
}


function validate3(evt) {
    var theEvent = evt || window.event;
    var key = theEvent.keyCode || theEvent.which;
    if (key != 9) { // don't prevent tab from causing to move to next field
        key = String.fromCharCode( key );
        var regex = /[a-zA-Z0-9\b]/;
        if( !regex.test(key) ) {
            theEvent.returnValue = false;
            if(theEvent.preventDefault) theEvent.preventDefault();
        }
    }
}

function validateText(evt, f_idButton) {
    var theEvent = evt || window.event;
    var key = theEvent.keyCode || theEvent.which;
    if (key == 9) { // don't prevent tab from causing to move to next field
        ;
    } else if (key == 13) {
        $("#add_btn" + f_idButton).click();
    } else {
        key = String.fromCharCode( key );
        var regex = /[a-zA-Z0-9\b]|\.|\,|\:|\_|\s|\;|\-/;
        if( !regex.test(key) ) {
            theEvent.returnValue = false;
            if(theEvent.preventDefault) theEvent.preventDefault();
        }
    }
}




$('input,select').keypress(function(event) { return event.keyCode != 13; }); //disable enter key
	
