var table_name = "#loadingTable"; var counter = 0; var newMice = {};

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
                { "sTitle": "Barcode" },
                { "sTitle": "Gender" },
            ],
        "bAutoWidth": false ,
        "aaSorting": [[1, 'desc']],
        "aoColumnDefs": [
            { "bSortable": false, "aTargets": [ 0 ] },
        ],
    });
    /* Add event listener for delet row  */
   jQuery(table_name +' tbody td img').live('click', function () {
        var barcodeM = jQuery(jQuery(jQuery(this).parents('tr')[0]).children()[2]).text();
        delete newMice[barcodeM];
        var nTr = jQuery(this).parents('tr')[0];
	    jQuery(table_name).dataTable().fnDeleteRow( nTr );
    } );
});

//funzione che aggiunge una nuova riga alla tabella riepilogativa dei topi da inserire.
function addRow() {
	if (document.getElementById("id_barcode").value != ""){
		var barcode = document.getElementById("id_barcode").value.toUpperCase();
		if (!alreadyUsed(barcode)){
		    var url = base_url + "/api.status/" + barcode;
		    jQuery.ajax({
		        url: url,
			    type: 'get',
			    success: function(transport) {
				    if (transport == "newbarcode"){
						jQuery("#finish").css("display", "inline");
					    if(document.getElementById('listDiv').style.display == 'none')
						    document.getElementById('listDiv').style.display = 'inline';
						var gender = jQuery("input:radio[name='gender']:checked").val();
						if (gender == 0)
							gender = "male";
						else
							gender = "female";
						newMice[barcode] = gender;
    					jQuery(table_name).dataTable().fnAddData( [null, counter, barcode, gender ] );
    					//console.log(newMice);
    					counter++;
				    }else{
					    alert("You can't insert a mouse with this barcode. It already exists.");
				    }
			    }
			});
	    }else{
	        alert("You've already inserted this barcode in this uploading session.");
	    }
	}else{
		alert("You've inserted a blank barcode")
	}
document.getElementById('id_barcode').value = "";
document.getElementById('id_barcode').focus();
}

function alreadyUsed(barcode){
    for (b in newMice){
    	if (b == barcode)
    		return true;
    }
    return false;
}

function checkKey(e){
	//alert(evt.which);
	var charCode = (e.which) ? e.which : event.keyCode
	if ( charCode == 13 ) //codice ASCII del carattere carriage return (invio)
		addRow('loadingTable');
}

function save(){
	jQuery("#finish").attr("disabled",true);
	var url = base_url + '/miceloading/';
	console.log(url);
	jQuery.ajax({
		url: url,
		type: 'POST',
		data: {'newMice': JSON.stringify(newMice)},
		dataType: 'text',
	}); 
}
