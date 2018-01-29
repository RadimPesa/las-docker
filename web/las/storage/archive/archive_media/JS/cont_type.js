
function disabilitapadri(){
	var selez=$(this).is(':checked');
	if (selez){
		$("#id_contpadri").attr("disabled",true);
	}
	else{
		$("#id_contpadri").attr("disabled",false);
	}
}

function disabilitafigli(){
	var selez=$(this).is(':checked');
	if (selez){
		$("#id_contfigli").attr("disabled",true);
	}
	else{
		$("#id_contfigli").attr("disabled",false);
	}
}

$(document).ready(function () {
	//faccio comparire sette righe nella select per il tipo di container interno
	$("#id_contpadri,#id_contfigli").attr("size","7");
	
	$("#id_root").click(disabilitapadri);
	$("#id_leaf").click(disabilitafigli);
	
	var spinner = $("#spi,#id_col,#id_row").spinner(
			{
				min:1,
				max:1000
			});
	
	$("#conferma").click(function(event){
		var regex=/^[0-9]+$/;
		//guardo se sono state inserite le colonne
		var colo=$("#id_col").val();
		if(colo==""){
			alert("Insert columns number");
			event.preventDefault();
		}
		else{
			if((!regex.test(colo))||(colo=="0")){
				alert("You can only insert number. Please correct columns value");
				event.preventDefault();
			}
		}
		//guardo se sono state inserite le righe
		var rig=$("#id_row").val();
		if(rig==""){
			alert("Insert rows number");
			event.preventDefault();
		}
		else{
			if((!regex.test(rig))||(rig=="0")){
				alert("You can only insert number. Please correct rows value");
				event.preventDefault();
			}
		}
		//verifico che il massimo numero di cont per posizione sia scritto giusto
		var posiz=$("#spi").val();
		if (posiz!=""){
			if((!regex.test(posiz))||(posiz=="0")){
				alert("You can only insert number. Please correct max n° containers value");
				event.preventDefault();
			}
		}
		//verifico che non sia stato scelto lo stesso tipo di container sia come padre che come figlio
		var lispadri=$("#id_contpadri").val();
		var lisfigli=$("#id_contfigli").val();
        for(var i=0;i<lispadri.length;i++){
        	if ($.inArray(lispadri[i],lisfigli)!=-1){
            	alert("One container is both father and child of this container. Please correct.");
            	event.preventDefault();
        		break;
            }
        }
		
	});
});
