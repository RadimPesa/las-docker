function acceptModules(username,url) { 
	//alert(requestId);
	var checkboxesModules =document.getElementsByName("modules_"+username);
	var modules ="";
	for (var i=0;i<checkboxesModules.length;i++){
		if (checkboxesModules[i].checked){
			if (modules=="")
				modules=checkboxesModules[i].value;
			else{
				modules=modules+","+checkboxesModules[i].value;
			}
		}
	}

	var request = $.ajax({
		url: url,
		type: "POST",
		async: false,
		data: {modules: modules, username:username},
   	});
	    			
	request.done(function(msg) {
		
		if (msg["message"]=='403'){
			alert("FORBIDDEN");
        	window.location.href ="/forbidden";
        	return
		}
		if (msg["message"]=='ok'){
			alert("Modules Updated!");			
		return;
		}
		if(msg["message"]=='error'){
			alert(msg["error_string"]);
			return;
		}		
	});
}


