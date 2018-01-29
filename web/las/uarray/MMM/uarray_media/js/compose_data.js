samples = {};

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

	aliquotTable();
	jQuery("#upload").click(function(){	
		readFile();
	});

    jQuery("#add_aliquot").click(function(){
        aliquotSubmit();
    });

    jQuery("#export_data").click(function(){
        composeDataset();
    });
	
});

function pad(n) { return ("0" + n).slice(-2); }

function checkKeyP(evt){
        var charCode = (evt.which) ? evt.which : event.keyCode
        if ( charCode == 13 ) //codice ASCII del carattere carriage return (invio)
            aliquotSubmit();
}

function aliquotTable(){
	var d = new Date();
    var user = jQuery('#user_name').attr('user');
    var filename = "SampleDataset_" + user + '_' + $.datepicker.formatDate('yy-mm-dd', d) + "--" + pad(d.getHours()) + "-" + pad(d.getMinutes()) + "-" + pad(d.getSeconds());
    jQuery("table#al_list").dataTable( {
        "bProcessing": false,
         "aoColumns": [
            { "sTitle": "Link" },
            { "sTitle": "Genealogy Id" },
            { "sTitle": "#samples"},
            { "sTitle": "Chip"},
            { "sTitle": "Position"},
            { "sTitle": "Scan Protocol"},
            { "sTitle": "Note Scan"},
            { "sTitle": "Scan Date"},
            { "sTitle": "Hybridization Date"},
            { "sTitle": "Delete",
              "sClass": "control center", 
              "sDefaultContent": '<span class="ui-icon ui-icon-close"></span>'},
        ],
    "bAutoWidth": false ,
    "aaSorting": [[1, 'asc']],
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 0 ] }
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

   jQuery(document).on('click','#al_list tbody td span.ui-icon-close', function() {
        var nTr = jQuery(this).parents('tr')[0];
        console.log(nTr);
        var posAl = jQuery("#al_list").dataTable().fnGetPosition(jQuery(this).parents('td')[0]);
        var idAl = jQuery("#al_list").dataTable().fnGetData(posAl[0]);
        samples[idAl[1]]--;
        jQuery("table#al_list").dataTable().fnDeleteRow( nTr );
        updateNumSamples();
        
    } );
}

function updateSamples (value){
	if (samples.hasOwnProperty(value['genid']) == false){
		samples[value['genid']] = 1;
	}
	else{
		samples[value['genid']] += 1;	
	}
}

function updateNumSamples(){
	var flag = false;
	$(jQuery('#al_list').dataTable().fnGetNodes()).each(function(index, value){
		var data = jQuery("#al_list").dataTable().fnGetData(value);
		data[2] = samples[data[1]];
		jQuery("#al_list").dataTable().fnUpdate(data, value);
		flag = true;
	});
	console.log(flag);
	if (flag){
		jQuery('#export_data').removeAttr('disabled');
	}
	else{
		jQuery('#export_data').attr('disabled','disabled');
	}
}


function aliquotSubmit(){
    // get values from the page
    var al_identifier = jQuery('#al_identifier').val();
    if (al_identifier == ''){
        return;
    }
    var url = base_url + '/api.getsample/' + al_identifier;    
    jQuery.ajax({
        type: 'get',
        url: url,
        success: function(transport) {
                if (transport.hasOwnProperty('response') ){
                    alert(transport['response'], "Error");
                } 
                else{
                    jQuery.each(transport['samples'], function(index, value){
						updateSamples (value);
                        jQuery('#al_list').dataTable().fnAddData([value['link'], value['genid'], samples[value['genid']], value['chip'], value['position'], value['scan_prot'], value['scan_note'], value['scan_date'], value['hyb_date'], null]);
                    });
            		updateNumSamples();
                }                        
            
            },
        error: function(data) {
                 alert(data.responseText, "Error");
            }
    });
}


function readFile (){
	var formData = new FormData($('#upload_aliquot_file')[0]);
	console.log(formData);
    $.ajax({
        url: base_url + "/api.readSamples",
        type: 'POST',
        //Ajax events
        success: function(transport) {
            jQuery.each(transport['samples'], function(index, value){
            	updateSamples (value);
                jQuery('#al_list').dataTable().fnAddData([value['link'], value['genid'], samples[value['genid']], value['chip'], value['position'], value['scan_prot'], value['scan_note'], value['scan_date'], value['hyb_date'], null]);
            });
            var control = $("#id_file");
            control.replaceWith( control = control.clone( true ) );
            updateNumSamples();
        },

        error: function(msg) {
            alert(msg['response']);
        },

        // Form data
        data: formData,
        //Options to tell jQuery not to process data or worry about content-type.
        cache: false,
        contentType: false,
        processData: false
    });
}

function composeDataset(){
	aliquots ={'samples':[]};
	$(jQuery('#al_list').dataTable().fnGetData()).each(function(index, value){
		aliquots['samples'].push(value[0]);
	});
	
	json_response = JSON.stringify(aliquots);
	var url = base_url + '/compose_dataset/'
	
	jQuery.ajax({
		type: 'POST',
		url: url,
		data: json_response, 
		dataType: "json",
		error: function(data) { 
		    alert("Submission data error! Please, try again.\n" + data.status, "Warning");
		}
	});
}