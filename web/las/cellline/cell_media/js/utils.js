// Funzione per premere 'Invio'
function pressEnter(buttonId,ev){ 
	if ((ev.which && ev.which == 13) || (ev.keyCode && ev.keyCode == 13)){ 
		document.getElementById(buttonId).click(); 
		return false; 
	} else  {
		return true; 
	}
}

Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};
