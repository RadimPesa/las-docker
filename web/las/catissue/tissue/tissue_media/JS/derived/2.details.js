//se la derivazione e' fallita blocco la scrittura negli altri campi
function blocca_campi(){
	var id_tasto=$(this).attr("id");
	//in numero_tasto[1] ho il valore della riga corrispondente al check box selezionato
	var numero_tasto=id_tasto.split("_");
	var id_inputs="#volume_"+numero_tasto[1]+",#id_date_meas_"+numero_tasto[1];
	//blocco il tasto per fare delle misure
	var tastomis="#add_misura_"+numero_tasto[1];
	var tastomisvedi="#view_misura_"+numero_tasto[1];
	if($(this).attr("checked")){
		$(id_inputs).attr("disabled",true);
		//$("#id_date_meas_"+numero_tasto[1]).parent().children("span.datetimeshortcuts").click(function(event){
		//	event.preventDefault();
		//});
		//mi occupo del tasto per misurare tutte le aliquote		
		$(tastomis).attr("disabled",true);
		$(tastomisvedi).attr("disabled",true);
	}
	else{
		$(id_inputs).attr("disabled",false);
		$(tastomis).attr("disabled",false);
		//$("#id_date_meas_"+numero_tasto[1]).parent().children("span.datetimeshortcuts").unbind('click');
		if($(tastomis).attr("sel")){
			$(tastomisvedi).attr("disabled",false);
		}
	}
	//devo vedere se tutte le derivazioni sono fallite. Se si' blocco il tasto per fare
	//le misure per tutti
	//prendo i check abilitati che mi indicano un fallimento
	var listafalliti=$("#aliq tr td:nth-child(6)").children(":checked");
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
	var idaldersched=$(gen).attr("id_aldersched");
	//faccio la post e comunico alla vista il gen per sapere quale protocollo di qualita'
	//selezionare
	var data = {
			primo:"True",
    		gen:genid,
    		idaldersched:idaldersched
    };
	var url=base_url+"/derived/execute/measure/";
	$.post(url, data, function (result) {
    	if (result == "failure") {
    		alert("Error");
    	}
    	apri_pagina_misura();
    	//abilito il tasto corrispondente a questo per vedere le misure inserite
    	var vedimis="#view_misura_"+numero[2];
    	$(vedimis).attr("disabled",false);
    });
	//ritardo l'apertura del popup per fare in modo che la post finisca bene
	//var t=setTimeout("apri_pagina_misura()",500);
	
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
	var idaldersched=$(gen).attr("id_aldersched");
	//faccio la post e comunico alla vista il gen per sapere quale valori delle misure
	//selezionare
	var data = {
			primo:"True",
    		gen:genid,
    		idaldersched:idaldersched
    };
	var url=base_url+"/derived/execute/measure/view/";
	$.post(url, data, function (result) {

    	if (result == "failure") {
    		alert("Error");
    	}
    	apri_pagina_view();
    });
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
			//guardo se la derivazione non e' fallita
			var fallita=$("#outcome_"+i+":checked");
			if (fallita.length==0){
				var gen=$(listainp[i]).attr("value");
				var idaldersched=$(listainp[i]).attr("id_aldersched");
				stringagen+=gen+"|"+idaldersched+"&";
			}
		}
		//faccio la post e comunico alla vista il gen per sapere quali valori delle misure
		//selezionare
		var data = {
				primo:"True",
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
		alert("Unable to do measure for all aliquots: derivation protocol is not the same for all of them.");
	}
}

function apri_pagina_misura_tutti(){
	var url=base_url+"/derived/execute/measureallaliquots/";
	window.open(url,"_blank","menubar=1,resizable=1,scrollbars=1,width=1250,height=800,left=100,top=100,screenX=100,screenY=100")	
}

function riprogramma(numtot,base,tasto){
	if (numtot!=0){
		var fallite=$("#aliq input:checked").not("[sel]");
		var idcheck=$(fallite[base]).attr("id");
		var n=idcheck.split("_");
		var numero=n[1];
		var g="#gen_"+numero;
		var gen=$(g).val();
		var num=numtot-1;
		var b=base+1;
		$("#dialog-confirm p").text("Do you want to reschedule derivation for aliquot "+gen+" (line "+(parseInt(numero)+1)+")?");
		$( "#dialog-confirm" ).dialog({
			resizable: false,
			height:180,
			modal: true,
			buttons: {
				"Yes": function() {
					$( this ).dialog( "close" );
					//se la devo riprogrammare cambio il valore nell'apposito input 
					//nascosto mettendo un nome che poi arriva con la post
					$("#sched_"+base).attr("name","riprogramma_"+numero);
					//$(fallite[base]).attr("sel","s");
					riprogramma(num,b,tasto);
				},
				"No": function() {
					$( this ).dialog( "close" );
					//$(fallite[base]).attr("sel","s");
					riprogramma(num,b,tasto);
				}
			}
		});
	}
	else{
		//aggiungo al form un campo con il nome del tasto che e' stato premuto
		//per confermare. Questo permette alla vista di capire se proseguire
		//al passo successivo oppure salvare solo
		var nome=$(tasto).attr("name");
		var input = $("<input>").attr("type", "hidden").attr("name", nome);
		$("#form_conf").append($(input));
		$("#form_conf").submit();
	}
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
		var tipoder="#tipo_der_"+i;
		var tipo=$(tipoder).val();
		if((tipo=="PL")||(tipo=="VT")){
			$("#add_misura_"+i+",#view_misura_"+i+",#id_date_meas_"+i).attr("disabled",true);
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
	
	$(".vDate").datepicker({
		 dateFormat: 'yy-mm-dd',
		 maxDate: 0
	});
	$(".vDate").datepicker('setDate', new Date());
	
	//devo eseguire le separazioni delle righe in base alla data presente
	//prendo gli input con le date
	//$($("#aliq tr")[0]).css("border-bottom","0.2em solid");
	var listarighe=$("#aliq tr.interna");
	var listainp=$("#aliq tr.interna").children(":nth-child(12)");
	var confronto=$(listainp[0]).text();
	for (var i=0;i<listainp.length;i++){
		var data=$(listainp[i]).text();
		if (data!=confronto){
			confronto=data;
			$(listarighe[i-1]).css("border-bottom","0.3em solid");
			//$(listarighe[i-1]).css("border-bottom-color","red");
		}
	}
	
	//conto le righe della tabella
	righe=$("#aliq tr");
	
	for(i=1;i<righe.length;i++){
		//modifico il nome del protocollo convertendo il %20 in spazi
		var idderprot="#nome_prot_der_"+(i-1);
		var tip=$(idderprot).attr("value");
		if (tip!=undefined){
			tip=tip.replace(/%20/g," ");
			$(idderprot).attr("value",tip);
		}
		idkit="#k_"+(i-1);
		
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
	}
	//devo disabilitare i tasti per misurare nel caso abbia delle estrazioni da sangue intero e quindi guardo che il tipo
	//di derivato prodotto sia PL o VT
	blocca_misure();
	
	//mi occupo del tasto per misurare tutte le aliquote
	$("#add_mis_tutti").click(function(event){
		event.preventDefault();
		misura_tutti();
	});
	
	for(i=0;i<righe.length-1;i++){
		id="#outcome_"+i;
		$(id).click(blocca_campi);
	}
	
	$("#conf_all,#next_step").click(function(event){
		//conto le righe della tabella
		righe=$("#aliq tr");
		var regex=/^[0-9.]+$/;
		
		//verifico che tutte le misure siano state inserite
		//prendo tutti i tasti add_misura non disabilitati
		/*var listatasti=$("#aliq tr td:nth-child(6)").children();
		for(i=0;i<listatasti.length;i++){
			if((!($(listatasti[i]).attr("disabled")))&&(!($(listatasti[i]).attr("sel")))){
				frase="Please insert measure for aliquot in line "+(i+1);
				alert(frase);
				event.preventDefault();
				x=1;
			}
		}*/
		
		var vett_kit=new Array();
		var vett_capa=new Array();
		for(i=1;i<righe.length;i++){
			
			idvol="#volume_"+(i-1);
			if((!($(idvol).attr("disabled")))&&(!($(idvol).attr("value")))){
				frase="Insert volume in line "+i;
				alert(frase);
				event.preventDefault();
				return;
			}
			else{
				numero=$(idvol).attr("value").trim();
				if((!($(idvol).attr("disabled")))&&(!regex.test(numero))){
				frase="You can only insert number. Correct volume in line "+i;
				alert(frase);
				event.preventDefault();
				return;
				}
			}
			//verifico la validita' della data
			var iddata="#id_date_meas_"+(i-1);
			var dd=$(iddata).attr("value").trim();			
			var bits =dd.split('-');
			var d = new Date(bits[0], bits[1] - 1, bits[2]);
			var booleano= d && (d.getMonth() + 1) == bits[1] && d.getFullYear() == Number(bits[0])&& d.getDate()==bits[2];
			if (!booleano){
				alert("Correct date format in line "+i);
				event.preventDefault();
				return;
			}
		}
		//se il resto e' tutto a posto, chiedo all'utente se vuole rifare le derivazioni
		//non andate a buon fine
		var fallite=$("#aliq input:checked");
		if (fallite.length!=0){
			event.preventDefault();
			for(i=0;i<fallite.length;i++){
				var idcheck=$(fallite[i]).attr("id");
				var n=idcheck.split("_");
				var numero=n[1];
				var esaus="#exh_"+numero;
				if (($(esaus).val()=="1")||($(esaus).val()=="True")){
					alert("You can't reschedule aliquot in line "+(parseInt(numero)+1)+" because is exhausted");
					$(fallite[i]).attr("sel","s");
				}
			}
			var fallite2=$("#aliq input:checked").not("[sel]");
			riprogramma(fallite2.length,0,this);
		}
	});
});