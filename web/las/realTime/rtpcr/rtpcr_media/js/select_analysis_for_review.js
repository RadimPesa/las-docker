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
    initHandlers();
});



// init the data table
function generate_table(){
    /*
     * Initialse DataTables, with image on the first column
     */
    jQuery("table#analysis_table").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Timestamp", "width": "10%" },
            { "sTitle": "Title", "width": "30%" },
            { "sTitle": "Description", "width": "50%" },
        ],
    "bAutoWidth": false ,
    "aaSorting": [[0, 'desc']]
    });

    jQuery("table#analysis_table tbody").click(function(event) {
        jQuery(jQuery('table#analysis_table').dataTable().fnSettings().aoData).each(function (){
            jQuery(this.nTr).removeClass('row_selected');
            jQuery('#select').removeAttr('disabled');
        });
        jQuery(event.target.parentNode).addClass('row_selected');
    });
}

function initHandlers (){
    jQuery('#select').click(function(event){
        var url =  './';
        var id_analysis = jQuery(jQuery('#analysis_table').dataTable().fnGetNodes()).filter(".row_selected").attr('analysis_index');
        window.location = nextUrl + '?id=' + id_analysis;
    });
}