experiment_info = {};
selected_aliquot = '';
selected_geneid = '';
selected_gene = ''
selected_mutid = '';
selected_mut_aa = '';
selected_mut_cds = '';
current_target = '';
targets_selected = [];
nTargets = 0;
colors = {}

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

    experiment_info['idplan'] = jQuery('#plan').attr('idplan');
    generate_table_selected_assays();
    generate_table_available_assays();

    jQuery('#settings_button').click(function(event){
        experiment_info['idinstrument'] = jQuery('#instrument_selection :selected').attr('instrumentid');
        experiment_info['type'] = jQuery('#type_selection :selected').val();
        jQuery('#instrument_selection').attr('disabled', 'disabled');
        jQuery('#type_selection').attr('disabled', 'disabled');
        jQuery('#experiment').show();
        jQuery('#targets').show();
        jQuery('#settings_button').attr('disabled', 'disabled');
        jQuery('#terminate_button').removeAttr('disabled');
        load_available_assays(jQuery('#type_selection').val());
    });

 
    jQuery('#addtargets').click(function(event){
        var dta = $("#table_available_assays").dataTable();
        var dts = $("#table_selected_assays").dataTable();
        var selTr = dta.$(".selectCheck:checked").parents("tr");
        var alreadySel = [];
        selTr.each(function(i, el) {
            var data = dta.fnGetData(el);
            if (targets_selected.indexOf(data[1]) == -1) {
                targets_selected.push(data[1]);
                dts.fnAddData([null, data[1], data[2]]);
            } else {
                alreadySel.push(data[2]);
            }
        });
        if (alreadySel.length) {
            alert("Assays already selected: " + alreadySel.join(", "));
        }
        dta.$(".selectCheck:checked").prop("checked", false);
    });
    
    jQuery('#terminate_button').click(function(event){
        submit_data();
    });


});


// generate and manage table of selected targets
function generate_table_selected_assays(){
    var dt = jQuery("#table_selected_assays").dataTable( {
    "bProcessing": true,
         "aoColumns": [
            { "sTitle": "",
               "mDataProp": null, 
               "sWidth": "20px", 
               "sDefaultContent": '<span class="ui-icon  ui-icon-closethick"></span>', 
                "bSortable": false
            },
            { "sTitle": "Id", "sWidth": "20px" },
            { "sTitle": "Name" }
        ],
    "aaSorting": [[0, 'desc']],
    "bAutoWidth": false,
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 1 ] }]
    });


    dt.on('click',"span.ui-icon-closethick", function () {
        var nTr = dt.$(this).parents('tr')[0];
        var data = dt.fnGetData(nTr);
        dt.fnDeleteRow(nTr, null, true);
        var i = targets_selected.indexOf(data[1]);
        targets_selected.splice(i, 1);
    }); 
}

function generate_table_available_assays() {
    jQuery("#table_available_assays").dataTable( {
    "bProcessing": true,
         "aoColumns": [
            {   "sTitle": "",
                "sWidth": "20px", 
                "sDefaultContent": "<input type='checkbox' class='selectCheck' ></input>", 
                "bSortable": false
            },
            { "sTitle": "Id", "sWidth": "20px" },
            { "sTitle": "Name" }
        ],
    "aaSorting": [[0, 'asc']],
    "bAutoWidth": false,
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 1 ] }],
    });

}

function load_available_assays(type) {
    console.log("Loading available assays (type ", type, ")");
    jQuery.ajax({
        type: 'GET',
        data: { 'assayType': type },
        url: './',
        success: function(transport) {
            console.log(transport)
            var adt = jQuery("#table_available_assays").dataTable();
            adt.fnClearTable();
            data = JSON.parse(transport);
            for (var i = 0; i < data['assays'].length; i++){
                console.log(data['assays'][i]);
                adt.fnAddData([null, data['assays'][i]['id'], data['assays'][i]['name']]);
            }
        }, 
        error: function(data) { 
            alert("Submission data error! Please, try again.\n" + data.status, "Warning");
        }
    });
}


function submit_data(){

    var selected_assays = $('#table_selected_assays').dataTable().fnGetData().map(function(el) {return el[1]});

    console.log(selected_assays);

    // send data
    var url =  base_url + '/define_experiment/';
    response = {'selected_assays': selected_assays, 'experiment_info':experiment_info};
    json_response = JSON.stringify(response);
    
    jQuery.ajax({
        type: 'POST',
        url: url,
        data: json_response, 
        dataType: "json",   
        error: function(data) { 
            alert("Submission data error! Please, try again.\n" + data.status, "Warning");
        }
    });

}