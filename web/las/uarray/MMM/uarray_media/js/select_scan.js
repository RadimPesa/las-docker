terminate_selected = 0;

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
    terminatePlan();

});



// init the data table
function generate_table(){
    /*
     * Initialse DataTables, with image on the first column
     */
    jQuery("table#plan_table").dataTable( {
        "bProcessing": false,
         "aoColumns": [
            { "sTitle": "Timestamp" },
            { "sTitle": "Scan protocol" },
            { "sTitle": "Notes" },
            { "sTitle": "Terminate", 
              "sClass": "control center", 
              "sDefaultContent": '<input type="checkbox" name="terminate" value="terminate" />'
            },
        ],
    "bAutoWidth": false ,
    "aaSorting": [[0, 'asc']]
    });

    jQuery("table#plan_table tbody [name=terminated]").click(function(event){
        if (jQuery(this).is(':checked'))
            terminate_selected++;
        else
            terminate_selected--;
        if (terminate_selected > 0)
            jQuery('#terminate').removeAttr('disabled');
        else
            jQuery('#terminate').attr('disabled', 'disabled');
        
    });

    jQuery("table#plan_table tbody").click(function(event) {
        jQuery(jQuery('table#plan_table').dataTable().fnSettings().aoData).each(function (){
            jQuery(this.nTr).removeClass('row_selected');
        });
        if (jQuery(jQuery(event.target.parentNode)[0]).is("tr")){
                if (jQuery(event.target.parentNode).attr('plan_index')){
                    jQuery(event.target.parentNode).addClass('row_selected');
                    jQuery('#select').removeAttr('disabled');
                }
        }
    });

    jQuery('checkbo.terminate')
}

function selectPlan (){
    jQuery('#select').click(function(event){
        var url =  base_url + '/select_scan/';
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


function terminatePlan (){
    jQuery('#terminate').click(function(event){
        var url =  base_url + '/select_scan/';
        var plan_terminate = [];
        jQuery.each( jQuery("#plan_table").dataTable().fnGetNodes(), function(i, row){
            rowData = jQuery("#plan_table").dataTable().fnGetData(i);
            id = jQuery(row).attr('plan_index');
            if (jQuery(row).find(':checkbox')[0].checked)
                plan_terminate.push(id);
        });
        var json_response = JSON.stringify({'terminate':true, 'plans':plan_terminate});

        
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