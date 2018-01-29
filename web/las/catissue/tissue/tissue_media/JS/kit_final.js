function cancella(i){
	document.getElementById('tab_riepilogo').deleteRow(i);
    if (document.getElementById('tab_riepilogo').rows.length == 1){
            document.getElementById('inizio2').style.display = 'none';
            document.getElementById('conferma').style.display = 'none';
    }
    //devo rimettere a posto la numerazione dei kit inseriti
    else{
    	var lista=$("#tab_riepilogo tr").not(":first-child").children(":first-child");
    	for (i=0;i<lista.length;i++){
    		$(lista[i]).text(i+1);
    		$(lista[i]).css("font-weight","bold");
    	}
    	//devo rimettere a posto anche il nome dei campi hidden che contengono il
    	//valore del barcode
    	var listacampi=$("#tab_riepilogo tr").not(":first-child").children(":nth-child(2)").children();
    	for (j=0;j<listacampi.length;j++){
    		var stringa="barc_"+j;
    		$(listacampi[j]).attr("name",stringa);
    	}
    }
    $("#barc").attr("value","");
    $("#barc").focus();
}

function aggiungi_barcode(){
	var barc=$("#barc").attr("value");
	$("#barc").focus();
	if (barc==""){
		alert("Please insert a barcode for the kit");
		//do il focus al campo con il barcode
		$("#barc").focus();
	}
	else{
		//verifico che il kit non esista gia'
		url=base_url+"/api/kitbarcode/"+barc;
		$.getJSON(url,function(d){
			if(d.data!="errore"){
				if (d.data=="0"){
					//rendo visibile la div e il tasto per confermare tutto
					$("#inizio2,#conferma").css("display","inline");
					
					var trovato=0;
					//mi da' i td in cui si trovano i barcode dei kit gia' presenti nella lista
					var listakit=$("#tab_riepilogo tr td:nth-child(2)");
					//confronto i kit che ci sono gia' nella tabella con quello
					//nuovo e se c'e' gia' non lo inserisco nella tabella
					for (i=0;i<listakit.length;i++){
						var b=$(listakit[i]).text();
						if(b==barc){
							trovato=1;
						}
					}
					if(trovato==0){
						var tabella = document.getElementById("tab_riepilogo");
						//prendo il numero di righe della tabella
						var rowCount = tabella.rows.length;
						var row = tabella.insertRow(rowCount);
				
						var cella1= row.insertCell(0);
					    cella1.innerHTML="<b>"+rowCount+"</b>";
					    var cella2= row.insertCell(1);
					    cella2.innerHTML="<input type='hidden' name='barc_"+(rowCount-1)+"' value="+barc+" />"+barc;
						//inserisco la cella con dentro l'immagine per cancellare
					    var cella3 = row.insertCell(2);
					    cella3.innerHTML ="<img width='14px' height='14px' style='float:left;cursor:pointer;' onclick='cancella(this.parentNode.parentNode.rowIndex)' src='"+media_url+"/tissue_media/img/admin/icon_deletelink.gif'></img>";					    
					}
					$("#barc").attr("value","");
				}
				else{
					alert("Kit barcode already exists");
				}
			}
		});
	}
}

$(document).ready(function () {
	//do il focus al campo con il barcode
	$("#barc").focus();
	
	$("#aggiungi").click(aggiungi_barcode);
	
	var tabfin=$("#tabellafinale");
	//se sono nella pagina del report finale
	if (tabfin.length!=0){
		//per il report finale
		generate_result_table("Kit","tabellafinale");
	}
	
	$("#barc").keypress(function(event){
		//13 e' il codice ASCII del CRLF
		if ( event.which == 13 ) {
			event.preventDefault();
			aggiungi_barcode();
		}
	});
	
	$("#conferma").click(function(event){
		var tabella = document.getElementById("tab_riepilogo");
		//prendo il numero di righe della tabella
		var righe = tabella.rows.length;
		//salvo il numero di righe totali nel campo che poi passo alla vista con
		//il form
		$("#righe_totali").attr("value",(righe-1));
	});
});