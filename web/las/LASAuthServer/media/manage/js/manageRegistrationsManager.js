function acceptRegistration(profileId,url) { 

	var checkboxesActivities =document.getElementsByName("activities_"+profileId);
	var action = "accept";
	var profile =profileId;
	var activities ="";
	for (var i=0;i<checkboxesActivities.length;i++){
		if (checkboxesActivities[i].checked){
			if (activities=="")
				activities=checkboxesActivities[i].value;
			else
				activities=activities+","+checkboxesActivities[i].value;
		}
	}

	var request = $.ajax({
		url: url,
		type: "POST",
		async: false,
		data: {activities: activities, action:action, profile:profile},
   	});
	    			
	request.done(function(msg) {
		
		if (msg["message"]=='403'){
			alert("FORBIDDEN");
        	window.location.href ="/forbidden";
        	return
		}
		if (msg["message"]=='ok'){
			alert("User registered and Activities Updated!");			
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

/*
function acceptRegistration2(profileId,url) { 
	var checkboxesActivities =document.getElementsByName("activities_"+profileId);
	var action = "accept";
	var profile =profileId;
	var activities ="";
	for (var i=0;i<checkboxesActivities.length;i++){
		if (checkboxesActivities[i].checked){
			if (activities=="")
				activities=checkboxesActivities[i].value;
			else
				activities=activities+","+checkboxesActivities[i].value;
		}
	}

	var request = $.ajax({
		url: url,
		type: "POST",
		async: false,
		data: {activities: activities, action:action, profile:profile},
   	});
	    			
	request.done(function(msg) {
		
		if (msg["message"]=='403'){
			alert("FORBIDDEN");
        	window.location.href ="/forbidden";
        	return
		}
		if (msg["message"]=='ok'){
			alert("User registered and Activities Updated!");			
		return;
		}
		if(msg["message"]=='error'){
			alert(msg["error_string"]);
			return;
		}		
	});
}

function rejectRegistration2(profileId,url) { 
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

function deleteRecord2(profileId,url) { 
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

*/
