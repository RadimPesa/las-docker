var dizkit={};

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
	
	//devo eseguire le separazioni delle righe in base alla data presente
	//prendo gli input con le date
	//$($("#aliq tr")[0]).css("border-bottom","0.2em solid");
	var listarighe=$("#aliq tr.interna");
	var listainp=$("#aliq tr.interna").children(":nth-child(9)");
	var confronto=$(listainp[0]).text();
	for (var i=0;i<listainp.length;i++){
		var data=$(listainp[i]).text();
		if (data!=confronto){
			confronto=data;
			$(listarighe[i-1]).css("border-bottom","0.3em solid");
			//$(listarighe[i-1]).css("border-bottom-color","red");
		}
	}
	
	//carico tutti i possibili kit dei protocolli presenti
	var dizprot={};
	for (var i=0;i<listarighe.length;i++){
		var protocollo=$("#proto_"+i).val();
		dizprot[protocollo]=1;
	}
	
	for (var key in dizprot){
		var urlkit=base_url+"/api/derived/kit/"+key;
	 	$.getJSON(urlkit,function(d){
	 		if(d.data!="errore"){
	 			var diztemp={};
	 			for (var i=0;i<d.data.length;i++){
	 				diztemp[d.data[i].barcode.toLowerCase()]=d.data[i].remainingCapacity;
	 			}
	 			dizkit[d.tipo]=diztemp;
	 		}
	 	});
	}
	
	//conto le righe della tabella
	var righe=$("#aliq tr");
	for(i=1;i<righe.length;i++){
		idkit="#k_"+(i-1);
		$(idkit).keypress(function(event){
			//13 e' il codice ASCII del CRLF
			if ( event.which == 13 ) {
			    event.preventDefault();
			    //verifico che il nuovo kit inserito esista
			    var trovato=0;
			    var id=$(this).attr("id");
			    var numerokit=id.split("_");
			    var protocollo=$("#proto_"+numerokit[1]).attr("value");
			    var barcode=$("#k_"+numerokit[1]).attr("value").toLowerCase();
			    var barc2=$("#k_"+numerokit[1]).attr("value");
			    //vedo se quel kit e' gia' stato inserito
			    var conta=0;
			    var inp=$("#aliq tr td:nth-child(7)").children();
			    for(i=0;i<inp.length;i++){
			    	if($(inp[i]).val()==barcode){
			    		conta+=1;
			 		}
			 	}
			    if(conta<=1){
		 			var diztemp=dizkit[protocollo];
		 			if (!(barcode in diztemp)){
		 				alert("Error. Kit barcode does not exist");
		 				$("#k_"+numerokit[1]).attr("value","");
		 				$("#cap_"+numerokit[1]).text("");
		 			}

		 			//devo copiare il codice del kit in questione anche nelle altre righe
		 			//che riguardino pero' lo stesso protocollo
		 			else{
		 				var capacit=diztemp[barcode];
		 				//salvo la capacita' del kit
		 				$("#cap_"+numerokit[1]).text(capacit);
		 				//prendo la lista delle righe con aliquote che 
		 				//utilizzano quel protocollo
		 			    var lista_tr=$("input:hidden[value="+protocollo+"]").parent();
		 			    //trovo l'indice all'interno della lista che corrisponde a quello della
		 			    //riga in cui ho gia' scritto il codice
		 			    var indice="";
		 			    for(i=0;i<lista_tr.length;i++){
		 			    	var id=$(lista_tr[i]).children(":nth-child(1)").attr("id");
		 			    	var numer=id.split("_");
		 			    	if (numer[1]==numerokit[1]){
		 			    		indice=i;
		 			    	}
		 			    }
		 			    //tolgo dalla lista attuale la tr in cui ho gia' scritto il codice
		 			    //del kit
		 			    lista_tr.splice(indice,1);
		 			    for(var i=0;i<lista_tr.length;i++){
		 			        if(( i<(capacit-1))&&($(lista_tr[i]).children(":nth-child(7)").children().val()=="")){
		 			        	$(lista_tr[i]).children(":nth-child(7)").children().attr("value",barc2);
		 			    	 	$(lista_tr[i]).children(":nth-child(8)").text(capacit);
		 			    	}
		 			    }
		 			}
			    }
			    else{
			    	$(this).val("");
			    	alert("Kit already selected");
			    }
			}
		});
	}
	
	$("#conf_all,#next_step").click(function(event){
		event.preventDefault();
		//metto un controllo per vedere se e' stato premuto l'invio per ogni riga con un codice
		//kit dentro
		var listarighe=$("#aliq tr.interna");
		for(var i=0;i<listarighe.length;i++){
			var barc=$("#k_"+i).val().toLowerCase();
			if (barc!=""){
				//se e' stato inserito un codice				
				var protocollo=$("#proto_"+i).attr("value");
				var diztemp=dizkit[protocollo];
	 			if (!(barc in diztemp)){
	 				alert("Error. Kit barcode in line "+(i+1)+" does not exist");		 				
	 				return;
	 			}
			}
		}
		var id=$(this).attr("id");
		if (id=="conf_all"){
			$("#form_conf").append("<input type='hidden' name='stop' />");
		}
		else{
			$("#form_conf").append("<input type='hidden' name='next' />");
		}
		$("#form_conf").submit();
	});
});
