var modules= new Array();
var lasauthmedia="";
var selectedModules= new Array();

function addModule(id,module){
	if (modules[id] == undefined)
		modules[id]=module;
	if (selectedModules[id] == undefined)
		selectedModules[id]= 0;
	
}

function sendMail(url){
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

	var toRecipients=localStorage.getItem("toRecipients");
	var ccRecipients=localStorage.getItem("ccRecipients");
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
	$('#toRecipients').val(localStorage.getItem("toRecipients"));
	$('#ccRecipients').val(localStorage.getItem("ccRecipients"));
	$('#bccRecipients').val(localStorage.getItem("bccRecipients"));
	
	
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