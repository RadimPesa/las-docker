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
    jQuery("table#plan_table").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Timestamp" },
            { "sTitle": "Title" },
            { "sTitle": "Description" },
            { "sTitle": "Times analysed" },
        ],
    "bAutoWidth": false,
    "aaSorting": [[3, 'asc'], [0, 'desc']]
    });

    jQuery("table#plan_table tbody").click(function(event) {
        jQuery(jQuery('table#plan_table').dataTable().fnSettings().aoData).each(function (){
            jQuery(this.nTr).removeClass('row_selected');
            jQuery('#select').removeAttr('disabled');
        });
        jQuery(event.target.parentNode).addClass('row_selected');
    });
}

function initHandlers (){
    jQuery('#hideanalysed').change(function() {
        var checked = $('#hideanalysed').attr("checked") == "checked" ? true : false;
        var dt = $("#plan_table").dataTable();
        if (!checked) {
            $.fn.dataTableExt.afnFiltering.pop();
        } else {
            $.fn.dataTableExt.afnFiltering.push(function( oSettings, aData, iDataIndex ) {
                return parseInt(aData[3]) == 0;        
            });
        }
        dt.fnDraw();
    });

    jQuery('#hideanalysed').attr("checked", true).change();

    jQuery('#select').click(function(event){
        var url =  './';
        var idplan = jQuery(jQuery('#plan_table').dataTable().fnGetNodes()).filter(".row_selected").attr('plan_index');
        var response = {'idplan': idplan}
        var json_response = JSON.stringify(response);
        console.log(json_response);
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