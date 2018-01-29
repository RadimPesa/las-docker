calcola=true;

function esegui_calcoli(i){
	$("#vol_temp_"+i).css("border","");
	var conce=$("#concen_"+i).val();
	//devo calcolare il volume effettivo da prelevare dall'aliquota in base alla sua
	//concentrazione, che puo' essere diversa da quella standard
	var loadv=parseFloat($("#loadvol_"+i).val());
	var quant=$("#quantity_"+i).val();
	var risul=(quant*1000)/conce;
	var ris=parseFloat(risul).toFixed(1);
	$("#vol_temp_"+i).val(ris);
	//calcolo l'acqua con cui diluire
	if (ris<=loadv){
		var rr=loadv-ris;
		var risultat=parseFloat(rr).toFixed(1);
		$("#h2o_"+i).text(risultat);
	}
	else{
		$("#h2o_"+i).text("0.0");
		$("#vol_temp_"+i).css("border","3px solid red");
	}
}

function calcola_val(){
	var id=$(this).attr("id");
	//l'id e' formato da calc_num. Es: calc_0
	var numero=id.split("_");
	var i=numero[1];
	esegui_calcoli(i);
}

function calcola_tutti(){
	var righe=$("#aliq tr.interna");
	for(var i=0;i<righe.length;i++){
		esegui_calcoli(i);
	}
	calcola=true;
}

function selez_deselez_tutte(){
	if ($(this).attr("sel")=="s"){	
		$(this).val("Set all aliquots exhausted");
		$(":checkbox").removeAttr("checked");
		$(this).removeAttr("sel");
	}
	else{
		$(this).val("Deselect all aliquots exhausted");
		$(":checkbox").attr("checked","checked");
		$(this).attr("sel","s");
	}
}

function selez_aliq(){
	//conto le righe totali
	var righe=$("#aliq tr.interna");
	var listasel=$(".exha:checked");
	if (righe.length==listasel.length){
		$("#seltutte").val("Deselect all aliquots exhausted");
		$("#seltutte").attr("sel","s");
	}
	else{
		$("#seltutte").val("Set all aliquots exhausted");
		$("#seltutte").removeAttr("sel");
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
	        		var trovato=false;
	        		var indice="";
	        		for(var i=0;i<lista_barc.length;i++){
	        			var codice=$(lista_barc[i]).text();
	        			if(codice.toLowerCase()==barcreale.toLowerCase()){
	        				trovato=true;
	        				indice=$(lis_indici[i]).text();
	        				break;
	        			}
	        		}      		
	        		if(trovato){
	        			jQuery("#dialogMess").html("Barcode: "+barcreale+"<br>GenID: "+val[3]+"<br>"+indice+"° sample in this working session");
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

function cambia_utente_provette(tasto){
	$("#dia2 p").text("Do you want to give these tubes to another user?");
	$("#dia2").dialog({
		resizable: false,
		height:180,
		modal: true,
		buttons: {
			"Yes": function() {
				$( this ).dialog( "close" );
				$("#dia3").dialog({
					resizable: true,
					height:500,
					modal: true,
					buttons: {
						"Ok": function() {
							var selez=$(".checkuser:checked");
							if(selez.length==0){
								alert("Please select a user");
								return;
							}
							$("#newuser_t").val($(selez).attr("id"));
							$( this ).dialog( "close" );
							var nome=$(tasto).attr("name");
							var input = $("<input>").attr("type", "hidden").attr("name", nome);
							$("#form_conf").append($(input));
							$("#form_conf").submit();
						},
						"Cancel": function() {
							$( this ).dialog( "close" );
							var nome=$(tasto).attr("name");
							var input = $("<input>").attr("type", "hidden").attr("name", nome);
							$("#form_conf").append($(input));
							$("#form_conf").submit();
						}
					}
				});
				
			},
			"No": function() {
				$( this ).dialog( "close" );
				var nome=$(tasto).attr("name");
				var input = $("<input>").attr("type", "hidden").attr("name", nome);
				$("#form_conf").append($(input));
				$("#form_conf").submit();
			}
		}
	});		
}

function selez_utente(){
	if ($(this).is(':checked')){	
		$(".checkuser:not(:checked)").attr("disabled",true);
	}
	else{
		$(".checkuser").attr("disabled",false);
	}
}

function set_quantity_to_all(){
	var quant=$("#quant_apply_all").val();
	$(".cl_quant").val(quant);
}

$(document).ready(function () {
	//copio dalla prima riga la quantita' usata e la salvo nell'input dell'Apply all
	var lisquant=$(".cl_quant");
	if(lisquant.length!=0){
		$("#quant_apply_all").val($(lisquant[0]).val());
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
	
	$("#button_apply_all").click(set_quantity_to_all);
	
	$("#quant_apply_all").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			set_quantity_to_all();
		}
	});
	
	var righe=$("#aliq tr.interna");
	var cancella_colonne=true;
	//vedo se sto retrotrascrivendo
	var comple=$("#complem").val();
	if (comple=="True"){
		for(var i=0;i<righe.length;i++){
			//metto nelle rispettive celle il volume e la concentrazione del campione
			var volum=$("#volu_"+i).val();
			var conce=$("#concen_"+i).val();
			$("#volum_"+i).text(volum);
			$("#conc_"+i).text(conce);
			esegui_calcoli(i);
			
			//Metto l'handler sui tasti per calcolare
			var calco="#calc_"+i;
			$(calco).click(calcola_val);
		}
	}
	
	$("#calcall").click(calcola_tutti);
	
	$("#seltutte").click(selez_deselez_tutte);
	//$("#deseltutte").click(deselez_tutte);
	
	$(".exha").click(selez_aliq);
	
	$(".checkuser").click(selez_utente);
	
	$("#conf_all,#next_step").click(function(event){
		//conto le righe della tabella
		var righe=$("#aliq tr.interna");
		var vett_kit=new Array();
		var vett_capa=new Array();
		var regex=/^[0-9.]+$/;
		event.preventDefault();
		//controllo che l'utente abbia premuto il tasto per ricalcolare 
		//i valori
		if (calcola==false){
			alert("You made some changes. Please click on 'Calculate all'");			
			return;
		}
		for(i=0;i<righe.length;i++){
			idquant="#quantity_"+i;
			if((!($(idquant).attr("disabled")))&&(!($(idquant).attr("value")))){
				frase="Insert quantity used in line "+(i+1);
				alert(frase);
				return;
			}
			else{
				numero=$(idquant).attr("value");
				if((!($(idquant).attr("disabled")))&&(!regex.test(numero))){
					frase="You can only insert number. Please correct quantity used in line "+(i+1);
					alert(frase);
					return;
				}
				/*else{
					//verifico che il volume inserito, che è quello da prelevare dalla provetta,
					//non sia piu' alto del volume totale della provetta. Questo solo se il volume
					//del campione non e' nullo
					var volprovetta=$("#volu_"+i).val();
					alert(numero);
					alert(volprovetta);
					if ((volprovetta!="None")&&(parseFloat(numero)>parseFloat(volprovetta))){
						alert("Volume used is higher than sample volume. Please correct value in line "+(i+1));
						event.preventDefault();
						x=1;
					}
				}*/
				//verifico che il valore inserito per la quantita' da caricare all'
				//inizio non superi il valore di max volume
				//solo se il maxvol non e' nullo, cioe' solo se sto facendo una 
				//retrotrascrizione
				var vol_reale=$("#vol_temp_"+i).val();
				var idmaxvol="#maxvol_"+i;
				var maxvol=$(idmaxvol).attr("value");
				if (maxvol!="None"){
					if(parseFloat(vol_reale)>parseFloat(maxvol)){
						alert("Quantity used is higher than protocol 'max volume'. Please correct value in line "+(i+1));
						return;
					}
				}
			}
		}
		
		//se il resto e' tutto a posto controllo che il volume della provetta sia
		//maggiore o uguale a quello che voglio prelevare. Se non e' cosi', faccio
		//inserire all'utente il nuovo volume
		for(i=0;i<righe.length;i++){
			var idquant="#vol_temp_"+i;
			var quantinizi=$(idquant).attr("value");
			var idvolu="#volu_"+i;
			var volu=$(idvolu).attr("value");
			var idesausto="#exhausted_"+i;
			var esausto=$(idesausto).attr("checked");
			//solo se l'aliquota e' derivata
			if ((volu!="None")&&(quantinizi!=undefined)){
				if(quantinizi>0){
					if(esausto!="checked"){
						var ris=parseFloat(volu)-parseFloat(quantinizi);
						if ((ris<0)||(volu<0)){
							val=prompt("Volume for aliquot in line "+(i+1)+" is lower than 'quantity used' you inserted.\n Please insert new aliquot volume value (in ul) or check 'Aliquot Exhausted'");
							if ((val!=null)&&(val!="")){
								$(idvolu).attr("value",val);
								$("#volum_"+i).text(val);
							
								//faccio la post e comunico alla vista il nuovo valore del volume per
								//l'aliq
								var gen="#gen_"+i;
								var genid=$(gen).attr("value");
								var data = {
							    		gen:genid,
							    		valore:val,
							    };
								var url=base_url+"/derived/changevolume/";
								$.post(url, data, function (result) {
		
							    	if (result == "failure") {
							    		alert("Error");
							    	}
							    });
							}
							else{
								return;
							}
						}
					}
				}
				else{					
					alert("Actual load volume has to be greater than 0. Please correct value in line"+(i+1));
					return;
				}
			}
		}
		//conto le righe totali
		var righe=$("#aliq tr.interna");
		var listasel=$(".exha:checked");
		//solo se non ho segnato come esaurite tutte le aliquote
		if (listasel.length<righe.length){
			cambia_utente_provette(this);
		}
		else{
			var nome=$(this).attr("name");
			var input = $("<input>").attr("type", "hidden").attr("name", nome);
			$("#form_conf").append($(input));
			$("#form_conf").submit();
		}
	});
});

