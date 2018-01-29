// init document
layouts = {};

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


    $('#chip_type_form').validationEngine({promptPosition : "centerRight", autoHidePrompt:true, autoHideDelay:1500});
    layoutSetting();
    generate_table_layout();
});



function layoutSetting(){
    jQuery('#id_number_Positions').change (function () {
        jQuery('#layout_setting').show();
        var url = base_url + '/api.getlayout/' + $('#id_number_Positions').val();
        jQuery.ajax({
            type:'GET',    
            url:url,
            async: false,
            success: function(transport) {
                layouts = {};
                var idLayout = -1
                $('#id_layout').empty();
                $.each(transport['layouts'], function(index, value) {
                    layouts[value['idg']] = value['rules']
                    
                    $('#id_layout').append($("<option/>", {
                        value: value['idg'],
                        text: 'Geometry ' + value['idg']
                    }));
                    idLayout = jQuery('#id_layout').find(":selected").val();
                    
                });
                setLayoutTable(idLayout);                  
            }
        });
    });
}

// init the data table
function generate_table_layout(){
    var oTable = jQuery("table#layout_table").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Position" },
            { "sTitle": "Identifier" },
        ],
    "bAutoWidth": false ,
    "aaSorting": [[0, 'asc']],
    "iDisplayLength": -1,
    "bLengthChange": false,
    "bFilter": false,
    "bInfo": false,
    "bPaginate": false,
    "fnDrawCallback": function () {
        $('#layout_table > tbody > tr').find('td:eq(1)').editable( 
            function(value, settings) { 
                return(value);
            }, {
            "callback": function( sValue, y ) {
                var aPos = oTable.fnGetPosition( this );
                oTable.fnUpdate( sValue.toUpperCase(), aPos[0], aPos[2] );
            },
            "height": "12px",
            "width": "50px"
        }
            )
    }
    });
    
}

// set the layout table according to response of the server
function setLayoutTable(idGeoSelected){
    jQuery("table#layout_table").dataTable().fnClearTable();
    console.log(idGeoSelected);
    if (idGeoSelected != -1){
        jQuery.each( layouts[idGeoSelected], function( key, value ) {
            jQuery("table#layout_table").dataTable().fnAddData([key,value]);
        });
    }    
    else{
        console.log($('#id_number_Positions').val());
        for (var i=1; i<= $('#id_number_Positions').val(); i++){
           jQuery("table#layout_table").dataTable().fnAddData([i,String(i)]); 
        }
    }
}


function insertType(){
    var status = $('#chip_type_form').validationEngine('validate');
    if (status == false){
        alert ("Please fill in all the fields (only Notes is optional)!");
        return;        
    }

    var title = jQuery('#id_title').val();
    var manufacturer = jQuery('#id_manufacturer').val();
    var organism = jQuery('#id_organism').val();
    var npos = jQuery('#id_number_Positions').val();
    var probes = jQuery('#id_probes_Number').val();
    var geoplatformid = jQuery('#id_GeoPlatform_Id').val();
    var manifest = jQuery('#id_manifest_File').val();
    var notes = jQuery('#id_notes').val();

    
    var layout = jQuery("table#layout_table").dataTable().fnGetData();
    console.log(layout);
    identifierLayout = {};
    finalLayout = {}
    var badIdenfier = false;
    $.each(layout, function(index, value){
        console.log(index, value[1]);
        if (identifierLayout.hasOwnProperty(value[1])){
            console.log('bad');
            badIdenfier = true;
            return false;
        }
        identifierLayout[value[1]] = value[0];
        finalLayout[value[0]] = value[1];
    });
    if (badIdenfier == true){
        alert('Identifiers should be unique');
        return;
    }
    var newLayout = -1;
    if (jQuery('#id_layout').find(":selected").val()){
        if (JSON.stringify(finalLayout) == JSON.stringify(layouts[jQuery('#id_layout').find(":selected").val()])){
            newLayout = jQuery('#id_layout').find(":selected").val();
        }
    }
    console.log(newLayout);
    
    var response = {'title': title, 'manufacturer':manufacturer, 'organism':organism, 'npos':npos, 'probes':probes, 'geoplatformid':geoplatformid, 'manifest':manifest, 'layout':finalLayout, 'newlayout':newLayout, 'notes':notes};
    var json_response = JSON.stringify(response);
    console.log(json_response);
    var url = base_url + '/new_chip_type/';
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

