nsamples = '';
mut_selected = false;
region_selected = false;
meas_selected = false;
formula_selected = false;


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

    nsamples = jQuery('#nsamples').attr('value');
    console.log(nsamples);
    jQuery("#input_selectable").selectable();
    jQuery("#output_selectable").selectable();

    jQuery('#move_out').click(function(event){
    	move_out_mask();
    });
    jQuery('#move_in').click(function(event){
    	move_in_mask();
    });

    jQuery('#define_mask_filter').click(function(event){
    	define_mask_filter();
    });

    jQuery('#define_mut_filter').click(function(event){
        define_mut_filter();
    });

    jQuery('#define_results_filter').click(function(event){
        define_results_filter();
    });

    jQuery('#define_formulas_filter').click(function(event){
        define_formulas_filter();
    });

    jQuery('#select_all_mut').click(function(event){
        select_mut();
    });

    jQuery('#select_all_reg').click(function(event){
        select_reg();
    });

    jQuery('#select_all_meas').click(function(event){
        select_meas();
    });

    jQuery('#select_all_formula').click(function(event){
        select_formula();
    });


    generate_mut_table();
    generate_region_table();
    generate_measure_table();
    generate_selected_masks();
    generate_selected_mutations();
    generate_selected_measures();
    generate_formula_table();


    $("input[name=andormut]").change(function () {
        if (jQuery(this).val() == 'and'){
            jQuery("#mutation_selection").dataTable().fnFilter(nsamples,6,false, true);
        }
        else{
            jQuery("#mutation_selection").dataTable().fnFilter('',6);
        }
    });
});


function select_mut(){
    mut_selected = !mut_selected;
    jQuery('[name=select_mut]').attr('checked', mut_selected);
    if (mut_selected){
        jQuery('#select_all_mut').val('Deselect All');
    }
    else{
        jQuery('#select_all_mut').val('Select All');   
    }
}

function select_reg(){
    region_selected = !region_selected;
    jQuery('[name=select_reg]').attr('checked', region_selected);
    if (region_selected){
        jQuery('#select_all_reg').val('Deselect All Regions');
    }
    else{
        jQuery('#select_all_reg').val('Select All Regions');   
    }
}

function select_meas(){
    meas_selected = !meas_selected;
    jQuery('[name=select_meas]').attr('checked', meas_selected);
        if (meas_selected){
        jQuery('#select_all_meas').val('Deselect All Measures');
    }
    else{
        jQuery('#select_all_meas').val('Select All Measures');   
    }
}

function select_formula(){
    formula_selected = !formula_selected;
    jQuery('[name=select_eq]').attr('checked', formula_selected);
        if (formula_selected){
        jQuery('#select_all_formula').val('Deselect All');
    }
    else{
        jQuery('#select_all_formula').val('Select All');   
    }
}


function move_out_mask(){
	
	jQuery('#input_selectable .ui-selected').each(function(index, value){
		jQuery('#output_selectable').append(jQuery(value).removeClass('ui-selected'));	
	});
}

function move_in_mask(){
	jQuery('#output_selectable .ui-selected').each(function(index, value){
		jQuery('#input_selectable').append(jQuery(value).removeClass('ui-selected'));	
	});
}

function define_mask_filter(){
    jQuery("#selected_masks").dataTable().fnClearTable();
    var i = 0;
	jQuery('#output_selectable .ui-selectee').each(function(index, value){
        console.log($(value).attr('key'));
	   	jQuery("#selected_masks").dataTable().fnAddData([$(value).attr('key'), $(value).attr('maskname'), $(value).attr('measure')]);
        i++;
	});
    if (i == 0)
        return;
	jQuery('#filter_mask').slideToggle("slow");
	jQuery('#target_filter').slideToggle("slow");
    jQuery('#div_selected_masks').show();
}


function define_mut_filter(){
    jQuery("#selected_mutations").dataTable().fnClearTable();
    var nmut = 0;

    jQuery.each( jQuery("#mutation_selection").dataTable().fnGetNodes(), function(i, row){
        rowData = jQuery("#mutation_selection").dataTable().fnGetData(i);
        if (jQuery(row).find(':checkbox')[0].checked){
            jQuery("#selected_mutations").dataTable().fnAddData([rowData[1], rowData[2], rowData[3], rowData[4], rowData[5]]);
            nmut++;
        }        
    });
    if (nmut == 0)
        return;
    console.log('slow');
    jQuery('#target_filter').slideToggle("slow");
    jQuery('#results_filter').slideToggle("slow");
    jQuery('#div_selected_mutations').show();
}



function define_results_filter(){
    jQuery("#selected_measures").dataTable().fnClearTable();
    var nmeas = 0
    var list_measures = [];    

    jQuery.each( jQuery("#measure_selection").dataTable().fnGetNodes(), function(i, row){
        rowData = jQuery("#measure_selection").dataTable().fnGetData(i);
        if (jQuery(row).find(':checkbox')[0].checked){
            jQuery("#selected_measures").dataTable().fnAddData([rowData[1], rowData[2], rowData[3]]);
            nmeas++;
            list_measures.push(rowData[1]);
        }        
    });

    if (nmeas == 0){
        return;
    }

    var genmeasures = []
    jQuery.each( jQuery("#selected_masks").dataTable().fnGetNodes(), function(i, row){
        rowData = jQuery("#selected_masks").dataTable().fnGetData(i);
        if (rowData[2].toString() != "-1"){
            genmeasures.push(rowData[2]);
        }
    });


    console.log('slow');
    jQuery('#results_filter').slideToggle("slow");
    jQuery('#results_computation').slideToggle("slow");
    retrieveFormulas(list_measures, genmeasures);
    jQuery('#div_selected_measures').show();
}


function define_formulas_filter(){

    var filter_session = jQuery('#filter_id').val();
    var url = base_url + '/filter_results/' + filter_session +'/'

    var response = {'mask': [], 'target':[], 'formula':[], 'measure':[], 'bbmeasure':[]};
    var nequation = 0;
    jQuery.each( jQuery("#formula_selection").dataTable().fnGetNodes(), function(i, row){
        rowData = jQuery("#formula_selection").dataTable().fnGetData(i);
        if (jQuery(row).find(':checkbox')[0].checked){
            nequation++;
            response['formula'].push(rowData[1]);
        }        
    });

    jQuery.each( jQuery("#selected_masks").dataTable().fnGetNodes(), function(i, row){
        rowData = jQuery("#selected_masks").dataTable().fnGetData(i);
        if (rowData[2].toString() == "-1"){
            response['mask'].push(rowData[0]);
        }
        else{
            response['bbmeasure'].push(rowData[0]);
        }

    });

    jQuery.each( jQuery("#selected_mutations").dataTable().fnGetNodes(), function(i, row){
        rowData = jQuery("#selected_mutations").dataTable().fnGetData(i);
        response['target'].push([rowData[0], rowData[2]]);        
    });

    jQuery.each( jQuery("#selected_measures").dataTable().fnGetNodes(), function(i, row){
        rowData = jQuery("#selected_measures").dataTable().fnGetData(i);
        response['measure'].push(rowData[0]);        
    });


    // gestire mask che sono measures
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

}


function retrieveFormulas(list_measures, genmeasures){
    var url =  base_url + '/api.getFormulas';
    jQuery.ajax({
        type: 'GET',
        data: 'measures='+ JSON.stringify(list_measures) + '&general_measures=' + JSON.stringify(genmeasures),
        url: url,
        success: function(transport) {
            jQuery('#formula_selection').dataTable().fnClearTable();
            $(transport).each(function(index, value){
                jQuery('#formula_selection').dataTable().fnAddData([ '<input type="checkbox" name="select_eq" value="selected_equation"/>', value['formulaid'], value['expression']]);
            });
        }, 
        error: function(data) { 
            alert("Submission data error! Please, try again.\n" + data.status, "Warning");
        }
    });
}


// init the data table
function generate_mut_table(){
    /*
     * Initialse DataTables, with image on the first column
     */
    jQuery("#mutation_selection").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Select" },
            { "sTitle": "Gene id" },
            { "sTitle": "Gene Symb" },
            { "sTitle": "Mutation" },
            { "sTitle": "AA" },
            { "sTitle": "CDS" },
            { "sTitle": "# samples" },
        ],
    "bAutoWidth": false ,
    "aaSorting": [[1, 'desc']],
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 1 ] },
    ],
    });
}

// init the data table
function generate_selected_masks(){
    /*
     * Initialse DataTables, with image on the first column
     */
    jQuery("#selected_masks").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Key" },
            { "sTitle": "Field" },
            { "sTitle": "Measure" },
        ],
    "bAutoWidth": false ,
    "aaSorting": [[0, 'desc']],
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 0 ,2] },
    ],
    });
    jQuery('#div_selected_masks').hide();
}

// init the data table
function generate_selected_mutations(){
    /*
     * Initialse DataTables, with image on the first column
     */
    jQuery("#selected_mutations").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Gene id" },
            { "sTitle": "Gene Symb" },
            { "sTitle": "Mutation" },
            { "sTitle": "AA" },
            { "sTitle": "CDS" },
        ],
    "bAutoWidth": false ,
    "aaSorting": [[0, 'desc']],
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 0 ] },
    ],
    });

    jQuery('#div_selected_mutations').hide();
}





// init the data table
function generate_selected_measures(){
    /*
     * Initialse DataTables, with image on the first column
     */
    jQuery("#selected_measures").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Key" },
            { "sTitle": "Measure" },
            { "sTitle": "Unity measure" },
        ],
    "bAutoWidth": false ,
    "aaSorting": [[0, 'desc']],
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 0 ] },
    ],
    });

    jQuery('#div_selected_measures').hide();
}



// init the data table
function generate_region_table(){
    /*
     * Initialse DataTables, with image on the first column
     */
    jQuery("#region_selection").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Select" },
            { "sTitle": "Key" },
            { "sTitle": "Region" },
        ],
    "bAutoWidth": false ,
    "aaSorting": [[1, 'desc']],
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 1 ] },
    ],
    });
}



// init the data table
function generate_measure_table(){
    /*
     * Initialse DataTables, with image on the first column
     */
    jQuery("#measure_selection").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Select" },
            { "sTitle": "Key" },
            { "sTitle": "Measure" },
            { "sTitle": "Unity measure" },
        ],
    "bAutoWidth": false ,
    "aaSorting": [[1, 'desc']],
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 1 ] },
    ],
    });
}


// init the data table
function generate_formula_table(){
    /*
     * Initialse DataTables, with image on the first column
     */
    jQuery("#formula_selection").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Select" },
            { "sTitle": "Key" },
            { "sTitle": "Formula" },
        ],
    "bAutoWidth": false ,
    "aaSorting": [[1, 'desc']],
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 1 ] },
    ],
    });
}