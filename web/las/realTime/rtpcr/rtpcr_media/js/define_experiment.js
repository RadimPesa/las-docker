experiment_info = {};
targets_selected = {};
selected_target_data = null;
nTargets = 0;
colors = {}
samples = {}

candidate_targets = {}

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
    generate_table_mut();
    generate_table_selected_targets();
    generate_table_experiment_targets();
    initTabAssay();

    initSamples();

    $( ".spinner" ).spinner({step: 1,
        numberFormat: "n",
        min : 1,
        spin: function( event, ui ) {
            var tr = $(this).closest('tr')
            var alid = $(tr).attr('alid');
            samples[alid] = parseFloat(ui['value']);
      }
    });

    $( ".spinner" ).on('keyup', function(){
        var v = $(this).val();
        var tr = $(this).closest('tr')
        var alid = $(tr).attr('alid');
        if ($.isNumeric(v) == false) {
            return $(this).val(1);
            samples[alid] = 1;
        }
        samples[alid] = parseInt(v);
    });


    //read_sel_targets();

    jQuery('#settings_button').click(function(event){
        experiment_info['idinstrument'] = jQuery('#instrument_selection :selected').attr('instrumentid');
        jQuery('#instrument_selection').attr('disabled', 'disabled');
        jQuery('#experiment').show();
        jQuery('#targets').show();
        jQuery('#settings_button').attr('disabled', 'disabled');
        jQuery('#terminate_button').removeAttr('disabled');
    });

    $(jQuery('#settings_button')[0]).click();

    jQuery('#addtarget_exp').click(function(event){
        for (var t  in candidate_targets){
            if (!targets_selected.hasOwnProperty(t)){
                var newArray = $.merge([null], candidate_targets[t].slice(1));
                jQuery('#table_experiment_targets').dataTable().fnAddData(newArray); 
                targets_selected[newArray[1]] = candidate_targets[t].slice(1);
            }
        }        
        candidate_targets = {};
        $('#selectAllCheck').prop('checked',false);
        $('.selectCheck').prop('checked',false);
    });

    initSearchGene();

    jQuery('#search_target').click(function(event){
        searchMut();
    });


    jQuery('#select_target').click(function(event){
        selectTarget();
    });

    
    jQuery('#reset_targets').click(function(event){
        jQuery('input[name=search_gene]').val('');
        jQuery("#table_mut").dataTable().fnFilter('');
        jQuery('#table_genes').dataTable().fnClearTable();
        jQuery('#table_mut').dataTable().fnClearTable();
        jQuery('#select_target').attr('disabled', 'disabled');
        selected_gene = '';
        selected_geneid = '';
        selected_mutid = '';
        selected_mut_name = '';
        selected_mut_seq = '';
    });
    

    jQuery('#terminate_button').click(function(event){
        submit_data();
    });

    jQuery('#saveAssay').click(function(event){
        saveAssay();
    });

});



function initSearchGene(){
    $("#search_gene").select2({
        width: 'resolve',
        placeholder: 'Start typing a gene symbol...',
        ajax: {
            url: urlAnnot + "newapi/geneInfo/",
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term // search term
                };
            },
            processResults: function (data, page) {
            // parse the results into the format expected by Select2.
            // since we are using custom formatting functions we do not need to
            // alter the remote JSON data
                console.log(data)
                return {results: data};
            },
        },
        minimumInputLength: 1,
        templateResult: function(item) {
            if (item.loading) return item.text;

            return $('<b>'+item.symbol+'</b>&nbsp;<span class="small">('+item.ac+')</span>');
        },
        templateSelection: function(item) {
            if (item.id != "")
                return $('<b>'+item.symbol+'</b>&nbsp;<span class="small">('+item.ac+')</span>');
            else
                return item.text;
        }
    });
    
}


function read_sel_targets(){
    var data = jQuery("#table_experiment_targets").dataTable().fnGetData();
    jQuery.each(data, function(key, d) {
        targets_selected[d[4]] = d[1];
        nTargets += 1;
    });
    jQuery("#table_experiment_targets").dataTable().fnDraw();
}


function generate_table_experiment_targets(){
    jQuery("#table_experiment_targets").dataTable( {
    "bProcessing": true,
         "aoColumns": [
            { "sTitle": "",
               "mDataProp": null, 
               "sWidth": "20px", 
               "sDefaultContent": '<span class="ui-icon  ui-icon-closethick"></span>', 
                "bSortable": false
            },
            { "sTitle": "target Id" },
            { "sTitle": "Name" },
            { "sTitle": "Genes" }, 
            { "sTitle": "Primer A" }, 
            { "sTitle": "Primer B" }, 
            { "sTitle": "Type" },
            { "sTitle": "Ref." },
            { "sTitle": "Start" }, 
            { "sTitle": "End" }, 
            { "sTitle": "Length" }, 
        ],
    "aaSorting": [[2, 'desc']],
    "bAutoWidth": false,

        "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 1 ] },
    ],
    'fnRowCallback': function(nRow, aData, iDisplayIndex, iDisplayIndexFull) {
        $('td:eq(5)', nRow).css('background-color', colors[aData[0]]);
        }
    });

    jQuery( document ).on('click',"#table_experiment_targets tbody td span.ui-icon-closethick", function () {
        var nTr = jQuery(this).parents('tr')[0];
        var pos = jQuery("#table_experiment_targets").dataTable().fnGetPosition(jQuery(this).parents('td')[0]);
        var rmTarget = jQuery("#table_experiment_targets").dataTable().fnGetData(nTr);
        jQuery("#table_experiment_targets").dataTable().fnDeleteRow(pos[0]);
        delete targets_selected[rmTarget[1]];
    }); 
}


// generate and manage table of selected targets
function generate_table_selected_targets(){
    jQuery("#table_selected_targets").dataTable( {
    "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Select<input type='checkbox' id='selectAllCheck'></input>",
                    "sWidth": "20px", 
                    "sDefaultContent": "<input type='checkbox' class='selectCheck' ></input>", 
                    "bSortable": false
                    },
            { "sTitle": "target Id" },
            { "sTitle": "Name" },
            { "sTitle": "Genes" }, 
            { "sTitle": "Primer A" }, 
            { "sTitle": "Primer B" }, 
            { "sTitle": "Type" },
            { "sTitle": "Ref." },
            { "sTitle": "Start" }, 
            { "sTitle": "End" }, 
            { "sTitle": "Length" }, 
        ],
    "aaSorting": [[2, 'desc']],
    "fnDrawCallback": function() {$('#selectAllCheck').prop('checked', false);},
    "fnRowCallback": function(nRow, aData, iDisplayIndex, iDisplayIndexFull) {
                if (candidate_targets.hasOwnProperty(aData[1])) {
                    $('td:eq(0)', nRow).children('.selectCheck').prop('checked',true);
                }
                return nRow;
            },            
    "bAutoWidth": false,
        "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 1 ] },
    ],
    });

    $('#selectAllCheck').prop('checked',false);

    $('#table_selected_targets').on('click','#selectAllCheck',function(){
        if(this.checked) { // check select status
            $('.selectCheck').each(function() { //loop through each checkbox
                $(this).prop('checked', true);
                var tr = $(this).closest('tr');
                var row = $('#table_selected_targets').dataTable().fnGetData(tr[0]);
                candidate_targets[row[1]] = row;
            });
        }else{
            $('.selectCheck').each(function() { //loop through each checkbox
                $(this).prop('checked', false);
                var tr = $(this).closest('tr');
                var row = $('#table_selected_targets').dataTable().fnGetData(tr[0]);
                delete candidate_targets[row[1]];
            });         
        }
    });
    
    
    
    $('#table_selected_targets').on('change','.selectCheck',function(){
        if (this.checked){
            $(this).prop('checked', true);
            var tr = $(this).closest('tr');
            var row = $('#table_selected_targets').dataTable().fnGetData(tr[0]);
            candidate_targets[row[1]] = row;
        }
        else{
            $(this).prop('checked', false);
            var tr = $(this).closest('tr');
            var row = $('#table_selected_targets').dataTable().fnGetData(tr[0]);
            delete candidate_targets[row[1]];
        }
    });

   
}




// generate and manage table of available targets
function generate_table_mut(){
    jQuery("#table_mut").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "target Id" },
            { "sTitle": "Name" },
            { "sTitle": "Genes" }, 
            { "sTitle": "Primer A" }, 
            { "sTitle": "Primer B" }, 
            { "sTitle": "Type" },
            { "sTitle": "Ref." },
            { "sTitle": "Start" }, 
            { "sTitle": "End" }, 
            { "sTitle": "Length" }, 
        ],
    "bAutoWidth": false ,
    "bDeferRender": true,
    "bProcessing": true,
    "aaSorting": [[1, 'desc']],
     "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 0 ] },
    ],
    "fnRowCallback": function( nRow, aData, iDisplayIndex ) {
        nRow.className += " mut_el";
        return nRow;
        }
    });
    
    // click on one row
    jQuery("#table_mut tbody").click(function(event) {
        jQuery(jQuery('#table_mut').dataTable().fnSettings().aoData).each(function (){
            jQuery(this.nTr).removeClass('row_selected');
        });
        if (jQuery(jQuery(event.target.parentNode)[0]).is("tr.mut_el")){
            var pos = jQuery("#table_mut").dataTable().fnGetPosition(jQuery(event.target.parentNode)[0]);
            var data = jQuery("#table_mut").dataTable().fnGetData(pos);
            selected_target_data = data;
            if (targets_selected.hasOwnProperty(data[0])){
                alert("Target just selected");
                selected_target_data = null;
                jQuery('#select_target').attr('disabled', 'disabled');
            }
            else{
                jQuery(event.target.parentNode).addClass('row_selected');
                jQuery('#select_target').removeAttr('disabled');
            }            
        }
    });
}



function searchMut(geneId){
    // send data
    var geneid = $("#search_gene").val();
    var url =  urlAnnot + '/newapi/rtpcrAmpliconInfo/';
    jQuery.ajax({
        type: 'GET',
        data: {'gene_uuid': geneid},
        url: url,
        success: function(transport) {
            jQuery('#table_mut').dataTable().fnClearTable();
            $(transport).each(function(index, value){
                console.log(value);
                var primerfw = null;
                var primerrv = null;

                for (var i= 0; i<value['primers'].length; i++){
                    if (primerfw == null){
                        primerfw = value['primers'][i]['name'];
                    }
                    else{
                        primerrv = value['primers'][i]['name'];
                    }
                }


                jQuery('#table_mut').dataTable().fnAddData([value['uuid'], value['name'], value['gene_symbol'], primerfw, primerrv, value['type'], value['ref'], value['start_base'], value['end_base'], value['length']]);
            });
        }, 
        error: function(data) { 
            alert("Submission data error! Please, try again.\n" + data.status, "Warning");
        }
    });
}


// select target and put in the final list
function selectTarget(){
    targets_selected[selected_target_data[0]] = selected_target_data;
    var newArray = $.merge([null], selected_target_data);
    jQuery('#table_experiment_targets').dataTable().fnAddData(newArray);
    selected_target_data = null;
    jQuery('#select_target').attr('disabled', 'disabled');
    jQuery(jQuery('#table_mut').dataTable().fnSettings().aoData).each(function (){
            jQuery(this.nTr).removeClass('row_selected');
    });
}




function submit_data(){
    var target_to_send = [];
    $(jQuery('#table_experiment_targets').dataTable().fnGetData()).each(function(index, value){
        target_to_send.push(value[1]);
    });

    if ( Object.keys(target_to_send).length == 0){
        alert('No target has been selected!')
        return;
    }
   
    // send data
    var url =  base_url + '/define_experiment/';
    response = {'experiment': experiment_info, 'targets':target_to_send, 'samples': samples};
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


function initTabAssay(){

    jQuery("table#assayTab").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "",
               "mDataProp": null, 
               "sWidth": "10px", 
               "sDefaultContent": '<span class="ui-icon  ui-icon-plusthick"></span>', 
                "bSortable": false
            },
            { "sTitle": "Label" },
            { "sTitle": "Name" },
            { "sTitle": "WG" },

        ],
    "bAutoWidth": false ,
    "aaSorting": [[2, 'desc']],
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 1 ] }],
    });

    jQuery( document ).on('click',"#assayTab tbody td span.ui-icon-plusthick", function () {
        var nTr = jQuery(this).parents('tr')[0];
        var pos = jQuery("#assayTab").dataTable().fnGetPosition(jQuery(this).parents('td')[0]);
        var assay = jQuery("#assayTab").dataTable().fnGetData(nTr);
        jQuery.ajax({
            type: 'GET',
            data: {'assayLabel': assay[1]},
            url: './',
            success: function(transport) {
                console.log(transport)
                data = JSON.parse(transport);
                for (var i=0; i< data['targets'].length; i++){
                    if (!targets_selected.hasOwnProperty(data['targets'][i]['uuid']) ){
                        targets_selected[data['targets'][i]['uuid']] = [data['targets'][i]['uuid'], data['targets'][i]['name'], data['targets'][i]['gene_symbol'], data['targets'][i]['primerfw'], data['targets'][i]['primerrv'], data['targets'][i]['type'], data['targets'][i]['ref'], data['targets'][i]['start_base'], data['targets'][i]['end_base'], data['targets'][i]['length'] ];
                        jQuery("#table_experiment_targets").dataTable().fnAddData([null, data['targets'][i]['uuid'], data['targets'][i]['name'], data['targets'][i]['gene_symbol'], data['targets'][i]['primerfw'], data['targets'][i]['primerrv'], data['targets'][i]['type'], data['targets'][i]['ref'], data['targets'][i]['start_base'], data['targets'][i]['end_base'], data['targets'][i]['length'] ])    
                    }
                }
            }, 
            error: function(data) { 
                alert("Submission data error! Please, try again.\n" + data.status, "Warning");
            }
        });
        
    }); 


}



function saveAssay(){
    var assayName = $('#nameAssay').val();
    var nTargets = Object.keys(targets_selected).length;
    console.log(Object.keys(targets_selected))
    if (assayName != ''){
        if ( nTargets != 0){
            jQuery.ajax({
                type: 'POST',
                data: {'action':'newAssay', 'name': assayName, 'targets':JSON.stringify(Object.keys(targets_selected))}, // insert data for the assay (name, list of amplicons)
                url: urlAssay,
                success: function(transport) {
                    data = JSON.parse(transport);
                    $('#nameAssay').val('');
                    infoBox('Saved');
                    updateAssayTable(data['assays']);
                }, 
                error: function(data) { 
                    console.log(data.responseText);
                    alert(data.responseText, "Error");
                }
            });
        }
        else{
            alert("Please insert at least one target")
        }
    }
    else{
        alert("Please insert a name.");
    }

}


function infoBox(message){
    $("#infobox").text(message);
    $("#infobox").fadeIn( "slow" );
    $("#infobox").css('margin', '10px 0px');
    $("#infobox").css('padding' ,'5px');
    setTimeout(function(){
        $("#infobox").fadeTo(1000,0, function(){
            $("#infobox").html("");
            $("#infobox").removeAttr('style');
            $("#infobox").hide();
        })
    }, 2000);
}


function updateAssayTable(assays){
    jQuery("table#assayTab").dataTable().fnClearTable();
    for (var i= 0; i< assays.length; i++){
       jQuery("table#assayTab").dataTable().fnAddData([null, assays[i]['label'], assays[i]['name'], assays[i]['wg']]);
    }

}


function initSamples(){
    var s = $('tr.aliquot_sample');
    for (var i=0; i< s.length; i++){
        var sid = $(s[i]).attr('alid')
        samples[sid] = 1;
    }
}