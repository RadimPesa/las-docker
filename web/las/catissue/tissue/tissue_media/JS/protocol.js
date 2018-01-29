function aggiorna_quantita(){
	var vett=$("#id_result option:selected").text();
	if((vett=="DNA")||(vett=="RNA")||(vett=="Protein")){
		$("label[for='id_load_Quantity']").text("Input:");
		$("#id_max_Volume,#id_l_quant").attr("disabled",true);
		$("#id_max_Volume,#id_l_quant").val("");
		$("#id_unity_measure").show();
	}
	else if((vett=="Complementary DNA")||(vett=="Complementary RNA")){
		$("label[for='id_load_Quantity']").text("Reaction quantity (ug):");
		$("#id_max_Volume,#id_l_quant").attr("disabled",false);
		$("#id_unity_measure").hide();
	}
}

function istruzioni_kit(){
	var nomekit=$("#id_kit option:selected").text();
	url=base_url+"/api/kit/"+nomekit;
	$.getJSON(url,function(d){
		if(d.data!="errore"){
			if((d.data!=null)&&(d.data!="")){
				url="/tissue_media/Kit_instructions/"+d.data;
				$("#Noistr,#file,#primo,#secondo").remove();
				$("#id_kit").after("<br id='primo'><br id='secondo'><a style='font-size:1.6em;' id='file' href="+url+" class='anchor' >Kit Instructions</a>");
				/*$("#file").attr("href",url);
				$("#file").attr("class","anchor");
				$("#file").text("Kit Instructions");*/
				$("#file").attr("onmouseover","tooltip.show('Click for kit instructions');");
				$("#file").attr("onmouseout","tooltip.hide();");
				titolo=$("#file").attr("href"); 
				nome=titolo.split("/");
				x=nome.length;
				t=nome[x-1];
				$(".anchor").popupWindow({
				height:500, 
				width:800, 
				top:50, 
				left:50,
				scrollbars:1,
				resizable:1,
				menubar:1,
				windowName:t
				}); 
			}
			else{
				$("#file,#Noistr,#primo,#secondo").remove();
				$("#id_kit").after("<br id='primo'><br id='secondo'><div id='Noistr' style='font-size:1.6em;'>No instructions available</div>");
			}
		}
		else
			alert("Select a kit");
	});
}

$(document).ready(function () {
	
	//per far apparire piu' elementi nella select con il materiale di partenza
	$("#id_source").attr("size","6");
	
	//serve per mettere il campo per l'unita' di misura del volume da caricare allo stesso livello del campo del volume da caricare
	$("#id_unity_measure").parent().attr("id","par_measure");
	$("label[for=id_load_Quantity]").after("<br><div id='div_temp' style='float:left;'></div><br style='clear:left;'>");
	$("#id_unity_measure,#id_load_Quantity").appendTo($("#div_temp"));
	$("#div_temp").children().css("float","left");
	$("#id_unity_measure").css("margin-left","1em");
	$("#par_measure").remove();	
	
	$("#id_name").attr("size","28");
	$("#id_load_Quantity,#id_max_Volume,#id_exp_Volume,#id_vol_Aliq,#id_conc_Aliq,#id_l_quant").attr("size","4");
	$("#id_num_Aliq").attr("size","1");
	//se nel form mancano dei dati
	listaerr=$(".errorlist");
	//solo se mancano dei dati nel form
	if(listaerr.length!=0){
		for(i=0;i<6;i++){
			$(".interna").prepend($(".f p:last"));
			$(".interna").prepend($(".f ul:last-child"));
		}
	}
	//se il form e' completo
	else{
		//per far entrare gli ultimi 4 campi del form nella sezione interna che sta a fianco
		//dell'altra
		for(var i=0;i<7;i++){
			$(".interna").prepend($(".f p:last"));
		}
	}
	aggiorna_quantita();
	$("#id_name").focus();
	$("#id_result").change(aggiorna_quantita);
	//$("#id_kit").change(istruzioni_kit)
	
	var tabfin=$("#prot_fin");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
		//per il report finale
		generate_result_table("Protocol","prot_fin");
	}
	
	$("#conferma").click(function(event){
		var regex=/^[0-9.]+$/;		
		//controllo la quantita' iniziale
		if($("#id_load_Quantity").attr("value")){
			var quant=$("#id_load_Quantity").attr("value");
			if((!regex.test(quant))){
				alert("You can only insert number. Correct value for input quantity");
				return;
			}
		}
		
		//controllo la quantita' attesa finale
		if($("#id_exp_Volume").attr("value")){
			var expvol=$("#id_exp_Volume").attr("value");
			if((!regex.test(expvol))){
				alert("You can only insert number. Correct value for expected volume");
				return;
			}
		}
		
		//controllo il volume dei derivati
		if($("#id_vol_Aliq").attr("value")){
			var quant=$("#id_vol_Aliq").attr("value");
			if((!regex.test(quant))){
				alert("You can only insert number. Correct value for derived aliquots volume");
				return;
			}
		}
		
		//controllo la concentrazione dei derivati
		if($("#id_conc_Aliq").attr("value")){
			var quant=$("#id_conc_Aliq").attr("value");
			if((!regex.test(quant))){
				alert("You can only insert number. Correct value for derived aliquots concentration");
				return;
			}
		}
		
		//controllo il numero di aliquote derivate da creare
		var regex2=/^[0-9]+$/;
		if($("#id_num_Aliq").attr("value")){
			var quant=$("#id_num_Aliq").attr("value");
			if((!regex2.test(quant))){
				alert("You can only insert number. Correct value for derived aliquots number");
				return;
			}
		}
		
		//controllo la quantita' massima
		if(!($("#id_max_Volume").attr("disabled"))&&($("#id_max_Volume").attr("value"))){
			var maxvol=$("#id_max_Volume").attr("value");
			if((!regex.test(maxvol))){
				alert("You can only insert number. Correct value for max volume.");
				return;
			}
			//se la quantita' da caricare e' maggiore del volume massimo, avverto
			//l'utente
			var quantit=$("#id_load_Quantity").attr("value");
			if(parseFloat(quantit)>parseFloat(maxvol)){
				alert("Quantity load is higher than max volume. Please correct.");
				return;
			}	
		}
		if(!($("#id_max_Volume").attr("disabled"))&&!($("#id_max_Volume").attr("value"))){
			alert("Insert max volume");
			return;
		}
		
		//controllo la quantita' in ul da inserire per le retrotrascrizioni
		if(!($("#id_l_quant").attr("disabled"))&&($("#id_l_quant").attr("value"))){
			var quantreaz=$("#id_l_quant").attr("value");
			if((!regex.test(quantreaz))){
				alert("You can only insert number. Correct value for reaction volume");
				return;
			}	
		}
		if(!($("#id_l_quant").attr("disabled"))&&!($("#id_l_quant").attr("value"))){
			alert("Insert reaction volume");
			return;
		}
		//controllo l'unicita' del nome del protocollo
		var nomeprot=$("#id_name").val();
		if($.inArray(nomeprot,lisprotocol)!=-1){
			alert("Protocol name already present. Please change it.");
			return;
		}
		
		$("#id_max_Volume,#id_l_quant").attr("disabled",false);
		$("#formdati").submit();
	});
});
