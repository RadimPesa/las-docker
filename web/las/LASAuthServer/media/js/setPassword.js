$(document).ready(function () {
	//per distinguere le due pagine in cui viene chiamato questo js, quella per cambiare la password e quella per impostarla da zero
	var input=$("#id_new_password1");
	if (input.length==0){
		input=$("#id_password1");
	}

	$(input).strength();


	$("#conf_all").click(function(event){
		//valore del plugin strength (weak, strong, ecc...)
		var valore=$("div.strength_meter").text();
		if(valore!="strong"){
			alert("Password is not strong enough. Please change it.");
			event.preventDefault();
		}
	});


});
