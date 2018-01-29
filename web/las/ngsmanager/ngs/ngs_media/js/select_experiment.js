// init document
jQuery(document).ready(function(){
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
            { "sTitle": "Title" },
            { "sTitle": "Description" }
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
}

function selectPlan (){
    jQuery('#select').click(function(event){
        var url =  base_url + '/select_experiment/';
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