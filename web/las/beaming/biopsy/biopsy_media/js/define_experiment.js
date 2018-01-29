experiment_info = {};
selected_aliquot = '';
selected_geneid = '';
selected_gene = ''
selected_mutid = '';
selected_mut_aa = '';
selected_mut_cds = '';
current_target = '';
targets_selected = {};
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
    generate_table_genes();
    generate_table_mut();
    generate_table_selected_targets();
    read_sel_targets();

    jQuery('#settings_button').click(function(event){
        experiment_info['idinstrument'] = jQuery('#instrument_selection :selected').attr('instrumentid');
        experiment_info['idlayout'] = jQuery('#layout_selection :selected').attr('layoutid');
        jQuery('#instrument_selection').attr('disabled', 'disabled');
        jQuery('#layout_selection').attr('disabled', 'disabled');
        jQuery('#experiment').show();
        jQuery('#targets').show();
        jQuery('#settings_button').attr('disabled', 'disabled');
        jQuery('#terminate_button').removeAttr('disabled');
        getLayout(experiment_info['idlayout']);
    });

    jQuery('#search_gene').click(function(event){
        searchGene();
        jQuery('#table_mut').dataTable().fnClearTable();
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
        selected_mut_cds = '';
        selected_mut_aa = '';
    });
    
    selectionAliquots();

    jQuery('#terminate_button').click(function(event){
        submit_data();
    });


});


function read_sel_targets(){
    var data = jQuery("#table_selected_targets").dataTable().fnGetData();
    jQuery.each(data, function(key, d) {
        targets_selected[d[1] + "|" + d[3]] = d[0];
        nTargets += 1;
        generateRandomColor(d[0]);
    });
    jQuery("#table_selected_targets").dataTable().fnDraw();
}

// generate and manage table of selected targets
function generate_table_selected_targets(){
    jQuery("#table_selected_targets").dataTable( {
    "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Id" },
            { "sTitle": "Gene Id" },
            { "sTitle": "Gene" },
            { "sTitle": "Mutation" },
            { "sTitle": "AA" },
            { "sTitle": "CDS" },
            { "sTitle": ""}
        ],
    "aaSorting": [[0, 'desc']],
    "bAutoWidth": false,

        "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 1 ] },
    ],
    'fnRowCallback': function(nRow, aData, iDisplayIndex, iDisplayIndexFull) {
        $('td:eq(5)', nRow).css('background-color', colors[aData[0]]);
        }
    });

    jQuery("#table_selected_targets tbody").click(function(event) {
        var flag = jQuery(jQuery(event.target.parentNode).children()[0]).hasClass('row_selected');
        console.log(flag);
        jQuery(jQuery('#table_selected_targets').dataTable().fnSettings().aoData).each(function (){
            jQuery(jQuery(this.nTr).children()[0]).removeClass('row_selected');
        });
        if (!flag){
            if (jQuery(jQuery(event.target.parentNode)[0]).is("tr")){
                var pos = jQuery("#table_selected_targets").dataTable().fnGetPosition(jQuery(event.target.parentNode)[0]);
                var data = jQuery("#table_selected_targets").dataTable().fnGetData(pos);
                current_target = data[0];
                console.log(current_target);
                $(jQuery(event.target.parentNode).children()[0]).addClass('row_selected');
            }
        }
        else{
            current_target = '';
        }
    });
}


// generate and manage table of available targets
function generate_table_genes(){
    jQuery("#table_genes").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Id" },
            { "sTitle": "Gene Symbol" }
        ],
    "bAutoWidth": false ,
    "aaSorting": [[0, 'desc']],
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 0 ] },
    ],
    "fnRowCallback": function( nRow, aData, iDisplayIndex ) {
        nRow.className += " gene_el";
        return nRow;
        }
    });
    jQuery('.dataTables_filter').hide();
    
    // click on one row
    jQuery("#table_genes tbody").click(function(event) {
        jQuery(jQuery('#table_genes').dataTable().fnSettings().aoData).each(function (){
            jQuery(this.nTr).removeClass('row_selected');
        });
        if (jQuery(jQuery(event.target.parentNode)[0]).is("tr.gene_el")){
            jQuery(event.target.parentNode).addClass('row_selected');
            var pos = jQuery("#table_genes").dataTable().fnGetPosition(jQuery(event.target.parentNode)[0]);
            var data = jQuery("#table_genes").dataTable().fnGetData(pos);
            selected_geneid = data[0];
            selected_gene = data[1];
            console.log(selected_geneid, selected_gene);
            searchMut(selected_geneid);
        }
    });  
}


// generate and manage table of available targets
function generate_table_mut(){
    jQuery("#table_mut").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "Id" },
            { "sTitle": "AA mutation" },
            { "sTitle": "CDS mutation" }
        ],
    "bAutoWidth": false ,
    "bDeferRender": true,
    "bProcessing": true,
    "aaSorting": [[0, 'desc']],
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
            selected_mutid = data[0];
            selected_mut_aa = data[1];
            selected_mut_cds = data[2];
            // define if target can be selected
            console.log(selected_mutid, selected_mut_aa, selected_mut_cds);
            
            if (targets_selected.hasOwnProperty(selected_geneid + "|" +selected_mutid)){
                alert("Target just selected");
                selected_mutid = '';
                selected_mut_cds = '';
                selected_mut_aa = '';
                jQuery('#select_target').attr('disabled', 'disabled');
            }
            else{
                jQuery(event.target.parentNode).addClass('row_selected');
                jQuery('#select_target').removeAttr('disabled');
            }            
        }
    });
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

function searchGene(){
    // send data
    geneName = jQuery('input[name=search_gene]').val();
    if (geneName == ''){
        return;
    }
    selected_geneid = '';
    selected_gene = '';
    var url =  base_url + '/api.getGenes/' + geneName;
    jQuery.ajax({
        type: 'GET',
        url: url,
        success: function(transport) {
            $(transport).each(function(index, value){
                jQuery('#table_genes').dataTable().fnClearTable();
                jQuery('#table_genes').dataTable().fnAddData([value['id_gene'], value['gene_name']]);
            });
        }, 
        error: function(data) { 
            alert("Submission data error! Please, try again.\n" + data.status, "Warning");
        }
    });
}



function searchMut(geneId){
    // send data
    var url =  base_url + '/api.getMutations/' + geneId;
    jQuery.ajax({
        type: 'GET',
        url: url,
        success: function(transport) {
            jQuery('#table_mut').dataTable().fnClearTable();
            $(transport).each(function(index, value){
                jQuery('#table_mut').dataTable().fnAddData([value['id_mutation'], value['aa_mut_syntax'], value['cds_mut_syntax']]);
            });
        }, 
        error: function(data) { 
            alert("Submission data error! Please, try again.\n" + data.status, "Warning");
        }
    });
}


// select target and put in the final list
function selectTarget(){
    var nSelected = Object.keys(targets_selected).length +1;
    generateRandomColor(nSelected);
    targets_selected[selected_geneid + "|" + selected_mutid] = nSelected;
    jQuery('#table_selected_targets').dataTable().fnAddData([nSelected, selected_geneid, selected_gene, selected_mutid, selected_mut_aa, selected_mut_cds, null]);
    selected_mutid = '';
    selected_mut_aa = '';
    selected_mut_cds = '';
    jQuery('#select_target').attr('disabled', 'disabled');
    jQuery(jQuery('#table_mut').dataTable().fnSettings().aoData).each(function (){
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
                jQuery(event.target.parentNode).css('background-color', '#E68080');
                selected_aliquot = current_al;
            }
        }
    });

}


function generateRandomColor(index){
    while (true){
        var i = Math.floor(Math.random() * 50)
        var r = Math.sin(0.3*i + 0) * 127 +128 ;
        var g = Math.sin(0.3*i + 2) * 127 +128 ;
        var b = Math.sin(0.3*i + 4) * 127 +128 ;
        /*
        var r = Math.floor(Math.random() * 256); //Math.floor((220-100)*Math.random()) + 150;//Math.floor(Math.random()*256);
        var g = Math.floor(Math.random() * 256);//Math.floor((220-100)*Math.random()) + 100;//Math.floor(Math.random()*256);
        var b = Math.floor(Math.random() * 256);//Math.floor((220-100)*Math.random()) + 100;//Math.floor(Math.random()*256);
        */
        console.log(r,g,b);
        var tempColor = RGB2Color(r,g,b);
        var flag = true;
        $.each(colors, function (key, value){
            console.log(value);
            var diff = Math.abs(r - parseInt(value.substring(1,3), 16)) + Math.abs(g - parseInt(value.substring(3,5), 16)) + Math.abs(b - parseInt(value.substring(5,7), 16));
            if (diff < 60){
                flag = false;
            }

        });
        if (flag){
            colors[index]= RGB2Color(r,g,b);//getHex(r,g,b);
            break;
        }
        
    }
}

function RGB2Color(r,g,b)
  {
    return '#' + byte2Hex(r) + byte2Hex(g) + byte2Hex(b);
  }

  function byte2Hex(n)
  {
    var nybHexString = "0123456789ABCDEF";
    return String(nybHexString.substr((n >> 4) & 0x0F,1)) + nybHexString.substr(n & 0x0F,1);
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
        target_to_send[value[0]] = {'gene':value[1], 'probe':value[3], 'genename': value[2], 'aa':value[4], 'cds':value[5]};
    });

    console.log(target_to_send);

    // iterate on all the cells to get the aliquots
    var samples = []
    $.each(jQuery('.cell'), function(index, value){
        if ($(value).is('[targetid]') && $(value).is('[alid]') ){
            aliquots[$(value).attr('alid')]['insert'] = true;
            samples.push({'pos':$(value).attr('id'), 'alid': $(value).attr('alid'), 'gene': target_to_send[$(value).attr('targetid')]['gene'], 'probe': target_to_send[$(value).attr('targetid')]['probe'], 'genename': target_to_send[$(value).attr('targetid')]['genename'], 'aa':target_to_send[$(value).attr('targetid')]['aa'], 'cds':target_to_send[$(value).attr('targetid')]['cds']});
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