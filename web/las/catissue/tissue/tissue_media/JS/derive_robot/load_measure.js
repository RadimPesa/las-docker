//se la derivazione e' fallita blocco la scrittura negli altri campi
function blocca_campi(){
	var id_tasto=$(this).attr("id");
	//in numero_tasto[1] ho il valore della riga corrispondente al check box selezionato
	var numero_tasto=id_tasto.split("_");
	var id_inputs="#volume_"+numero_tasto[1]+",#id_date_meas_"+numero_tasto[1];
	if($(this).attr("checked")){
		$(id_inputs).attr("disabled",true);
	}
	else{
		$(id_inputs).attr("disabled",false);		
	}
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
	        			if(codice.toLowerCase().trim()==barcreale.toLowerCase().trim()){
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
	var tabfin=$("#aliquote_fin");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
		//per il report finale
		generate_result_table("Quantification","aliquote_fin");
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
	
	$(".vDate").datepicker({
		 dateFormat: 'yy-mm-dd',
		 maxDate: 0
	});
	$(".vDate").datepicker('setDate', new Date());
	
	$("#id_exp_name").keypress(validateFreeInput);
	
	//devo eseguire le separazioni delle righe in base alla data presente
	//prendo gli input con le date
	var listarighe=$("#aliq tr.interna");
	var listainp=$("#aliq tr.interna").children(":nth-child(9)");
	var confronto=$(listainp[0]).text();
	for (var i=0;i<listainp.length;i++){
		var data=$(listainp[i]).text();
		if (data!=confronto){
			confronto=data;
			$(listarighe[i-1]).css("border-bottom","0.3em solid");
		}
	}
	
	//faccio in modo di far sentire il click anche se e' sul testo del checkbox
	$(".td_prot_name").click(function(){
		var check=$(this).parent().children().children(":checkbox");		
		if($(check).is(":checked")){
			$(check).removeAttr("checked");
		}
		else{
			$(check).attr("checked","checked");
		}		
	});
	var tipoesp=$("#tipoproc").val();
	if(tipoesp!="revalue"){
		//conto le righe della tabella
		var righe=$("#aliq tr");
		
		for(var i=0;i<righe.length-1;i++){
			//modifico il nome del protocollo convertendo il %20 in spazi
			var idderprot="#nome_prot_der_"+i;
			var tip=$(idderprot).attr("value");
			if (tip!=undefined){
				tip=tip.replace(/%20/g," ");
				$(idderprot).attr("value",tip);
			}	
			id="#outcome_"+i;
			$(id).click(blocca_campi);
		}
	}
	
	$("#conf_all").click(function(event){
		//conto le righe della tabella
		var righe=$("#aliq tr");
		var regex=/^[0-9.]+$/;
		if(tipoesp!="revalue"){
			for(i=1;i<righe.length;i++){
				
				idvol="#volume_"+(i-1);
				if((!($(idvol).attr("disabled")))&&(!($(idvol).attr("value")))){
					alert("Please insert volume in line "+i);
					event.preventDefault();
					return;
				}
				else{
					numero=$(idvol).attr("value").trim();
					if((!($(idvol).attr("disabled")))&&(!regex.test(numero))){
					alert("You can only insert number. Please correct volume in line "+i);
					event.preventDefault();
					return;
					}
				}			
			}
		}
		//verifico la validita' della data
		var iddata="#id_date_meas";
		var dd=$(iddata).attr("value").trim();			
		var bits =dd.split('-');
		var d = new Date(bits[0], bits[1] - 1, bits[2]);
		var booleano= d && (d.getMonth() + 1) == bits[1] && d.getFullYear() == Number(bits[0])&& d.getDate()==bits[2];
		if (!booleano){
			alert("Please correct measurement date format");
			event.preventDefault();
			return;
		}
		
		if(!($("#id_exp_name").attr("value"))){
			alert("Please insert experiment name");
			event.preventDefault();
			return;
		}
		
		var lisprotcheck=$(".checkuser:checked");
		if(lisprotcheck.length==0){
			alert("Please select at least one quality control protocol");
			event.preventDefault();
			return;
		}
		//per il tipo di container		
		var tipo=$("#id_container option:selected").val();
		if(tipo==""){
			alert("Please select source container type");
			event.preventDefault();
			return;
		}
		if(tipoesp!="revalue"){
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
		}
	});
});
