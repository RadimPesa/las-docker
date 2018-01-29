//e' una lista di dizionari, in cui ogni diz e' un container nuovo
var listagen=new Array();
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
					//in val[0] ho l'id, in val[1] ho il barcode
					var stringa="<option value="+lista[i].id+">"+lista[i].actualName+"</option>"
					$("#id_tipi option[value=\"\"]").after(stringa);
				}
			}
		});
	}
}

function autocompletamento(){
	tip=$("#id_tipi option:selected").val();
	$("#id_father").autocomplete({
		source:base_url+'/archive/ajax/container/autocomplete/?tipo='+tip
	});
	$("#id_father").attr("disabled",false);
}

/* Get the rows which are currently selected */
function fnGetSelected( oTableLocal )
{
	var aReturn = new Array();
	var aTrs = oTableLocal.fnGetNodes();
	
	for ( var i=0 ; i<aTrs.length ; i++ )
	{
		if ( $(aTrs[i]).hasClass('row_selected') )
		{
			aReturn.push( aTrs[i] );
		}
	}
	return aReturn;
}

function pos_vuote(){
	var barcpadre=$("#id_father").val();
	var tab=$("#tabposition").dataTable();
	tab.fnClearTable();
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
							var listapos=JSON.parse(d.data);
							if (listapos.length==0){
								alert("Container full");
							}
							else{
								for(var i=0;i<listapos.length;i++){	
									var coo=listapos[i].position.toString();
									var coord=coo.split(",");
									tab.fnAddData( [listapos[i].id, coord[0],coord[1] ] );
								}
								tab.$("tr").click(function(event) {
									$(tab.fnSettings().aoData).each(function (){
										$(this.nTr).removeClass('row_selected');
									});
									$(this).addClass('row_selected');
								});
							}
						}
					}
					else{
						alert("Error");
					}
				});
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

function selezionatutto(){
	if ($(this).val()=="Select all"){
		$(this).val("Deselect all");
		$("#id_Aliquot_Type option").attr("selected","selected");
	}
	else{
		$(this).val("Select all");
		$("#id_Aliquot_Type option").removeAttr("selected");
	}
}

function inserisci_container(){
	//devo vedere se sono stati inseriti tutti i dati
	var regex=/^[0-9]+$/;
	var bloccato=false;
	var tab=$("#tabposition").dataTable();
	var tab2=$("#cont_table").dataTable();
	
	var barc=$("#id_barcode").val();
	if (barc==""){
		alert("Insert barcode");
		bloccato=true;
	}
	else{
		//devo controllare che quel codice non l'abbia gia' usato in questa sessione
		
	}
	
	var tipi=$("#id_tipi option:selected").val();
	if(tipi==""){
		alert("Select container type");
		bloccato=true;
	}
	
	var lisaliq=$("#id_Aliquot_Type option:selected");
	if (lisaliq.length==0){
		alert("Select biological content");
		bloccato=true;
	}
	//guardo se sono state inserite le colonne
	var colo=$("#id_col").val();
	if(colo==""){
		alert("Insert columns number");
		bloccato=true;
	}
	else{
		if((!regex.test(colo))||(colo=="0")){
			alert("You can only insert number. Please correct columns value");
			bloccato=true;
		}
	}
	//guardo se sono state inserite le righe
	var rig=$("#id_row").val();
	if(rig==""){
		alert("Insert rows number");
		bloccato=true;
	}
	else{
		if((!regex.test(rig))||(rig=="0")){
			alert("You can only insert number. Please correct rows value");
			bloccato=true;
		}
	}
	
	//la posizione non è obbligatoria, però se il data table con la lista delle posizioni vuote
	//contiene qualcosa, allora devo controllare che l'utente abbia selezionato
	var lisvuote=$("#tabposition .dataTables_empty");
	var padre=$("#id_father").val();
	//vuol dire che c'è qualcosa nella tabella e allora devo fare il controllo
	if (lisvuote.length==0){
		var selezionati = fnGetSelected( tab );
		if (selezionati.length==0){
			alert("Select a position for container");
			bloccato=true;
		}
		else{
			var pos=$(selezionati[0]).children(":nth-child(1)").text();
		}
	}
	else{
		if(padre!=""){
			alert("Click on \"Empty positions\" and select a position for container");
			bloccato=true;
		}
		pos="";
	}
	
	if((bloccato==false)){
		var tipo=$("#id_tipi option:selected").text();
		var geom=rig+"x"+colo;
		
		tab2.fnAddData( [null, contacont,barc, tipo,geom,padre,pos ] );
		
		//creo il dizionario con i dati dentro
		var diz={};
		diz['barcode']=barc;
		diz['conttipo']=tipi;
		diz['geometry']=geom;
		diz['padre']=padre;
		diz['pos']=pos;
		
		var lisaliq=$("#id_Aliquot_Type option:selected");
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
	}
}

$(document).ready(function () {
	
	$("#tabposition").dataTable({
		"bPaginate": true,
		"bLengthChange": true,
		"bFilter": true,
		"bSort": true,
		"bInfo": true,
		"aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
		"bAutoWidth": false });
	
	var oTable = $("#cont_table").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { 
               "sTitle": null, 
               "sClass": "control_center", 
               "sDefaultContent": '<img src="/archive/archive_media/img/admin/icon_deletelink.gif" width="15px" height="15px" >'
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
});