function modifica(){
	var percorso=$(this).attr("href");
	var mod=percorso.replace(/\^\^/gi, " ");
	$(this).attr("href",mod);
}

function vedi_file(){
	var gen=$("#id_aliquot").attr("value");
	var tabella = document.getElementById("derivati");
	//prendo il numero di righe della tabella
	var rowCount = tabella.rows.length;
	rowCount=parseInt(rowCount);
	$("#derivati").css("display","none");
	if (gen==""){
		alert("Insert a genealogy ID");
	}
	else{
		//cancello i file di prima
		for(var k=rowCount;k>1;k--){
			tabella.deleteRow(k-1);
		}
		url=base_url+"/api/derived/file/"+gen;
		$.getJSON(url,function(d){
			if(d.data!="errore"){
				if((d.data!=null)&&(d.data!="")){
					file=d.data.split("|");
					for (i=0;i<(file.length-1);i++){
						$("#derivati").css("display","");
						var valori=file[i].split("&");
						mod=valori[0].replace(/ /gi, "^^");
						url="/tissue_media/Derived_aliquots/"+mod;
						//prendo il numero di righe della tabella
						var rowCount = tabella.rows.length;
						rowCount=parseInt(rowCount);
						var row = tabella.insertRow(rowCount);
						//centro tutte le celle che apparterranno alla riga
						$(row).attr("align","center");
						//inserisco la cella con dentro il numero d'ordine
					    var cell1 = row.insertCell(0);
					    cell1.innerHTML =rowCount;
					    var indice=(rowCount-1).toString();
					    var cell2 = row.insertCell(1);
					    cell2.innerHTML="<a id='file_"+i+"' href="+url+" class='anchor' >"+valori[0]+"</a>";
					    var cell3 = row.insertCell(2);
					    cell3.innerHTML=valori[2];
					    var cell4 = row.insertCell(3);
					    cell4.innerHTML=valori[1];
					    //$("#derivati").append("<br><a style='font-size:1.5em;' id='file_"+i+"' href="+url+" class='anchor' >"+(i+1)+")&nbsp;"+valori[0]+"</a>&nbsp;&nbsp;&nbsp;<h2 style='font-size:1.4em;display:inline;font-weight:normal;'>("+valori[2]+" executed on "+valori[1]+")</h2><br>");
						$("#file_"+i).click(modifica);
						$("#file_"+i).attr("onmouseover","tooltip.show('Click for viewing file');");
						$("#file_"+i).attr("onmouseout","tooltip.hide();");
						titolo=$("#file_"+i).attr("href"); 
						nome=titolo.split("/");
						x=nome.length;
						t=nome[x-1];
					}
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
					alert("There is no files to view for this aliquot");
				}
			}
			else{
				alert("Non-existent genealogy ID");
			}
		});
	}
}

$(document).ready(function () {
	//per l'autocompletamento
	$("#id_aliquot").autocomplete({
		source:base_url+'/ajax/derived/autocomplete/'
	});
	
	$("#id_aliquot").focus();
	
	$("#id_aliquot").keypress(function(event){
		//13 e' il codice ASCII del CRLF
		if ( event.which == 13 ) {
			event.preventDefault();
			vedi_file();
		}
	});
	
	$("#conferma1").click(vedi_file);
});