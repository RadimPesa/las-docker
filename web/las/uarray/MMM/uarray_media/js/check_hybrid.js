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
    readProt();
    save_stop();
    proceed();

    jQuery('#protocol_info').click(function(event){
        jQuery( "#protocol-dialog" ).dialog({
            resizable: false,           
            modal: true,
            draggable: false,
            buttons: {    
                   "Ok": function(){
                        // edit canceled
                        jQuery(this).dialog("close");
                    }
                }
        });
    });
    jQuery('#recomupute').click(function(event){
        recomputeHyb ();
    });

        
});

function pad(n) { return ("0" + n).slice(-2); }

// init the data table
function generate_toval_table(){
    /*
     * Initialse DataTables, with image on the first column
     */
    var actionname = 'AliquotsToPrepare'
    var d = new Date();
    var user = jQuery('#user_name').attr('user');
    var filename = actionname + "_" + user + '_' + $.datepicker.formatDate('yy-mm-dd', d) + "--" + pad(d.getHours()) + "-" + pad(d.getMinutes()) + "-" + pad(d.getSeconds());
    jQuery("table#aliquot_toval_table").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Id Aliquot" },
            { "sTitle": "Genealogy ID" },
            { "sTitle": "Sample features" },
            { "sTitle": "Owner" },
            { "sTitle": "Experimental group" },
            { "sTitle": "Volume (ul)" },
            { "sTitle": "Concentration (ng/ul)" },
            { "sTitle": "Technical Replicates" },
            { "sTitle": "Barcode" },
            { "sTitle": "Plate position" },
            { "sTitle": "Plate" },
            { "sTitle": "Rack position" },
            { "sTitle": "Rack" },
            { "sTitle": "Freezer" },
        ],
    "bAutoWidth": false ,
    "aaSorting": [[0, 'asc']],
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 0 ] },
    ],
    "sDom":'T<\"clear\">lfrtip',
        "oTableTools": {
                "aButtons": [ "copy", 
                {
                                "sExtends": "csv",
                                "sButtonText": "Las",
                                "sTitle": filename,
                                "sFileName": "*.las",
                                "sFieldSeperator": "\t",
                                "sFieldBoundary": "",
                                "mColumns": "visible"
                }, 
                {
                                "sExtends": "pdf",
                                "sButtonText": "Pdf",
                                "sPdfOrientation": "landscape",
                                "sPdfMessage": "Laboratory Assistant Suite - Microarray Manager - " + user + " - " + $.datepicker.formatDate('yy/mm/dd', d) + " @ " + pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds()),
                                "sTitle": filename,
                                "mColumns": "visible"
                }
                , "print"],
                "sSwfPath": base_url + "/uarray_media/js/DataTables-1.9.4/extras/TableTools/media/swf/copy_csv_xls_pdf.swf"
        }
    });

}



function generate_validated_table(){
    /*
     * Initialse DataTables, with image on the first column
     */
    var actionname = 'PreparedAliquots'
    var d = new Date();
    var user = jQuery('#user_name').attr('user');
    var filename = actionname + "_" + user + '_' + $.datepicker.formatDate('yy-mm-dd', d) + "--" + pad(d.getHours()) + "-" + pad(d.getMinutes()) + "-" + pad(d.getSeconds());
    jQuery("table#aliquot_validated_table").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Id Aliquot" },
            { "sTitle": "Genealogy ID" },
            { "sTitle": "Barcode" },
            { "sTitle": "Sample features" },
            { "sTitle": "Owner" },
            { "sTitle": "Experimental group" },
            { "sTitle": "Original Volume (ul)" },
            { "sTitle": "Original Concentration (ng/ul)" },
            { "sTitle": "Technical Replicates" },
            { "sTitle": "cRNA Volume (ul)" },
            { "sTitle": "Water Volume (ul)" },
            { "sTitle": "Buffer (ul)" },
            { "sTitle": "Exhausted",
              "sDefaultContent": '<input type="checkbox" name="exhausted" value="exhausted" />'},
            { "sTitle": "",
              "sDefaultContent": '<span class ="ui-icon ui-icon-pencil"></span>'},
            { "sTitle": ""}

        ],
        "bAutoWidth": false ,
        "aaSorting": [[0, 'asc']],
        "aoColumnDefs": [
            { "bVisible": false, "aTargets": [ 0, 14] },
            { "bSortable": false, "aTargets": [ 12, 13, 14] }
        ],
        "sDom":'T<\"clear\">lfrtip',
        "oTableTools": {
                "aButtons": [ "copy", 
                {
                                "sExtends": "csv",
                                "sButtonText": "Las",
                                "sTitle": filename,
                                "sFileName": "*.las",
                                "sFieldSeperator": "\t",
                                "sFieldBoundary": "",
                                "mColumns": "visible"
                }, 
                {
                                "sExtends": "pdf",
                                "sButtonText": "Pdf",
                                "sPdfOrientation": "landscape",
                                "sPdfMessage": "Laboratory Assistant Suite - Microarray Manager - " + user + " - " + $.datepicker.formatDate('yy/mm/dd', d) + " @ " + pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds()),
                                "sTitle": filename,
                                "mColumns": "visible"
                }
                , "print"],
                "sSwfPath": base_url + "/uarray_media/js/DataTables-1.9.4/extras/TableTools/media/swf/copy_csv_xls_pdf.swf"
        },
        'fnRowCallback': function(nRow, aData, iDisplayIndex, iDisplayIndexFull) {
            if (aData[14] == "True") {
                $('td:eq(0)', nRow).addClass('conditionalRowColor');
                $('td:eq(1)', nRow).addClass('conditionalRowColor');
                $('td:eq(2)', nRow).addClass('conditionalRowColor');
                $('td:eq(3)', nRow).addClass('conditionalRowColor');
                $('td:eq(4)', nRow).addClass('conditionalRowColor');
                $('td:eq(5)', nRow).addClass('conditionalRowColor');
                $('td:eq(6)', nRow).addClass('conditionalRowColor');
                $('td:eq(7)', nRow).addClass('conditionalRowColor');
                $('td:eq(8)', nRow).addClass('conditionalRowColor');
                $('td:eq(9)', nRow).addClass('conditionalRowColor');
                $('td:eq(10)', nRow).addClass('conditionalRowColor');
                $('td:eq(11)', nRow).addClass('conditionalRowColor');
                $('td:eq(12)', nRow).addClass('conditionalRowColor');
                $('td:eq(13)', nRow).addClass('conditionalRowColor');
                $('td:eq(14)', nRow).addClass('conditionalRowColor');
                $('td:eq(15)', nRow).addClass('conditionalRowColor');
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
                $('td:eq(9)', nRow).removeClass('conditionalRowColor');
                $('td:eq(10)', nRow).removeClass('conditionalRowColor');
                $('td:eq(11)', nRow).removeClass('conditionalRowColor');
                $('td:eq(12)', nRow).removeClass('conditionalRowColor');
                $('td:eq(13)', nRow).removeClass('conditionalRowColor');
                $('td:eq(14)', nRow).removeClass('conditionalRowColor');
                $('td:eq(15)', nRow).removeClass('conditionalRowColor');
            }
            return nRow;
        }
    });
    jQuery(document).on('click','#aliquot_validated_table tbody td span.ui-icon-pencil', function() {
            var posAl = jQuery("#aliquot_validated_table").dataTable().fnGetPosition(jQuery(this).parents('td')[0]);
            var idAl = jQuery("#aliquot_validated_table").dataTable().fnGetData(posAl[0]);
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
    var idtype = '';
    // check if there is a value
    if (sample_identifier == ""){
        alert("Insert an indentifier!");
        return;
    }

    if (aliquots_toval.hasOwnProperty( 'B' + sample_identifier)){
        sample_identifier = 'B' + sample_identifier;
        idtype = 'B';
    }
    else{
        sample_identifier = 'S' + sample_identifier;
        idtype = 'S';
    }



    // check if exists in the current session
    if (aliquots_toval.hasOwnProperty(sample_identifier)){
        var alertI = "False"
        console.log(aliquots_toval[sample_identifier])
        var al_conc = parseFloat(aliquots_toval[sample_identifier]['concentration']);
        var al_repl = parseInt(aliquots_toval[sample_identifier]['replicates'])
        // compute cRNA volume according to the protocol info
        var cRNAVolume = (hybrid_prot['loadQuantity']/al_conc * al_repl);
        // check if the volume is sufficient for the hybridization
        if (cRNAVolume > parseFloat(aliquots_toval[sample_identifier]['volume'])){
            alert("Insufficient Volume!","Warning");
            alertI = "True";
        }
        var temp = cRNAVolume + hybrid_prot['hybBuffer'];
        console.log(cRNAVolume, hybrid_prot['loadQuantity'], parseFloat(aliquots_toval[sample_identifier]['concentration']), parseInt(aliquots_toval[sample_identifier]['replicates']));
        var waterVolume = (hybrid_prot['totalVolume'] - temp);
        aliquots_validated[sample_identifier] = aliquots_toval[sample_identifier];

        // remove the aliquot from the list
        jQuery.each(jQuery("#aliquot_toval_table").dataTable().fnGetData(), function(key, d) {
            if (idtype == 'B'){
                if (d[8] == jQuery('#alidentifier').val()){
                    jQuery("#aliquot_toval_table").dataTable().fnDeleteRow(key);
                    return false;
                }
            }
            else {
                if (idtype == 'S'){
                    if (d[8] == jQuery('#alidentifier').val()){
                        jQuery("#aliquot_toval_table").dataTable().fnDeleteRow(key);
                        return false;
                    }
                }
            }
        });
        delete aliquots_toval[sample_identifier];
        // insert the new values
        aliquots_validated[sample_identifier]['cRNAVolume'] = cRNAVolume.toFixed(2);
        aliquots_validated[sample_identifier]['waterVolume'] = waterVolume.toFixed(2);
        aliquots_validated[sample_identifier]['hybBuffer'] = hybrid_prot['hybBuffer'];
        aliquots_validated[sample_identifier]['loadQuantity'] = hybrid_prot['loadQuantity'];
        aliquots_validated[sample_identifier]['totalVolume'] = hybrid_prot['totalVolume'];
        aliquots_validated[sample_identifier]['warning'] = alertI;
        jQuery('#aliquot_validated_table').dataTable().fnAddData([aliquots_validated[sample_identifier]['idaliquot'], aliquots_validated[sample_identifier]['genid'], aliquots_validated[sample_identifier]['barcode'], aliquots_validated[sample_identifier]['sample_features'], aliquots_validated[sample_identifier]['owner'], aliquots_validated[sample_identifier]['exp_group'], aliquots_validated[sample_identifier]['volume'], aliquots_validated[sample_identifier]['concentration'], aliquots_validated[sample_identifier]['replicates'], aliquots_validated[sample_identifier]['cRNAVolume'], aliquots_validated[sample_identifier]['waterVolume'], aliquots_validated[sample_identifier]['hybBuffer'], null, null, aliquots_validated[sample_identifier]['warning'], aliquots_validated[sample_identifier]['barcode']]);
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
        var prefix = 'S';
        if (d[1] != ""){
            prefix = 'B';
        }
        aliquots_toval[prefix+d[8]] = {'idaliquot':d[0], 'genid': d[1], 'sample_features':d[2], 'owner':d[3], 'exp_group':d[4], 'volume':parseFloat(d[5]), 'concentration':parseFloat(d[6]), 'replicates': parseInt(d[7]), 'barcode':d[8],  'pos':d[9], 'father_container':d[10], 'rack_pos':d[11], 'rack': d[12], 'freezer':d[13]}
    });
}

function readProt(){
    hybrid_prot['loadQuantity'] = parseFloat(jQuery("#protocol-dialog").find('td[name=loadQuantity]').attr('val'));
    hybrid_prot['hybBuffer'] = parseFloat(jQuery("#protocol-dialog").find('td[name=hybBuffer]').attr('val'));
    hybrid_prot['totalVolume'] = parseFloat(jQuery("#protocol-dialog").find('td[name=totalVolume]').attr('val'));
}

function editRow(idAl, posAl){
    var sample_identifier = '';
    console.log(idAl);
    var prefix = 'S';
    if (idAl[1] != ""){
        prefix = 'B';
    }
    sample_identifier = prefix + idAl[2]
    // set info of the aliquot 
    console.log(sample_identifier);
    jQuery("#aliquot-dialog").find('td[name=genealogy]').text(aliquots_validated[sample_identifier]['genid']);
    jQuery("#aliquot-dialog").find('td[name=sample_identifier]').text(aliquots_validated[sample_identifier]['barcode']);
    jQuery("#aliquot-dialog").find('td[name=sample_features]').text(aliquots_validated[sample_identifier]['sample_features']);
    jQuery("#aliquot-dialog").find('td[name=owner]').text(aliquots_validated[sample_identifier]['owner']);
    jQuery("#aliquot-dialog").find('td[name=exp_group]').text(aliquots_validated[sample_identifier]['exp_group']);
    jQuery("#aliquot-dialog").find('td[name=volume]').text(aliquots_validated[sample_identifier]['volume']);
    jQuery("#aliquot-dialog").find('td[name=concentration]').text(aliquots_validated[sample_identifier]['concentration']);
    jQuery("#aliquot-dialog").find('td[name=replicates]').text(aliquots_validated[sample_identifier]['replicates']);
    jQuery("#aliquot-dialog").find('td[name=cRNAVolume]').text(aliquots_validated[sample_identifier]['cRNAVolume']);
    jQuery("#aliquot-dialog").find('td[name=waterVolume]').text(aliquots_validated[sample_identifier]['waterVolume']);
    jQuery("#aliquot-dialog").find('td[name=warning]').text(aliquots_validated[sample_identifier]['warning']);
    jQuery("#aliquot-dialog").find('input[name=totalVolume]').val(aliquots_validated[sample_identifier]['totalVolume']);
    jQuery("#aliquot-dialog").find('input[name=hybBuffer]').val(aliquots_validated[sample_identifier]['hybBuffer']);
    jQuery("#aliquot-dialog").find('input[name=loadQuantity]').val(aliquots_validated[sample_identifier]['loadQuantity']);


    jQuery( "#aliquot-dialog" ).dialog({
            resizable: false,           
            modal: true,
            draggable: false,
            width: 380,
            buttons: {    
                   "Ok": function(){
                        // edit canceled
                        recomputeHyb();
                        aliquots_validated[sample_identifier]['cRNAVolume'] = jQuery("#aliquot-dialog").find('td[name=cRNAVolume]').text();
                        aliquots_validated[sample_identifier]['waterVolume'] = jQuery("#aliquot-dialog").find('td[name=waterVolume]').text();
                        aliquots_validated[sample_identifier]['hybBuffer'] = jQuery("#aliquot-dialog").find('input[name=hybBuffer]').val();
                        aliquots_validated[sample_identifier]['loadQuantity'] = jQuery("#aliquot-dialog").find('input[name=loadQuantity]').val();
                        aliquots_validated[sample_identifier]['totalVolume'] = jQuery("#aliquot-dialog").find('input[name=totalVolume]').val();
                        aliquots_validated[sample_identifier]['warning'] = jQuery("#aliquot-dialog").find('td[name=warning]').text();
                        jQuery("#aliquot_validated_table").dataTable().fnUpdate([aliquots_validated[sample_identifier]['idaliquot'], aliquots_validated[sample_identifier]['genid'], aliquots_validated[sample_identifier]['barcode'], aliquots_validated[sample_identifier]['sample_features'], aliquots_validated[sample_identifier]['owner'], aliquots_validated[sample_identifier]['exp_group'], aliquots_validated[sample_identifier]['volume'], aliquots_validated[sample_identifier]['concentration'], aliquots_validated[sample_identifier]['replicates'], aliquots_validated[sample_identifier]['cRNAVolume'], aliquots_validated[sample_identifier]['waterVolume'], aliquots_validated[sample_identifier]['hybBuffer'], null, null, aliquots_validated[sample_identifier]['warning'], aliquots_validated[sample_identifier]['barcode']], posAl);
                        jQuery(this).dialog("close");
                    }
                }
        });


}

function recomputeHyb (){
    var totalVolume = parseFloat(jQuery("#aliquot-dialog").find('input[name=totalVolume]').val());
    var hybBuffer = parseFloat(jQuery("#aliquot-dialog").find('input[name=hybBuffer]').val());
    var loadQuantity = parseFloat(jQuery("#aliquot-dialog").find('input[name=loadQuantity]').val());
    var replicates = parseInt(jQuery("#aliquot-dialog").find('td[name=replicates]').text());
    var volume = parseFloat(jQuery("#aliquot-dialog").find('td[name=volume]').text());
    var concentration =  parseFloat(jQuery("#aliquot-dialog").find('td[name=concentration]').text());
    console.log(loadQuantity, concentration, replicates);
    var cRNAVolume = (loadQuantity/concentration * replicates);
    console.log(cRNAVolume);
    var alertI = "False";
    // check if the volume is sufficient for the hybridization
    if (cRNAVolume > volume){
        alert("Insufficient Volume!","Warning");
        console.log('here');
        alertI = "True";
    }
    jQuery("#aliquot-dialog").find('td[name=warning]').text(alertI);
    var temp = cRNAVolume + hybBuffer;
    var waterVolume = (totalVolume - temp);
    jQuery("#aliquot-dialog").find('td[name=cRNAVolume]').text(cRNAVolume.toFixed(2));
    jQuery("#aliquot-dialog").find('td[name=waterVolume]').text(waterVolume.toFixed(2));       
}



function prepareData(){
    aliquot_warnings = 0;
    jQuery.each( jQuery("#aliquot_validated_table").dataTable().fnGetNodes(), function(i, row){
        rowData = jQuery("#aliquot_validated_table").dataTable().fnGetData(i);
        
        var sample_identifier = '';
        if (rowData[1] != ""){
            sample_identifier = 'B' + rowData[2];
        }
        else{
            sample_identifier = 'S' + rowData[2];

        } 
        
        console.log(rowData);
        if (rowData[14] == "True"){
            aliquot_warnings++;
        }
        console.log(sample_identifier);    
        aliquots_validated[sample_identifier]['exhausted'] = jQuery(row).find(':checkbox')[0].checked;
    });
}


function save_stop() {
    jQuery("#save_stop").click(function() {
        prepareData();
        console.log('save and stop');
        if (aliquot_warnings>0){
            alert('Please verify the preparation of the aliquots highlighted in yellow.');
        }
        else{
            submitData('stop');    
        }
    });  
}


function proceed() {
    jQuery("#proceed").click(function() {
        prepareData();
        if (aliquot_warnings>0){
            alert('Please verify the preparation of the aliquots highlighted in yellow.');
        }
        else{
            submitData('continue');
        }
    });  
}


function submitData (status){
    var response = {'val_aliquots':  aliquots_validated, 'status':status, 'sessionid': session_id};
    var json_response = JSON.stringify(response);
    console.log(json_response);
    var url = base_url + '/check_hybrid/';
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