nomemarker="";

//serve a cambiare la scritta con il tipo di marker in base alla tecnica scelta
function aggiorna_marker(){
	var idtecnica=$("#id_technique option:selected").val();
	nomemarker=dizrel[idtecnica];
	$("#marker").text(nomemarker);
	if(nomemarker=="Probe"){
		$("#span_probe").show();
	}
	else{
		$("#span_probe").hide();
	}
}

//funzione che gestisce l'apertura della pagina per inserire un nuovo marker
function apri_pagina_nuovo_marker(){
	var valtech=$("#id_technique option:selected").val();
	if(valtech==""){
		alert("Please first select a technique");
	}
	else{
		var tipomark=dizrel[valtech];
		if(tipomark=="Probe"){
			//se e' un probe apro la pagina del modulo delle annotazioni in cui posso inserire una sequenza nucleotidica
			//L'utente salva li' la sequenza e dopo il modulo delle annotazioni comunica a me il nuovo probe salvato e io gli faccio
			//vedere la schermata parzialmente compilata con il nome. Se l'utente vuole puo' aggiungere gli altri dati del probe nei 
			//vari campi
			var url=urlannotazioni+"/create_targetseq/?biobank=yes";
		}
		else{
			var url=base_url+"/label/newMarker/?technique="+valtech;
		}
		window.open(url,"_blank","menubar=1,resizable=1,scrollbars=1,width=1250,height=800,left=100,top=100,screenX=100,screenY=100");
	}
}

function seleziona_marker(event,element){	
	var marker=$("#id_markname").val();
	$("#id_markname2").val(marker);
	if(marker==""){
		alert("Please insert marker name");
		return;
	}
	if(nomemarker==""){
		alert("Please first select a technique");
		return;
	}
	//in nomemarker ho il tipo di marker (probe, colorante, anticorpo)
	lismarkerpresenti=dizmarker[nomemarker];
	if($.inArray(marker,lismarkerpresenti)==-1){
		alert("Marker does not exist. Please change name");
		$("#id_markname,#id_markname2").val("");
		return;
	}
	//se e' tutto a posto simulo un click sul tasto nascosto che e' collegato
	//alla libreria boxlist e che mi mette il marker nella lista
	$("#add_btnprot").click();
	$("#id_markname").val("");
	//disabilito la scelta della tecnica altrimenti l'utente puo' inserire piu' marker
	//per varie tecniche
	$("#id_technique").attr("disabled",true);
}

function abilita_tecnica(){	
	//riabilito la possibilita' di scegliere la tecnica se non ci sono valori di marker selezionati
	var lisval=$("#id_markname2").boxlist("getValues");
	if(lisval.length==0){
		$("#id_technique").attr("disabled",false);
	}
}

//funzione che gestisce l'apertura della pagina per cercare un probe in base al gene
function apri_pagina_cerca_gene(){
	var valtech=$("#id_technique option:selected").val();
	if(valtech==""){
		alert("Please first select a technique");
	}
	else{
		var url=base_url+"/label/searchProbe/";
		window.open(url,"_blank","menubar=1,resizable=1,scrollbars=1,width=1000,height=800,left=100,top=100,screenX=100,screenY=100");
	}
}

$(document).ready(function () {
	$("#id_technique").change(aggiorna_marker);
	
	$("#addMark").click(apri_pagina_nuovo_marker);
	
	$("#search_gene").click(apri_pagina_cerca_gene);
	
	$("#id_markname").autocomplete({
        source: function(request, response) {
        	if(nomemarker==""){
        		alert("Please first select a technique");
        		$("#id_markname").val("");
        		return;
        	}
            $.ajax({
                url: base_url+'/api/label/markname/autocomplete/',
                dataType: "json",
                data: {
                    term: request.term,
                    marker:nomemarker
                },
                success: function(data) {
                    response(data);
                }
            });
        },
    });
	
	$("#id_markname").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			seleziona_marker();
		}
	});
	
	$("#id_markname2").boxlist();
	
	$("#id_name").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
		}
	});
	
	var tabfin=$("#prot_fin");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
    	generate_result_table("Protocol","prot_fin");
	}
	
	$("#add_marker").click(seleziona_marker);
	
	$("span.listdel,span.boxlistdel").live("click", function () {
		abilita_tecnica();
	});
	
	$("#tastofile").click(function(){
		$("#id_file").click();
	});
	
	$("#id_file").change(function(){
		var files = $('#id_file')[0].files;
		var nomfile="";
		for (var i = 0; i < files.length; i++) {
	        nomfile+=files[i].name.split("\\").pop()+","
	    }
		//tolgo la virgola finale
		nomfile = nomfile.substring(0, nomfile.length - 1)
		$("#filename").val(nomfile);
	});
	
	$("#conferma").click(function(event){
		event.preventDefault();
		var nome=$("#id_name").val();
		if(nome==""){			
			alert("Please insert protocol name");
			return;
		}		
		var lisval=$("#id_markname2").boxlist("getValues");
		if(lisval.length==0){
			alert("Please insert a marker");
			return;
		}
		
		var timer = setTimeout(function(){$("body").addClass("loading");},500);
		var data = {
    			salva:true,
    			dati:JSON.stringify(lisval),	    		
	    };
		var url=base_url+"/label/protocol/";
		$.post(url, data, function (result) {
	    	if (result == "failure") {
	    		alert("Error");
	    	}
	    	clearTimeout(timer);
	    	$("body").removeClass("loading");
	    	$("#id_technique").attr("disabled",false);
	    	$("#form_fin").append("<input type='hidden' name='final' />");
	    	$("#form_fin").submit();
	    });		
	});
});
