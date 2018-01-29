var modules= new Array();
var lasauthmedia="";
usersList=new Array();
checkArray=new Array();
var emailsList=new Array();
function addModule(id,module){
	if (modules[id] == undefined)
		modules[id]=new Array();

}

function addUserToModule(id,username,email){
	if (modules[id] == undefined){
		modules[id]= new Array();
		modules[id].push(username);
		emailsList[username]=email;
	}
	else{
		modules[id].push(username);
		emailsList[username]=email;
	}

}
function moveUsers(){
	var found=false;
	$('input:checkbox:checked.modules').each( 
	    function() { 
	    	found=true;
	    	if (this.value !="all"){
	    		for (index in modules[this.value]){
	    			usersList.push(modules[this.value][index]);
	    		}
	    	}   
	    } 
	);
	if (found==false){
		alert("You have to select at least one module!");
	 	return;
	}
	var result = [];
  	$.each(usersList, function(i, e) {
    	if ($.inArray(e, result) == -1) result.push(e);
  	});
	usersList = result;
	
        if(usersList.length>0){
            row= '<tr><td></td><td><input type="button" onClick="selectAllTo()" value="ALL"/></td>'
            row+= '<td><input type="button" name="allcc" onClick="selectAllCc()" value="ALL"/></td>'
            row+= '<td><input type="button" name="allbcc" onClick="selectAllBcc()" value="ALL"/></td>'
            row+= '<td><input type="button" name="allno" onClick="selectAllNo()" value="ALL"/></td></tr>'
                $('#usersTable tr:last').after(row);
    
        }      
	for (index in usersList){
		row= "<tr><td title=\""+emailsList[usersList[index]]+ "\" >"+usersList[index]+"</td><td><input type=\"radio\" value=\"to\" id=\"to_"+index+"\" name=\""+usersList[index]+"\"/></td>"
		row+="<td><input type=\"radio\" value=\"cc\" id=\"cc_"+index+"\" name=\""+usersList[index]+"\"/></td>"
		row+="<td><input type=\"radio\" value=\"bcc\" id=\"bcc_"+index+"\" name=\""+usersList[index]+"\"/ checked></td>"	 
		row+="<td><input type=\"radio\" value=\"no\" id=\"no_"+index+"\" name=\""+usersList[index]+"\"/ ></td></tr>"
		$('#usersTable tr:last').after(row);
	}
	
	$('table#modulesTable input[type=checkbox]').attr('disabled','true');
	$('#move_users').bind('click',disabler);
	$("#submit").css("display", "inline");

}

function selectAllTo(){
    $(':radio[value="to"]').attr('checked',true);
}
function selectAllBcc(){
    $(':radio[value="bcc"]').attr('checked',true);
}
function selectAllCc(){
    $(':radio[value="cc"]').attr('checked',true);
}
function selectAllNo(){
    $(':radio[value="no"]').attr('checked',true);
}


function disabler(event) {
    event.preventDefault();
    return false;
}


$(document).ready(function() {
    if($(".modules").length == $(".modules:checked").length) {
        $("#all").attr("checked", "checked");
    } else {
        $("#all").removeAttr("checked");
    }
	
    $(function(){
    // add multiple select / deselect functionality
	 	$("#all").click(function () {
	    	$('.modules').attr('checked', this.checked);     
	    });
	    // if all checkbox are selected, check the selectall checkbox
	    // and viceversa
	    $(".modules").change(function(){
	 
	        if($(".modules").length == $(".modules:checked").length) {
	            $("#all").attr("checked", "checked");
	        } else {
	            $("#all").removeAttr("checked");
	        }
	        
	    });
	});
	
} );

function reset(){
	$(usersTable).empty();
	var thead="<thead><tr><th>Users</th><th>To</th><th>CC</th><th>BCC</th><th>Don't send</th></tr></thead>"
	$('#usersTable').append(thead);
	$('#move_users').unbind('click',disabler);
	$('table#modulesTable input[type=checkbox]').removeAttr('disabled');
	usersList=[];
	$("#submit").css("display", "none");
}

function send(url){
	var toRecipients="";
	var ccRecipients="";
	var bccRecipients="";
	
	for (index in usersList){
		if ($("#to_"+index).is(':checked'))
			toRecipients+=usersList[index]+",";
		else if ($("#cc_"+index).is(':checked'))
			ccRecipients+=usersList[index]+",";
		else if ($("#bcc_"+index).is(':checked'))
			bccRecipients+=usersList[index]+",";

	}
	if ((toRecipients.length==0)&&(ccRecipients.length==0)&&(bccRecipients.length==0)){
		alert("Select at least one user!");
		return ;
	}

	localStorage.setItem("toRecipients",toRecipients);
	localStorage.setItem("ccRecipients",ccRecipients);
	localStorage.setItem("bccRecipients",bccRecipients);
	
	var form = $('<form action="' + url + '" method="post">' +
  		'<input type="hidden" name="step" value="1" />' +
		'</form>');
	$('body').append(form);
	$(form).submit();

}
