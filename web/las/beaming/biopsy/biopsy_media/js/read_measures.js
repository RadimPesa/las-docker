aliquots = []

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

    generate_table();
    addFile();
    /*
    jQuery('#submit').click(function(){
        submitMeasures();    
    })
    */
});


// init the data table
function generate_table(){
    /*
     * Initialse DataTables, with image on the first column
     */
    var d = new Date();
    var user = jQuery('#user_name').attr('user');
    var filename = "Measures_" + user + '_' + $.datepicker.formatDate('yy-mm-dd', d) + "--" + pad(d.getHours()) + "-" + pad(d.getMinutes()) + "-" + pad(d.getSeconds());
    var oTable = jQuery("table#measure_table").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Position" },
            { "sTitle": "Aliquot Id" },
            { "sTitle": "Genealogy Id" },
            { "sTitle": "Gene Id" },
            { "sTitle": "Gene" },
            { "sTitle": "Mutation" },
            { "sTitle": "AA" },
            { "sTitle": "CDS" },
            { "sTitle": "Value (Editable)" },
            { "sTitle": "Type Id" },
            { "sTitle": "Measure Type " },
            { "sTitle": "Unity Measure" },
            { "sTitle": "Region Id" },
            { "sTitle": "Region" },

        ],
    "bAutoWidth": false ,
    "aaSorting": [[0, 'asc']],
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 1,3,9,12 ] },
        ],
    "aLengthMenu": [
        [10, 50, 100, 200, -1],
        [10, 50, 100, 200, "All"]
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
                            "sPdfMessage": "Laboratory Assistant Suite - Beaming Manager - " + user + " - " + $.datepicker.formatDate('yy/mm/dd', d) + " @ " + pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds()),
                            "sTitle": filename,
                            "mColumns": "visible"
            }
            , "print"],
            "sSwfPath": base_url + "/biopsy_media/js/DataTables-1.9.4/extras/TableTools/media/swf/copy_csv_xls_pdf.swf"
    },
    "fnDrawCallback": function () {
        jQuery('#measure_table > tbody > tr').find('td:eq(6)').editable( 
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


// read data from the table after post of file
function readTable(){
    var data = jQuery("#measure_table").dataTable().fnGetData();
    jQuery.each(data, function(key, d) { 
        aliquots.push({'aliquotid':d[1], 'value':d[8], 'mtype':d[9], 'region':d[12]});
    });
    
}


function updateInput(){
    readTable();
    $('#aliquots_list').val(JSON.stringify(aliquots));
    console.log(aliquots);
    return true;
}

function addFile (){
    $("#form_measures").on("change", " input[type=file]:last", function(){
            var item = $(this).clone(true);
            var fileName = $(this).val();
            if(fileName){
                $(this).parent().append(item);
            }  
        });
}

