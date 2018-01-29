aliquote_inserite=new Array();
valori_campioni=[];

function cancella(riga){
	
	var tab=$("#aliquote").dataTable();
	var righe=tab.$("tr");
    var genealogy=$(righe[(riga.rowIndex)-1]).children(":nth-child(2)").text();
    //cancello il campione dalla lista finale prendendo il suo indice all'interno della lista
    var indice=$.inArray(genealogy,aliquote_inserite);
    if(indice!=-1){
    	aliquote_inserite.splice(indice,1);
    }
    //cancello il campione anche dalla lista con tutti i dati
    for (var j=0;j<valori_campioni.length;j++){
    	var valore=valori_campioni[j];
    	var val=valore.split("|");
    	//il gen e' il primo valore
    	var gen=val[0];
    	if(gen==genealogy){
    		valori_campioni.splice(j,1);
    		break;
    	}
    }
    //cancello la riga dal data table
    var indice=tab.fnGetPosition(riga);
    tab.fnDeleteRow(indice);
    
    if (document.getElementById('aliquote').rows.length > 1){
    	var lista=tab.$("tr").children(":first-child");
    	for (var j=0;j<lista.length;j++){
    		//per aggiornare il contenuto di una cella (nuovo valore, riga,colonna)
    		tab.fnUpdate(j+1,j,0);
    	}
    }
}

function inizializza(){
	var tab=$("#aliquote").dataTable();
	var righe=tab.$("tr");

	if(righe.length>0){
		$("#conferma").attr("disabled",false);
	}
	var nascondi=true;
	for(var i=0;i<righe.length;i++){
		var gen=$(righe[i]).children(":nth-child(2)").text();
		var barc=$(righe[i]).children(":nth-child(3)").text();
		var pos=$(righe[i]).children(":nth-child(4)").text();
		if(pos!=""){
			nascondi=false;
		}
		var stringa=gen+"|"+barc+"|"+pos;
		valori_campioni.push(stringa);
		aliquote_inserite.push(gen);
	}
	if(nascondi){
		tab.fnSetColumnVis( 3, false );
	}
}

function aggiungi_aliquota(){
	//sono le righe della tabella dove sono visualizzate le aliquote da rivalutare
	var tab=$("#aliquote").dataTable();
	var righe=tab.$("tr");
	//genealogy ID dell'aliquota da rivalutare
	gen=$("#id_aliquot").attr("value");
	var r=(righe.length);
	if(gen==""){
		alert("Insert a valid genealogy ID");
	}
	else{
		var split=$("#aliquot_split");
		var sp=""
		if (split.length!=0){
			sp="split";
		}
		var codice=gen.replace(/#/g,"%23");
		url=base_url+"/api/revaluate/aliquot/"+codice+"/"+sp;
		$.getJSON(url,function(d){
			if(d.data!="errore"){
				if(d.data=="inesistente"){
					alert("Aliquot doesn't exist in storage");
				}
				else if(d.data=="derivato"){
					alert("Aliquot is not a derived aliquot");
				}
				else if(d.data=="presente"){
					if (split.length!=0){
						alert("Aliquot is already scheduled for splitting");
					}
					else{
						alert("Aliquot is already scheduled for revaluation");
					}
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
						var barc=val[1];
						var pos=val[2];
						//funzione che restituisce la posizione di un valore in una lista. Se il valore non c'è, allora restituisce -1
						if($.inArray(gen,aliquote_inserite)==-1){
							aliquote_inserite.push(gen);
							valori_campioni.push(lisvalori[j]);
							var indice=parseInt(aliquote_inserite.length);
							var riga=tab.fnAddData( [indice, gen, barc, pos, null] );
							if(pos!=''){
								tab.fnSetColumnVis( 3, true );
							}
						}
						$("#id_aliquot").val("");
						$("#id_aliquot").focus();
						$("#conferma").attr("disabled",false);
					}
				}			
			}
		});		
	}
}

//serve a capire se la tabella con le aliq pianificate e' vuota
//o meno
function vuota(){
	var listarighe=$("#aliquote tr");
	if(listarighe.length>2){
		return false;
	}
	//devo capire se c'e' una sola provetta o se la tabella e' vuota
	else if (listarighe.length==2){
		//prendo il contenuto della riga e vedo quanti td ha dentro
		var celle=$("#aliquote tr.odd td");
		if (celle.length==1){
			//la tabella e' vuota
			return true;
		}
		else{
			return false;
		}
	}
}

$(document).ready(function () {
	
	
	$("#tastofile").click(function(){
		$("#id_file").click();
	});
	
	$("#id_file").change(function(){
		var files = $('#id_file')[0].files;
		var nomfile="";
		for (var i = 0; i < files.length; i++) {
	        nomfile+=files[i].name.split("\\").pop()+","
	    }
		//tolgo la virgola finale
		nomfile = nomfile.substring(0, nomfile.length - 1)
		$("#filename").val(nomfile);
	});
	
	var tab=$("#aliquote").dataTable({
		"bPaginate": true,
		"bLengthChange": true,
		"bFilter": true,
		"bSort": true,
		"bInfo": true,
		"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
		"bAutoWidth": false,
		"aoColumnDefs": [
  	        { "bSortable": false, "aTargets": [ 4 ] },
  	        { "sDefaultContent": "<img src='"+media_url+"/tissue_media/img/admin/icon_deletelink.gif' width='13px' height='13px' onclick='cancella(this.parentNode.parentNode)' >" , "aTargets": [ 4 ]},
  	    ],});
	
	
	var tabfin=$("#aliquote_fin");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
		//per il report finale
		var split=$("#aliquot_split");
    	if (split.length!=0){
    		generate_result_table("Split","aliquote_fin");
		}
    	else{
    		generate_result_table("Revaluation","aliquote_fin");
    	}
	}
	else{
		inizializza();
	}

	$("#nuova_aliquota").attr("disabled",true);
	$("#id_aliquot").attr("size","32");
	
	//aggiungo il tasto Add_file e il collegamento al file che spiega come deve essere
	//fatto il file con la lista delle aliquote
	url=media_url+"/tissue_media/File_Format/DerivedAliquot.txt";
	$("#addfile").after("<br><a id='file' href="+url+" class='anchor' >File Format</a>");
	//creo la finestra di popup
	$(".anchor").popupWindow({ 
		height:500, 
		width:800, 
		top:50, 
		left:50,
		scrollbars:1,
		resizable:1,
		menubar:1
		}); 
	$("#id_aliquot").attr("onFocus","$(\"#nuova_aliquota\").attr(\"disabled\",false);");
	
	$("#nuova_aliquota").click(aggiungi_aliquota);
	$("#id_aliquot").keypress(function(event){
		if ( event.which == 13 ) {
			event.preventDefault();
			aggiungi_aliquota();
		}
	});
	
	$("#addfile").click(function(event){
		event.preventDefault();

    	//comunico la struttura dati al server
    	var data = {
    			salva:true,
    			dati:JSON.stringify(valori_campioni),
	    };
    	var split=$("#aliquot_split");
    	if (split.length!=0){
    		var url=base_url+"/split/insert/";
		}
    	else{
    		var url=base_url+"/revalue/insert/";
    	}
		$.post(url, data, function (result) {
	    	if (result == "failure") {
	    		alert("Error");
	    	}
	    	else{
	    		$("#form_file").append("<input type='hidden' name='aggiungi_file' />");
	    	
	    		$("#form_file").submit();
	    	}
	    });
	});
	
	$("#conferma").click(function(event){
		event.preventDefault();
		if(vuota()){
			alert("Please insert some aliquots");
		}
		else{
	    	//comunico la struttura dati al server
	    	var data = {
	    			salva:true,
	    			dati:JSON.stringify(valori_campioni),
		    };
	    	var split=$("#aliquot_split");
	    	if (split.length!=0){
	    		var url=base_url+"/split/insert/";
			}
	    	else{
	    		var url=base_url+"/revalue/insert/";
	    	}
			$.post(url, data, function (result) {
		    	if (result == "failure") {
		    		alert("Error");
		    	}
		    	else{
		    		$("#form_fin").append("<input type='hidden' name='conferma' />");
		    	
		    		$("#form_fin").submit();
		    	}
		    });
		}
	});

});