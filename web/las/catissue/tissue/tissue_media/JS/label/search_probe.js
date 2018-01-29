dizprobe={};

function inizializza(){
	$("#search_gene").autocomplete({
		source:base_url+'/api/label/gene/autocomplete/',
		select: function (event, ui) {
            $("#search_gene").attr("gene_uuid",ui.item.id);            
        }	
	});
	
	$("#search_target").click(cercaGene);
	
	$("#search_gene").keypress(function(event){
		if ( event.which == 13 ) {
			cercaGene();
		}
	});
	
	jQuery("#table_mut").dataTable({
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "target Id" },
            { "sTitle": "Name" },
            { "sTitle": "Gene" },
            { "sTitle": "Type" },
            { "sTitle": "Reference" },
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
            { "sTitle": "Gene" },
            { "sTitle": "Type" },
            { "sTitle": "Reference" },
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
	
	$("#selez").click(selezionaTarget);
	
	$("#table_mut tbody").click(function(event) {
        if (jQuery(jQuery(event.target.parentNode)[0]).is("tr.gene_el")){
        	jQuery(jQuery('#table_mut').dataTable().fnSettings().aoData).each(function (){
                jQuery(this.nTr).removeClass('row_selected');
        	});
        	jQuery(event.target.parentNode).toggleClass('row_selected');            
        }        
    });
	
	/* Add event listener for deleting row  */
    $("#table_mut_selez tbody td.control_center img").live("click", function () {
        var gene = $($($(this).parents('tr')[0]).children()[1]).text();
        delete dizprobe[gene];
        var nTr = $(this).parents('tr')[0];
        $("#table_mut_selez").dataTable().fnDeleteRow( nTr );
        $("#selez").attr("disabled",false);
        $("#nomeprobe").val("");
    });
}

function cercaGene(){
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
            alert("Submission data error! Please, try again.\n" + data.status, "Warning");
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
		tipomarker=$("#tipo_marker").val();
		lismarkerpresenti=window.opener.dizmarker[tipomarker];
		
		//mi da' il numero di colonne che ci sono nel data table
		var lunghezza = oSettings.aoColumns.length;
		for(var j=0;j<selezionati.length;j++){
			var idgen=$(selezionati[j]).children(":nth-child(1)").text();
			
			//solo se non ho gia' messo la riga sotto
			if(!(idgen in dizprobe)){
				var nomemark=$(selezionati[j]).children(":nth-child(1)").text();
				if($.inArray(nomemark,lismarkerpresenti)==-1){
					alert("Marker does not exist. First you have to create it.");
					return;
				}
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
			}
			$(selezionati[j]).toggleClass('row_selected');
			$("#selez").attr("disabled",true);
		}
	}
}

function chiudiFinestra(){
	var marker=$("#nomeprobe").val();
	if (marker==""){
		alert("Please select a probe");
		return;
	}
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

$(document).ready(function () {
	$("a:contains('LAS Home')").remove();
	$("#home").removeAttr("href");
	inizializza();
	
	$("#close").click(chiudiFinestra);
});
