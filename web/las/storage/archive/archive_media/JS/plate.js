blocca=true;

function blocca_campi(){
	var aim=$("#id_aim option:selected").text();
	var tipo=$("#id_Aliquot_Type option:selected").text();

	if (aim=="Working"){
		blocca=false;
		if (tipo=="Viable"){
			//$("#id_x").attr("value","4");
			//$("#id_y").attr("value","6");
			$("#id_cont_tipo option:contains(PlateCostar)").attr("selected","selected");
			$("#id_geometry option:contains(4x6)").attr("selected","selected");
			$("#id_rack,#id_storage,#id_position,#controlla").attr("disabled",true);
			$("#id_file_plate").attr("disabled",true);
		}
		else{
			//$("#id_x").attr("value","8");
			//$("#id_y").attr("value","12");
			$("#id_cont_tipo option:contains(PlateThermoStandard)").attr("selected","selected");
			$("#id_geometry option:contains(8x12)").attr("selected","selected");
			$("#id_rack,#id_storage,#id_barcode,#id_position,#controlla").attr("disabled",true);
			$("#id_file_plate").attr("disabled",false);
		}
	}
	else if(aim=="Transient"){
		//$("#id_x").attr("value","8");
		//$("#id_y").attr("value","12");
		$("#id_cont_tipo option:contains(PlateThermoStandard)").attr("selected","selected");
		$("#id_geometry option:contains(8x12)").attr("selected","selected");
		$("#id_rack,#id_storage,#id_barcode,#id_position,#controlla").attr("disabled",true);
		$("#id_file_plate").attr("disabled",false);
		blocca=false;
	}
	else if(aim=="Archive"){
		//$("#id_x").attr("value","8");
		//$("#id_y").attr("value","12");
		$("#id_cont_tipo option:contains(PlateThermoStandard)").attr("selected","selected");
		$("#id_geometry option:contains(8x12)").attr("selected","selected");
		$("#id_rack,#id_storage,#id_barcode,#id_position,#controlla").attr("disabled",false);
		$("#id_file_plate").attr("disabled",true);
		blocca=true;
	}
	else if (aim=="Extern"){
		//$("#id_x,#id_y").attr("value","9");
		$("#id_cont_tipo option:contains(PlateThermoStandard)").attr("selected","selected");
		$("#id_geometry option:contains(8x12)").attr("selected","selected");
		$("#id_rack,#id_storage,#id_barcode,#id_position,#controlla").attr("disabled",false);
		$("#id_file_plate").attr("disabled",true);
		blocca=true;
	}	
}

function blocca_campi_aliquote(){
	var tipo=$("#id_Aliquot_Type option:selected").text();
	var aim=$("#id_aim option:selected").text();
	if((aim=="Working")&&(tipo=="Viable")){
		//$("#id_x").attr("value","4");
		//$("#id_y").attr("value","6");
		$("#id_cont_tipo option:contains(PlateCostar)").attr("selected","selected");
		$("#id_geometry option:contains(4x6)").attr("selected","selected");
		$("#id_file_plate").attr("disabled",true);
		$("#id_barcode").attr("disabled",false);
	}
	else if((aim=="Working")&&(tipo!="Viable")){
		//$("#id_x").attr("value","8");
		//$("#id_y").attr("value","12");
		$("#id_cont_tipo option:contains(PlateThermoStandard)").attr("selected","selected");
		$("#id_geometry option:contains(8x12)").attr("selected","selected");
		$("#id_file_plate").attr("disabled",false);
		$("#id_barcode").attr("disabled",true);
	}
}

function aggiorna_tipo_container(){
	var tipo=$("#id_cont_tipo option:selected").text();
	if (tipo=="PlateCostar"){
		$("#id_geometry option:contains(4x6)").attr("selected","selected");
		$("#id_Aliquot_Type option:contains(Viable)").attr("selected","selected");
		$("#id_aim option:contains(Working)").attr("selected","selected");
		$("#id_rack,#id_storage,#id_position,#controlla").attr("disabled",true);
		$("#id_file_plate").attr("disabled",true);
		blocca=false;
	}
	else if (tipo=="PlateThermoStandard"){
		$("#id_geometry option:contains(8x12)").attr("selected","selected");
	}
}

function autocompletamento(){
	freezer=$("#id_storage option:selected").val();
	$("#id_rack").autocomplete({
		source:base_url+'/ajax/container/autocomplete/?fr='+freezer
	});
	$("#sect_foto").css("display","none");
	blocca=true;
}

function aggiorna_check(){
	$("#sect_foto").css("display","none");
	blocca=true;
}

function controlla_disp_cont(){
	var fr=$("#id_storage option:selected").val();
	var rack=$("#id_rack").val().trim();
	var pos=$("#id_position").val().trim();
	var tipo_cont=$("#id_cont_tipo option:selected").val();
	var url=base_url+"/api/check_availability/"+fr+"/"+rack+"/None/"+pos+"/"+tipo_cont+"/";
	$.getJSON(url,function(d){
		if(d.data!="errore"){
			if (d.data=="1"){
				$("#foto_contr").attr("src",media_url+"/archive_media/img/ok2.png");
				$("#div_foto").text("Available");
				blocca=false;
			}
			else{
				$("#foto_contr").attr("src",media_url+"/archive_media/img/n_ok.png");
				$("#div_foto").text("Not available");
				blocca=true;
			}
			if(d.data=="err_posizione"){
				alert("Position is inconsistent with container geometry");
			}
			if(d.data=="err_tipo_cont"){
				alert("Selected rack can't contain this container type");
			}
			$("#sect_foto").css("display","");	
		}
	});
}

$(document).ready(function () {
	//se nel form mancano dei dati
	listaerr=$(".errorlist");
	//solo se mancano dei dati nel form
	if(listaerr.length!=0){
		for(i=0;i<4;i++){
			$(".interna").prepend($(".f p:last"));
			$(".interna").prepend($(".f ul:last-child"));
		}
	}
	//se il form e' completo
	else{
		//per far entrare gli ultimi 4 campi del form nella sezione interna che sta a fianco
		//dell'altra
		for(i=0;i<4;i++){
			$(".interna").prepend($(".f p:last"));
		}
	}
	//per modificare il form in modo che si possano inserire piu' file in contemporanea
	$("#id_file_plate").attr("multiple","");
	
	//per inserire il collegamento verso la pagina che spiega come deve essere fatto il file
	url=media_url+"/archive_media/File_Format/Plate.txt";
	$(".f p:nth-child(2)").after("<a style='font-size:1.6em;' id='file' href="+url+" class='anchor' >File Format</a><br><br>");
	$(".anchor").popupWindow({ 
		height:500, 
		width:800, 
		top:50, 
		left:50,
		scrollbars:1,
		resizable:1,
		menubar:1
		}); 
	//riduco la dimensione degli input
	$("input").attr("size","6");
	$("#id_rack").attr("size","20");
	$("#id_barcode").attr("size","10");
	
	//quando si carica la pagina vedo che valori ci sono e agisco di conseguenza
	blocca_campi();
	
	freezer=$("#id_storage option:selected").val();
	//per l'autocompletamento dei rack
	$("#id_rack").autocomplete({
		source:base_url+'/ajax/container/autocomplete/?fr='+freezer
	});
	
	//$("#inizio").draggable().resizable();
	$("#id_aim").change(blocca_campi);
	$("#id_Aliquot_Type").change(blocca_campi_aliquote);
	$("#id_storage").change(autocompletamento);
	$("#controlla").click(controlla_disp_cont);
	$("#id_position,#id_rack").keypress(aggiorna_check);
	$("#id_cont_tipo").change(aggiorna_tipo_container);
	
	$("#conferma_piastra").click(function(event){
		var aim=$("#id_aim option:selected").text();
		if((aim=="Archive")||(aim=="Extern")){
			if(!($("#id_rack").attr("value"))||($("#id_storage option:selected").text()=="---------")||(!($("#id_barcode").attr("value")))){
				alert("You have to insert plate barcode and rack number");
				event.preventDefault();
			}
		}
		if((aim=="Working")||(aim=="Transient")){
			if(!($("#id_file_plate").attr("value"))&&(!($("#id_file_plate").attr("disabled")))){
				alert("You have to load plate file");
				event.preventDefault();
			}
		}
		if((aim=="Working")){
			if($("#id_file_plate").attr("disabled")&&(!($("#id_barcode").attr("value")))){
				alert("You have to insert plate barcode");
				event.preventDefault();
			}
		}
		if(blocca==true){
			alert("Please click on 'Check' button or change position");
			event.preventDefault();
		}
	});
	
});