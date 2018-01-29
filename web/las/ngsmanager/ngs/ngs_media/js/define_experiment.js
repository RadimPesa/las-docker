experiment_info = {};
targets = {};
nTargets = 0;
selected_aliquot = '';
selected_gene = '';
selected_mut = '';
current_target = '';
targets_selected = {};
colors = {}

// init document
jQuery(document).ready(function(){
    experiment_info['idplan'] = jQuery('#plan').attr('idplan');
    generate_table_target();
    generate_table_selected_targets();
    jQuery('#settings_button').click(function(event){
        experiment_info['idinstrument'] = jQuery('#instrument_selection :selected').attr('instrumentid');
        experiment_info['idlayout'] = jQuery('#layout_selection :selected').attr('layoutid');
        jQuery('#instrument_selection').attr('disabled', 'disabled');
        jQuery('#layout_selection').attr('disabled', 'disabled');
        jQuery('#experiment').show();
        jQuery('#settings_button').attr('disabled', 'disabled');
        jQuery('#terminate_button').removeAttr('disabled');
        getLayout(experiment_info['idlayout']);
    });

    jQuery('#insert_target').click(function(event){
        addTarget();
    });


    jQuery('#search_target').click(function(event){
        searchTarget();
    });

    jQuery('input[name=insert_gene]').keyup(function() {
        searchTarget();
    });

    jQuery('input[name=insert_probe]').keyup(function() {
        searchTarget();
    });


    jQuery('#reset_targets').click(function(event){
        jQuery('input[name=insert_probe]').val('');
        jQuery('input[name=insert_gene]').val('');
        resetFilters();
    });

    jQuery('#select_target').click(function(event){
        selectTarget();
    });

    selectionAliquots();

    jQuery('#terminate_button').click(function(event){
        submit_data();
    });


});

// generate and manage table of selected targets
function generate_table_selected_targets(){
    jQuery("#table_selected_targets").dataTable( {
    "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Id" },
            { "sTitle": "Gene" },
            { "sTitle": "Mutation" },
            { "sTitle": "Color"}
        ],
    "aaSorting": [[0, 'desc']],
    "bAutoWidth": false,
    "bFilter": false,
    
    'fnRowCallback': function(nRow, aData, iDisplayIndex, iDisplayIndexFull) {
        $('td:eq(3)', nRow).css('background-color', colors[aData[0]]);
        }
    });

    jQuery("#table_selected_targets tbody").click(function(event) {
        var flag = jQuery(jQuery(event.target.parentNode).children()[0]).hasClass('row_selected');
        jQuery(jQuery('#table_selected_targets').dataTable().fnSettings().aoData).each(function (){
            jQuery(jQuery(this.nTr).children()[0]).removeClass('row_selected');
        });
        if (!flag){
            if (jQuery(jQuery(event.target.parentNode)[0]).is("tr")){
                var pos = jQuery("#table_targets").dataTable().fnGetPosition(jQuery(event.target.parentNode)[0]);
                var data = jQuery("#table_targets").dataTable().fnGetData(pos);
                current_target = data[0];
                $(jQuery(event.target.parentNode).children()[0]).addClass('row_selected');
            }
        }
        else{
            current_target = '';
        }
    });
}


// generate and manage table of available targets
function generate_table_target(){
    jQuery("#table_targets").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Id" },
            { "sTitle": "Gene" },
            { "sTitle": "Mutation" }
        ],
    "bAutoWidth": false ,
    "aaSorting": [[0, 'desc']],
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 0 ] },
    ],
    "fnRowCallback": function( nRow, aData, iDisplayIndex ) {
        nRow.className += " target_el";
        return nRow;
        }
    });
    jQuery('.dataTables_filter').hide();
    
    // click on one row
    jQuery("#table_targets tbody").click(function(event) {
        jQuery(jQuery('#table_targets').dataTable().fnSettings().aoData).each(function (){
            jQuery(this.nTr).removeClass('row_selected');
        });
        if (jQuery(jQuery(event.target.parentNode)[0]).is("tr.target_el")){
            var pos = jQuery("#table_targets").dataTable().fnGetPosition(jQuery(event.target.parentNode)[0]);
            var data = jQuery("#table_targets").dataTable().fnGetData(pos);
            selected_gene = data[1];
            selected_mut = data[2];
            // define if target can be selected
            if (targets_selected.hasOwnProperty(selected_gene + "|" +selected_mut)){
                alert("Target just selected");
                selected_gene = '';
                selected_mut = '';
                jQuery('#select_target').attr('disabled', 'disabled');
            }
            else{
                jQuery(event.target.parentNode).addClass('row_selected');
                jQuery('#select_target').removeAttr('disabled');
            }
        }
    });


    var target_list = jQuery("table#table_targets").dataTable().fnGetData();
    jQuery().each(target_list, function (index, value){
        targets[value[1] + '|' + value[2]] = value[0];
        if (nTargets<value[0]){
            nTargets=value[0];
        }
    });    
}

// add a target
function addTarget(){
    var probe = jQuery('input[name=insert_probe]').val().toUpperCase();
    var gene = jQuery('input[name=insert_gene]').val().toUpperCase();
    if (probe == "" || gene == ""){
        return;
    }
    if (targets.hasOwnProperty(gene+'|'+ probe)){
        alert ('Target just present. Please click on search to find it.');
        return;
    }
    jQuery("#table_targets").dataTable().fnAddData([nTargets+1,gene,probe]);
    targets[gene+'|'+ probe] = nTargets+1;
    nTargets++;
}



// retrieve the layout of the container and reproduce it
function getLayout(idGeo){
    var url =  base_url + '/api.getLayout/' + idGeo;
    jQuery.ajax({
        type: 'GET',
        url: url, 
        success: function(transport) {
            jQuery('#plate').append(transport);
            addListenerGeometry();
        },  
        error: function(data) { 
            alert("Submission data error! Please, try again.\n" + data.status, "Warning");
        }
    });
}

// reset filters on available targets
function resetFilters(){
    jQuery("#table_targets").dataTable().fnFilter('');
    jQuery("#table_targets").dataTable().fnFilter('',1);
    jQuery("#table_targets").dataTable().fnFilter('',2);
}


// search available target
function searchTarget(){
    var probe = jQuery('input[name=insert_probe]').val().toUpperCase();
    var gene = jQuery('input[name=insert_gene]').val().toUpperCase();
    resetFilters();
    if (gene != ""){
        jQuery("#table_targets").dataTable().fnFilter(gene,1,false, true);
    }
    if (probe != ""){
        jQuery("#table_targets").dataTable().fnFilter(probe,2,false, true);
    }
}

// select target and put in the final list
function selectTarget(){
    var nSelected = Object.keys(targets_selected).length +1;
    generateRandomColor(nSelected);
    targets_selected[selected_gene + "|" + selected_mut] = nSelected;
    jQuery('#table_selected_targets').dataTable().fnAddData([nSelected, selected_gene, selected_mut, null]);
    selected_gene = '';
    selected_mut = '';
    jQuery('#select_target').attr('disabled', 'disabled');
    jQuery(jQuery('#table_targets').dataTable().fnSettings().aoData).each(function (){
            jQuery(this.nTr).removeClass('row_selected');
    });



}

// add evetn listener for the conatiner
function addListenerGeometry(){
    // all the row
    jQuery('.row').on('click', function(event){
        var cell = ''
        if ($(event.target).is('strong'))
            cell = event.target.parentNode
        else{
            if ($(event.target).is('td'))
                cell = event.target
        }
        var rowId = jQuery(cell).attr('row');
        // management of aliquots
        if (selected_aliquot != ""){
            jQuery('.cell').filter('[row=' + rowId +']').text('AL' + selected_aliquot);
            jQuery('.cell').filter('[row=' + rowId +']').attr('alid', selected_aliquot);
        }
        else {
            if (current_target == ""){
                jQuery('.cell').filter('[row=' + rowId +']').text('0');
                jQuery('.cell').filter('[row=' + rowId +']').removeAttr('alid');
            }
        }
        // management of targets
        if (current_target != ""){
            jQuery('.cell').filter('[row=' + rowId +']').css('background-color',colors[current_target]);
            jQuery('.cell').filter('[row=' + rowId +']').attr('targetid', current_target);
        }
        else{
            if (selected_aliquot == ""){
                jQuery('.cell').filter('[row=' + rowId +']').removeAttr('style');
                jQuery('.cell').filter('[row=' + rowId +']').removeAttr('targetid');
            }
        }
    });

    // all the column
    jQuery('.column').on('click', function(event){
        var cell = ''
        if ($(event.target).is('strong'))
            cell = event.target.parentNode
        else{
            if ($(event.target).is('td'))
                cell = event.target
        }
        var colId = jQuery(cell).attr('col');
        // management of aliquots
        if (selected_aliquot != ""){
            jQuery('.cell').filter('[col=' + colId +']').text('AL' + selected_aliquot);
            jQuery('.cell').filter('[col=' + colId +']').attr('alid', selected_aliquot);
        }
        else{
            if (current_target == ""){
               jQuery('.cell').filter('[col=' + colId +']').text('0');
               jQuery('.cell').filter('[col=' + colId +']').removeAttr('alid');
            }
        }
        // management of targets
        if (current_target != ""){
            jQuery('.cell').filter('[col=' + colId +']').css('background-color',colors[current_target]);
            jQuery('.cell').filter('[col=' + colId +']').attr('targetid', current_target);
        }
        else{
            if (selected_aliquot == ""){
                jQuery('.cell').filter('[col=' + colId +']').removeAttr('style');
                jQuery('.cell').filter('[col=' + colId +']').removeAttr('targetid');
            }
        }
    });

    // management of button click
    jQuery('.cell').on('click', function(event){
        // management of aliquots
        if (selected_aliquot != ""){
            $(event.target).attr('alid', selected_aliquot);
            $(event.target).text('AL' + selected_aliquot);
        }
        else{
            if (current_target == ""){
                $(event.target).removeAttr('alid');
                $(event.target).text('0');
            }
        }
        if (current_target != ""){
            $(event.target).attr('targetid', current_target);
            $(event.target).css('background-color',colors[current_target]);
        }
        else{
            if (selected_aliquot == ""){
                $(event.target).removeAttr('targetid');
                $(event.target).removeAttr('style'); 
            }
        }
    });
}


function selectionAliquots(){
    jQuery('.sample').on('click', function(event){
        if ($(event.target.parentNode).is('tr') || $(event.target.parentNode).is('th')){
            current_al = jQuery(event.target.parentNode).attr('alid');
            jQuery('.sample').parent().css('background-color', 'white');
            if (current_al == selected_aliquot){
                selected_aliquot = '';
            }
            else{
                jQuery(event.target.parentNode).css('background-color', 'red');
                selected_aliquot = current_al;
            }
        }
    });

}


function generateRandomColor(index){
    var r = Math.floor((220-100)*Math.random()) + 150;//Math.floor(Math.random()*256);
    var g = Math.floor((220-100)*Math.random()) + 100;//Math.floor(Math.random()*256);
    var b = Math.floor((220-100)*Math.random()) + 100;//Math.floor(Math.random()*256);
    colors[index]= getHex(r,g,b);
}

// intToHex()
 function intToHex(n){
    n = n.toString(16);
    // eg: #0099ff. without this check, it would output #099ff
    if( n.length < 2) 
        n = "0"+n; 
    return n;
 }
 
 // getHex()
 // shorter code for outputing the whole hex value
 function getHex(r, g, b){
    return '#'+intToHex(r)+intToHex(g)+intToHex(b); 
 }



function submit_data(){

    var aliquots = {}
    jQuery('.aliquot_sample').each(function(index, value){
        aliquots[$(value).attr('alid')] = {'genid':$(value).attr('genid'), 'insert':false};
    });

    console.log(aliquots);

    var target_to_send = {};

    $(jQuery('#table_selected_targets').dataTable().fnGetData()).each(function(index, value){
        target_to_send[value[0]] = {'gene':value[1], 'probe':value[2]};
    });

    console.log(target_to_send);

    // iterate on all the cells to get the aliquots
    var samples = []
    $.each(jQuery('.cell'), function(index, value){
        if ($(value).is('[targetid]') && $(value).is('[alid]') ){
            aliquots[$(value).attr('alid')]['insert'] = true;
            samples.push({'pos':$(value).attr('id'), 'alid': $(value).attr('alid'), 'gene': target_to_send[$(value).attr('targetid')]['gene'], 'probe': target_to_send[$(value).attr('targetid')]['probe']});
        }
    });
    console.log(samples);
    var flagInterrupt = false;
    $.each(aliquots, function(key, value){
        if (value['insert'] == false){
            alert('Insert all the aliquots before submit the experiment.');
            flagInterrupt = true;
            return;
        }
    });
    
    if (flagInterrupt == true)
        return;


    // send data
    var url =  base_url + '/define_experiment/';
    response = {'samples': samples, 'experiment_info':experiment_info};
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