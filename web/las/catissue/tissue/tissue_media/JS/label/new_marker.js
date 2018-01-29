dizprobe={};

//dato il nome di un parametro presente nella URL, restituisce il suo valore
function getUrlParameter(sParam)
{
    var sPageURL = window.location.search.substring(1);
    var sURLVariables = sPageURL.split('&');
    for (var i = 0; i < sURLVariables.length; i++) 
    {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == sParam)
        {
            return sParameterName[1];
        }
    }
    return null;
}

function inizializza(){
	tecn=$("#nometecn").val();
	$(".f input").attr("size","10");
	$("#id_dilution1,#id_dilution2").attr("size","3");
	$("#id_gene").attr("size","35");
	var idtecnica=getUrlParameter("technique");
	if (idtecnica==null){
		idtecnica=$("#idtecn").val();
	}
	//prendo dal dizionario i valori
	var dizval=dizrel[idtecnica];
	var nomemark=dizval["name"];
	$("label[for='id_name']").text(nomemark+" name:");
	$("label[for='id_time']").text(dizval["time"]+":");
	$("label[for='id_temperature']").text(dizval["temperature"]+":");
	$("#nomemarker").val(nomemark);
	//se non e' un probe allora cancello il valore da quegli input per fare in modo che l'utente lo inserisca dalla schermata, cioe' scelga un gene 
	//collegato ad un anticorpo
	if((tecn!="FISH")&&(tecn!="CISH")&&(tecn!="RNAScope")){
		$("#nomeprobe,#uuid").val("");
	}
	else{
		//altrimenti metto a read only il campo per inserire il nome del marker, evitando che l'utente lo modifichi, visto che l'ha gia' inserito
		//prima nella schermata del modulo di annotazioni
		$("#id_name").attr("readonly","readonly");
	}
	
	$("#id_producer").autocomplete({
		source:base_url+'/ajax/label/producer/autocomplete/'
	});
	
	$("#id_gene").keydown(function(){
		$("#id_gene").attr("gene_uuid","");
		$("#uuid").val("");
	});
	
	$("#id_gene").autocomplete({
		source:base_url+'/api/label/gene/autocomplete/',
		select: function (event, ui) {
			//usato solo negli anticorpi: metto il valore in id_gene
            $("#id_gene").attr("gene_uuid",ui.item.id);
            $("#uuid").val(ui.item.id);
            //se voglio bloccarlo e non fargli fare piu' niente dopo quello che ho scritto, allora metto return false
            //return false;
        }
	//mi fa vedere la lista dei valori formattati coerentemente in base ai tag html. Ad esempio il gene
	//in grassetto e l'altra parte piu' piccola. Il problema e' che il valore selezionato dalla lista 
	//diventa il valore dell'attributo "value" dell'input text e li' non si riesce a fargli interpretare 
	//i tag html
	})/*.data("autocomplete")._renderItem = function (ul, item) {
        return $("<li></li>")
            .data("item.autocomplete", item)
            .append("<a>" + item.label + "</a>")
            .appendTo(ul);
    }*/;
	
	/*$("#search_target").click(cercaGene);
	
	$("#search_gene").keypress(function(event){
		if ( event.which == 13 ) {
			cercaGene();
		}
	});*/
	
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
	
	jQuery("#table_mut").dataTable({
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "target Id" },
            { "sTitle": "Name" },
            { "sTitle": "Genes" },
            { "sTitle": "Type" },
            { "sTitle": "Ref." },
            { "sTitle": "Start" },
            { "sTitle": "End" },
            { "sTitle": "Length" },
        ],
	    "bAutoWidth": false ,
	    "bDeferRender": true,
	    "bProcessing": true,
	    "aaSorting": [[1, 'desc']],
	     "aoColumnDefs": [
	        { "bVisible": false, "aTargets": [ 0 ] },
	    ],
	    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
	    "fnRowCallback": function( nRow, aData, iDisplayIndex ) {
	    	if(nRow.className.indexOf("gene_el")==-1){
	        	nRow.className += " gene_el";
			}
	        return nRow;
	    }
	});
	
	jQuery("#table_mut_selez").dataTable({
        "bProcessing": true,
         "aoColumns": [
			{ 
			    "sTitle": null, 
			    "sClass": "control_center", 
			    "sDefaultContent": "<img src='"+media_url+"/tissue_media/img/admin/icon_deletelink.gif' width='15px' height='15px' >"
			},
            { "sTitle": "Name" },
            { "sTitle": "Genes" },
            { "sTitle": "Type" },
            { "sTitle": "Ref." },
            { "sTitle": "Start" },
            { "sTitle": "End" },
            { "sTitle": "Length" },
        ],
	    "bAutoWidth": false ,
	    "bDeferRender": true,
	    "bProcessing": true,
	    "aaSorting": [[1, 'desc']],
	    "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
	});
	
	//$("#selez").click(selezionaTarget);
		
}

/*function cercaGene(){
    var geneid = $("#search_gene").attr("gene_uuid");
    var url =  base_url+"/api/label/ampliconinfo/";
    jQuery.ajax({
        type: 'GET',
        data: {'gene_uuid': geneid},
        url: url,
        success: function(transport) {
            console.log(transport);
            jQuery('#table_mut').dataTable().fnClearTable();
            //se la lista che contiene i probe e' vuota, allora cancello comunque i dati nella tabella e poi lo comunico all'utente
            if(transport.length==0){
            	alert("No probe found");
            }
            else{
            	$(transport).each(function(index, value){                
            		jQuery('#table_mut').dataTable().fnAddData([value['uuid'], value['name'], value['gene_symbol'], value['type'], value['ref'], value['start_base'], value['end_base'], value['length']]);
            	});
            }
        },
        error: function(data) {
            alert("Submission data error! Please try again.\n" + data.status, "Warning");
        }
    });
}

function selezionaTarget(){
	var tab=$("#table_mut").dataTable();
	var tabsotto=$("#table_mut_selez").dataTable();
	//ho un vettore con le righe selezionate dall'utente
	var selezionati = fnGetSelected( tab );
	if (selezionati.length==0){
		alert("Please select a probe");
	}
	else{
		var oSettings = tab.fnSettings();
		//mi da' il numero di colonne che ci sono nel data table
		var lunghezza = oSettings.aoColumns.length;
		for(var j=0;j<selezionati.length;j++){
			var idgen=$(selezionati[j]).children(":nth-child(1)").text();
			//solo se non ho gia' messo la riga sotto
			if(!(idgen in dizprobe)){
				var listadatitemp=new Array();
				//posto vuoto per la "X" della cancellazione
	 			listadatitemp.push(null)
				var listmp=new Array();				
				for (var k=0;k<lunghezza;k++){
					var figlio=":nth-child("+(k+1)+")";
					var dato=$(selezionati[j]).children(figlio).html();					
					listadatitemp.push(dato);
					var valore=$(selezionati[j]).children(figlio).text();
					listmp.push(valore);
				}
				var rowPos=tabsotto.fnAddData(listadatitemp);				
				dizprobe[listmp[0]]="";
				$("#nomeprobe").val(listmp[0]);
				//mi da' la posizione della tr che gli passo. [0] perche' per far funzionare getposition e usando jQuery e non js normale
				//devo accedere all'elemento interno all'involucro che mette jQuery quando recupera un oggetto DOM
				var pos=tab.fnGetPosition($(selezionati[j])[0]);
				//in data ho una lista con dento tutti i valori della riga della tabella. In [0] ho l'uuid che e' nella colonna nascosta iniziale
				var data =tab.fnGetData(pos);
				var uuid=data[0];
				$("#uuid").val(uuid);
			}
			$(selezionati[j]).toggleClass('row_selected');
			$("#selez").attr("disabled",true);
		}
	}
} */

function chiudiFinestra(){
	var marker=$("#nom_marker").val();
	var tipomarker=$("#tipo_marker").val();
	window.opener.$("#id_markname2").val(marker);
	window.opener.$("#add_btnprot").click();
	
	if(tipomarker in window.opener.dizmarker){
		var lista=window.opener.dizmarker[tipomarker];		
	}
	else{
		var lista=[];
	}
	lista.push(marker);
	window.opener.dizmarker[tipomarker]=lista;
	
	window.opener.$("#id_technique").attr("disabled",true);
	window.close();	
}

$(document).ready(function () {
	$("a:contains('LAS Home')").remove();
	$("#home").removeAttr("href");
	//guardo se sono nella prima pagina o in quella di conferma
	var chiudi=$("#close");
	if(chiudi.length==0){
		inizializza();
	}
	else{
		$("#close").click(chiudiFinestra);
	}

    $("#conferma1").click(function(event){		
		var regex=/^[0-9]+$/;
		var regex2=/^[0-9.]+$/;
		var diluiz1=$("#id_dilution1").val();
		if((diluiz1!="")&&(!regex.test(diluiz1))){
			alert("You can only insert number. Please correct value for dilution factor");
			event.preventDefault();
			return;
		}
		var diluiz2=$("#id_dilution2").val();
		if((diluiz2!="")&&(!regex.test(diluiz2))){
			alert("You can only insert number. Please correct value for dilution factor");
			event.preventDefault();
			return;
		}
		//il tempo puo' accettare valori decimali perche' e' espresso in ore
		var tempo=$("#id_time").val();
		if((tempo!="")&&(!regex2.test(tempo))){
			alert("You can only insert number. Please correct value for time");
			event.preventDefault();
			return;
		}
		var temp=$("#id_temperature").val();
		if((temp!="")&&(!regex.test(temp))){
			alert("You can only insert number. Please correct value for temperature");
			event.preventDefault();
			return;
		}
		
		if((tecn=="FISH")||(tecn=="CISH")||(tecn=="RNAScope")){
			var probeselez=$("#nomeprobe").val();
			if(probeselez==""){
				event.preventDefault();
				alert("Please select a probe");
				return;
			}
		}
		//se la tecnica e' un'altra
		else{
			var probeselez=$("#id_name").val();
			if(probeselez==""){
				event.preventDefault();
				alert("Please insert a valid name");
				return;
			}
			if((tecn=="IF")||(tecn=="IHC")){
				//controllo che l'utente abbia inserito un gene valido come obiettivo dell'anticorpo
				var uuid=$("#uuid").val();
				if((uuid=="")||(uuid==undefined)){
					event.preventDefault();
					alert("Please insert gene target");
					return;
				}
			}
		}
		//devo vedere se esiste gia' il marker guardando nella lista che mi ha passato il server
		//e se si' do' errore
		var nomemarker=$("#nomemarker").val();
		if($.inArray(probeselez,lismarker)!=-1){
			alert(nomemarker+" already exists. Please change name");
			event.preventDefault();
			return;
		}
	});
});
