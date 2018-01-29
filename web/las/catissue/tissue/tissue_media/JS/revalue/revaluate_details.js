//se metto il campione esaurito, blocco l'inserimento delle misure
function blocca_campi(){
	var id_tasto=$(this).attr("id");
	//in numero_tasto[1] ho il valore della riga corrispondente al check box selezionato
	var numero_tasto=id_tasto.split("_");
	//blocco il tasto per fare delle misure
	var tastomis="#add_misura_"+numero_tasto[1];
	var tastomisvedi="#view_misura_"+numero_tasto[1];
	if($(this).attr("checked")){
		//mi occupo del tasto per misurare le aliquote		
		$(tastomis).attr("disabled",true);
		$(tastomisvedi).attr("disabled",true);
	}
	else{
		$(tastomis).attr("disabled",false);
		if($(tastomis).attr("sel")){
			$(tastomisvedi).attr("disabled",false);
		}
	}
	//devo vedere se tutte le aliquote sono esaurite. Se si' blocco il tasto per fare
	//le misure per tutti
	//prendo i check abilitati che mi indicano un fallimento
	var listafalliti=$("#aliq tr td:nth-child(8)").children(":checked");
	var listatot=$("#aliq tr td:nth-child(2)");
	if(listafalliti.length==listatot.length){
		$("#add_mis_tutti").attr("disabled",true);
	}
	else{
		$("#add_mis_tutti").attr("disabled",false);
	}
	blocca_misure();
}

function misura(){	
	//prendo il genid dell'aliq di cui e' stato premuto il tasto per le misure
	var id=$(this).attr("id");
	//l'id e' formato da add_misura_num. Es: add_misura_0
	var numero=id.split("_");
	var gen="#gen_"+numero[2];
	var genid=$(gen).attr("value");
	//faccio la post e comunico alla vista il gen per sapere quale protocollo di qualita'
	//selezionare
	var data = {
			primo:"True",
			revaluate:"True",
    		gen:genid,
    };
	var url=base_url+"/derived/execute/measure/";
	$.post(url, data, function (result) {

    	if (result == "failure") {
    		alert("Error");
    	}
    });
	//ritardo l'apertura del popup per fare in modo che la post finisca bene
	var t=setTimeout("apri_pagina_misura()",500);
	//abilito il tasto corrispondente a questo per vedere le misure inserite
	var vedimis="#view_misura_"+numero[2];
	$(vedimis).attr("disabled",false);
}

function apri_pagina_misura(){
	var url=base_url+"/derived/execute/measure/";
	window.open(url,"_blank","menubar=1,resizable=1,scrollbars=1,width=1250,height=800,left=100,top=100,screenX=100,screenY=100");
}

function vedi_misura(){
	
	//prendo il genid dell'aliq di cui e' stato premuto il tasto per le misure
	var id=$(this).attr("id");
	//l'id e' formato da view_misura_num. Es: view_misura_0
	var numero=id.split("_");
	var gen="#gen_"+numero[2];
	var genid=$(gen).attr("value");
	//faccio la post e comunico alla vista il gen per sapere quale valori delle misure
	//selezionare
	var data = {
			primo:"True",
			riv:"True",
    		gen:genid,
    };
	var url=base_url+"/derived/execute/measure/view/";
	$.post(url, data, function (result) {

    	if (result == "failure") {
    		alert("Error");
    	}
    });
	//ritardo l'apertura del popup per fare in modo che la post finisca bene
	var t=setTimeout("apri_pagina_view()",500);
}

function apri_pagina_view(){
	var url=base_url+"/derived/execute/measure/view/";
	window.open(url,"_blank","menubar=1,resizable=1,scrollbars=1,width=1250,height=600,left=100,top=100,screenX=100,screenY=100");	
}

function misura_tutti(){
	//prendo i protocolli di derivazione delle aliquote
	var listaprot=$("#aliq tr.interna .campi_prot");
	//guardo se sono tutti uguali: prendo il primo e lo confronto con tutti gli altri
	var trovato=false;
	for(i=0;i<listaprot.length;i++){
		var prot_principale=$(listaprot[0]).attr("value");
		var prot_nuovo=$(listaprot[i]).attr("value");
		if(prot_principale!=prot_nuovo){
			trovato=true;
			break;
		}
	}
	if(trovato==false){
		//prendo tutti gli input con dentro i gen delle aliquote da misurare
		var stringagen="";
		var listainp=$("#aliq tr td:nth-child(3)").children();
		for(i=0;i<listainp.length;i++){
			//guardo se l'aliquota non e' esaurita
			var esaurita=$("#exh_"+i+":checked");
			if (esaurita.length==0){
				var gen=$(listainp[i]).attr("value");
				stringagen+=gen+"&";
			}
		}
		//faccio la post e comunico alla vista il gen per sapere quali valori delle misure
		//selezionare
		var data = {
				primo:"True",
				revaluate:"True",
	    		gen:stringagen,
	    };
		var url=base_url+"/derived/execute/measureallaliquots/";
		$.post(url, data, function (result) {

	    	if (result == "failure") {
	    		alert("Error");
	    	}
	    	apri_pagina_misura_tutti();
	    });
		//ritardo l'apertura del popup per fare in modo che la post finisca bene
		//var t=setTimeout("apri_pagina_misura_tutti()",500);
	}
	else{
		alert("Unable to do measure for all aliquots: type is not the same for all of them.");
	}
}

function apri_pagina_misura_tutti(){
	var url=base_url+"/derived/execute/measureallaliquots/";
	window.open(url,"_blank","menubar=1,resizable=1,scrollbars=1,width=1250,height=800,left=100,top=100,screenX=100,screenY=100");
}

function convalida_aliquota(){
	var barcreale=$("#id_valid_barc").val();
	if(barcreale!=""){
		var url = base_url + "/api/tubes/" + barcreale+"&&" ;
	    $.getJSON(url,function(d){ 	
	        if(d.data!="errore"){
	        	var dat=d.data.toString();
	        	var val=dat.split(",");
	            //in val[0] ho il barcode del campione, in val[3] ho il genid
	            //se e' lungo 5 vuol dire che la provetta non e' vuota
	        	$("#aliq tr").css("background-color","#E8E8E8");
	            if (val.length==5){
	        		//devo vedere se il codice e' all'interno della lista di quelli da trattare in questa sessione
	        		//o se proprio non c'entra niente con questa schermata
	        		var lista_barc=$(".lis_barcode");
	        		var lis_indici=$(".lis_indici");
	        		var lis_gen=$(".lis_gen");
	        		var trovato=false;
	        		var indice="";
	        		var gen="";
	        		for(var i=0;i<lista_barc.length;i++){
	        			var codice=$(lista_barc[i]).text();
	        			if(codice.toLowerCase()==barcreale.toLowerCase()){
	        				trovato=true;
	        				indice=$(lis_indici[i]).text();
	        				gen=$(lis_gen[i]).text();
	        				break;
	        			}
	        		}      		
	        		if(trovato){
	        			jQuery("#dialogMess").html("Barcode: "+barcreale+"<br>GenID: "+gen+"<br>"+indice+"° sample in this working session");
	        			var riga=$(lis_indici[indice-1]).parent();
	        			$(riga).css("background-color","#B6B5B5");
	        		}
	        		else{
	        			jQuery("#dialogMess").html("Barcode: "+barcreale+"<br>GenID: "+val[3]+"<br><br>Aliquot IS NOT in this working session, please change tube");
	        		}   	
	            }
	            //vuol dire che la provetta e' vuota
	            else{
	            	jQuery("#dialogMess").html("Barcode: "+barcreale+"<br><br>Container is empty or does not exist");
	            	
	            }   
	            jQuery("#dia1").dialog({
		            resizable: false,
		            height:200,
		            width:450,
		            modal: true,
		            draggable :false,
		            buttons: {
		                "Ok": function() {
		                    jQuery( this ).dialog( "close" );
		                    $("#id_valid_barc").focus();
		                },
		            },
		        });
	        }
	        
	        $("#id_valid_barc").val("");
	    });
	}
	else{
		alert("Please insert barcode");
	}
}

function blocca_misure(){
	var righe=$("#aliq tr.interna");
	for(var i=0;i<righe.length;i++){
		var tipoaliq="#tipoaliquota_"+i;
		var tipo=$(tipoaliq).val();
		if(tipo!="Derived"){
			$("#add_misura_"+i+",#view_misura_"+i).attr("disabled",true);
		}
	}
	//devo vedere se tutti i tasti Add measure sono disabilitati devo disabilitare anche il tasto generale di "misura tutti"
	var tastidisabilitati=$(".add_measure:disabled");
	if(tastidisabilitati.length==righe.length){
		$("#add_mis_tutti").attr("disabled",true);
	}
	else{
		$("#add_mis_tutti").attr("disabled",false);
	}
}

$(document).ready(function () {
	var tabfin=$("#aliquote_fin");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
		//per il report finale
		generate_result_table("Revaluation","aliquote_fin");
	}
	
	$("#validate_barc").click(function(event){
		event.preventDefault();
		convalida_aliquota();
	});
	
	$("#id_valid_barc").keypress(function(event){
		//13 e' il codice ASCII del CRLF
		if ( event.which == 13 ) {
			event.preventDefault();
			convalida_aliquota();
		}
	});
	
	//conto le righe della tabella
	var righe=$("#aliq tr");
	for(var i=1;i<righe.length;i++){
		//disabilito i tasti di misura in modo che non mi facciano partire la 
		//sottomissione del form
		idmis="#add_misura_"+(i-1);
		$(idmis).click(function(event){
			event.preventDefault();
		});
		$(idmis).click(misura);
		
		idvedimis="#view_misura_"+(i-1);
		$(idvedimis).attr("disabled",true);
		$(idvedimis).click(function(event){
			event.preventDefault();
		});
		$(idvedimis).click(vedi_misura);
		
		id="#exh_"+(i-1);
		$(id).click(blocca_campi);

	}
	//devo disabilitare i tasti per misurare nel caso abbia dei campioni non derivati
	blocca_misure();
	
	//mi occupo del tasto per misurare tutte le aliquote
	$("#add_mis_tutti").click(function(event){
		event.preventDefault();
		misura_tutti();
	});
	
	$("#conf_all").click(function(event){
		//verifico che tutte le misure siano state inserite
		//prendo tutti i tasti add_misura
		var listatr=$("#aliq tr.interna");
		for(i=0;i<listatr.length;i++){
			var tasto="#add_misura_"+String(i);
			if((!($(tasto).attr("disabled")))&&(!($(tasto).attr("sel")))){
				alert("Please insert measure for aliquot in line "+(i+1));
				event.preventDefault();
				return;
			}
			else if(($(tasto).attr("disabled"))&&(!($("#exh_"+String(i)).is(":checked")))){
				alert("Please set 'exhausted' for aliquot in line "+(i+1));
				event.preventDefault();
				return;
			}
		}
	});
});