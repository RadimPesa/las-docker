//aliquots = []
samples = {}

selectedVal = {}
selectedProbe = {}



$.arrayIntersect = function(a, b)
{
    return $.grep(a, function(i)
    {
        return $.inArray(i, b) > -1;
    });
};


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
    initSNP();
    filterByGene();
    initMuttable();
    initProbeTable();

    
    $('#measure_table').dataTable({
        "aaSorting": [[0, 'asc']],
        "bFilter": false, 
        "bInfo": false,
        "iDisplayLength": -1,
        "bPaginate": false,
        "aoColumnDefs": [
        {'bSortable': false, 'aTargets': [ 'no-sort' ] }
       ]
    });


    $("#formMeas").on('submit',function(e) {
        e.preventDefault();
        uploadMeasFile();
    });

    /*
    jQuery('#submit').click(function(){
        submitMeasures();    
    })
    */
});


function initProbeTable(){
    jQuery("table#probeTable").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "",
              "sWidth": "20px", 
              "sDefaultContent": "<input type='checkbox' class='selectCheck' ></input>", 
              "bSortable": false
            },
            { "sTitle": "Probeid" },
            { "sTitle": "Probe" },
            { "sTitle": "Allele" },
            { "sTitle": "Alteration" },
        ],
    "bAutoWidth": false ,
    "aaSorting": [[2, 'desc']],
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 1 ] }],
    "fnRowCallback": function(nRow, aData, iDisplayIndex, iDisplayIndexFull) {
        $('td:eq(0)', nRow).children('input[type="checkbox"]').on('change', function () {
            var optionSelected = $(this).attr('name');
            if ($(this).is(':checked')){
                selectedProbe[aData[1]] = true;
            }
            else{
                delete selectedProbe[aData[1]];
            }
            
        });
        return nRow;
    },            
    });

}



function initMuttable(){
    jQuery("table#mutTable").dataTable( {
        "bProcessing": true,
         "aoColumns": [
            { "sTitle": "",
              "sWidth": "20px", 
              "sDefaultContent": "<input type='checkbox' class='selectCheck' ></input>", 
              "bSortable": false
            },
            { "sTitle": "Mutid" },
            { "sTitle": "SNP" },
            { "sTitle": "Alteration" },
            { "sTitle": "Value",
              "sDefaultContent": "<input type='number' min=0 max=1 step=0.1 disabled></input>", 
              "bSortable": false },

        ],
    "bAutoWidth": false ,
    "aaSorting": [[2, 'desc']],
    "aoColumnDefs": [
        { "bVisible": false, "aTargets": [ 1 ] }],

    "fnRowCallback": function(nRow, aData, iDisplayIndex, iDisplayIndexFull) {
        $('td:eq(0)', nRow).children('input[type="checkbox"]').on('change', function () {
            var optionSelected = $(this).attr('name');
            if ($(this).is(':checked')){
                selectedVal[aData[1]] = {'val': 0.5, 'name': aData[3]};
                $('td:eq(3)', nRow).children('input[name="' + optionSelected +'"]').attr('disabled', false);
                $('td:eq(3)', nRow).children('input[name="' + optionSelected +'"]').val(0.5);
            }
            else{
                selectedVal[aData[1]] = {'val': 0, 'name': aData[3]};
                //delete selectedVal[aData[1]];
                $('td:eq(3)', nRow).children('input[name="' + optionSelected +'"]').attr('disabled', true);
                $('td:eq(3)', nRow).children('input[name="' + optionSelected +'"]').val('');
            }
            
        });
        $('td:eq(3)', nRow).children('input[type="number"]').on('change', function () {
            selectedVal[aData[1]]['val'] = $(this).val();          
        });
        return nRow;
    },            

    });

}






// init the data table
function generate_table(){

    // manage amplicon bad seq
    $('.ui-icon-wrench').on('click', function(){
        var sid = $(this).parent('td').attr('genealogy');

        $('#probeSample').text(sid);
        $("table#probeTable").dataTable().fnClearTable();
        $("table#probeTable").dataTable().fnFilter('');

        selectedProbe = {}
        for (var k in probes){
            for (var i=0; i < probes[k].length; i++){
                if (samples.hasOwnProperty(sid)){
                    if (samples[sid].hasOwnProperty('bs')) {
                        if ( $.inArray( probes[k][i]['snp_uuid'] , samples[sid]['bs'] ) != -1 ){
                            $("table#probeTable").dataTable().fnAddData( [ '<input type="checkbox" displayname="'+ probes[k][i]['name'] + '"  name="' + probes[k][i]['uuid'] + '" checked>', probes[k][i]['snp_uuid'],  probes[k][i]['name'] , probes[k][i]['allele'],  probes[k][i]['alt'] ] );
                            selectedProbe[probes[k][i]['snp_uuid']] = true;
                        }
                        else{
                            $("table#probeTable").dataTable().fnAddData( [ '<input type="checkbox" displayname="'+ probes[k][i]['name'] + '"  name="' + probes[k][i]['snp_uuid'] + '">', probes[k][i]['snp_uuid'],  probes[k][i]['name'] , probes[k][i]['allele'], probes[k][i]['alt'] ] );
                        }
                    }
                    else{
                        $("table#probeTable").dataTable().fnAddData( [ '<input type="checkbox" displayname="'+ probes[k][i]['name'] + '"  name="' + probes[k][i]['snp_uuid'] + '">', probes[k][i]['snp_uuid'],  probes[k][i]['name'] , probes[k][i]['allele'], probes[k][i]['alt'] ] );
                    }
                }
                else{
                    $("table#probeTable").dataTable().fnAddData( [ '<input type="checkbox" displayname="'+ probes[k][i]['name'] + '"  name="' + probes[k][i]['snp_uuid'] + '">', probes[k][i]['snp_uuid'],  probes[k][i]['name'] , probes[k][i]['allele'], probes[k][i]['alt'] ] );
                }        
            }
        }

        $('#probedialog').dialog({
            autoOpen: false,
            modal: true,
            width: 500,
            resizable: false,
            buttons:
            [
                {
                    text: "OK",
                    click: function() {
                        addRead(sid, 'bs', Object.keys(selectedProbe), true);
                        $(this).dialog("close");
                    }
                },
                {
                    text: "Cancel",
                    click: function() {
                        $(this).dialog("close");
                    }
                }
            ]
        }).dialog("open");

    });


    $('.ui-icon-pencil').hover(
            function(){
                var partr = $(this).parent('td').parent('tr');
                $(partr).find('td.genealogy').addClass('overMut');
            },
            function(){
                var partr = $(this).parent('td').parent('tr');
                $(partr).find('td.genealogy').removeClass('overMut');
            }
    );


    $('.ui-icon-pencil').on('click', function(){
        var partd = $(this).parent('td');
        var sid = $(partd).attr('sid');
        var tid = $(partd).attr('tid');

        $('#obsSample').text(sid);

        selectedVal = {}

        $('input[name=radioMut]').unbind('change');

        $('input[name=radioMut]').on('change', function(){
                var optionSelected = $(this).val();
                if (optionSelected == 'bs'){
                    $('#mutlist').hide();
                }
                else{
                    $('#mutlist').show();
                    $("table#mutTable").dataTable().fnClearTable();
                    $("table#mutTable").dataTable().fnFilter('');
                    var mutVal = 1/targets[tid].length;
                    for (m in targets[tid]){
                        $("table#mutTable").dataTable().fnAddData([ '<input type="checkbox" displayname="'+ targets[tid][m]['name'] + " (Allele "+ targets[tid][m]['allele'] + ")" + '"  name="' + targets[tid][m]['snp_uuid'] + '" checked>', targets[tid][m]['snp_uuid'],  targets[tid][m]['name'] + " (Allele "+ targets[tid][m]['allele'] + ")", targets[tid][m]['alt'], '<input type="number" name="' + targets[tid][m]['snp_uuid'] + '" min=0 max=1 step=0.1 value="' +  mutVal + '"/>']);
                        selectedVal[targets[tid][m]['snp_uuid']] = {'val': mutVal, 'name': targets[tid][m]['alt']};
                    }
                }

        });


        $("table#mutTable").dataTable().fnClearTable();
        $("table#mutTable").dataTable().fnFilter('');
        


        for (m in targets[tid]) {
            var mutVal = null;
            var checked = false;
            var allowedMut = true;
            if (samples.hasOwnProperty(sid)){
                if (samples[sid].hasOwnProperty('mut')){
                    if (samples[sid]['mut'].hasOwnProperty(tid) ){
                        if (samples[sid]['mut'][tid].hasOwnProperty(targets[tid][m]['snp_uuid'])){
                            checked = true;
                            mutVal = samples[sid]['mut'][tid][targets[tid][m]['snp_uuid']]['val'];
                        }
                    }
                }

            }
            //if (allowedMut){
                if (checked){
                    $("table#mutTable").dataTable().fnAddData([ '<input type="checkbox" displayname="'+ targets[tid][m]['name'] + " (Allele "+ targets[tid][m]['allele'] + ")" + '"  name="' + targets[tid][m]['uuid'] + '" checked>', targets[tid][m]['snp_uuid'],  targets[tid][m]['name'] + " (Allele "+ targets[tid][m]['allele'] + ")", targets[tid][m]['alt'], '<input type="number" name="' + targets[tid][m]['snp_uuid'] + '" min=0 max=1 step=0.1 value="' +  mutVal + '"/>']);
                    selectedVal[targets[tid][m]['snp_uuid']] = {'val': mutVal, 'name': targets[tid][m]['alt']};
                    $('input[name=radioMut][value=mut]').prop('checked', true);
                    $('#mutlist').show();

                }
                else{
                    $("table#mutTable").dataTable().fnAddData([ '<input type="checkbox" displayname="'+ targets[tid][m]['name'] + " (Allele "+ targets[tid][m]['allele'] + ")" + '"  name="' + targets[tid][m]['snp_uuid'] + '">', targets[tid][m]['snp_uuid'],  targets[tid][m]['name'] + " (Allele "+ targets[tid][m]['allele'] + ")", targets[tid][m]['alt'], '<input type="number" name="' + targets[tid][m]['snp_uuid'] + '" min=0 max=1 step=0.1 disabled/>']);
                    $('input[name=radioMut][value=bs]').prop('checked', true);
                    $('#mutlist').hide();
                }
            //}
            
        }

        
        $('#mutdialog').dialog({
            autoOpen: false,
            modal: true,
            width: 500,
            resizable: false,
            buttons:
            [
                {
                    text: "OK",
                    click: function() {
                        //console.log(sid, tid)
                        var status = $('input[name=radioMut]:checked').val();
                        if ( status == 'mut'){

                            var availableMut = $("table#mutTable").dataTable().fnGetData();
                            console.log(availableMut)
                            if (availableMut.length == 0){
                                alert('Invalid data.');
                                return;
                            }
                            var cumVal = 0;
                            console.log(selectedVal)             
                            for (var i= 0  in selectedVal){
                                var tval = selectedVal[i]['val'];
                                console.log(tval)
                                if (tval < 0 || tval > 1){
                                    alert('Invalid data');
                                    return;
                                }
                                flagCum = true;
                                cumVal += parseFloat(tval);
                            }
                            console.log( cumVal);
                            if ( cumVal > 1 || cumVal < 0.99){
                                alert('Invalid data. The sum of values should be equal to 1');
                                return;
                            }
                            
                            dictValues = {}
                            dictValues[tid] = selectedVal
                            console.log(sid, tid);
                            addRead(sid, 'mut', dictValues, true);
                        }
                        else{
                            var dictBs = {};
                            for (var i=0; i < targets[tid].length; i++){
                                dictBs[ targets[tid][i]['snp_uuid'] ] = true;
                            }

                            addRead(sid, 'bs', Object.keys(dictBs), true);    
                            delRead(sid, 'mut', tid);
                        }
                        
                                                

                        $(this).dialog("close");
                    }
                },
                {
                    text: "Cancel",
                    click: function() {
                        $(this).dialog("close");
                    }
                }
            ]
        }).dialog("open");
    });

}

// check if a mutation belongs to an amplicon (probe)
function mutBelongsToProbe(tid, pid, mid){
    for (var i=0; i< probes[tid].length; i++){
        if (probes[tid][i]['snp_uuid'] == pid){
            if (targets[tid][mid]['allele'] == probes[tid][i]['allele']){
                return true;
            }
        }
    }
    return false;
}

function untouchedSamples() {
    return Object.keys(sampleTouched).filter(function (k) { return !sampleTouched[k]; });
}

// add measure and update result table
function addRead(sid, status, values, update=false, plate=null, well=null){
    console.log("[addRead]", sid, status, values, update);
    if (update) sampleTouched[sid] = true;

    if (!samples.hasOwnProperty(sid)){
        samples[sid] = {'plate': plate, 'well': well};
    }

    if (status == 'mut'){
	    if (!samples[sid].hasOwnProperty(status)){
        	samples[sid][status] = {};
	    }
    }
    if (status == 'bs'){
            if (!samples[sid].hasOwnProperty(status)){
                samples[sid][status] = [];
            }
    }

       
    console.log(status, values);
    if (status == 'bs'){ 
        var a = samples[sid][status];
        samples[sid][status] = a.concat(values.filter(function (item) {
            return a.indexOf(item) < 0;
        }));

        if (samples[sid][status].length == 0){
            delRead(sid, status, null);
        }
        else{
            $('#measure_table td[genealogy="'+ sid + '"]').find('span.bs').addClass('filteron');
        }
        
        for (var t in probes){
            targetProbes = []    
            for (var p in probes[t]){
                targetProbes.push(probes[t][p]['snp_uuid']);    
            }
            
            var intersection = $.arrayIntersect(targetProbes, Object.keys(values) );
            //console.log(intersection);
            var currText = $('#measure_table td[sid="'+ sid + '"][tid="'+ t + '"]').find('.mut').text();
            var currCss = $('#measure_table td[sid="'+ sid + '"][tid="'+ t + '"]').css("background-color")
            if (intersection.length == targetProbes.length){
                delRead(sid, 'mut', t);
                $('#measure_table td[sid="'+ sid + '"][tid="'+ t + '"]').css("background-color", "orange");
                $('#measure_table td[sid="'+ sid + '"][tid="'+ t + '"]').find('.mut').text('N/A');
            }
            else{
                //console.log(currText, sid, t);    
                $('#measure_table td[sid="'+ sid + '"][tid="'+ t + '"]').css("background-color", currCss);
                $('#measure_table td[sid="'+ sid + '"][tid="'+ t + '"]').find('.mut').text(currText);    
            }                

        }
        
        
    }
    else{ // mut status
            for (var tid in values){
                samples[sid][status][tid] = values[tid];
                
                for (var p in probes[tid]){
                    if (samples.hasOwnProperty(sid)){
                        if ( samples[sid].hasOwnProperty('bs')){
                            var indexProbe = samples[sid]['bs'].indexOf(probes[tid][p]['snp_uuid']);
                            if (indexProbe != -1){
                                samples[sid]['bs'].splice(indexProbe, 1);        
                            }
                            if (samples[sid]['bs'].length == 0){
                                delRead(sid, 'bs', null);
                            }
                            
                        }
                    }                    
                }

                var mutTextList = [];
                //console.log(values[tid]);
                //console.log(tid);
                
                if (Object.keys(values[tid]).length == 0){
                    delRead(sid, status, tid);
                    return;
                }

                for (var i in values[tid]){
                    //console.log(values[tid][i]);
                    var displayname = values[tid][i]['name'];
                    var tval = values[tid][i]['val'];
                    mutTextList.push( displayname + ' ' + tval.toString());
                }
                //console.log($('#measure_table td[sid="'+ sid + '"][tid="'+ tid + '"]'), tid, sid); 
                $('#measure_table td[sid="'+ sid + '"][tid="'+ tid + '"]').css("background-color", "lightgreen");   
                mutText = ''
                for (var i=0; i<mutTextList.length; i++){
                    mutText += mutTextList[i]
                    if (i+1 > 0 && i +1 <= mutTextList.length -1 ){
                        mutText += ' | '
                    }
                }
                $('#measure_table td[sid="'+ sid + '"][tid="'+ tid + '"]').find('.mut').text(mutText);
            }            
    }
}


function delRead(sid, status, tid){
    console.log("[delRead]", sid, status, tid);
    if (tid){
        if (samples.hasOwnProperty(sid) ){
            if (samples[sid].hasOwnProperty(status)){
                delete samples[sid][status][tid];
                if (status == 'mut'){
                    if ( Object.keys( samples[sid][status] ).length == 0){
                        delete samples[sid][status]; 
                    }
                }
                else{
                    if (samples[sid][status].length == 0)
                        delete samples[sid][status];
                }
            }
        }
        
    }
    else{
        delete samples[sid][status];
    }

    if (!samples[sid].hasOwnProperty('bs')){
        $('#measure_table td[genealogy="'+ sid + '"]').find('span.bs').removeClass('filteron');
    }
    if (status == 'mut'){    
        $('#measure_table td[sid="'+ sid + '"][tid="'+ tid + '"]').css("background-color", "orange");
        $('#measure_table td[sid="'+ sid + '"][tid="'+ tid + '"]').find('.mut').text('N/A');
    }

    if (Object.keys(samples[sid]).length == 0)
        delete samples[sid];

}

function updateInput(){
    $('#aliquots_list').val(JSON.stringify(samples));
    //console.log(JSON.stringify(samples));
    var untouched = untouchedSamples();
    $("#measure_table").dataTable().$("tr").each(function () {$(this).children("td:eq(0)").removeClass("highlight");});
    if (untouched.length > 0) {
        $.each(untouched, function(ind, el) {$("#measure_table").dataTable().$("tr[sid='" + el + "']").children("td:eq(0)").addClass("highlight");});
        return window.confirm("No values have been uploaded or manually inserted for the highlighted samples. 'N/A' values will be saved for all known alleles for these samples. Do you wish to proceed?", "Yes", "No");
    }
    return true;
}



function filterByGene(){
    $('#geneFilter').on('change', function(){
        if ($(this).val() == 'All'){ // show all columns
            $('#measure_table th').show();
            $('#measure_table td').show();
        }
        else{//show only column with target gene
            var t = $(this).val();
            $('#measure_table th').hide();
            $('#measure_table th.genealogy').show();
            $('#measure_table td').hide();  
            $('#measure_table td.genealogy').show();
            $('#measure_table th.' + t).show();  
            $('#measure_table td[tid=' + t+']').show();  
        }
    });

}


function uploadMeasFile(){
    var formData = new FormData($('#formMeas')[0]);
    formData.append("actionForm", "fileMeas");
    formData.append("geneMut", JSON.stringify(targets));
    formData.append("probes", JSON.stringify(probes));
    
    $.ajax({
        url: './',  //Server script to process data
        type: 'POST',
        // Form data
        data: formData,
        //Options to tell jQuery not to process data or worry about content-type.
        cache: false,
        contentType: false,
        processData: false,
        success: function(transport) {
            data = JSON.parse(transport);
            console.log(data);
            for (var sid in data){
                for (var status in data[sid]){
                    addRead(sid, status, data[sid][status], true);
                    if (status == 'mut')
                        for (var rs  in data[sid][status] ){
                            tids = Object.keys(data[sid][status][rs])
                            for (var i=0; i< tids.length; i++ ){
                                delRead(sid, 'bs', tids[i]);
                            }
                        }
                    if (status == 'bs'){
                        for (var tid = 0; tid < data[sid][status].length; tid++){
                            for (var rs in probes){
                                for (var i = 0; i < probes[rs].length; i++){
                                    console.log(probes[rs], data[sid][status][tid])
                                    if (data[sid][status][tid] == probes[rs][i]['snp_uuid']){
                                        delRead(sid, 'mut', rs);
                                    }
                                }
                            }   
                        }                           

                    }
                }
            }
            $('#measFile').replaceWith($('#measFile').clone()); 
            
        },
        error: function(data) {
            alert(data.responseText, 'Error');
        }
    });
    

}

function initSNP(){
    var list = $('#measure_table td.genealogy').map(function(){return [[$(this).attr("genealogy"), $(this).attr("plate"), $(this).attr("well")]];}).get();
    for (var i=0; i<list.length; i++){
        //var mutDict = {}
        var snp_list = [];
        for (var t in targets){            
            //mutDict[t] = {}
            for (var j=0; j< targets[t].length; j++){                
                //mutDict[t][ targets[t][j]['snp_uuid'] ] = {'name': targets[t][j]['alt'] , 'val': 1/targets[t].length}
                snp_list.push(targets[t][j]['snp_uuid']);
            }
        }
        //addRead(list[i], 'mut', mutDict);
        addRead(list[i][0], 'bs', snp_list, false, list[i][1], list[i][2]);
        for (var t in targets){            
            delRead(list[i][0], 'mut', t);
        }
    }

}


