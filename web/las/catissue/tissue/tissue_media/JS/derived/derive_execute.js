var contatore=1;
var listaappoggio=new Array();
var listabarcgenerale=new Array();
var lgenletti=new Array();
var tipoderivato="";

//serve a capire se la tabella sotto, con le aliq da derivare effettivamente, e' vuota
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
	//solo se nella tabella di sopra ho delle aliquote
	var listarighe=$("#aliq_definitive tr");
	var righesopra=$("#aliq_originali tr");
	if ((righesopra.length>1)||(listarighe.length>1)){
		var lbarc="";
		var lgen="";
		var lis_pezzi_url=[];
		var utente=$("#actual_username").val();
		var url=base_url+"/api/storage/tube/";
		var listagen=$("#aliq_originali tr").children(":nth-child(2)").not("th");
		//prendo i barcode della tabella di sopra
		listabarc=$("#aliq_originali tr").children(":nth-child(9)").not("th");
		//prendo i campi relativi alla piastra della tabella di sopra
		listapias=$("#aliq_originali tr").children(":nth-child(7)").not("th");
		//prendo i campi relativi alla posizione della provetta della tabella di sopra
		listapos=$("#aliq_originali tr").children(":nth-child(8)").not("th");
		//prendo i campi relativi alla posizione della piastra della tabella di sopra
		listapospiastra=$("#aliq_originali tr").children(":nth-child(6)").not("th");
		//prendo i campi relativi al rack della tabella di sopra
		listarack=$("#aliq_originali tr").children(":nth-child(5)").not("th");
		//prendo i campi relativi alla posizione della tabella di sopra
		listafreezer=$("#aliq_originali tr").children(":nth-child(4)").not("th");
		//prendo i campi relativi alla disponibilita' della prima tabella
		listadisp=$("#aliq_originali tr").children(":nth-child(11)").not("th");
		
		for (var i=0;i<listagen.length;i++){
			//mi da' il gen attuale
			var gen=$(listagen[i]).text();
			lgen=lgen+gen+"&";
			lgen = lgen.replace(/#/g, "%23");
			if (lgen.length>2000){
	            lis_pezzi_url.push(lgen);
	            lgen="";
			}
		}
		if (lgen==""){
			lgen="-";
			lis_pezzi_url.push("-");
		}
		else{
			lis_pezzi_url.push(lgen);
		}
		var timer = setTimeout(function(){$("body").addClass("loading");},1000);
		for (var j=0;j<lis_pezzi_url.length;j++){		
			urlst=url+lis_pezzi_url[j]+"/"+utente;
			$.getJSON(urlst,function(d){
				if (d.data!="errore"){
					diz=JSON.parse(d.data);
					if(Object.size(diz)!=0){
						//scrivo nel campo apposito l'indicazione della posizione della provetta
						for(var i=0;i<listagen.length;i++){
							var gen=String($(listagen[i]).text().trim());
							var listaval=diz[gen];
							if(listaval!=undefined){
								var val=listaval.split("|");
								
								if(val[0]!="None"){
									listabarcgenerale.push(val[0].toUpperCase());
								}
								//questo e' per le piastre con i pozzetti che non hanno le provette con barcode.
								//Carico quindi il valore della piastra stessa
								else{
									if($.inArray(val[2].toUpperCase(),listabarcgenerale)==-1){
										listabarcgenerale.push(val[2].toUpperCase());
									}
								}
								//solo se non e' gia' in lista lo inserisce
								if(($.inArray(val[0].toUpperCase(),listaappoggio)==-1)&&(val[0]!="None")){
									listaappoggio.push(val[0].toUpperCase());	
								}
								if(($.inArray(val[2].toUpperCase(),listaappoggio)==-1)&&(val[2]!="None")){
									listaappoggio.push(val[2].toUpperCase());
								}
								if(($.inArray(val[4].toUpperCase(),listaappoggio)==-1)&&(val[4]!="None")){
									listaappoggio.push(val[4].toUpperCase());
								}
								if(($.inArray(val[5].toUpperCase(),listaappoggio)==-1)&&(val[5]!="None")){
									listaappoggio.push(val[5].toUpperCase());
								}
								
								$(listabarc[i]).text(val[0]);
								$(listapos[i]).text(val[1]);
								$(listapias[i]).text(val[2]);
								$(listapospiastra[i]).text(val[3]);
								$(listarack[i]).text(val[4]);
								$(listafreezer[i]).text(val[5]);
								$(listadisp[i]).text(val[6]);
							}
						}
					}
					//lo faccio solo una volta alla fine del ciclo generale
					if (contatore==lis_pezzi_url.length){
						$("#aliq_originali,#aliq_definitive").dataTable({
							"bPaginate": true,
							"bLengthChange": true,
							"bFilter": true,
							"bSort": true,
							"bInfo": true,
							"bAutoWidth": false, 
							"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]]});
						//$("#aliq_originali_wrapper").css("float","left");
						//$("#aliq_originali_wrapper,#aliq_definitive_wrapper").css("width","85%");
						
						trova_figli_container();
						clearTimeout(timer);
						$("body").removeClass("loading");
					}
					
				}
				else{
					alert("Problems while interacting with storage");
				}
				contatore++;
			});
			//per evidenziare condizioni di errore
			//.error(function() { 
			//	alert("Problems while interacting with storage"); 
			//});
		}
	}
	else{
		$("#aliq_originali,#aliq_definitive").dataTable({
			"bPaginate": true,
			"bLengthChange": true,
			"bFilter": true,
			"bSort": true,
			"bInfo": true,
			"bAutoWidth": false, 
			"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]]});
	}
}

function conf_barcode(){
	var barcorig=$("#id_barcode").attr("value");
	var barc=barcorig.toUpperCase();
	if ($.inArray(barc,listaappoggio)!=-1){
		
		if ($.inArray(barc,listabarcgenerale)!=-1){
			var tabella=$("#aliq_originali").dataTable();
			var tabellasotto=$("#aliq_definitive").dataTable();
			var aTrs = tabella.fnGetNodes();			
			var oSettings = tabella.fnSettings();
			//mi da' il numero di colonne che ci sono nel data table
			var lunghezza = (oSettings.aoColumns.length);
			var contat=0;
			// scandisce tutte le righe della tabella
			var avviso=false;
	        jQuery.each(tabella.fnGetData(), function(key, d) {
	        	if ((d[8].toUpperCase() == barc)||(d[6].toUpperCase()== barc)||(d[4].toUpperCase()==barc)||(d[3].toUpperCase()==barc)){
	        		//mi da' la riga del data table
					var riga=aTrs[key];
	        		var fi=":nth-child("+(lunghezza)+")";
	        		var dispon=$(riga).children(fi).text();
	        		if (dispon=="Yes"){
	        			//devo prendere il valore del tipo di derivato che si trova nella cella per fare in modo che le righe
	        			//che scelgo siano tutte coerenti in questo senso
	        			var fi=":nth-child(3)";
		        		var tipder=$(riga).children(fi).children().val();
	        			if (tipoderivato==""){
	        				tipoderivato=tipder;
	        			}
	        			else{
	        				if (tipder!=tipoderivato){
	        					if(!avviso){
		        					alert("Please select derivation with same derivative");
									$("#id_barcode").attr("value","");
									$("#id_barcode").focus();
									avviso=true;
	    	        			}
	        				}
	        			}
	        			if(!avviso){
		        			var listadatitemp=new Array();
				        	
							//lunghezza-1 perche' l'ultima colonna e' l'available e non mi serve nella tabella sotto
							for (var k=0;k<(lunghezza-1);k++){
								var figlio=":nth-child("+(k+1)+")";
								var dato=$(riga).children(figlio).html();
								listadatitemp.push(dato);
							}
							var rowPos=tabellasotto.fnAddData(listadatitemp);
							
			                tabella.fnDeleteRow(riga);
			                contat++;
			                if ($.inArray(barcorig,lgenletti)==-1){
			                	//d[1] e' il genid della riga
			                	lgenletti.push(d[1]);
			                }
	        			}
	        		}
	        		else{
	        			if(!avviso){
		        			alert("Container is not available. You can't select it.");
							$("#id_barcode").attr("value","");
							$("#id_barcode").focus();
							avviso=true;
	        			}
	        		}
	            }
	        });
			$("#id_barcode").attr("value","");
			$("#id_barcode").focus();
			//tolgo il codice dalla lista generale
			removeBarcode(barc);
			//aggiorno la scritta con il numero di provette confermate
			if (contat==1){
				$("#contatore").text("You validated "+String(contat)+" aliquot");
			}
			else{
				$("#contatore").text("You validated "+String(contat)+" aliquots");
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
			$("#inferio").css("display","inline");
		}
		else{
			alert("You did not schedule to derive all children's container. Please validate barcode singularly.");
			$("#id_barcode").attr("value","");
			$("#id_barcode").focus();
		}
	}
	else{
		alert("Invalid barcode");
		$("#id_barcode").attr("value","");
		$("#id_barcode").focus();
	}	
}

function trova_figli_container(){
	var lbarc="";
	var url=base_url+"/api/transfer/listbarcode/";	
	for (var i=0;i<listabarcgenerale.length;i++){
		lbarc=lbarc+listabarcgenerale[i]+"&";
	}
	lbarc = lbarc.substring(0, lbarc.length - 1)
	var codice=lbarc.replace(/#/g,"%23");
	//var urlst=url+codice;
	var data = {
			lbarc:codice
    };
	$.post(url, data, function (result) {
		if (result.data!="errore"){
			var lista=result.data;
			for(var i=0;i<lista.length;i++){
				listabarcgenerale.push(lista[i].toUpperCase());
			}
			
		}
	});
}

//restituisce le dimensioni di un dict
Object.size = function(obj) {
    var size = 0, key;
    for (key in obj) {
        if (obj.hasOwnProperty(key)) size++;
    }
    return size;
};

function removeBarcode(barcode){
    for (var i=0; i < listabarcgenerale.length; i++){
        if (listabarcgenerale[i] == barcode){
        	listabarcgenerale.splice(i,1);
        }
    }
}

$(document).ready(function () {
	
	//do il focus al campo con il barcode della provetta
	$("#id_barcode").focus(); 		
	
	$("#id_barcode").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			conf_barcode();
		}
	});
	
	aggiorna_dati();
	
	$("#conf").click(conf_barcode);
	//metto un controllo per capire se l'utente clicca per confermare tutto senza riempire la lista
	$("#conf_all").click(function(event){
		event.preventDefault();
		//vuol dire che la lista delle aliquote da derivare e' vuota
		if(vuota()){
			alert("You have to add some aliquots to derivation list");		
		}
		else{
			//comunico la struttura dati al server
	    	var data = {
	    			salva:true,
	    			lgen:JSON.stringify(lgenletti)
		    };
	    	//per capire a quale url fare la post
	    	var url=base_url+"/derived/execute/effective/";
	    	
			$.post(url, data, function (result) {
		    	if (result == "failure") {
		    		alert("Error");
		    	}
		    	else{
		    		$("#form_conf").append("<input type='hidden' name='conferma' />");
		    	
		    		$("#form_conf").submit();
		    	}
			});
		}
	});
});