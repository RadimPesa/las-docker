
function sendMail(url){
    users=[];
    $("input[type='checkbox']:checked").each(
        function() {
            var className = $(this).attr('class');
            if (className != 'checkCategory'){
                if ($.inArray($(this).attr('username'),users)==-1)
                    users.push($(this).attr('username'));
            }
        }
    );
    console.log(users);
    return false;
	var path="";
	var oFile = document.getElementById('file').files[0];
    // filter for image files
     
    if (oFile!=null){
    	if(oFile.size > 5242880) {
        	alert("File superiore a 5 MB!");
        	return;
        }
        path=document.getElementById('file').value;
    }
	var subject="";
	var message="";
	if(($('#subject').val()=="") ||($('#message').val()=="")){
		alert("Insert a valid Subject / Message!");
		return;
	}
	else{
		subject=$('#subject').val();
		message=$('#message').val();
	} 

	var bccRecipients=localStorage.getItem("bccRecipients");
	var request = $.ajax({
		url: url,
		type: "POST",
		async: false,
		data: {toRecipients:toRecipients,ccRecipients:ccRecipients,bccRecipients:bccRecipients, message:message, subject:subject, path:path},
   	});
	    			
	request.done(function(msg) {
		
		if (msg["message"]=='403'){
			alert("FORBIDDEN");
        	window.location.href ="/forbidden";
        	return
		}
		if (msg["message"]=='ok'){
			alert("Mail Sent!");			
		return;
		}
		if(msg["message"]=='error'){
			alert("Fatal error! Contact us to fix the bug!");
			return;
		}		
	});
}

function updateInput(){
	var subject="";
	var message="";
	if(($('#subject').val()=="") ||($('#message').val()=="")){
		alert("Insert a valid Subject / Message!");
		return false;
	}
    users=[];
    $("input[type='checkbox']:checked").each(
        function() {
            var className = $(this).attr('class');
            if (className != 'checkCategory'){
                if ($.inArray($(this).attr('username'),users)==-1)
                    users.push($(this).attr('username'));
            }
        }
    );
    if (users.length>0)
    	$('#bccRecipients').val(JSON.stringify(users));
    else{
        alert('Please insert at least one recipient!');
        return false;
   }
	
	
	return true;
}

function resetFiles(){
	$(".file").val("");
} 
$(document).ready(function() {
	$("#main").on("change", " input[type=file]:last", function(){
	    var item = $(this).clone(true);
	    var fileName = $(this).val();
	    if(fileName){
	        $(this).parent().append("<br/>").append(item);
	    }  
	});


});
