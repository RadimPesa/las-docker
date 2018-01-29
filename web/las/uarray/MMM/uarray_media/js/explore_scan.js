scanevent = {};
current_chip = '';

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

    eventTable();
    sampleTable();
    fileTable();
    jQuery("#load_chip").click(function(){
        barcodeSubmit();
    });
});

function checkKeyP(evt){
        var charCode = (evt.which) ? evt.which : event.keyCode
        if ( charCode == 13 ) //codice ASCII del carattere carriage return (invio)
            barcodeSubmit();
}

function eventTable(){
    jQuery("table#event_table").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Id" },
            { "sTitle": "Start Time" },
            { "sTitle": "End Time" },
            { "sTitle": "Protocol"},
            { "sTitle": "Notes"},
            { "sTitle": "Link"},
            { "sTitle": "Files",
              "sClass": "control center", 
              "sDefaultContent": '<span class="ui-icon ui-icon-search"></span>'},
        ],
    "bAutoWidth": false ,
    "aaSorting": [[1, 'asc']],
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 0,5 ] }
        ]
    });

    jQuery("table#event_table tbody").click(function(event) {
        if ($(event.target).is('span'))
            return;
        var flag = jQuery(jQuery(event.target.parentNode)[0]).hasClass('row_selected');
        jQuery(jQuery('table#event_table').dataTable().fnSettings().aoData).each(function (){
           jQuery(this.nTr).removeClass('row_selected');
        });
        if (!flag){
            if (jQuery(jQuery(event.target.parentNode)[0]).is("tr")){   
                console.log(jQuery(event.target.parentNode));
                jQuery(jQuery(event.target.parentNode)[0]).addClass('row_selected');
            }
        }
    });

    jQuery( document ).on('click', "#event_table tbody td span.ui-icon-search", function () {
        console.log('getevent');
        var nTr = jQuery(this).parents('tr')[0];
        var pos = jQuery("#event_table").dataTable().fnGetPosition(jQuery(this).parents('td')[0]);
        var data = jQuery("#event_table").dataTable().fnGetData(pos[0]);
        console.log(data);
        getFiles(data[5], 'uarraychip');
        jQuery('#files').show();
    });
}


function sampleTable(){
    jQuery("table#sample_table").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Sample Identifier" },
            { "sTitle": "Position" },
            { "sTitle": "Q/C"},
            { "sTitle": "Link Rep"},
            { "sTitle": "Files",
              "sClass": "control center", 
              "sDefaultContent": '<span class="ui-icon ui-icon-search"></span>'},
        ],
    "bAutoWidth": false ,
    "iDisplayLength": -1,
    "bLengthChange": false,
    "bFilter": false,
    "bInfo": false,
    "bPaginate": false,
    "aaSorting": [[1, 'asc']],
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 3 ] }
        ]
    });

    jQuery( document ).on('click',"#sample_table tbody td span.ui-icon-search", function () {
        console.log('getsample');
        var nTr = jQuery(this).parents('tr')[0];
        console.log(nTr);
        var pos = jQuery("#sample_table").dataTable().fnGetPosition(jQuery(this).parents('td')[0]);
        var data = jQuery("#sample_table").dataTable().fnGetData(pos[0]);
        console.log(data);
        getFiles(data[3], 'uarraysample');
        jQuery('#files').show();
    });
}


function fileTable(){
    jQuery("table#file_table").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Name" },
            { "sTitle": "Extension"},
            { "sTitle": "Owner"},            
            { "sTitle": "Created"},
            { "sTitle": "Download"}, 
        ],
    "bAutoWidth": false ,
    "iDisplayLength": -1,
    "bLengthChange": false,
    "bInfo": false,
    "bPaginate": false,
    "aaSorting": [[0, 'asc']],
    });

}


function barcodeSubmit(){
    // get values from the page
    var barcode = jQuery('#id_barcode').val();
    if (barcode == '' || barcode == current_chip){
        return;
    }
    var url = base_url + '/api.getchip/' + barcode + '/explore';
    startLag();    
    jQuery.ajax({
        type: 'get',
        url: url,
        success: function(transport) {
                if (transport.hasOwnProperty('response') ){
                    alert(transport['response'], "Error");
                } 
                else{
                    current_chip = barcode;
                    console.log(transport);
                    scanevent = {};
                    jQuery('#scan_events').show();
                    jQuery('#sample_scanned').show();
                    
                    jQuery('#event_table').dataTable().fnClearTable();
                    jQuery('#sample_table').dataTable().fnClearTable();
                    jQuery.each(transport['scanevents'], function(index, value){
                        console.log(transport);
                        jQuery('#event_table').dataTable().fnAddData([value['id'], value['startScanTime'], value['endScanTime'], value['protocol'], value['notes'], value['link'], null]);
                        scanevent[ value['id'] ] = value['assignments'];
                        if (index == 0){
                            jQuery(jQuery('#event_table').dataTable().fnGetNodes(0)).addClass('row_selected');
                            updateSamples(value['id']);
                        }
                    });
                }                        
                endLag();
            },
        error: function(data) {
                endLag();
                alert(data.responseText, "Error");
            }
    });
}

function updateSamples(id){
    jQuery.each(scanevent[id], function (index, value){
        jQuery('#sample_table').dataTable().fnAddData([value['sample'], value['position'], value['qc'], value['link'], null]);
    });
}


function getFiles(link, typeO){
    var url = base_url + '/api.getlink/' + link + "/" + typeO;    
    jQuery.ajax({
        type: 'get',
        url: url,
        success: function(transport) {
                console.log(transport)
                if (transport.hasOwnProperty('response') ){
                    alert(transport['response'], "Error");
                } 
                else{
                    jQuery('#file_table').dataTable().fnClearTable();
                    $.each(transport['info']['sources'], function(index, value){
                        jQuery('#file_table').dataTable().fnAddData([value['name'], value['extension'], value['owner'], value['created'] , '<a href="'+base_url + "/get_file/" + value['link'] + '"> <span class="ui-icon ui-icon-arrowthickstop-1-s"></span></a>' ]);
                    });
                    console.log(transport);
                }
            },
        error: function(data) {
                 alert(data.responseText, "Error");
            }
    });
}
