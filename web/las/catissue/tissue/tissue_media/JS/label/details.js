//lista con i barc caricati manualmente dalla schermata di esecuzione che permette di eseguire senza pianificare
var listavetrini=[];
var colors = {};
var contaaliq=1;
//diz con chiave gen|posizione e come valore un diz con tutte le caratteristiche del protocollo con i vari marker
var dizfin={}

function inizializza(){
	//tutte le tabelle hanno come id rna e come attributo plate il codice. Metto quest'ultimo come id
	var listabelle=$("table[plate]");
	if (listabelle.length>0){
		$("#posiz").css("display","");
		for (var i=0;i<listabelle.length;i++){
			var barc=$(listabelle[i]).attr("plate");
			$(listabelle[i]).attr("id",barc);
			$(listabelle[i]).find("th").text("Barcode: "+barc);
			$(listabelle[i]).addClass("tabvetrini");
		}
		
		$(".tabvetrini td").attr("align","center");
		$(".tabvetrini td,.tabvetrini th").css("border","1px solid black");
		$(".tabvetrini th").css("padding","5px");
		$(".tabvetrini").attr("align","left");
		//per cancellare il br che c'e' prima della lettere nell'intestazione delle righe
		$(".tabvetrini br").remove();
		//$(".tabvetrini button[sel=\"s\"]").attr("disabled",false);
		$(".tabvetrini button").not("[sel]").attr("disabled",true);
		//mi occupo del tooltip
		var listabutton=$(".tabvetrini button[sel=\"s\"]");
		for(var i=0;i<listabutton.length;i++){
			var gen=$(listabutton[i]).attr("gen");
			var fr="tooltip.show(\""+gen+"\")";
			$(listabutton[i]).parent().attr("onmouseover",fr);
			$(listabutton[i]).parent().attr("onmouseout","tooltip.hide()");
		}
		//abilito tutti i tasti i cui gen sono contenuti nella lista con i gen pianificati
		for (var j=0;j<listagen.length;j++){
			$(".tabvetrini button[gen='"+listagen[j]+"']").attr("disabled",false);
		}
	}		
}

function aggiungi_aliquota(){
	//genealogy ID dell'aliquota da inserire
	gen=$("#id_valid_barc").attr("value");
	if(gen==""){
		alert("Insert a genealogy ID or barcode");
	}
	else{
		var codice=gen.replace(/#/g,"%23");

		var url=base_url+"/api/label/aliquot/"+codice+"/save";
		$.getJSON(url,function(d){
			if(d.data!="errore"){
				if(d.data=="inesistente"){
					alert("Aliquot does not exist in storage");
				}				
				else if(d.data=="tipoerr"){
					alert("Aliquot type is incompatible with this procedure");
				}
				else if(d.data=="presente"){
					alert("Aliquot is already scheduled for this procedure");
				}
				else{
					var trovato=0;
					//in d.data ho una lista con genid|barcode|posizione
					var lisvalori=d.data;
					//confronto i genid che ci sono gia' nella lista generale con quello
					//nuovo e se c'e' gia' non lo inserisco nella tabella
					for (var j=0;j<lisvalori.length;j++){
						trovato=0;
						var val=lisvalori[j].split("|");
						var gen=val[0];
						//inserisco i nuovi gen nella lista riepilogativa che serve a disabilitare sui vetrini i gen non pianificati
						listagen.push(gen);
						var barc=val[1];
						//solo se non l'ho gia' caricato
						if($.inArray(barc,listavetrini)==-1){
							//prendo il tipo dell'aliquota dal gen. Puo' essere solo PS o OS perche' gli altri tipi
							//li ho gia' scremati prima
							var aliqtipo=gen.substring(20,22);
							var url=base_url+"/api/generic/load/"+barc+"/"+aliqtipo+"/plate";
							$.getJSON(url,function(d){
								if(d.data!="errore"){
									var codhtml=d.data.substring(0,(d.data.length)-12);
									$("#posiz").append(codhtml);
									$("#posiz").append("<br style='clear:left;'><br>");
									inizializza();
								}
							});
							listavetrini.push(barc);
						}
					}
					$("#id_valid_barc").val("");
					$("#id_valid_barc").focus();
				}
			}
		});
	}
}

//quando scelgo un protocollo dal menu' a tendina, devo far comparire le informazioni relative ai marker
//di quel protocollo
function seleziona_protocollo(){
	var idprot=$("#id_protoc option:selected").val();
	var lismarker=dizgen[idprot]["marker"];
	$("#infomarker").empty();
	var nometecnica=dizgen[idprot]["tecnica"];
	var stringa="<tr><td colspan='"+String(lismarker.length)+"' align='center' ><b>Technique: </b>"+nometecnica+"</td</tr><tr>";
	//scandisco la lista dei marker
	for(var i=0;i<lismarker.length;i++){
		var elem=lismarker[i];
		var diluizione=elem["Dilution"];
		if (diluizione!=""){
			var dil=diluizione.split(":");			
		}
		else{
			var dil=["1",""];
		}
		var dizfeatmark=dizmarkfeature[elem["type"]];
		//ho un dizionario con nome e unita' di misura delle feature relative al tempo e alla temperatura
		var tempo=dizfeatmark["time"]["name"];
		var unitatempo=dizfeatmark["time"]["unit"];
		var temperat=dizfeatmark["temperature"]["name"];
		var unitatemperat=dizfeatmark["temperature"]["unit"];
		stringa+="<td><table border='1px solid black' style='width:100%;' ><tr><td><b>Name:</b></td><td class='markname'>"+elem["name"]+"</td></tr><tr><td><b>Type:</b></td><td class='typename'>"+elem["type"]+"</td></tr>" +
			"<tr><td><b>Producer:</b></td><td><input id='id_producer_"+String(i)+"' type='text' class='produt' maxlength='20' size='7' value='"+elem["Producer"]+"' ></td></tr>" +
			"<tr><td><b>Catalogue number:</b></td><td><input id='id_catalogue_"+String(i)+"' type='text' class='catalogo' maxlength='20' size='7' value='"+elem["Catalogue number"]+"' ></td></tr>"+
			"<tr><td><b>Dilution factor:</b></td><td><input id='id_dilution_sin_"+String(i)+"' type='number' class='diluizsin' style='display:inline;width:5em;' value='"+dil[0]+"' max='100' min='1' size='3'>:"+ 
			"<input id='id_dilution_dx_"+String(i)+"' type='number' style='display:inline;width:5em;' class='diluizdx' value='"+dil[1]+"' max='1000000' min='1' size='3'></td></tr>"+
			"<tr><td><b>"+tempo+" ("+unitatempo+"):</b></td><td><input id='id_time_"+String(i)+"' type='text' class='tempo' maxlength='10' size='7' value='"+elem[tempo]+"' ></td></tr>"+
			"<tr><td><b>"+temperat+" ("+unitatemperat+"):</b></td><td><input id='id_temp_"+String(i)+"' type='text' class='temperatura' maxlength='10' size='7' value='"+elem[temperat]+"' ></td></tr>";
		//se non e' istologia devo aggiungere un campo per il canale o per l'agente rivelatore
		if(nometecnica!="Histology"){
			var lista=dizcanali[nometecnica];
			if((nometecnica=="IHC")||(nometecnica=="CISH")){
				var label="Staining";
			}
			else{
				var label="Channel";
			}
			stringa+="<tr><td><b>"+label+":</b></td><td><select id='id_technique_"+String(i)+"' class='canale' ><option value='' >---------</option>";
			for(var j=0;j<lista.length;j++){
				stringa+="<option value='"+lista[j]["id"]+"' >"+lista[j]["name"]+"</option>";
			}
			stringa+="</select></td></tr>";
		}
		stringa+="</table></td>";
	}
	stringa+="</tr>";
	$("#infomarker").append(stringa);
}

function generateRandomColor(idprot){
    var correctionFactor = 0;
    while (true){
	console.log('Generating color with correctionFactor = ',correctionFactor);
        var i = Math.floor(Math.random() * 50);
        var r = Math.sin(0.3*i + 0) * 127 +128;
        var g = Math.sin(0.3*i + 2) * 127 +128;
        var b = Math.sin(0.3*i + 4) * 127 +128;

        var tempColor = RGB2Color(r,g,b);
        var flag = true;
        $.each(colors, function (key, value){
            //console.log(value);
            var diff = Math.abs(r - parseInt(value.substring(1,3), 16)) + Math.abs(g - parseInt(value.substring(3,5), 16)) + Math.abs(b - parseInt(value.substring(5,7), 16));
            if (diff < 60 - correctionFactor){
                flag = false;
            }
        });
        if (flag){
            colors[idprot]= RGB2Color(r,g,b);//getHex(r,g,b);
            break;
        } else {
            // if you get here, try to increment correctionFactor
	    correctionFactor += 10;
	}
    }
}

function RGB2Color(r,g,b){
    return '#' + byte2Hex(r) + byte2Hex(g) + byte2Hex(b);
}

function byte2Hex(n){
    var nybHexString = "0123456789ABCDEF";
    return String(nybHexString.substr((n >> 4) & 0x0F,1)) + nybHexString.substr(n & 0x0F,1);
}

//per inserire i valori nel dizionario finale da inviare poi alla schermata
function riempi_dizionario(genid,idprot,pos,codvetrino){
	//prendo i valori dei marker
	var lismark=$(".markname");
	var diztemp={};
	for (var i=0;i<lismark.length;i++){
		var dizmark={};
		var nomemark=$(lismark[i]).text();
		var tipomark=$($(lismark[i]).parent().parent().find(".typename")).text();
		var prod=$($(lismark[i]).parent().parent().find(".produt")).val();
		var catalogo=$($(lismark[i]).parent().parent().find(".catalogo")).val();
		var dilsin=$($(lismark[i]).parent().parent().find(".diluizsin")).val();
		var dildx=$($(lismark[i]).parent().parent().find(".diluizdx")).val();
		var tempo=$($(lismark[i]).parent().parent().find(".tempo")).val();
		var temperatura=$($(lismark[i]).parent().parent().find(".temperatura")).val();
		var tecn=dizgen[idprot]["tecnica"];
		dizmark["Producer"]=prod;
		dizmark["Catalogue number"]=catalogo;
		dizmark["Dilution"]=dilsin+":"+dildx;
		var nometempo=dizmarkfeature[tipomark]["time"]["name"];
		dizmark[nometempo]=tempo;
		var nometemperat=dizmarkfeature[tipomark]["temperature"]["name"];
		dizmark[nometemperat]=temperatura;
		if(tecn!="Histology"){
			var prod=$(lismark[i]).parent().parent().find(".canale");
			var idcanale=$($(prod).children(":selected")).text();
			dizmark[idcanale]="";
		}
		diztemp[nomemark]=dizmark;
	}
	//prendo il protocollo selezionato che e' quello di base che ho scelto e da cui sono partito
	//per impostare i valori dei vari parametri. Ho l'id del protocollo.
	var prot=$("#id_protoc option:selected").val();
	dizfin[genid+"|"+codvetrino+"|"+pos+"|"+prot]=diztemp;
}

//viene eseguita quando clicco su un posto di un vetrino e mi assegna il campione a quel protocollo
function assegna_protocollo(button){
	var idprot=$("#id_protoc option:selected").val();
	if(idprot!=""){
		if(controlla_valori(idprot)){
			//e' il codice esadecimale del colore
			var colore=colors[idprot];
			$(button).css("background-color",colore);
			$(button).attr("disabled",true);
			//rimuovo l'attributo sel altrimenti se caricassi un altro vetrino me lo riattiverebbe
			$(button).removeAttr("sel");
			var codvetrino=$(button).parent().parent().parent().parent().attr("plate");
			var pos=$(button).attr("pos");
			var nomeprot=$("#id_protoc option:selected").text();
			var genid=$(button).attr("gen");
			$("#aliquots_table").dataTable().fnAddData( [null, contaaliq, genid, codvetrino, pos, nomeprot] );
			contaaliq++;
			riempi_dizionario(genid,idprot,pos,codvetrino);
			//tolgo dalla lista dei gen pianificati questo che ho assegnato adesso
			for (var i=0; i < listagen.length; i++){
		        if (listagen[i] == genid){
		        	listagen.splice(i,1);
		        }
		    }
		}
	}
	else{
		alert("Please select a protocol");
	}
}

function deleteAliquot(genID,barc,pos){
	var button=$("#"+barc).find("button[gen='"+genID+"']");
	$(button).css("background-color","rgb(249, 248, 242)");
	$(button).attr("disabled",false);
	$(button).attr("sel","s");
	//cancello dal dizionario generale il campione eliminato
	var chiave=genID+"|"+barc+"|"+pos;
	if(chiave in dizfin){
		delete dizfin[chiave];
	}
	if($.inArray(genID,listagen)==-1){
		listagen.push(genID);
	}
}

//per vedere se sono stati completati tutti i campi dei marker di quel protocollo
function controlla_valori(idprot){
	var regex=/^[0-9]+$/;
	var regex2=/^[0-9.]+$/;	
	
	var lisprod=$(".produt");
	for (var i=0;i<lisprod.length;i++){
		var valore=$(lisprod[i]).val();
		if(valore==""){
			var nomemark=$(lisprod[i]).parent().parent().parent().find(".markname").text();
			alert("Please insert producer for "+nomemark);
			return false;
		}
	}
	var lista=$(".catalogo");
	for (var i=0;i<lista.length;i++){
		var valore=$(lista[i]).val();
		if(valore==""){
			var nomemark=$(lista[i]).parent().parent().parent().find(".markname").text();
			alert("Please insert catalogue number for "+nomemark);
			return false;
		}
	}
	var lista=$(".diluizsin,.diluizdx");
	for (var i=0;i<lista.length;i++){
		var valore=$(lista[i]).val();
		var nomemark=$(lista[i]).parent().parent().parent().find(".markname").text();
		if(valore==""){			
			alert("Please insert dilution factor for "+nomemark);
			return false;
		}
		if(!regex.test(valore)){
			alert("You can only insert number. Please correct value for dilution factor of "+nomemark);
			return false;
		}
	}
	var lista=$(".tempo");
	for (var i=0;i<lista.length;i++){
		var valore=$(lista[i]).val();
		var nomemark=$(lista[i]).parent().parent().parent().find(".markname").text();
		if(valore==""){			
			alert("Please insert time for "+nomemark);
			return false;
		}
		//il tempo puo' accettare valori decimali perche' e' espresso in ore
		if(!regex2.test(valore)){
			alert("You can only insert number. Please correct value for time of "+nomemark);
			return false;
		}
	}
	var lista=$(".temperatura");
	for (var i=0;i<lista.length;i++){
		var valore=$(lista[i]).val();
		var nomemark=$(lista[i]).parent().parent().parent().find(".markname").text();
		if(valore==""){			
			alert("Please insert temperature for "+nomemark);
			return false;
		}
		if(!regex.test(valore)){
			alert("You can only insert number. Please correct value for temperature of "+nomemark);
			return false;
		}
	}
	var tecn=dizgen[idprot]["tecnica"];	
	if(tecn!="Histology"){
		var lista1=$(".canale");
		var lista2=$(".canale option:selected");
		for (var i=0;i<lista2.length;i++){
			var valore=$(lista2[i]).val();
			if(valore==""){
				var listipogenerico=$(lista1[i]).parent().siblings();
				var nometipogenerico=$(listipogenerico[0]).text().toLowerCase();
				nometipogenerico=nometipogenerico.substring(0,nometipogenerico.length-1);
				var nomemark=$(lista1[i]).parent().parent().parent().find(".markname").text();
				alert("Please insert "+nometipogenerico+" for "+nomemark);
				return false;
			}
		}
	}
	return true;
}

//scatta quando seleziono una tecnica dal menu'. Serve per far vedere nel menu' dei protocolli solo quelli
//legati alla tecnica scelta
function filtra_protocolli(){
	var tecnica=$("#id_tech option:selected").val();
	var listaprot=diztecnica[tecnica];
	//nascondo tutti i protocolli e poi faccio vedere solo quelli legati a quella tecnica
	$("#id_protoc option[value!='']").css("display","none");
	for (var i=0;i<listaprot.length;i++){
		$("#id_protoc option[value='"+listaprot[i]+"']").css("display","");
	}
	$("#id_protoc option[value='']").attr("selected","selected");
	$("#infomarker").empty();
}

//restituisce le dimensioni di un dict
Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};

$(document).ready(function () {
	var tabfin=$("#aliquote_fin");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
    	generate_result_table("Slide_labelling","aliquote_fin");
	}
	else{
		inizializza();
		
		//devo popolare il select con dentro le tecniche
		var stringa="";
		for (var k in diztecnica){
			stringa+="<option value="+k+" >"+k+"</option>";
		}
		$("#id_tech").append(stringa);
		
		var oTable = $("#aliquots_table").dataTable({
	        "bProcessing": true,
	         "aoColumns": [
	            { 
	               "sTitle": null, 
	               "sClass": "control_center", 
	               "sDefaultContent": "<img src='"+media_url+"/tissue_media/img/admin/icon_deletelink.gif' width='15px' height='15px' >"               
	            },
	            { "sTitle": "ID Operation" },
	            { "sTitle": "Genealogy ID" },
	            { "sTitle": "Slide barcode" },
	            { "sTitle": "Position" },
	            { "sTitle": "Protocol" }
	        ],
		    "bAutoWidth": false ,
		    "aaSorting": [[1, 'desc']],
		    "aoColumnDefs": [
		        { "bSortable": false, "aTargets": [ 0 ] },
		    ],
		    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
	    });
	}
	
	$("#id_valid_barc").autocomplete({
	    source: function(request, response) {	    	
    		var diz={
	                term: request.term,
	                WG:workingGroups,
	                label:"Yes"
	        };
	        $.ajax({
	            url: base_url+'/ajax/derived/autocomplete/',
	            dataType: "json",
	            data: diz,
	            success: function(data) {
	                response(data);
	            }
	        });
	    },
    });
	
	$("#validate_barc").click(aggiungi_aliquota);
	$("#id_valid_barc").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			aggiungi_aliquota();
		}
	});
	
	$("#id_tech").change(filtra_protocolli);
	
	$("#id_protoc").change(seleziona_protocollo);
	//prendo la lista dei protocolli tranne il primo valore del select che e' quello con ---
	var lisprot=$("#id_protoc option[value!='']");
	for (var i=0;i<lisprot.length;i++){
		var id=$(lisprot[i]).val();
		generateRandomColor(id);
	}
	
	$(".tabvetrini button[sel=\"s\"]").live("click", function () {
		assegna_protocollo(this);
	});
	
	$("#aliquots_table tbody td.control_center img").live("click", function () {
		var genID = $($($(this).parents('tr')[0]).children()[2]).text();
        var barc = $($($(this).parents('tr')[0]).children()[3]).text();
        var pos = $($($(this).parents('tr')[0]).children()[4]).text();
        deleteAliquot(genID,barc,pos);
        var nTr = $(this).parents('tr')[0];
        $("#aliquots_table").dataTable().fnDeleteRow( nTr );
    });
	
	//quando clicco sul pulsante submit
    $("#finish,#next").click(function(event){
    	event.preventDefault();
    	if (Object.size(dizfin) > 0){
    		var idtasto=$(this).attr("id");
	    	var timer = setTimeout(function(){$("body").addClass("loading");},500);	    	
	    	//comunico la struttura dati al server
	    	var data = {
	    			salva:true,
	    			dati:JSON.stringify(dizfin)	    		
		    };
			var url=base_url+"/label/execute/save/";
			$.post(url, data, function (result) {
		    	if (result == "failure") {
		    		alert("Error");
		    	}
		    	clearTimeout(timer);
		    	$("body").removeClass("loading");
		    	//se e' next passo alla schermata di caricamento dei file
		    	if(idtasto=="next"){
		    		$("#form_fin").append("<input type='hidden' name='next' />");
		    	}
		    	else{
		    		$("#form_fin").append("<input type='hidden' name='final' />");
		    	}
		    	$("#form_fin").submit();
		    });
    	}
    	else{
    		alert("Please select some aliquots to label");
    	}
	});
});
