function acceptRegistration(profileId,url) { 
	var checkboxesModules =document.getElementsByName("modules_"+profileId);
	var action = "accept";
	var profile =profileId;
	var modules ="";
	for (var i=0;i<checkboxesModules.length;i++){
		if (checkboxesModules[i].checked){
			if (modules=="")
				modules=checkboxesModules[i].value;
			else
				modules=modules+","+checkboxesModules[i].value;
		}
	}

	var request = $.ajax({
		url: url,
		type: "POST",
		async: false,
		data: {modules: modules, action:action, profile:profile},
   	});
	    			
	request.done(function(msg) {
		
		if (msg["message"]=='403'){
			alert("FORBIDDEN");
        	window.location.href ="/forbidden";
        	return
		}
		if (msg["message"]=='ok'){
			alert("User registered and Modules Updated!");			
		return;
		}
		if(msg["message"]=='error'){
			alert(msg["error_string"]);
			return;
		}		
	});
}

function rejectRegistration(profileId,url) { 
	var action = "reject";
	var profile =profileId;
	var request = $.ajax({
		url: url,
		type: "POST",
		async: false,
		data: {action:action, profile:profile},
   	});
	    			
	request.done(function(msg) {
		
		if (msg["message"]=='403'){
			alert("FORBIDDEN");
        	window.location.href ="/forbidden";
        	return
		}
		if (msg["message"]=='ok'){
			alert("User rejected!");			
		return;
		}
		if(msg["message"]=='error'){
			alert(msg["error_string"]);
			return;
		}		
	});
}

function deleteRecord(profileId,url) { 
	var action = "delete";
	var profile =profileId;
	var request = $.ajax({
		url: url,
		type: "POST",
		async: false,
		data: {action:action, profile:profile},
   	});
	    			
	request.done(function(msg) {
		
		if (msg["message"]=='403'){
			alert("FORBIDDEN");
        	window.location.href ="/forbidden";
        	return
		}
		if (msg["message"]=='ok'){
			alert("Record Deleted!");			
		return;
		}
		if(msg["message"]=='error'){
			alert(msg["error_string"]);
			return;
		}		
	});
}
