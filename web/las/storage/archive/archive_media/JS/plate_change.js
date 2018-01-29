//dizionario con chiave il tipo generico e valore la lista di tipi cont
var diztipigen={};
//dizionario con chiave il cont e valore il dizionario con i dati delle sue caratteristiche vecchie
var dizcontinfo={};
//dizionario con chiave il cont e valore il dizionario con i dati delle sue caratteristiche nuove
var dizinfonuove={};
//per tenere traccia del cont caricato
var barccaricato="";
var contacont=1;

function selezionatutto(){
	if ($(this).attr("sel")=="s"){
		$(this).val("Select all");
		$("#id_Aliquot_Type option").removeAttr("selected");
		$(this).removeAttr("sel");
	}
	else{
		$(this).val("Deselect all");
		$("#id_Aliquot_Type option").attr("selected","selected");
		$(this).attr("sel","s");
	}
}

function aggiorna_geom(){
	//faccio comparire la giusta geometria
	var righ=$("#id_tipi option:selected").attr("rows");
	var col=$("#id_tipi option:selected").attr("col");
	$("#id_row").val(righ);
	$("#id_col").val(col);
}

//quando si seleziona un generic container, fa comparire i cont tipi collegati
function aggiorna_tipi_cont(tipocont){
	var tipo_generico=$("#id_generic option:selected").val();
	if(tipo_generico!=""){
		if (tipo_generico in diztipigen){
			var lista=diztipigen[tipo_generico];
			aggiorna_tipi(lista,tipocont);
		}
		else{
			var url=base_url+"/api/generic/type/"+tipo_generico+"/";
			$.getJSON(url,function(d){
				if(d.data!="errore"){					
					var lista=d.data;
					diztipigen[tipo_generico]=lista;
					aggiorna_tipi(lista,tipocont);
				}
			});
		}
	}
}

function aggiorna_tipi(lista,tipocont){
	$("#id_tipi option").not(":first").remove();
	for(var i=lista.length-1;i>=0;i--){
		//mi occupo della geometria
		var geom=lista[i].idGeometry.toString();
		var geo=geom.split("x");
		var righe=geo[0];
		var col=geo[1];
		var stringa="<option value="+lista[i].id+" rows="+righe+" col="+col+" >"+lista[i].actualName+"</option>"
		$("#id_tipi option[value=\"\"]").after(stringa);
	}
	if (tipocont!=null){
		$("#id_tipi option[value='"+tipocont+"']").attr("selected","selected");
	}
}

function carica_container(){
	if ($("#barcodecont").val() == "")
		alert("Please insert container barcode");
	else{
		var codice=$("#barcodecont").val().trim();
		if(codice in dizcontinfo){
			d=dizcontinfo[codice];
			carica_container2(d,codice);
		}
		else{
			var timer = setTimeout(function(){$("body").addClass("loading");},500);
			var url=base_url+"/api/get/infocontainer/"+codice+"/";
			$.getJSON(url,function(d){
				carica_container2(d,codice);
				dizcontinfo[codice]=d;
				clearTimeout(timer);
		    	$("body").removeClass("loading");
			});
		}
	}
}

function carica_container2(d,codice){
	if(d.data=="inesist"){
		alert("Container does not exist");
		$("#insert").attr("disabled",true);
	}
	else if(d.data=="pieno"){
		alert("Container is not empty. You cannot change its features");
		$("#insert").attr("disabled",true);
	}
	else{
		var dizgen=JSON.parse(d.diz);
		var diz=dizgen[codice];
		var tipogen=diz["generic"];
		$("#id_generic option[value='"+tipogen+"']").attr("selected","selected");
		var tipocont=diz["type"];
		aggiorna_tipi_cont(tipocont);
		var laliq=diz["aliq"];
		$("#id_Aliquot_Type option").removeAttr("selected");
		$("#seltutto").val("Select all");
		$("#seltutto").removeAttr("sel");
		for(var i=0;i<laliq.length;i++){
			$("#id_Aliquot_Type option[value='"+laliq[i]+"']").attr("selected","selected");
		}
		var lisnonselez=$("#id_Aliquot_Type option").not(":selected");
		if(lisnonselez.length==0){
			$("#seltutto").val("Deselect all");
			$("#seltutto").attr("sel","s");
		}
		var row=diz["row"];
		$("#id_row").val(row);		
		var col=diz["col"];
		$("#id_col").val(col);
		var mono=diz['monouso'];
		$("#id_use").removeAttr("checked");
		if(mono){
			$("#id_use").attr("checked","checked");
		}
		$("#insert").attr("disabled",false);
		barccaricato=codice;
	}
}

function inserisci_container(){
	//devo vedere se sono stati inseriti tutti i dati
	var regex=/^[0-9]+$/;
	var tab2=$("#cont_table").dataTable();
	
	var tipi=$("#id_tipi option:selected").val();
	if(tipi==""){
		alert("Select container type");
		return;
	}
	
	var lisaliq=$("#id_Aliquot_Type option:selected");
	if (lisaliq.length==0){
		alert("Select biological content");
		return;
	}
	//guardo se sono state inserite le colonne
	var colo=$("#id_col").val();
	if(colo==""){
		alert("Insert columns number");
		return;
	}
	else{
		if((!regex.test(colo))||(colo=="0")){
			alert("You can only insert number. Please correct columns value");
			return;
		}
	}
	//guardo se sono state inserite le righe
	var rig=$("#id_row").val();
	if(rig==""){
		alert("Insert rows number");
		return;
	}
	else{
		if((!regex.test(rig))||(rig=="0")){
			alert("You can only insert number. Please correct rows value");
			return;
		}
	}
	//guardo se il padre puo' contenere quelle aliquote
	var d=dizcontinfo[barccaricato];
	var dizgen=JSON.parse(d.diz);
	var diz=dizgen[barccaricato];
	var lispadretmp=diz["aliqpadre"].toString();
	var lispadre=lispadretmp.split(",");
	var lisaliq=$("#id_Aliquot_Type option:selected");
	for(var i=0;i<lisaliq.length;i++){
		var id=$(lisaliq[i]).val();
		if($.inArray(id,lispadre)==-1){
			alert("Father container cannot support biological content you chose");
			return;
		}
	}
	
	//guardo se il padre puo' contenere quel tipo di cont
	var lispadretmp=diz["tipipadre"].toString();
	var lispadre=lispadretmp.split(",");
	var ltipi=$("#id_tipi option:selected");
	for(var i=0;i<ltipi.length;i++){
		var id=$(ltipi[i]).val();
		if($.inArray(id,lispadre)==-1){
			alert("Father container cannot support container type you chose");
			return;
		}
	}
		
	var tipo=$("#id_tipi option:selected").text();
	var geom=rig+"x"+colo;
	var monouso=String($("#id_use").is(":checked"));
	var disp=monouso.charAt(0).toUpperCase() + monouso.substring(1);
	
	var tipialiqabbr="";
	var tipialiqid="";
	for(var i=0;i<lisaliq.length;i++){
		var abbr=$(lisaliq[i]).attr("abbr");
		var id=$(lisaliq[i]).attr("value");
		tipialiqabbr+=abbr+"-";
		tipialiqid+=id+"-";
	}
	tipialiqabbr = tipialiqabbr.substring(0, tipialiqabbr.length - 1);
	tipialiqid = tipialiqid.substring(0, tipialiqid.length - 1);
	
	if(barccaricato in dizinfonuove){
		var diztemp=dizinfonuove[barccaricato];
		var pos=diztemp["postabella"];
		//per aggiornare il contenuto di una cella (nuovo valore, riga,colonna)
		tab2.fnUpdate(tipo,pos,2);
		tab2.fnUpdate(tipialiqabbr,pos,3);
		tab2.fnUpdate(geom,pos,4);
		tab2.fnUpdate(disp,pos,5);
	}
	else{
		var postmp=tab2.fnAddData( [contacont,barccaricato, tipo,tipialiqabbr,geom,disp] );
		var pos=postmp[0];
		contacont++;
	}
	
	//creo il dizionario con i dati dentro
	var diz={};
	diz["conttipo"]=tipi;
	diz["geometry"]=geom;
	diz["aliqabbr"]=tipialiqabbr;
	diz["aliqid"]=tipialiqid;
	diz["uso"]=disp;
	diz["postabella"]=pos;
	dizinfonuove[barccaricato]=diz;	
	
	$("#conferma").attr("disabled",false);
	$("#barcodecont").val("");
}

$(document).ready(function () {
	var oTable = $("#cont_table").dataTable( {
        "bProcessing": true,
         "aoColumns": [
			{ "sTitle": "ID Operation" },
            { "sTitle": "Barcode" },
            { "sTitle": "Type" },
            { "sTitle": "Biological content" },
            { "sTitle": "Geometry" },
            { "sTitle": "Disposable" },
        ],
	    "bAutoWidth": false ,
	    "aaSorting": [[0, 'desc']],
	    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
    });
	
	var spinner = $("#id_col,#id_row").spinner(
	{
		min:1,
		max:1000
	});
	
	//per il tasto che seleziona tutti i tipi di aliquota
	$("#seltutto").click(selezionatutto);
	//per aggiornare i tipi di container dato il tipo generico
	$("#id_generic").change(function(){
		aggiorna_tipi_cont(null);
	});
	//dato un barcode carica le informazioni associate
	$("#loadcont").click(carica_container);
	//per aggiornare la geometria in base al tipo cont scelto
	$("#id_tipi").change(aggiorna_geom);
	
	$("#insert").click(inserisci_container);
	
	$("#barcodecont").keypress(function(event){
		//13 e' il codice ASCII del CRLF
		if ( event.which == 13 ) {
			carica_container();
		}
	});
	
	$("#id_Aliquot_Type").attr("size","7");
	
	$("#conferma").click(function(event){
		event.preventDefault();		
		var data = {
			salva:true,
			dati:JSON.stringify(dizinfonuove),
	    };
		var url=base_url+"/plate/change/";
		$.post(url, data, function (result) {
	    	if (result == "failure") {
	    		alert("Error");
	    	}
	    	$("#form_fin").append("<input type='hidden' name='final' />");
	    	$("#form_fin").submit();
	    });
	});	
});
