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
    generate_result_table();

});


function generate_result_table(){
    var d = new Date();
    var user = jQuery('#user_name').attr('user');
    var filename = "Results_" + user + '_' + $.datepicker.formatDate('yy-mm-dd', d) + "--" + d.getHours() + "-" + d.getMinutes() + "-" + d.getSeconds();
    jQuery("table#table_res").dataTable( {
        "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        "iDisplayLength": -1,
        "sDom":'TRC<\"clear\">lfrtip',
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
                                "sPdfMessage": "Laboratory Assistant Suite - Liquid Biopsy Manager - " + user + " - " + $.datepicker.formatDate('yy/mm/dd', d) + " @ " + d.getHours() + ":" + d.getMinutes() + ":" + d.getSeconds(),
                                "sTitle": filename,
                                "mColumns": "visible"
                }
                , "print"],
                "sSwfPath": base_url + "/profiling_media/js/DataTables-1.9.4/extras/TableTools/media/swf/copy_csv_xls_pdf.swf"
        }
    });
}