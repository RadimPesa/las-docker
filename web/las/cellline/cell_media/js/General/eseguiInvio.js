// Funzione per premere 'Invio'
function eseguiInvio(IdPulsante,ev){ 
	if ((ev.which && ev.which == 13) || (ev.keyCode && ev.keyCode == 13)){ 
		document.getElementById(IdPulsante).click(); 
		return false; 
	} else  {
		return true; 
	}
}
