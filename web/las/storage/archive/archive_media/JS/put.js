var listabarcgenerale=new Array();
var lbarcletti=new Array();
var listaappoggio=new Array();

function removeBarcode(barcode){
    for (var i=0; i < listaappoggio.length; i++){
        if (listaappoggio[i] == barcode){
			listaappoggio.splice(i,1);
			// console.log("Removed "+ barcode + "\n");
			break; //break if found
        }
    }
}


//serve a trovare quali padri possono essere accettati nella schermata.
//Si tratta di quei padri i cui figli devono essere tutti riposizionati
function trova_figli_container(){
	var timer = setTimeout(function(){$("body").addClass("loading");},1500);
	var lbarc="";
	var listabarc=$("#aliq_originali tr").children(":nth-child(8)").not("th");
	var listapias=$("#aliq_originali tr").children(":nth-child(6)").not("th");
	for (var i=0;i<listabarc.length;i++){
		//mi da' il barcode attuale
		var barc=$(listabarc[i]).text();
		listabarcgenerale.push(barc.toUpperCase());
		listaappoggio.push(barc.toUpperCase());
		//se il codice e' None vuol dire che la riga riguarda una piastra
		//con i pozzetti da riposizionare. Quindi aggiungo il codice della piastra
		//alla lista da passare alla API cosi' in risposta avro' questa piastra tra 
		//quelle selezionabili
		if(barc=="None"){
			var pias=$(listapias[i]).text();
			listabarcgenerale.push(pias.toUpperCase());
			// console.log("Added "+ pias + " to listabarcgenerale");
		}
	}
	
	var url=base_url+"/api/check/listcontainer/";	
	
	for (var i=0;i<listabarcgenerale.length;i++){
		lbarc=lbarc+listabarcgenerale[i]+"&";
	}
	lbarc = lbarc.substring(0, lbarc.length - 1)
	var codice=lbarc.replace(/#/g,"%23");

	var data = {
			lbarc:codice
    };
	$.post(url, data, function (result) {
		if (result.data!="errore"){
			var lista=result;
			for(var i=0;i<lista.length;i++){
				listabarcgenerale.push(lista[i].toUpperCase());
				// console.log("Added "+ lista[i].toUpperCase() + " to listabarcgenerale");
			}
			clearTimeout(timer);
			$("body").removeClass("loading");
		}
	});
}

//serve a capire se la tabella sotto e' vuota
//o meno
function vuota(){
	var listarighe=$("#aliq_definitive tr");
	if(listarighe.length>2){
		return false;
	}
	//devo capire se c'e' una sola provetta o se la tabella e' vuota
	else if (listarighe.length==2){
		//prendo il contenuto della riga e vedo quanti td ha dentro
		var celle=$("#aliq_definitive tr.odd td");
		if (celle.length==1){
			//la tabella e' vuota
			return true;
		}
		else{
			return false;
		}
	}
}

function aggiorna_dati(){
	var listarighe=$("#aliq_originali tr").not(":first");
	//var listarack=$("#aliq_originali tr").children(":nth-child(4)").not("th");
	//var listafreezer=$("#aliq_originali tr").children(":nth-child(3)").not("th");
	for(var i=0;i<listarighe.length;i++){
		var pias=$($(listarighe[i]).children(":nth-child(6)")).text();
		var rack=$($(listarighe[i]).children(":nth-child(4)")).text();
		var freezer=$($(listarighe[i]).children(":nth-child(3)")).text();
		if(($.inArray(pias.toUpperCase(),listaappoggio)==-1)&&(pias!="None")){
			listaappoggio.push(pias.toUpperCase());
		}
		
		if(($.inArray(rack.toUpperCase(),listaappoggio)==-1)&&(rack!="None")){
			listaappoggio.push(rack.toUpperCase());
		}
		
		if(($.inArray(freezer.toUpperCase(),listaappoggio)==-1)&&(freezer!="None")){
			listaappoggio.push(freezer.toUpperCase());
		}
	}
	var diff = $(listaappoggio).not(listabarcgenerale).get();
	// console.log("listaappoggio has " + listaappoggio.length + " elements: " + JSON.stringify(listaappoggio, null, 2));
	// console.log("listabarcgenerale has " + listabarcgenerale.length + " elements: " + JSON.stringify(listabarcgenerale, null ,2));
	// console.log("The diff is: " + JSON.stringify(diff, null ,2));
}

function conf_barcode(){
	if($("#id_barcode").val()==""){
		alert("You have to fill tube barcode field");
	}
	else{
		var barcorig=$("#id_barcode").attr("value");
		var barc=barcorig.toUpperCase();
		if ($.inArray(barc,listaappoggio)!=-1){
			// console.log(barc + " is in listaappoggio \n");
			// if ($.inArray(barc,listabarcgenerale)!=-1){   //
				var tabella=$("#aliq_originali").dataTable();
				var tabellasotto=$("#aliq_definitive").dataTable();
				var aTrs = tabella.fnGetNodes();			
				var oSettings = tabella.fnSettings();
				//mi da' il numero di colonne che ci sono nel data table
				var lunghezza = oSettings.aoColumns.length;
				// scandisce tutte le righe della tabella
				var contatore=0;
		        jQuery.each(tabella.fnGetData(), function(key, d) {
				// looks in d[7]=barcode, d[5]=plate, d[3]=rack, d[2]=freezer
		        	if ((d[7].toUpperCase() == barc)||(d[5].toUpperCase()==barc)||(d[3].toUpperCase()==barc)||(d[2].toUpperCase()==barc)){
						removeBarcode(barc);
						//mi da' la riga del data table
						var riga=aTrs[key];
		        		var listadatitemp=new Array();
			        	
						for (var k=0;k<lunghezza;k++){
							var figlio=":nth-child("+(k+1)+")";
							var dato=$(riga).children(figlio).html();
							listadatitemp.push(dato);
						}
						var rowPos=tabellasotto.fnAddData(listadatitemp);
						
		                tabella.fnDeleteRow(riga);
		                contatore++;
		                if ($.inArray(barcorig,lbarcletti)==-1){
		                	lbarcletti.push(barcorig);
		                }
		            }
		        });		
				$("#id_barcode").attr("value","");
				$("#id_barcode").focus();
				//tolgo il codice dalla lista generale
				// removeBarcode(barc); //remove solo d7 all nell'each
				//aggiorno la scritta con il numero di provette confermate
				if (contatore==1){
					$("#contatore").text("You validated "+String(contatore)+" aliquot");
				}
				else{
					$("#contatore").text("You validated "+String(contatore)+" aliquots");
				}
				
				//per rimettere a posto la numerazione della tabella sopra e sotto
				var lista=tabella.$("tr").children(":first-child");
		    	for (var j=0;j<lista.length;j++){
		    		//per aggiornare il contenuto di una cella (nuovo valore, riga,colonna), il false e' 
		    		//per fare in modo che la tabella non si riaggiorni scombinando così gli ordinamenti dell'utente
		    		tabella.fnUpdate(j+1,j,0,false,true);
		    	}
		    	var lista=tabellasotto.$("tr").children(":first-child");
		    	for (var j=0;j<lista.length;j++){
		    		//per aggiornare il contenuto di una cella (nuovo valore, riga,colonna)
		    		tabellasotto.fnUpdate(j+1,j,0,false,true);
		    	}
			tabellasotto.fnDraw();
			// }
			// else{
			// 	alert("You don't have to position all children's container. Please validate barcode singularly.");
			// 	$("#id_barcode").attr("value","");
			// 	$("#id_barcode").focus();
			// 	$("#contatore").text("");
			// }

		}
		else{
			alert("Invalid Barcode");
			// console.log(JSON.stringify(listaappoggio));
			// console.log(JSON.stringify(listabarcgenerale));
			$("#id_barcode").attr("value","");
			$("#id_barcode").focus();
			$("#contatore").text("");
		}
	}
}

$(document).ready(function () {
	var cc=$("#cont_fin");
	
	//solo se non sono nell'ultima pagina faccio tutto questo
	if (cc.length==0){
		trova_figli_container();
		aggiorna_dati();
		
		$("#aliq_originali,#aliq_definitive").dataTable({
			"bPaginate": true,
			"bLengthChange": true,
			"bFilter": true,
			"bSort": true,
			"bInfo": true,
			"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
			"bAutoWidth": false });
		
		//do il focus al campo con il barcode della provetta
		$("#id_barcode").focus(); 
		
		$("#conf").click(conf_barcode);
		
		$("#id_barcode").keypress(function(event){
			if ( event.which == 13 ) {
				event.preventDefault();
				conf_barcode();
			}
		});
		
		//metto un controllo per capire se l'utente clicca per confermare tutto senza riempire la lista
		$("#conf_all").click(function(event){
			event.preventDefault();
			if(vuota()){
				alert("You have to add some containers.");
			}
			else{
				//comunico la struttura dati al server
		    	var data = {
		    			salva:true,
		    			lbarc:JSON.stringify(lbarcletti)
			    };
			    // console.log("listaappoggio has " + listaappoggio.length + " elements: " + JSON.stringify(listaappoggio, null, 2));
				var url=base_url+"/put/last/";
				$.post(url, data, function (result) {
			    	if (result == "failure") {
			    		alert("Error");
			    	}
			    	$("#form_fin").append("<input type='hidden' name='final' />");
                    $("#form_fin").submit();
				});
			}
		});
	}
});
