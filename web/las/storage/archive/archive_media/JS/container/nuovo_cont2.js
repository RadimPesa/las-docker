//e' una lista di dizionari, in cui ogni diz e' un container nuovo
var listagen=[];
//e' un dizionario con chiave il barcpadre e come valore la sua struttura in html
var dizpadri={};
var contacont=1;

function aggiorna_tipi_cont(){
	var tipo_generico=$("#id_generic option:selected").val();
	if(tipo_generico!=""){
		var url=base_url+"/api/generic/type/"+tipo_generico+"/";
		$.getJSON(url,function(d){
			if(d.data!="errore"){
				$("#id_tipi option").not(":first").remove();
				var lista=d.data;
				for(var i=lista.length-1;i>=0;i--){
					//mi occupo della geometria
					var geom=lista[i].idGeometry.toString();
					var geo=geom.split("x");
					var righe=geo[0];
					var col=geo[1];
					var oneUse=lista[i].oneUse.toString();
					var stringa="<option value="+lista[i].id+" rows="+righe+" col="+col+" oneuse="+oneUse+" >"+lista[i].actualName+"</option>"
					$("#id_tipi option[value=\"\"]").after(stringa);
				}
			}
		});
	}
}

function autocompletamento(){
	var tip=$("#id_tipi option:selected").val();
	$("#id_father").autocomplete({
		source:base_url+'/ajax/container/autocomplete/?tipo='+tip
	});
	$("#id_father").attr("disabled",false);
	//faccio comparire la giusta geometria
	var righ=$("#id_tipi option:selected").attr("rows");
	var col=$("#id_tipi option:selected").attr("col");
	$("#id_row").val(righ);
	$("#id_col").val(col);
	//seleziono o meno il check del oneuse
	var oneuse=$("#id_tipi option:selected").attr("oneuse");
	if (oneuse=="True"){
		$("#id_use").attr("checked",true);
	}
	else{
		$("#id_use").attr("checked",false);
	}
}

function cerca_pos(padre,pos){
	var strbarc="";
	var cont=0;
	for (var i=0;i<listagen.length;i++){
		var diz=listagen[i];
		if ((diz["padre"]==padre)&&(diz["pos"]==pos)){
			//return [true,diz["barcode"]];
			strbarc+=diz["barcode"]+"&";
			cont++;
		}
	}
	if (cont==0){
		return [false,"",0];
	}
	else{
		var barc=strbarc.substring(0,strbarc.length-1);
		return [true,barc,cont];
	}
}

function pos_vuote(){
	var barcpadre=$("#id_father").val();
	$("#divposiz table").children().remove();
	//var tab=$("#tabposition").dataTable();
	//tab.fnClearTable();
	if (barcpadre!=""){
		var tipi=$("#id_tipi option:selected").val();
		if(tipi!=""){
			var lisaliq=$("#id_Aliquot_Type option:selected");
			var tipialiq="";
			for(var i=0;i<lisaliq.length;i++){
				var id=$(lisaliq[i]).val();
				tipialiq+=id+"&";
			}
			tipialiq = tipialiq.substring(0, tipialiq.length - 1)
			if (tipialiq!=""){
				/*if (dizpadri[barcpadre]!=undefined){
					var vett=dizpadri[barcpadre];
					carica_piastra(vett[0], vett[1], barcpadre);
				}
				else{*/
					//chiamo la API per avere le posizioni vuote
					var url=base_url+"/api/positions/empty/"+barcpadre+"/"+tipi+"/"+tipialiq;
					$.getJSON(url,function(d){
						if(d.data!="errore"){
							if(d.data=="inesistente"){
								alert("Container doesn't exist");
							}
							else if(d.data=="err_tipo_cont"){
								alert("This father can't contain this container type");
							}
							else if(d.data=="err_tipo_aliq"){
								alert("This father can't support biological content you chose");
							}
							else{
								dizpadri[barcpadre]=[d.data,d.listafin,d.aliq,d.cont];
								carica_piastra(d.data,d.listafin,barcpadre);
							}
						}
						else{
							alert("Error");
						}
					});
				//}
			}
			else{
				alert("Please select biological content");
			}
		}	
		else{
			alert("Please select container type");
		}
	}
	else{
		alert("Please insert father barcode");
	}
}

function carica_piastra(codhtml,listaposizioni,barcpadre){
	$("#divposiz").children().replaceWith(codhtml);
	$("#divposiz tr").css("text-align","center");
	$("#divposiz td br").remove();
	var listatasti=$("#divposiz table button");
	var posmax=$("#divposiz table").attr("posmax");
	//mi occupo dei container che ho inserito nelle sessioni precedenti
	for (var i=0;i<listatasti.length;i++){
		var lispos=$(listatasti[i]).attr("id").split("-");
		var pos=lispos[1];
		//se la posizione e' stata occupata in questa sessione
		var valori=cerca_pos(barcpadre,pos);
		var occupato=valori[0];		
		if(occupato){
			var barcode=valori[1];
			var num=valori[2];
			var barcattuale=$(listatasti[i]).attr("barcode");
			if(barcattuale!=undefined){
				var barcode=barcattuale+"&"+barcode;
				var numattuale=$(listatasti[i]).text();
				if(!(isNaN(numattuale))){
					var num=String(parseInt(numattuale)+parseInt(num))
				}
			}
			$(listatasti[i]).attr("barcode",barcode);
			$(listatasti[i]).attr("sel","s");
			$(listatasti[i]).text(num);
			var fr="tooltip.hide()";
			$(listatasti[i]).attr("onmouseout",fr);
		}
	}
	
	$(listatasti).attr("disabled",false);
	//mi occupo del tooltip per il barcode
	var listabutton=$("#divposiz table button[sel=\"s\"]");
	for(i=0;i<listabutton.length;i++){
		var bcode=$(listabutton[i]).attr("barcode");
		var codici=bcode.split("&");
		var strbarc="";
		for (var jj=0;jj<codici.length;jj++){
			strbarc+=codici[jj]+"<br>";
		}
		strbarc=strbarc.substring(0,strbarc.length-4);
		var fr="tooltip.show(\""+strbarc+"\")";
		$(listabutton[i]).attr("onmouseover",fr);
		$(listabutton[i]).attr("onmouseout","tooltip.hide();");
		//verifico se il numero di cont presenti in quella pos e' minore o maggiore
		//di posmax
		var testo=$(listabutton[i]).text();
		//per capire se e' un numero o una stringa. Ad es. nel caso del #
		if (!(isNaN(testo))){
			var testo=parseInt(testo);
			$(listabutton[i]).removeAttr("sel");
			if(posmax!="None"){
				var posm=parseInt(posmax);
				if(testo>=posmax){
					$(listabutton[i]).attr("sel","s");
					$(listabutton[i]).css("color","graytext");
				}
			}
		}
	}
	
	$(listatasti).click(function(event){
		event.preventDefault();
	});
	
	$(listatasti).not("[sel]").click(function(event){
		event.preventDefault();
		seleziona_pos(this);
	});
	
	//coloro il tasto con la prima posizione libera
	var listapos=listaposizioni;
	for (var j=0;j<listapos.length;j++){								
		var id="#r-"+listapos[j];
		if (!($(id).attr("sel"))){
			$(id).css("background-color","#ABB9BA");
			$(id).attr("scelto","s");
			break;
		}
	}
}

function seleziona_pos(elem){
	//tolgo il colore di sfondo a tutti i tasti
	$("#divposiz table button").css("background-color","#F9F8F2");
	$("#divposiz table button").removeAttr("scelto");
	$(elem).css("background-color","#ABB9BA");
	$(elem).attr("scelto","s");
}

function canc_container(barc,posiz){
	for (var i=0;i<listagen.length;i++){
		var diz=listagen[i];
		if ((diz["barcode"]==barc)&&(diz["pos"]==posiz)){
			listagen.splice(i,1);
			break;
		}
	}
}

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

function inserisci_container(){
	//devo vedere se sono stati inseriti tutti i dati
	var regex=/^[0-9]+$/;
	var bloccato=false;
	var tab2=$("#cont_table").dataTable();
	
	var barc=$("#id_barcode").val();
	if (barc==""){
		alert("Insert barcode");
		return;
	}
	else{
		//devo controllare che quel codice non l'abbia gia' usato in questa sessione
		for (var j=0;j<listagen.length;j++){
			var diz=listagen[j];
			if (diz["barcode"]==barc){
				alert("Barcode already used in this session. Please change it.");
				bloccato=true;
				break;
			}
		}
		//controllo che il barcode non abbia spazi
		if (barc.indexOf(" ") != -1){
			alert("Error. There is a space in barcode");
			return;
		}
	}
	
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
	
	//la posizione non è obbligatoria, però se il campo del padre
	//contiene qualcosa, allora devo controllare che l'utente abbia selezionato una posizione
	//var lisvuote=$("#tabposition .dataTables_empty");
	var padre=$("#id_father").val();
	var listatr=$("#divposiz table").children();
	//vuol dire che c'è qualcosa nella tabella e allora devo fare il controllo
	if ((padre!="")&&(listatr.length!=0)){
		var selezionati = $("#divposiz table button[scelto]");
		if (selezionati.length==0){
			alert("Select a position for container");
			return;
		}
		else{
			//devo verificare la coerenza tra tipi di aliq inserite e quelle del padre
			var vett=dizpadri[padre];
			if(vett!=undefined){
				//in vett[2] ho la lista delle aliq che vanno bene con quel padre
				if(vett[2]!=""){
				var lisriferimento=vett[2].split("-");
				var lisaliq=$("#id_Aliquot_Type option:selected");
					for(var i=0;i<lisaliq.length;i++){
						var id=$(lisaliq[i]).val();
						if($.inArray(id,lisriferimento)==-1){
							alert("This father can't support biological content you chose");
							bloccato=true;
							break;
						}
					}
				}
				
				//devo verificare la coerenza tra il tipo di container che inserisco e i tipi di cont che il padre puo' contenere
				var lisrif=vett[3].split("-");
				if(($.inArray(tipi,lisrif)==-1)||(vett[3]=="")){
					alert("This father can't contain this container type");
					return;
				}
			}
			else{
				alert("Click on \"Load\" and select a position for container");
				return;
			}
			var lispos=$(selezionati[0]).attr("id").split("-");
			var pos=lispos[1];
		}
	}
	else{
		if(padre!=""){
			alert("Click on \"Load\" and select a position for container");
			return;
		}
		pos="";
	}
	
	if(bloccato==false){
		//devo controllare che quel codice non esista gia' nel DB
		//metto xy perche' non ho un tipo di aliquota per il container
		var url=base_url+"/api/biocassette/"+barc + "/xy/";
		$.getJSON(url,function(d){
			if((d.data=="err_esistente")||(d.data=="err_tipo")){
				alert("Error. Barcode you entered already exists");
				bloccato=true;
			}
			else{
		
				var tipo=$("#id_tipi option:selected").text();
				var geom=rig+"x"+colo;
				
				tab2.fnAddData( [null, contacont,barc, tipo,geom,padre,pos ] );
				
				var usosingolo="n";
				if($("#id_use").is(":checked")){
					usosingolo="s";
				}
				//creo il dizionario con i dati dentro
				var diz={};
				diz['barcode']=barc;
				diz['conttipo']=tipi;
				diz['geometry']=geom;
				diz['padre']=padre;
				diz['pos']=pos;
				diz['uso']=usosingolo;
				
				var tipialiq="";
				for(var i=0;i<lisaliq.length;i++){
					var id=$(lisaliq[i]).val();
					tipialiq+=id+"&";
				}
				tipialiq = tipialiq.substring(0, tipialiq.length - 1)
				diz['aliq']=tipialiq;
				
				listagen.push(diz);
				console.log(diz);
				console.log(listagen);
				contacont++;
				$("#conferma").attr("disabled",false);
				//chiamo la funzione per ripopolare la tabella delle posizioni, in modo che non compaia più 
				//la posizione usata
				//vuol dire che c'è qualcosa nella tabella delle posizioni e allora devo aggiornarle
				if ((padre!="")&&(listatr.length!=0)){
					pos_vuote();
				}
				$("#id_barcode").val("");
			}
		});
	}
}

$(document).ready(function () {
	//devo selezionare tutti i valori della tabella delle entita' biologiche
	//$("#id_Aliquot_Type option").attr("selected","selected");
	
	$("#id_use").attr("checked",true);
	
	var oTable = $("#cont_table").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { 
               "sTitle": null, 
               "sClass": "control_center", 
               "sDefaultContent": '<img src="/archive_media/img/admin/icon_deletelink.gif" width="15px" height="15px" >'
            },
            { "sTitle": "ID Operation" },
            { "sTitle": "Barcode" },
            { "sTitle": "Type" },
            { "sTitle": "Geometry" },
            { "sTitle": "Father" },
            { "sTitle": "Position" },
        ],
	    "bAutoWidth": false ,
	    "aaSorting": [[1, 'desc']],
	    "aoColumnDefs": [
	        { "bSortable": false, "aTargets": [ 0 ] },
	    ],
	    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
    });
	
	/* Add event listener for deleting row  */
    $("#cont_table tbody td.control_center img").live("click",  function () {
        var barcriga = $($($(this).parents('tr')[0]).children()[2]).text();
        var posiz = $($($(this).parents('tr')[0]).children()[6]).text();
        canc_container(barcriga,posiz);
        var nTr = $(this).parents('tr')[0];
        $("#cont_table").dataTable().fnDeleteRow( nTr );
        var barcpadre=$("#id_father").val();
        if(barcpadre!=""){
        	pos_vuote();
        }
    });
	
	var spinner = $("#id_col,#id_row").spinner(
	{
		min:1,
		max:1000
	});
	
	$("#id_father").keypress(function(event){
		//13 e' il codice ASCII del CRLF
		if ( event.which == 13 ) {
			event.preventDefault();
			pos_vuote();
		}
	});
	
	//per aggiornare i tipi di container
	$("#id_generic").change(aggiorna_tipi_cont);
	//per l'autocompletamento sul container padre
	$("#id_tipi").change(autocompletamento);
	//per il tasto che fa comparire le posizioni vuote
	$("#posiz").click(pos_vuote);
	//per il tasto che seleziona tutti i tipi di aliquota
	$("#seltutto").click(selezionatutto);
	
	$("#insert").click(function(event){
		event.preventDefault();
		inserisci_container();
	});
	
	//quando clicco sul pulsante submit
    $("#conferma").click(function(event){
    	event.preventDefault();
    	//comunico la struttura dati al server
    	var data = {
    			salva:true,
    			dati:JSON.stringify(listagen),
	    };
		var url=base_url+"/container/insert/";
		
		$.ajax({
			  type: 'POST',
			  url: url,
			  data: data,
			  success: function (result) {
			    	if (result == "failure") {
			    		alert("Error in sending data");
			    	}
			    	$("#form_fin").append("<input type='hidden' name='final' />");
			    	$("#form_fin").submit();
			  },
			  async:false
			});
		
		/*$.post(url, data, function (result) {
	    	if (result == "failure") {
	    		alert("Error in sending data");
	    	}
	    	
	    	$("#form_fin").append("<input type='hidden' name='final' />");
	    	$("#form_fin").submit();
	    });*/
	});
	
});
