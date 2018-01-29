scan_prot = {}
prot_info = {}

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

    setInfoProtocol();
    saveProtocol();




});



function setInfoProtocol(){

    jQuery("#setinfo").click(function(){
        if(jQuery("input#id_name").val()==""){
            alert("Please define a name for the new Protocol.","Warning");
        }
        else{
            var name = jQuery('#id_name').val();
            var software_id = jQuery("#id_software option:selected").val();
            var software = jQuery("#id_software option:selected").text();
            var instrument_id = jQuery("#id_instrument option:selected").val();
            var instrument = jQuery("#id_instrument option:selected").text();
            var qc = jQuery('[name=qc]:checked').val();
            var qc_text = jQuery('[name=qc]:checked').attr('text');
            // retirve info for the new protocol and check if a protocol with the same name exists
            var url =  base_url + '/api.scanprotocolinfo/' + name + '/' + instrument_id;
            jQuery.ajax({
                type: 'get',
                url: url,
                async: false,
                success: function(transport) {
                    scan_prot = transport;
                }
            });

            console.log(scan_prot);
            if (scan_prot['protocolcheck'] == false){
                prot_info = {'name': name, 'idInstrument': instrument_id, 'idSoftware': software_id, 'qc':qc};
                jQuery('#id_name').attr('disabled', 'disabled');
                jQuery('#id_software').attr('disabled', 'disabled');
                jQuery('#id_instrument').attr('disabled', 'disabled');
                jQuery('#message').append('<b>Name: </b>' + name + '<br/><b>Software: </b>' + software + '<br/><b>Instrument: </b>' + instrument + '<br/><b>Q/C required: </b>' + qc_text);
                jQuery('#message').show();
                jQuery('#saveprot').show();
                jQuery('#setinfo').attr('disabled', 'disabled');
                jQuery.each(scan_prot['params'], function (index, value){

                    jQuery('#parameters_values tbody:first').append('<tr><td>' + value['id'] + '</td><td>'+ value['name'] + '</td><td>' + value['default_value'] + '</td><td>' + value['unity'] + '</td></tr>');

                });
                generate_table();
                jQuery('#parameters_values').show();

            }
            else{
                alert ("Not unique name for the protocol. Please change it before proceding with parameter setting.");
            }



        }
    });


}


function generate_table(){
    /*
     * Initialse DataTables, with image on the first column
     */
    //var oTable = jQuery("table#aliquot_table").dataTable();
    //oTable.fnDestroy();
    var oTable = jQuery("#parameters_values").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "#" },
            { "sTitle": "Name" },
            { "sTitle": "Value (Editable)" },
            { "sTitle": "Unity Measure" }
        ],
    "bAutoWidth": false ,
    "aaSorting": [[0, 'asc']],
    "iDisplayLength": -1,
    "bLengthChange": false,
    "bFilter": false,
    "bInfo": false,
    "bPaginate": false,
    "aoColumnDefs": [
        { "bSortable": false, "aTargets": [ 0 ] },
        { "bVisible": false, "aTargets": [ 0 ] }
        ],   
    "fnDrawCallback": function () {
        $('#parameters_values > tbody > tr').find('td:eq(1)').editable( 
            function(value, settings) { 
                return(value);
            }, {
            "callback": function( sValue, y ) {
                var aPos = oTable.fnGetPosition( this );
                oTable.fnUpdate( sValue, aPos[0], aPos[2] );
            },
            "height": "12px",
            "width": "50px"
        }
            )
    }
    });
}


function saveProtocol(){
    jQuery('#saveprot').click( function (event){
        var table_data = jQuery("#parameters_values").dataTable().fnGetData();
        var params = {};
        jQuery.each(table_data, function(index, value){
            params[value[0]] = value[2];
        });
        var response = {'protocol': prot_info, 'params': params };
        var json_response = JSON.stringify(response);
        var url =  base_url + '/scan_protocols/';
        console.log(json_response);
        jQuery.ajax({
            type:'POST',    
            url:url,
            data: json_response, 
            dataType: "json",                       
            error: function(data) { 
                alert("Submission data error! Please, try again.\n" + data.responseText.slice(0,500), "Error"); 
            }

        });
    });
}