var table_name = "#statusTable"; var counter = 0; var newStatus = {};
var barcodeUsed = {}

jQuery(document).ready(function () {
    var oTable = jQuery(table_name).dataTable( {
	    "bProcessing": true,
	     "aoColumns": [
                { 
                   "sTitle": null, 
                   "sClass": "control center", 
                   //"sDefaultContent": '<img src="' + base_url + '/xeno_media/img/admin/icon_deletelink.gif">'
                   "sDefaultContent": '<img src="/xeno_media/img/admin/icon_deletelink.gif">'
                },
                { "sTitle": "Operation Counter" },
                { "sTitle": "Identifier" },
                { "sTitle": "Barcode" },
                { "sTitle": "Old Status" },
                //{ "sTitle": "New Status" },
            ],
        "bAutoWidth": false ,
        "aaSorting": [[1, 'desc']],
        "aoColumnDefs": [
            { "bSortable": false, "aTargets": [ 0 ] },
        ],
    });
    /* Add event listener for delete row  */
   jQuery(table_name +' tbody td img').live('click', function () {
        var identifier = jQuery(jQuery(jQuery(this).parents('tr')[0]).children()[2]).text();
        var barcode = jQuery(jQuery(jQuery(this).parents('tr')[0]).children()[3]).text();
        delete newStatus[identifier];
        delete barcodeUsed[barcode];
        var nTr = jQuery(this).parents('tr')[0];
	    jQuery(table_name).dataTable().fnDeleteRow( nTr );
    } );
});


function alreadyUsed(identifier){
	for (id in barcodeUsed){
		if (identifier == id)
			return true;
	}
	return false;
}

//funzione che aggiunge una nuova riga alla tabella riepilogativa dei topi da inserire.
//preleva i dati dai campi di input
function addRow(tableID) {
if (document.getElementById("id_barcode").value != ""){
	var barcode = document.getElementById("id_barcode").value.toUpperCase();
	if (!alreadyUsed(barcode)){
	    var url = base_url + "/api.status/" + barcode;
	    var oldS = "";
	    var newS = document.getElementById('tStatus').value;
	    jQuery.ajax({
	    	url:url,
			method: 'get',
			success: function(transport) {
				console.log(transport);
				if ((transport == "newbarcode")||(transport=="otherwg")){
				    alert("This xenopatients does not exist.");
			    }else{
			    	for (bioM in transport){
			    		for (id in transport[bioM]){
			    			console.log(id);
			    			oldS = transport[bioM][id];
				    		var url = base_url + "/api.status/destination/" + oldS + '2' + newS + '/' + id;
					        //mando anche il barcode all'API per farmi dare cosi' anche il genID, altrimenti avrei dovuto usare un'altra API
						    jQuery.ajax({
								url:url,
								method: 'get',
								async: false,
								success: function(transport) {
									console.log(transport);
								    var response = transport.responseJSON;    
							    	flag = transport.flag;
								    if (flag){
									    document.getElementById('finishDiv').style.display = 'inline';
									    document.getElementById('listDiv').style.display = 'inline';
										jQuery(table_name).dataTable().fnAddData( [null, counter, id, barcode, oldS ] );
										newStatus[id] = newS;
										barcodeUsed[barcode] = true;
										counter++;
									    //vedo se era un topo presente nella lista dei sacrifici; se sì, segnalo il sacrificio all'operatore
									    //console.log(jQuery('#'+id));
									    //jQuery('#'+id).append("<img id='" + id + "_img' src='" + base_url + "/xeno_media/img/admin/icon_success.gif'></img>");
                                        jQuery('#'+id).append("<img id='" + id + "_img' src='/xeno_media/img/admin/icon_success.gif'></img>");
								    }else{
									    alert("The operation required cannot be performed.");
								    }
								}
							    
						    });
			    		}
			    		
		    		}
			    }
		    }
	    });
    }else{
        alert("You've already used this barcode in this session.");
    }
}else{
	alert("You've inserted a blank barcode")
}
document.getElementById('id_barcode').value = "";
document.getElementById('id_barcode').focus();
}

function checkKey(evt){
	var charCode = (evt.which) ? evt.which : event.keyCode
	if ( charCode == 13 ) //codice ASCII del carattere carriage return (invio)
		addRow('statusTable');
}

function save(){
	jQuery("#finish").attr("disabled",true);
	var url = base_url + '/miceStatus/';
	jQuery.ajax({
		url: url,
		type: 'POST',
		data: {'newStatus': JSON.stringify(newStatus)},
		dataType: 'text', 
	}); 
}
