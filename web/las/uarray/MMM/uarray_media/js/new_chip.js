chipsRequested = {};
chipsCounter = 0;

jQuery(document).ready(function(){

    jQuery("input#id_barcode").val("");

    jQuery("input#id_barcode").focus();
    jQuery('#id_exp_date').datepicker({ minDate: 1, dateFormat: "yy-mm-dd" });
    jQuery("#dialog-form").find('#id_exp_date').datepicker({ dateFormat: "yy-mm-dd" });
    

    generate_table();
    initRequest ();

    jQuery('#submit_chips').attr("disabled", "disabled");


    // CRFS TOKEN
    jQuery('html').ajaxSend(function(event, xhr, settings) {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
        // Only send the token to relative URLs i.e. locally.
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
    });
});



// init the data table
function generate_table(){
    /*
     * Initialse DataTables, with image on the first column
     */

    jQuery("table#chip_table").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "#" },
            { "sTitle": "Barcode" },
            { "sTitle": "Type" },
            { "sTitle": "Owner" },
            { "sTitle": "Exp Date" },
            { "sTitle": "Lot" },
            { "sTitle": "Dmap file" },
            { "sTitle": "Notes" },
            {"sTitle": "idType" },
            { "sTitle": null, 
              "sClass": "control center", 
              "sDefaultContent": '<span class="ui-icon ui-icon-closethick"></span><span class ="ui-icon ui-icon-pencil"></span>'
            },
        ],
    "bAutoWidth": false ,
    "aaSorting": [[0, 'desc']],
    "aoColumnDefs": [
        { "bSortable": false, "aTargets": [ 9 ] },
        { "bVisible": false, "aTargets": [ 8 ] },
        ]
    });

    /* Add event listener for delete row  */
   jQuery(document).on('click', "#chip_table tbody td span.ui-icon-closethick", function(event) {
        var nTr = jQuery(this).parents('tr')[0];
        console.log(nTr);
        var posChip = jQuery("#chip_table").dataTable().fnGetPosition(jQuery(this).parents('td')[0]);
        var idChip = jQuery("#chip_table").dataTable().fnGetData(posChip[0]);
        delete chipsRequested[idChip[1]];
        chipsCounter--;
        if (chipsCounter== 0){
            jQuery('#submit_chips').attr('disabled', 'disabled');
        }
        jQuery("table#chip_table").dataTable().fnDeleteRow( nTr );
    } );
    /* Add event listener for edit row  */
   jQuery(document).on('click', "#chip_table tbody td span.ui-icon-pencil", function(event){
        var posChip = jQuery("#chip_table").dataTable().fnGetPosition(jQuery(this).parents('td')[0]);
        var idChip = jQuery("#chip_table").dataTable().fnGetData(posChip[0]);
        console.log(idChip);
        if (idChip[1] != "")
            editRow(idChip[1], posChip[0]);
        else
            editRow(idChip[2], posChip[0]);
    } );


}


function checkChipExists (chipbarcode){
    if (chipsRequested.hasOwnProperty(chipbarcode)){
        return true;
    }
    else{
        var url =  base_url + '/api.getchip/' + chipbarcode + '/info';
        var checkFlag = true;
        jQuery.ajax({
            type: 'get',
            url: url,
            async: false,
            success: function(transport) {
                if (transport.hasOwnProperty('response')){
                    checkFlag = false;
                }
                return checkFlag;
            }
        });
        return checkFlag;
    }
}

function checkKeyP(evt){
    var charCode = (evt.which) ? evt.which : event.keyCode
    if ( charCode == 13 ) //codice ASCII del carattere carriage return (invio)
         insertRow();
}


// insert a new row using the data of the form
function insertRow(){
    var table = jQuery("#chip_table");  
    // initialize variable depending on genealogy
  
    var barcode = jQuery("#id_barcode").val();
    var owner = jQuery("#id_owner").val();
    var chipType = jQuery("#id_type option:selected").text();
    var lot = jQuery("#id_lot").val();
    var dmap = jQuery("#id_DMAP_file").val();
    var date = jQuery("#id_exp_date").val();
    var notes = jQuery("#id_notes").val();
    var idType = jQuery("#id_type option:selected").val();

    if (barcode == ""){
        alert("Insert the barcode");
    }
    else{
        if (owner == "" && lot=="" && dmap == "" && date == ""){
            alert ("All the following fields should be specified: owner, exp data, lot and dmap file.");
        }
        else{
            if (checkChipExists(barcode) == false){
                chipsCounter++;
                console.log([chipsCounter, barcode, chipType, owner, date, lot, dmap, notes, idType, null]);
                updateDict(chipsCounter, barcode, owner, chipType, lot, dmap, date, notes, idType);
                table.dataTable().fnAddData([chipsCounter, barcode, chipType, owner, date, lot, dmap, notes, idType , null] );
            }
            else{
                alert("Chips is already present in the system. Please check the barcode");
            }
        }
    }
    jQuery('#id_barcode').val('');
    jQuery('#id_barcode').focus();
}


// edit a row of the table
function editRow(idAl, posAl){
    console.log("editRow");
    console.log(idAl);
    console.log(chipsRequested[idAl]);
	jQuery("#dialog-form").find('input[name=barcode]').attr('value',idAl);
    jQuery("#dialog-form").find('input[name=barcode]').attr('disabled','disabled');
	jQuery("#dialog-form").find('select[name=type]').find('option[value=' + chipsRequested[idAl]['idType']+']').attr('selected','selected');
	jQuery("#dialog-form").find('input[name=owner]').attr('value',chipsRequested[idAl]['owner']);
	jQuery("#dialog-form").find('input[name=exp_date]').attr('value',chipsRequested[idAl]['exp_date']);
	jQuery("#dialog-form").find('input[name=lot]').attr('value',chipsRequested[idAl]['lot']);
	jQuery("#dialog-form").find('input[name=DMAP_file]').attr('value',chipsRequested[idAl]['dmap']);
	jQuery("#dialog-form").find('textarea[name=notes]').attr('value',chipsRequested[idAl]['notes']);


    jQuery( "#dialog-form" ).dialog({
            resizable: false,			
            //height: 465,
			width: 500,
			modal: true,
            draggable: false,
			buttons: {
					"Ok": function(){
							// take the values from popup
                            var owner = jQuery("#dialog-form").find('input[name=owner]').val();
                            var date = jQuery("#dialog-form").find('input[name=exp_date]').val();
                            var lot = jQuery("#dialog-form").find('input[name=lot]').val();
                            var dmap = jQuery("#dialog-form").find('input[name=DMAP_file]').val();
                            var notes = jQuery("#dialog-form").find('textarea[name=notes]').val();
                            var chipType = jQuery("#dialog-form").find("select[name=type] option:selected").text();
                            var idType = jQuery("#dialog-form").find("select[name=type] option:selected").val();
                            var counter = chipsRequested[idAl]['counter'];
                            delete chipsRequested[idAl];
                            updateDict(counter, idAl, owner, chipType, lot, dmap, date, notes, idType);
                            // update the row with the new values

                            updateRowTable(idAl, posAl);
							// popup close
						    jQuery('#dialog-form').dialog("close");
						    
						},
					"Cancel": function(){
                        // edit canceled
                        jQuery(this).dialog("close");
                        }
					
			}
			
		});
        
}



// update a row (pencil button)
function updateRowTable(idAl, posAl){
        jQuery("#chip_table").dataTable().fnUpdate([chipsRequested[idAl]['counter'], idAl, chipsRequested[idAl]['chipType'], chipsRequested[idAl]['owner'], chipsRequested[idAl]['exp_date'], chipsRequested[idAl]['lot'], chipsRequested[idAl]['dmap'], chipsRequested[idAl]['notes'], chipsRequested[idAl]['idType'], null], posAl);

}



// update dictionary. The key is the sample_identifier (genealogy or label). Manage the two cases
function updateDict(counter, barcode, owner, chipType, lot, dmap, date, notes, idType){
    chipsRequested[barcode] = {'owner':owner, 'chipType': chipType, 'lot': lot, 'dmap': dmap, 'exp_date': date,'notes':notes, 'counter':counter, 'idType':idType};

    if (counter > chipsCounter)
        chipsCounter = counter;
    if (chipsCounter > 0)
        jQuery('#submit_chips').removeAttr("disabled");

}

function initRequest (){
    jQuery("#submit_chips").click( function(event){
            //event.stopImmediatePropagation();
            //event.preventDefault();
            console.log('submit');
            var url = base_url + "/new_chip/";
            //serializzo tutto
            var json_response = JSON.stringify(chipsRequested);
            // invio al server
            console.log(json_response);
            jQuery.ajax({
                        type:'POST',    
                        url:url,
                        data: json_response, 
                        dataType: "json",                  
                        error: function(data) { 
                            alert("Submission data error! Please, try again.\n" +data.responseText.slice(0,500), "Error"); 
                        }
            });
     });
}
