function acceptPermissions(username,url) { 
	var checkboxesModules =document.getElementsByName("permissions_"+username);
	var permissions ="";
	for (var i=0;i<checkboxesModules.length;i++){
		if (checkboxesModules[i].checked){
			if (permissions=="")
				permissions=checkboxesModules[i].value;
			else{
				permissions=permissions+","+checkboxesModules[i].value;
			}
		}
	}

	var request = $.ajax({
		url: url,
		type: "POST",
		async: false,
		data: {permissions: permissions, username:username},
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


