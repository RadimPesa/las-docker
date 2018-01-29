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
    selectPlan();

});



// init the data table
function generate_table(){
    /*
     * Initialse DataTables, with image on the first column
     */
    jQuery("table#plan_table").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Timestamp" },
            { "sTitle": "Owner" },
            { "sTitle": "Delete",
            "sClass": "control center", 
            "sDefaultContent": '<span style="text-align:center;" class="ui-icon ui-icon-closethick">pippo</span>',
            "sWidth": "5%"},
        ],
    "bAutoWidth": false ,
    "aaSorting": [[0, 'desc']]
    });

    jQuery("table#plan_table tbody").click(function(event) {
        jQuery(jQuery('table#plan_table').dataTable().fnSettings().aoData).each(function (){
            jQuery(this.nTr).removeClass('row_selected');
            jQuery('#select').removeAttr('disabled');
        });
        jQuery(event.target.parentNode).addClass('row_selected');
    });

    /* Add event listener for delete row  */
    jQuery("#plan_table tbody td span.ui-icon-closethick").click(function(event) {
        var nTr = jQuery(this).parents('tr')[0];
        var idplan = jQuery(nTr).attr('plan_index');
        var user = jQuery('#user_name').attr('user'); 
        var response = {'idplan': idplan, 'user':user}
        var json_response = JSON.stringify(response);
        var url =  base_url + '/api.deleterequest';
        jQuery.ajax({
            type: 'POST',
            url: url,
            async: false,
            data: json_response, 
            dataType: "json",
            success: function(transport) {
                jQuery("table#plan_table").dataTable().fnDeleteRow( nTr );
            },
            error: function(data) { 
                alert("Submission data error! Please, try again.\n" + data.status, "Warning");
            }
        });
        
    });

}

function selectPlan (){
    jQuery('#select').click(function(event){
        var url =  base_url + '/pending_request/';
        var idplan = jQuery(jQuery('#plan_table').dataTable().fnGetNodes()).filter(".row_selected").attr('plan_index');
        var response = {'idplan': idplan}
        var json_response = JSON.stringify(response);
        jQuery.ajax({
            type: 'POST',
            url: url,
            data: json_response, 
            dataType: "json",
            error: function(data) { 
                alert("Submission data error! Please, try again.\n" + data.status, "Warning");
            }
        });
        
    });
}