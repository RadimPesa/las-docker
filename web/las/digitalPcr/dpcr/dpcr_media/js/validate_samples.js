aliquots_toval = {};
aliquots_validated = {};
hybrid_prot = {};
aliquot_warnings = 0;
session_id = '';



// init document
jQuery(document).ready(function(){
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
    session_id = jQuery('#sessionid').attr('val');

    generate_toval_table();
    generate_validated_table();
    readTable();
    jQuery('#submit_barcode').click(function(event){
        submit_identifier();
    });

    save_stop();
    proceed();

        
});


// init the data table
function generate_toval_table(){
    /*
     * Initialse DataTables, with image on the first column
     */
    jQuery("table#aliquot_toval_table").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Id Aliquot" },
            { "sTitle": "Genealogy ID" },
            { "sTitle": "Sample features" },
            { "sTitle": "Owner" },
            { "sTitle": "Volume" },
            { "sTitle": "Concentration" },
            { "sTitle": "Taken Volume" },
            { "sTitle": "Barcode" },
            { "sTitle": "Father Container" },
            { "sTitle": "Position" }
        ],
    "bAutoWidth": false ,
    "aaSorting": [[0, 'desc']],
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 0 ] },
    ],
    });

}



function generate_validated_table(){
    /*
     * Initialse DataTables, with image on the first column
     */
    var oTable = jQuery("table#aliquot_validated_table").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Id Aliquot" },
            { "sTitle": "Genealogy ID" },
            { "sTitle": "Sample features" },
            { "sTitle": "Owner" },
            { "sTitle": "Original Volume" },
            { "sTitle": "Original Concentration" },
            { "sTitle": "Taken Volume (Editable)" },
            { "sTitle": "Exhausted",
              "sDefaultContent": '<input type="checkbox" name="exhausted" value="exhausted" />'},
            { "sTitle": "Barcode"}

        ],
        "bAutoWidth": false ,
        "aaSorting": [[0, 'desc']],
        "aoColumnDefs": [
            { "bVisible": false, "aTargets": [ 0, 8] },
            { "bSortable": false, "aTargets": [ 8] }
        ],
        'fnDrawCallback': function () {
            jQuery('#aliquot_validated_table > tbody > tr').find('td:eq(5)').editable( 
                function(value, settings) { 
                    return(value);
            }, {
            "callback": function( sValue, y ) {
                var aPos = oTable.fnGetPosition( this );
                aliquot_warnings = 0;
                oTable.fnUpdate( parseFloat(sValue), aPos[0], aPos[2] );
            },
            "height": "12px",
            "width": "50px"
        }
            )
        },
        'fnRowCallback': function(nRow, aData, iDisplayIndex, iDisplayIndexFull) {
            console.log(aData);
            if (aData[4] < aData[6]) {
                $('td:eq(0)', nRow).addClass('conditionalRowColor');
                $('td:eq(1)', nRow).addClass('conditionalRowColor');
                $('td:eq(2)', nRow).addClass('conditionalRowColor');
                $('td:eq(3)', nRow).addClass('conditionalRowColor');
                $('td:eq(4)', nRow).addClass('conditionalRowColor');
                $('td:eq(5)', nRow).addClass('conditionalRowColor');
                $('td:eq(6)', nRow).addClass('conditionalRowColor');
                $('td:eq(7)', nRow).addClass('conditionalRowColor');
                $('td:eq(8)', nRow).addClass('conditionalRowColor');
                aliquot_warnings++;
                }
            else{
                $('td:eq(0)', nRow).removeClass('conditionalRowColor');
                $('td:eq(1)', nRow).removeClass('conditionalRowColor');
                $('td:eq(2)', nRow).removeClass('conditionalRowColor');
                $('td:eq(3)', nRow).removeClass('conditionalRowColor');
                $('td:eq(4)', nRow).removeClass('conditionalRowColor');
                $('td:eq(5)', nRow).removeClass('conditionalRowColor');
                $('td:eq(6)', nRow).removeClass('conditionalRowColor');
                $('td:eq(7)', nRow).removeClass('conditionalRowColor');
                $('td:eq(8)', nRow).removeClass('conditionalRowColor');
            }
            return nRow;
        }
    });

   jQuery("#aliquot_validated_table tbody td span.ui-icon-pencil").live('click', function () {
        var posAl = jQuery("#aliquot_validated_table").dataTable().fnGetPosition(jQuery(this).parents('td')[0]);
        var idAl = jQuery("#aliquot_validated_table").dataTable().fnGetData(posAl[0]);
        console.log(idAl);
        editRow(idAl, posAl[0]);
    } );

}



function checkKeyP(evt){
    var charCode = (evt.which) ? evt.which : event.keyCode
    if ( charCode == 13 ) //codice ASCII del carattere carriage return (invio)
            submit_identifier();
}




function submit_identifier(){
    var sample_identifier = jQuery('#alidentifier').val();
    // check if there is a value
    if (sample_identifier == ""){
        alert("Insert an indentifier!");
        return;
    }
    // check if exists in the current session
    if (aliquots_toval.hasOwnProperty(sample_identifier)){
        console.log(aliquots_toval[sample_identifier]);
        // compute cRNA volume according to the protocol info
        
        // check if the volume is sufficient for the hybridization
        if (aliquots_toval[sample_identifier]['volumetaken'] > aliquots_toval[sample_identifier]['volume']){
            alert("Insufficient Volume!","Warning");
        }
        aliquots_validated[sample_identifier] = aliquots_toval[sample_identifier];

        // remove the aliquot from the list
        jQuery.each(jQuery("#aliquot_toval_table").dataTable().fnGetData(), function(key, d) {
            if (d[7] == jQuery('#alidentifier').val()){
                jQuery("#aliquot_toval_table").dataTable().fnDeleteRow(key);
                return false;
            }
        });
        delete aliquots_toval[sample_identifier];
        // insert the new values
        aliquot_warnings = 0;
        jQuery('#aliquot_validated_table').dataTable().fnAddData([aliquots_validated[sample_identifier]['idaliquot'], aliquots_validated[sample_identifier]['genid'], aliquots_validated[sample_identifier]['sample_features'], aliquots_validated[sample_identifier]['owner'], aliquots_validated[sample_identifier]['volume'], aliquots_validated[sample_identifier]['concentration'], aliquots_validated[sample_identifier]['volumetaken'], null, aliquots_validated[sample_identifier]['barcode']]);
        if (Object.keys(aliquots_toval).length == 0){
            jQuery('#proceed').removeAttr('disabled');
            jQuery('#save_stop').removeAttr('disabled');
        }
    }
    else{
            alert("Invalid identifier!");
    }
    jQuery('#alidentifier').val('');

}



function readTable(){
    var data = jQuery("#aliquot_toval_table").dataTable().fnGetData();
    jQuery.each(data, function(key, d) {
        aliquots_toval[d[7]] = {'idaliquot':d[0], 'genid': d[1], 'sample_features':d[2], 'owner':d[3], 'volume':parseFloat(d[4]), 'concentration':parseFloat(d[5]), 'volumetaken': parseFloat(d[6]), 'barcode':d[7], 'father_container':d[9], 'pos':d[10]}
    });
}




function prepareData(){
    jQuery.each( jQuery("#aliquot_validated_table").dataTable().fnGetNodes(), function(i, row){
        rowData = jQuery("#aliquot_validated_table").dataTable().fnGetData(i);
        var sample_identifier = rowData[8];
        console.log(sample_identifier);    
        aliquots_validated[sample_identifier]['exhausted'] = jQuery(row).find(':checkbox')[0].checked;
        aliquots_validated[sample_identifier]['volumetaken'] = rowData[6];
    });
}


function save_stop() {
    jQuery("#save_stop").click(function() {
        console.log('save and stop');
        if (aliquot_warnings>0){
            alert('Please verify the preparation of the aliquots highlighted in yellow.');
        }
        else{
            prepareData();
            submitData('stop');    
        }
    });  
}


function proceed() {
    jQuery("#proceed").click(function() {
        if (aliquot_warnings>0){
            alert('Please verify the preparation of the aliquots highlighted in yellow.');
        }
        else{
            prepareData();
            submitData('continue');
        }
    });  
}


function submitData (status){
    var response = {'val_aliquots':  aliquots_validated, 'status':status, 'sessionid': session_id};
    var json_response = JSON.stringify(response);
    console.log(json_response);
    var url = base_url + '/validate_samples/';
    
    jQuery.ajax({
        type:'POST',    
        url:url,
        data: json_response, 
        dataType: "json",                  
        error: function(data) { 
            alert("Submission data error! Please, try again.\n" + data.status, "Warning");
        }
    });

}