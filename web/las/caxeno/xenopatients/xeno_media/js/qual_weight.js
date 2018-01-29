var typeMeasure = "qual"; groups = {}; physBio = {}; var barcodeSiteList = []; 

jQuery(document).ready(function () {
    listKey = ['qual','qualuser', 'qualtimestamp', 'qualPhysBio'];
    document.getElementById('id_weight').focus();
    jQuery("#radio li").attr('style','float:left');
    jQuery("label[for='id_value_3']").attr('style','padding-right:5px');
    oTable = jQuery('#measure').dataTable( {
        "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        "iDisplayLength": -1,
        "aoColumnDefs": [
            { "bVisible": false, "aTargets": [2,8,10,12,13,16 ] },
        ],
        "aaSorting": [[0, 'asc']]
    });
    checkStorageMeasure(listKey, oTable, 'qual');
    console.log(physBio);
    //jQuery("label[for='id_site']").css('margin-left', '75px');
    var valueMap = [];
    $('#slider input[type="radio"]').each( function(){
            console.log( this.value );
            valueMap.push(this.value);
        }
    );
    $("#slider").empty();
    $('#slider').slider({
        range: false,
        min: 0,
        max: valueMap.length-1,
        step:1,
        slide: function(event, ui) {
            $("#id_value").val(valueMap[ui.value]);
        }
    }).each(function() {
        var opt = $(this).data().uiSlider.options;
        var vals = valueMap.length-1;
        for (var i = 0; i <= vals; i+=2) {
            var el = $('<label>'+(valueMap[i])+'</label>').css('left',(i/vals*100)+'%');
            $( "#slider" ).append(el);
        }
        var hslider = $( "#slider" ).outerHeight();
        var hlabel = $($( "#slider label" )[0]).outerHeight();
        console.log(hslider, hlabel);
        $('#slider_container').css('height', hslider + hlabel);
    });
    $("#id_value").val(valueMap[0]);
    $('#slider').css('width', '15%');
    $('#slider').css('margin-left', '15px');
    $('#slider').css('margin-bottom', '20px');
    $('#slider').css('margin-right', '20px');
    $('#input').css('margin-top', '5px');
    $('#a').css('margin-top', '5px');
    $('#slider').css('margin-top', '5px');
} );

function isNewSite(barcode, site){
    if (barcodeSiteList.indexOf(barcode + site) > -1)
        return false;
    return true;
}

function isInCurrentTable(genID){
    console.log(genID);
    var nodes = oTable.fnGetNodes();
    console.log(nodes);
    for (var i = 0; i < nodes.length; i++ ){
        if (genID == oTable.fnGetData( i, 1 ) )
            return true;
    }
    return false;
}

function updateStruct(msg, currG, genID, scope, explNotes){
    try {
        console.log('updateStruct');
        groups[currG][genID][6] = msg;
        if (msg == "ready for explant"){
            groups[currG][genID][7] = scope;
            groups[currG][genID][10] = explNotes;
        }else{
            groups[currG][genID][7] = "";
            groups[currG][genID][10] = "";
            if (msg = "sacrifice without explant"){
                groups[currG][genID][11] = "";
                groups[currG][genID][12] = "";
                groups[currG][genID][13] = "";
                groups[currG][genID][14] = "";
                groups[currG][genID][15] = "";
            }
        }
    }catch(e) {
        alert(e);
    }
}


function wToB(evt){
    var charCode = (evt.which) ? evt.which : event.keyCode
    if ( charCode == 13 ) //codice ASCII del carattere carriage return (invio)
        $('#id_barcode').focus();
}

function checkKey(evt){
    var charCode = (evt.which) ? evt.which : event.keyCode
    if ( charCode == 13 ) //codice ASCII del carattere carriage return (invio)
        makeMeasure();
}

function saveQual (){
    jQuery("#save").attr("disabled",true);
    var currGroup = jQuery('#tableList').attr('currgroup');
    if (Object.size(groups) > 0){
	    jQuery.ajax({
		    url: base_url + '/measurement/qual',
		    type: 'POST',
		    data: {'obj':JSON.stringify(groups), 'lastG':currGroup},
		    dataType: 'text',
	    });
    }else{
        alert("You cannot save an empty measurement set.");
        jQuery("#save").attr("disabled",false);
    }
}

function supervisor (){
   //scorre tutte le righe selezionate
   //setta a 'true' la richiesta per il supervisor 
    var nodes = oTable.fnGetNodes();
    var rows = fnGetSelected();
    if (rows.length > 0){
        for(var i = 0; i < nodes.length; i++) {
            var row = nodes[i];
            if (jQuery.inArray(row, rows) > -1){
                    //oTable.fnUpdate(data, row, column, redraw[bool], predraw[bool]);
                    oTable.fnUpdate('true', i, 16, false, false);
                    var currG = jQuery('#tableList').attr('currgroup');
                    var genID = oTable.fnGetData(i,1);
                    groups[currG][genID][16] = 'true';
                    //console.log(groups);
                    storageIt('qual', JSON.stringify(groups));
                    //togliere la selezione della riga
                    jQuery(row).toggleClass('row_selected');
                }
            }
    }else
        alert("You have to select al least one row.");
}

function makeMeasure(){
    var barcode = document.getElementById("id_barcode").value.toUpperCase();
    var site = jQuery("#id_site :selected").val();
    var url = base_url + "/api.mouseformeasure/" + barcode + '/' + site;
    if ($('#id_weight').val() == ""){
        alert("Please insert a weight measure");
    }
    else{

        var wCheck = "";
        var wCheckFlag = true;
        if (document.getElementById("id_weight").value!=""){
            wCheck = document.getElementById("id_weight").value;
            wCheck = wCheck.replace(',','.');
            if (parseFloat(wCheck) < 0)
                wCheckFlag = false;
        }        
        if (!isNaN(wCheck) && wCheckFlag == true){
            if (document.getElementById("id_barcode").value != ""){
                jQuery.ajax({
                    url:url,
                    method:'get',
                    datatype:'json', 
                    async:false,
                    success: function(transport){
                        if (transport['status'] == "err"){
                            alert(transport['message']);
                        }else{
                            var mouse = transport;
                            console.log(mouse);
                            var status = mouse['generalInfo']['status'];
                            if (status == 'implanted' || status == 'ready for explant' || status == 'explantLite' || status == 'waste' || status == 'transferred'){
                                var mouseGroup = mouse['generalInfo']['group'];
                                if (document.getElementById('tableList').rows[0].cells.length == 0){
                                    groups[mouseGroup] = {};
                                    addToList(mouseGroup);
                                }else{
                                    console.log('gruppo topo' + mouseGroup);
                                    var currGroup = jQuery('#tableList').attr('currGroup');
                                    console.log(currGroup + ' -->  ' + mouseGroup);
                                    if (currGroup != mouseGroup){
                                        //add group to list
                                        console.log('add new');
                                        var newG = isNewGroup(mouseGroup);
                                        console.log(newG);
                                        if (newG){
                                            if ( groups.hasOwnProperty(mouseGroup) == false ){
                                                console.log('newG');
                                                //console.log(groups);
                                                console.log(mouseGroup);
                                                groups[mouseGroup] = {};
                                                storageIt('qual', JSON.stringify(groups));
                                            }
                                            addToList(mouseGroup);
                                            swapTable(mouseGroup, 'true');
                                        }else
                                            swapTable(mouseGroup, 'false');
                                    }
                                } 
                                jQuery('#tableList').attr('currGroup', mouseGroup);
                                //if (isNewMeasure(barcode, site)){
                                if (isNewSite(barcode, site)){
                                    addRow('measure', mouseGroup, status, mouse, groups);
                                    barcodeSiteList.push(barcode + site);

                                }else
                                    alert("You've already measured this site of this mouse in the current session.");
                            }else{
                                alert('This mouse is ' + status + '. Only implanted mice and mice ready for explant (with or without sacrifice) can be measured');
                            }
                        }
                    }
                });
            }else{
                alert("You've inserted a blank barcode");
            }
        }
        else{
            alert("Weight must be a positive integer/decimal number.");
        }
    }
}

//aggiunge una riga alla tabella prendendo i dati dall'input utente. Effettua vari controlli sull'input.
function addRow(tableID, mouseGroup,status, mouse, groups_) {
    console.log(mouseGroup);
    var barcode = document.getElementById("id_barcode").value.toUpperCase();
    if (physBio.hasOwnProperty(barcode) == false ){
        var url = base_url + "/api.phystobio/" + barcode;
        jQuery.ajax({
            url:url,
            method:'get',
            datatype:'json', 
            async:false,
            success: function(transport){
                console.log(transport);
                physBio[barcode] = {};
                physBio[barcode] = transport;
            }
        });
    }
    var table = document.getElementById(tableID);
    var rowCount = oTable.fnGetNodes().length;
    var checkSuper = "";var value="";
    console.log('rows '+rowCount);
    value = $("#id_value").val();
    value = 'N.D.'
    var notes = document.getElementById("id_notes").value;
    var wCheck = 0;
    if (document.getElementById("id_weight").value!=""){
        wCheck = document.getElementById("id_weight").value;
        wCheck = wCheck.replace(',','.');
    }               
    if (!isNaN(wCheck) && parseFloat(wCheck) >= 0){
        var genID = "";var group = "";var explant = "";var scope = "";var scopeNotes = "";var treatment = "";/*var date = "";var time = "";*/var extra = "";
        var acute = "";var duration = "";var continueFlag = Boolean(false); var dateS = ""; var oldW = ""; var oldWDate = ""; var weight = wCheck;
        var counterH = getIndex(oTable) + 1;
        genID = mouse['generalInfo']['genID'];
        if (status == 'ready for explant'){
            explant = "ready for explant";
        }else{
            if (status == 'explantLite')
                explant = "explant without sacrifice";
            else
                explant = "not programmed for explant";
        }
        console.log('STATUS: ' + status);
        scope = mouse['expl']['scope'];
        scopeNotes = mouse['expl']['scopeNotes'];
        dateS = mouse['treat']['start'];
        if (mouse['treat']['duration'] != "")
            duration = mouse['treat']['duration'] + ' [' + mouse['treat']['typeTime'] + ']';
        if (mouse['treat']['nameA'] != "")
            treatment = getName(mouse['treat']['nameP'], mouse['treat']['nameA']);
        extra = "actual"; 
        if (mouse['treat']['forces_explant'])
            acute = "true";
        else
            acute = "false";
        oldW = mouse['weight']['w'];
        oldWDate = mouse['weight']['dateW'];
        if (groups.hasOwnProperty(mouseGroup)){
            console.log(mouseGroup, genID, groups.hasOwnProperty(mouseGroup));
            console.log('genid ' + genID);
            if (genID in groups[mouseGroup]){
                console.log("A");
                if (groups[mouseGroup][genID][6] != ""){ //info relative ad espianti
                    explant = groups[mouseGroup][genID][6];
                    scope = groups[mouseGroup][genID][7];
                    scopeNotes = groups[mouseGroup][genID][10];
                }
                if ( (groups[mouseGroup][genID][11] != "") || ( groups[mouseGroup][genID][12] == "stop" ) ){ //info relative a trattamenti
                    //explant = groups[mouseGroup][genID][5];
                    //scope = groups[mouseGroup][genID][6];
                    //scopeNotes = groups[mouseGroup][genID][10];/*info expl per eventuali tratt acuti*/
                    treatment = groups[mouseGroup][genID][11];
                    extra = groups[mouseGroup][genID][12];
                    dateS = groups[mouseGroup][genID][14];
                    duration = groups[mouseGroup][genID][15];
                }
            }else{
                console.log("B");
                groups[mouseGroup][genID] = [];
            }
        }else{
            console.log("C");
            groups[mouseGroup] = {};
            groups[mouseGroup][genID] = [];
        }

        console.log([counterH, genID, value, oldW, oldWDate, explant, scope, notes, barcode, weight, scopeNotes, treatment, extra, acute, dateS, duration, checkSuper]);
        groups[mouseGroup][genID]=[counterH, genID, value, weight, oldW, oldWDate, explant, scope, notes, barcode, scopeNotes, treatment, extra, acute, dateS, duration, checkSuper];
        //console.log(groups);
        storageIt('qual', JSON.stringify(groups));
        storageIt('qualPhysBio', JSON.stringify(physBio));
        //jQuery('#measure').dataTable().fnAddData([counterH,genID,value,oldW,oldWDate,explant,scope,notes,barcode,weight,scopeNotes,treatment,extra,acute,dateS,duration,checkSuper]);
        jQuery('#measure').dataTable().fnAddData([counterH, genID, value, weight, oldW, oldWDate, explant, scope, notes, barcode, scopeNotes, treatment, extra, acute, dateS, duration, checkSuper]);
        /* Add a click handler to the rows - this could be used as a callback */
        jQuery("#measure tr:last").click( function() {
            jQuery(this).toggleClass('row_selected');
        });
        document.getElementById('id_barcode').value = "";
        document.getElementById('id_notes').value = "";
        document.getElementById('id_weight').value = "";
    }else
        alert("Weight must be a positive integer/decimal number.");
}

function checkTreat(url,currG,row,barcode,index){
    console.log('checkt');
    for (biomouse in physBio[barcode]){
        var genID = physBio[barcode][biomouse]['genID'];
        var mouseGroup = physBio[barcode][biomouse]['group'];
        if (groups.hasOwnProperty(mouseGroup)){
            if (groups[mouseGroup].hasOwnProperty(genID)){
                if (groups[mouseGroup][genID][12] == 'actual'){
                    groups[mouseGroup][genID][12] = 'stop';
                    jQuery.ajax({
                        url:url,
                        async:false,
                        type:'get',
                        success: function(response){
                            if (response['forces_explant'] == true ){
                                groups[mouseGroup][genID][6] = 'ready for explant';
                                groups[mouseGroup][genID][7] = 'Archive (end of experiment)';
                                groups[mouseGroup][genID][13] = "true";
                            }
                        }
                    });
                }else{
                    groups[mouseGroup][genID][14] = '';
                }
                groups[mouseGroup][genID][11] = '';
                groups[mouseGroup][genID][12] = 'actual';
                groups[mouseGroup][genID][14] = '';
                groups[mouseGroup][genID][15] = '';
            }else{
                //gruppo inserito, ma topo no
                groups[mouseGroup][genID] = ["",genID,"","","","", "","",barcode,"","","","actual","", '', "",""];
            }
        }else{
            //topo e gruppo da inserire
            groups[mouseGroup] = {};
            groups[mouseGroup][genID] = ["",genID,"","","","", "","",barcode,"","","","actual","", '', "",""];
        }
        console.log('aaaaaaaaaa', mouseGroup, currG);
        console.log(genID, isInCurrentTable(genID));
        if (mouseGroup == currG  && isInCurrentTable(genID) == true ){
            row = getRow(genID);
            index = oTable.fnGetPosition(row);
            if (oTable.fnGetData(index, 12) == 'actual'){
                if (oTable.fnGetData(index, 13) == "true"){
                    oTable.fnUpdate("ready for explant", index, 6, false, false);
                    oTable.fnUpdate("Archive (end of experiment)", index, 7, false, false);
                }
            }else{
                oTable.fnUpdate("", index, 14, false, false);
            }
            oTable.fnUpdate("", index, 11, false, false);
            oTable.fnUpdate("", index, 14, false, false);
            oTable.fnUpdate("", index, 15, false, false);
            if (jQuery(row).hasClass('row_selected'))
                jQuery(row).toggleClass('row_selected');   
        }
        storageIt('qual', JSON.stringify(groups));
    }
}

//stoppa il trattamento dei topi selezionati
function stopTreat() {
    var nodes = oTable.fnGetNodes();
    var rows = fnGetSelected();
    if (rows.length > 0){
        for(var i = 0; i < nodes.length; i++) {
            var row = nodes[i];
            if (jQuery.inArray(row, rows) > -1){
                var barcode = oTable.fnGetData(i,9);
                var url = base_url + "/api.acute_treatment/" + oTable.fnGetData(i,11);
                //alert(url);
                var currG = jQuery('#tableList').attr('currgroup');
                var genID = oTable.fnGetData(i,1);
                console.log('a');
                checkTreat(url, currG, row, barcode,i);
                //console.log(groups);
            }
        }
    }
}

function addTreat(currG, barcode, nameP, nameA, date, duration, time, index){
    for (biomouse in physBio[barcode]){
        var mouseGroup = physBio[barcode][biomouse]['group'];
        var genID = physBio[barcode][biomouse]['genID'];
        if (groups.hasOwnProperty(mouseGroup)){
            if (groups[mouseGroup].hasOwnProperty(genID)){
                //topo gia' inserito, da aggiornare
                groups[mouseGroup][genID][11] = getName(nameP, nameA);
                groups[mouseGroup][genID][12] = "new";
                groups[mouseGroup][genID][14] = date + ' ' + time;
                groups[mouseGroup][genID][15] = duration;
            }else{
                //gruppo inserito, ma topo no
                groups[mouseGroup][genID] = ["",genID,"","","","", "","",barcode,"","",getName(nameP, nameA),"new","",date + ' ' + time, duration,""];
            }
        }else{
            //topo e gruppo da inserire
            groups[mouseGroup] = {};
            groups[mouseGroup][genID] = ["",genID,"","","","", "","",barcode,"","",getName(nameP, nameA),"new","",date + ' ' + time, duration,""];
        }
        if (mouseGroup == currG  && isInCurrentTable(genID) == true ){
            //aggiornare tabella
            row = getRow(genID);
            index = oTable.fnGetPosition(row);
            if (jQuery(row).hasClass('row_selected'))
                jQuery(row).toggleClass('row_selected');
            oTable.fnUpdate(getName(nameP, nameA), index, 11, false, false);
            oTable.fnUpdate("new", index, 12, false, false);
            oTable.fnUpdate(date + ' ' + time, index, 14, false, false);
            oTable.fnUpdate(duration, index, 15, false, false);
        }
    }
    storageIt('qual', JSON.stringify(groups));
}

function makeAction(msg){
    var nodes = oTable.fnGetNodes();
    var rows = fnGetSelected();
    if (rows.length > 0){
        var currG = jQuery('#tableList').attr('currgroup');
        for(var i = 0; i < nodes.length; i++) {
            var row = nodes[i];
            if (jQuery.inArray(row, rows) > -1){
                var scope = $("#id_scope_detail option:selected" ).text();
                var explNotes = document.getElementById('explNotes').value;
                var barcode = oTable.fnGetData(i,9);
                var idGen = oTable.fnGetData(i,1);
                if (msg == 'explant without sacrifice'){
                    var mouseGroup = currG;
                    if (groups.hasOwnProperty(mouseGroup)){
                        if (groups[mouseGroup].hasOwnProperty(idGen)){
                            //topo gia' inserito, da aggiornare
                            updateStruct(msg, mouseGroup, idGen, scope, explNotes);
                        }else{
                            //gruppo inserito, ma topo no
                            groups[mouseGroup][idGen] = ["",idGen,"","","",msg, scope,"",barcode,"",explNotes,"","","","","",""];
                        }
                    }else{
                        //topo e gruppo da inserire
                        groups[mouseGroup] = {};
                        groups[mouseGroup][idGen] = ["",idGen,"","","",msg, scope,"",barcode,"",explNotes,"","","","","",""];
                    }
                    if (mouseGroup == currG  && isInCurrentTable(idGen) == true ){
                        //aggiornare tabella
                        oTable.fnUpdate(msg, i, 6, false, false);
                        //togliere la selezione della riga
                        if (jQuery(row).hasClass('row_selected'))
                            jQuery(row).toggleClass('row_selected');
                        oTable.fnUpdate("", i, 7, false, false);
                        oTable.fnUpdate("", i, 10, false, false);
                    }                
                }else{
                    console.log(barcode);
                    for (biomouse in physBio[barcode]){
                        var mouseGroup = physBio[barcode][biomouse]['group'];
                        var idGen = physBio[barcode][biomouse]['genID'];
                        if (msg == 'sacrifice without explant'){
                            explNotes = "";
                            scope = "";
                        }
                        if (groups.hasOwnProperty(mouseGroup)){
                            if (groups[mouseGroup].hasOwnProperty(idGen)){
                                //topo gia' inserito, da aggiornare
                                updateStruct(msg, mouseGroup, idGen, scope, explNotes);
                            }else{
                                //gruppo inserito, ma topo no
                                groups[mouseGroup][idGen] = ["",idGen,"","","",msg, scope,"",barcode,"",explNotes,"","","","","",""];
                            }
                        }else{
                            //topo e gruppo da inserire
                            groups[mouseGroup] = {};
                            groups[mouseGroup][idGen] = ["",idGen,"","","",msg, scope,"",barcode,"",explNotes,"","","","","",""];
                        }
                        console.log(currG, idGen);
                        console.log(isInCurrentTable(idGen));
                        if (mouseGroup == currG  && isInCurrentTable(idGen) == true ){
                            //aggiornare tabella
                            var row = getRow(idGen);
                            var index = oTable.fnGetPosition(row);
                            oTable.fnUpdate(msg, index, 6, false, false);
                            //togliere la selezione della riga
                            if (jQuery(row).hasClass('row_selected'))
                                jQuery(row).toggleClass('row_selected');
                            if (msg == "ready for explant"){
                                oTable.fnUpdate(scope, index, 7, false, false);
                                oTable.fnUpdate(explNotes, index, 10, false, false);
                            }else{
                                oTable.fnUpdate("", index, 7, false, false);
                                oTable.fnUpdate("", index, 10, false, false);
                            }
                            if (msg == 'sacrifice without explant'){
                                oTable.fnUpdate("", index, 11, false, false);
                                oTable.fnUpdate("", index, 12, false, false);
                                oTable.fnUpdate("", index, 13, false, false);
                                oTable.fnUpdate("", index, 14, false, false);
                                oTable.fnUpdate("", index, 15, false, false);
                            }
                        }
                    }
                }
                storageIt('qual', JSON.stringify(groups));
            }
        }
        document.getElementById('id_barcode').value = "";
        document.getElementById('id_weight').value = "";
        document.getElementById('id_weight').focus();
    }else
        alert("You have to select al least one row.");
}


function wToBlank(evt){
    var charCode = (evt.which) ? evt.which : event.keyCode
    console.log(charCode)
    if ( charCode == 13) //codice ASCII del carattere carriage return (invio)
        if ($('#id_weight').val() == ''){
            $('#id_weight').focus();
        }
        else{
            if ($('#id_barcode').val() == ''){
                $('#id_barcode').focus();
            }
            else{
                makeMeasure();
            }
        }        
}