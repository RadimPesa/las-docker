var result1="";
var result2="";
var modules=[];
var username="";

function moveRight(event) {
	var perms_array=result1.split(",");
	for (var i=0;i<(perms_array.length-1);i++){
		if(perms_array[i]!=""){
			var perm_clone = $("#"+perms_array[i]).clone(true);
			$(perm_clone).removeClass('ui-selected');
			$("#"+perms_array[i]).remove();
			$("#sortable2"+event.data.mod).append(perm_clone);
		}
	}
	return;
}
	
function moveLeft(event)
{
	var perms_array=result2.split(",");
	
	for (var i=0;i<(perms_array.length-1);i++){
		if(perms_array[i]!=""){
			var perm_clone = $("#"+perms_array[i]).clone(true);
			$(perm_clone).removeClass('ui-selected');
			$("#"+perms_array[i]).remove();
			$("#sortable1"+event.data.mod).append(perm_clone);

		}
	}
	return;
}

$(document).ready(function() {
	for (var i=0;i<modules.length;i++){
		$("#move_right"+modules[i]).click({mod: modules[i]},moveRight);
		$("#move_left"+modules[i]).click({mod: modules[i]},moveLeft); 	
	}
				
});

$(function() {
    for (var i=0;i<modules.length;i++){
    	$( "#sortable1"+modules[i]).selectable({
            stop: function() {
                result1 = ""
                $( ".ui-selected", this ).each(function() {
                    result1+=this.id+","
                });
            }
        });
        
        $( "#sortable2"+modules[i]).selectable({
            stop: function() {
                result2 = ""
                $( ".ui-selected", this ).each(function() {
                    result2+=this.id+","
                });
            }
        });
    }
});

function UpdatePostOrder(url) { 
	$('*').css('cursor','progress'); 
	var arr = [];
	var arr2 = [];
	for (var i=0;i<modules.length;i++){
  		$("#sortable2"+modules[i]+" li").each(function(){
	    	arr.push($(this).attr('id'));
	  	});
	  	
	  	$("#sortable1"+modules[i]+" li").each(function(){
	    	arr2.push($(this).attr('id'));
	  	});
	}
	
	var permessiOk=arr.join(',');
	var permessiNok=arr2.join(',');
	var request = $.ajax({
			url: url,
			type: "POST",
			async:false,
			data: {permessiOk: permessiOk,permessiNok: permessiNok, username: username},
   	});
    			
	request.done(function(msg) {
		$('*').css('cursor','default'); 
		
		if (msg["message"]=='403'){
			alert("FORBIDDEN");
        	window.location.href ="/forbidden";
        	return
		}
		if (msg["message"]=='ok'){
			alert("Permission updated");
			

		return;
		}
		if(msg["message"]=='error'){
			alert(msg["error_string"]);
			return;
		}
	});
}
