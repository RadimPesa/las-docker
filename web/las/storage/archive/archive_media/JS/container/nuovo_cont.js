blocca=true;

function aggiorna_freezer(){
	var tipo_cont=$("#id_cont_tipo option:selected").text();
	var url=base_url+"/api/insert_cont/"+tipo_cont+"/";
	$.getJSON(url,function(d){
		if(d.data!="errore"){
			$("#id_freezer option").not(":first").remove();
			var lista=d.data.split(";");
			for(i=lista.length;i>1;i--){
				var k=i-2;
				var val=lista[i-2].split(":");
				//in val[0] ho l'id, in val[1] ho il barcode
				var stringa="<option value="+val[0]+">"+val[1]+"</option>"
				$("#id_freezer option[value=\"\"]").after(stringa);
			}
		}
	});
}

function controlla_disp_cont(){
	var fr=$("#id_freezer option:selected").val();
	var piastra=$("#id_plate").val();
	var tipo_cont=$("#id_cont_tipo option:selected").val();
	var nome_tipo_cont=$("#id_cont_tipo option:selected").text();
	if (piastra==undefined){
		piastra="None";
	}
	else{
		piastra=piastra.trim();
	}
	var pos=$("#id_position").val().trim();
	if(pos==""){
		pos="None";
	}	
	//se salvo una biocassetta aggiungo alla pos un identificatore che nella
	//API mi faccia poi capire che sto aggiungendo una biocas e non una provetta
	else if ((nome_tipo_cont=="FF")||(nome_tipo_cont=="OF")||(nome_tipo_cont=="CH")){
		pos=pos+"&BIOC";
	}
	var url=base_url+"/api/check_availability/"+fr+"/None/"+piastra+"/"+pos+"/"+tipo_cont+"/";
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
			if(d.data=="inesist"){
				alert("Plate/Drawer doesn't exist in storage");
			}
			if(d.data=="err_posizione"){
				alert("Position is inconsistent with container geometry");
			}
			if(d.data=="err_tipo_cont"){
				alert("Selected Plate/Drawer can't contain this container type");
			}
			$("#sect_foto").css("display","");	
		}
	});
}

function aggiorna_check(){
	$("#sect_foto").css("display","none");
	blocca=true;
}

$(document).ready(function () {
	
	//vedo se e' presente il campo freezer per capire se sto inserendo un rack
	var freezer=$("#id_freezer");
	if (freezer.length!=0){
		$("#id_cont_tipo").change(aggiorna_freezer);
	}
	
	$("#controlla").click(controlla_disp_cont);
	$("#id_position,#id_plate").keypress(aggiorna_check);
	$("#id_freezer,#id_cont_tipo").change(aggiorna_check);
	
	
	//vedo se e' presente il campo plate per capire se sto inserendo una singola provetta
	//Imposto quindi la geometria a 1x1
	var piastra=$("#id_plate");
	if (piastra.length!=0){
		var elem=$("#id_geom option:contains(1x1)")[0];
		$(elem).attr("selected","selected");
	}
	
	$("#conferma_tutto").click(function(event){
		if($("#id_barcode").val()==""){
			alert("You have to insert container barcode");
			event.preventDefault();
		}
		
		var cont=$("#id_cont_tipo option:selected").text();
		if(cont=="---------"){
			alert("You have to select a container type");
			event.preventDefault();
		}
		var geom=$("#id_geom option:selected").text();
		if(geom=="---------"){
			alert("You have to select a geometry");
			event.preventDefault();
		}
		//vedo se � presente il campo freezer e se � vuoto
		var fr=$("#id_freezer option:selected").text();
		if((fr!="")&&(fr=="---------")){
			alert("You have to select a freezer");
			event.preventDefault();
		}
		//vedo se il campo posizione c'� e se � vuoto
		var pos=$("#id_position").val();
		if((pos!=undefined)&&(pos=="")&&!($("#id_position").attr("disabled"))){
			alert("You have to insert position");
			event.preventDefault();
		}
		//se sono nella schermata di inserimento freezer e non c'e' il tasto check
		var cont=$("#controlla");
		if (cont.length==0){
			blocca=false;
		}
		if(blocca==true){
			alert("Please click on 'Check' button or change position");
			event.preventDefault();
		}
	});
});