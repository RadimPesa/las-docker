//aliquots = []

samples = {}

selectedVal = {}
selectedProbe = {}
idNewMut = 1;


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


function addNewMutation(mut){
    //var mut = {alt: "A", chrom: "12", end: 25398280, gene_ac: "ENSG00000133703", gene_symbol: "KRAS", gene_uuid: "b142984b8257469f9a35fee9fd0eab4b", hgvs_c: "c.39_40insT", hgvs_g: "chr12:g.25398279_25398280insA", hgvs_p: "p.V14Cfs*20", num_bases: null, ref: null, start: 25398279, strand: "-", tx_ac: "ENST00000311936", type: "ins", uuid: null, };
    var index = -1
    for(var i = 0, len = targets[mut['gene_symbol']].length; i < len; i++) {
        if (targets[mut['gene_symbol']][i].hgvs_c === mut.hgvs_c) {
            index = i;
            break;
        }
    }

    if (index == -1){
        mut['uuid'] = 'newMut_'+ idNewMut;
        targets[mut['gene_symbol']].push(mut);
        var actualGene = $('#targetMutTable').val();
        console.log(actualGene);
        if (actualGene == mut['gene_symbol']){
            $("table#mutTable").dataTable().fnAddData([ '<input type="checkbox" displayname="'+mut['hgvs_c'] + '"  name="' + mut['uuid'] + '">', mut['uuid'],  mut['hgvs_c'] ,'<input type="number" name="' + mut['uuid'] + '" min=0 max=1 step=0.1 disabled/>']);
        }
        idNewMut += 1;
        $('#targets').val(JSON.stringify(targets));
        // save on server
        $.ajax({
            url: base_url + '/api.newmutation',
            type: 'POST',
            data: JSON.stringify({'mut': mut}),
            dataType: 'json',
            //Options to tell jQuery not to process data or worry about content-type.
            cache: false,
            contentType: false,
            processData: false,
            success: function(transport) {
                //data = JSON.parse(transport);
                console.log('saved');
            },
            error: function(data) {
                alert(data.responseText, 'Error');
            }
        });
    }

}


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
            { "sTitle": "Gene Symbol" },
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
            { "sTitle": "Mutation" },
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
                selectedVal[aData[1]] = {'val': 0.5, 'name': aData[2]};
                $('td:eq(2)', nRow).children('input[name="' + optionSelected +'"]').attr('disabled', false);
                $('td:eq(2)', nRow).children('input[name="' + optionSelected +'"]').val(0.5);
            }
            else{
                delete selectedVal[aData[1]];
                $('td:eq(2)', nRow).children('input[name="' + optionSelected +'"]').attr('disabled', true);
                $('td:eq(2)', nRow).children('input[name="' + optionSelected +'"]').val('');
            }

        });
        $('td:eq(2)', nRow).children('input[type="number"]').on('change', function () {
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
                        if ( $.inArray( probes[k][i]['uuid'] , samples[sid]['bs'] ) != -1 ){
                            $("table#probeTable").dataTable().fnAddData( [ '<input type="checkbox" displayname="'+ probes[k][i]['name'] + '"  name="' + probes[k][i]['uuid'] + '" checked>', probes[k][i]['uuid'],  probes[k][i]['name'] , probes[k][i]['gene_symbol'] ] );
                            selectedProbe[probes[k][i]['uuid']] = true;
                        }
                        else{
                            $("table#probeTable").dataTable().fnAddData( [ '<input type="checkbox" displayname="'+ probes[k][i]['name'] + '"  name="' + probes[k][i]['uuid'] + '">', probes[k][i]['uuid'],  probes[k][i]['name'] , probes[k][i]['gene_symbol'] ] );
                        }
                    }
                    else{
                        $("table#probeTable").dataTable().fnAddData( [ '<input type="checkbox" displayname="'+ probes[k][i]['name'] + '"  name="' + probes[k][i]['uuid'] + '">', probes[k][i]['uuid'],  probes[k][i]['name'] , probes[k][i]['gene_symbol'] ] );
                    }
                }
                else{
                    $("table#probeTable").dataTable().fnAddData( [ '<input type="checkbox" displayname="'+ probes[k][i]['name'] + '"  name="' + probes[k][i]['uuid'] + '">', probes[k][i]['uuid'],  probes[k][i]['name'] , probes[k][i]['gene_symbol'] ] );
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
                        addRead(sid, 'bs', Object.keys(selectedProbe));
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


        $("table#mutTable").dataTable().fnClearTable();
        $("table#mutTable").dataTable().fnFilter('');

        $('#targetMutTable').val(tid);


        selectedVal = {}
        for (m in targets[tid]) {
            var mutVal = null;
            var checked = false;
            var allowedMut = true;
            if (samples.hasOwnProperty(sid)){
                if (samples[sid].hasOwnProperty('bs')){
                    for (var i= 0; i< samples[sid]['bs'].length; i++){
                        if (mutBelongsToProbe(tid, samples[sid]['bs'][i], m)){
                            allowedMut = false;
                            break;
                        }

                    }

                }
                if (samples[sid].hasOwnProperty('mut')){
                    if (samples[sid]['mut'].hasOwnProperty(tid) ){
                        if (samples[sid]['mut'][tid].hasOwnProperty(targets[tid][m]['uuid'])){
                            checked = true;
                            mutVal = samples[sid]['mut'][tid][targets[tid][m]['uuid']]['val'];
                        }
                    }
                }

            }
            if (allowedMut){
                if (checked){
                    $("table#mutTable").dataTable().fnAddData([ '<input type="checkbox" displayname="'+ targets[tid][m]['hgvs_c'] + '"  name="' + targets[tid][m]['uuid'] + '" checked>', targets[tid][m]['uuid'],  targets[tid][m]['hgvs_c'] ,'<input type="number" name="' + targets[tid][m]['uuid'] + '" min=0 max=1 step=0.1 value="' +  mutVal + '"/>']);
                    selectedVal[targets[tid][m]['uuid']] = {'val': mutVal, 'name': targets[tid][m]['hgvs_c']};
                }
                else{
                    $("table#mutTable").dataTable().fnAddData([ '<input type="checkbox" displayname="'+ targets[tid][m]['hgvs_c'] + '"  name="' + targets[tid][m]['uuid'] + '">', targets[tid][m]['uuid'],  targets[tid][m]['hgvs_c'] ,'<input type="number" name="' + targets[tid][m]['uuid'] + '" min=0 max=1 step=0.1 disabled/>']);
                }
            }

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
                        var availableMut = $("table#mutTable").dataTable().fnGetData();
                        if (availableMut.length == 0){
                            $(this).dialog("close");
                            return;
                        }

                        for (var i= 0  in selectedVal){
                            var tval = selectedVal[i]['val'];
                            if (tval < 0.01 || tval > 1){
                                alert('Invalid data');
                                return;
                                }
                        }
                        dictValues = {}
                        dictValues[tid] = selectedVal
                        addRead(sid, 'mut', dictValues);
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
        if (probes[tid][i]['uuid'] == pid){
            var ref = probes[tid][i]['ref'];
            if (probes[tid][i]['type'] == 'gDNA'){
                ref = ref.replace('chr', '');
            }
            if (targets[tid][mid]['chrom'] == ref){
                if (targets[tid][mid]['start'] >= probes[tid][i]['start_base'] &&  targets[tid][mid]['start'] <= probes[tid][i]['end_base'] && targets[tid][mid]['end'] >= probes[tid][i]['start_base'] &&  targets[tid][mid]['end'] <= probes[tid][i]['end_base'])
                    return true;
            }
        }
    }
    return false;
}


// add measure and update result table
function addRead(sid, status, values){
    if (!samples.hasOwnProperty(sid)){
        samples[sid] = {};
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




    if (status == 'bs'){
        if (values.length == 0){
            console.log(status);
            delRead(sid, status, null); // n/a for a set of amplicons --> update the table with the alert icon
        }
        else{
            samples[sid][status] = values;
            $('#measure_table td[genealogy="'+ sid + '"]').find('span.bs').addClass('filteron');
        }


        for (var t in probes){
            targetProbes = []
            for (var p in probes[t]){
                targetProbes.push(probes[t][p]['uuid']);
            }
            var intersection = $.arrayIntersect(targetProbes, values);
            console.log(intersection);
            var currText = $('#measure_table td[sid="'+ sid + '"][tid="'+ t + '"]').find('.mut').text();
            var currCss = $('#measure_table td[sid="'+ sid + '"][tid="'+ t + '"]').css("background-color")
            if (intersection.length == targetProbes.length){
                delRead(sid, 'mut', t);
                $('#measure_table td[sid="'+ sid + '"][tid="'+ t + '"]').css("background-color", "orange");
                $('#measure_table td[sid="'+ sid + '"][tid="'+ t + '"]').find('.mut').text('N/A');
            }
            else{
                console.log(currText, sid, t);
                if (currText == 'N/A'){
                    $('#measure_table td[sid="'+ sid + '"][tid="'+ t + '"]').css("background-color", 'lightgreen');
                    $('#measure_table td[sid="'+ sid + '"][tid="'+ t + '"]').find('.mut').text('WT');
                }
                else{
                    $('#measure_table td[sid="'+ sid + '"][tid="'+ t + '"]').css("background-color", currCss);
                    $('#measure_table td[sid="'+ sid + '"][tid="'+ t + '"]').find('.mut').text(currText);
                }
            }

        }



    }
    else{ // mut status
            for (var tid in values){
                samples[sid][status][tid] = values[tid];
                var mutTextList = [];
                console.log(values[tid]);
                console.log(tid);
                if (Object.keys(values[tid]).length == 0){
                    delRead(sid, status, tid);
                    return;
                }

                for (var i in values[tid]){
                    console.log(values[tid][i]);
                    var displayname = values[tid][i]['name'];
                    var tval = values[tid][i]['val'];
                    mutTextList.push( displayname + ' ' + tval.toString());
                }
                console.log($('#measure_table td[sid="'+ sid + '"][tid="'+ tid + '"]'), tid, sid);
                $('#measure_table td[sid="'+ sid + '"][tid="'+ tid + '"]').css("background-color", "red");
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

    if (status == 'bs'){
        $('#measure_table td[genealogy="'+ sid + '"]').find('span.bs').removeClass('filteron');
    }
    if (status == 'mut'){
        $('#measure_table td[sid="'+ sid + '"][tid="'+ tid + '"]').css("background-color", "lightgreen");
        $('#measure_table td[sid="'+ sid + '"][tid="'+ tid + '"]').find('.mut').text('WT');
    }

    if (Object.keys(samples[sid]).length == 0)
        delete samples[sid];

}

function updateInput(){
    $('#aliquots_list').val(JSON.stringify(samples));
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
            for (var sid in data){
                for (var status in data[sid]){
                    addRead(sid, status, data[sid][status]);
                }
            }
            $('#measFile').replaceWith($('#measFile').clone());

        },
        error: function(data) {
            alert(data.responseText, 'Error');
        }
    });


}
