var barcodeSiteList = []; var groups = {}; var typeMeasure = "quant"; var barcodeSiteList = [];
var nDecimal = 3; //variabile usata per chiamare la funzione trunc, inviandolo come valore del paramentro decimal
physBio = {};

jQuery(document).ready(function () {
    listKey = ['quant','quantuser', 'quanttimestamp', 'quantPhysBio'];
    jQuery("label[for='id_notes']").append("<br>");
    jQuery("label[for='id_x_measurement']").append("<br>");
    jQuery("label[for='id_y_measurement']").append("<br>");
    jQuery("label[for='id_z_measurement']").append("<br>");
    jQuery("label[for='id_barcode_of_mouse']").append("<br>");
    jQuery("label[for='threshold']").append("<br>");
    $('#id_weight').focus();
    oTable = jQuery('#measure').dataTable( {
        "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        "iDisplayLength": -1,
        "aoColumnDefs": [
            { "bVisible": false, "aTargets": [ 2,3,4,11,13,15,16 ] },
        ],
        "aaSorting": [[0, 'asc']]
    });
    checkStorageMeasure(listKey, oTable, 'quant');
    jQuery("#siteForm").css("margin-top","-9px");

} );


function isNewSite(barcode, site){
    if (barcodeSiteList.indexOf(barcode + site) > -1)
        return false;
    return true;
}

function trunc(n, decimal){
    decimal++;
    n = n.toString();
    if(n.indexOf(".")>0)
            n = n.substring(0,n.indexOf(".")+decimal);
    n = parseFloat(n);
    return n;
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
        groups[currG][genID][9] = msg;
        if (msg == "ready for explant"){
            groups[currG][genID][10] = scope;
            groups[currG][genID][13] = explNotes;
        }else{
            groups[currG][genID][10] = "";
            groups[currG][genID][13] = "";
            if (msg = "sacrifice without explant"){
                groups[currG][genID][14] = "";
                groups[currG][genID][15] = "";
                groups[currG][genID][16] = "";
                groups[currG][genID][17] = "";
                groups[currG][genID][18] = "";
            }
        }
    }catch(e) {
        alert(e);
    }
}

function calcAvg(){
    var tot = 0; var counter_for_avg = 0; var avg = 0;
    var nodes = oTable.fnGetNodes();
    for(var i = 0; i < nodes.length; i++) {
        var row = nodes[i];
        tot = tot + parseFloat(oTable.fnGetData(i, 5));
        counter_for_avg++;
    }
    var avg =  trunc( (tot/counter_for_avg), nDecimal);
    document.getElementById('avg').innerHTML = 'Average volume of the cage: ' + avg;
    if (avg > document.getElementById('threshold').value)
        document.getElementById('avg').style.color='red';
    else
        document.getElementById('avg').style.color='black';
}

function makeMeasure(){
    var barcode = document.getElementById("id_barcode_of_mouse").value.toUpperCase();
    var site = jQuery("#id_site :selected").val();
    var url = base_url + "/api.mouseformeasure/" + barcode + '/' + site;
    var xCheck = document.getElementById("id_x_measurement").value;
    var yCheck = document.getElementById("id_y_measurement").value;
    var zCheck = document.getElementById("id_z_measurement").value;
    var wCheck = "0";
    if (document.getElementById("id_weight").value!=""){
        wCheck = document.getElementById("id_weight").value;
    }
    else{
        alert("Please insert the weight");
        return;
    }
    var wCheckFlag = true;
    if (document.getElementById("id_weight").value!=""){
        wCheck = document.getElementById("id_weight").value;
        wCheck = wCheck.replace(',','.');
        if (parseFloat(wCheck) < 0)
            wCheckFlag = false;
        }

    xCheck = xCheck.replace(',','.');
    yCheck = yCheck.replace(',','.');
    zCheck = zCheck.replace(',','.');


    if (document.getElementById("id_barcode_of_mouse").value != ""){
        if ((!isNaN(xCheck)) && (!isNaN(yCheck)) && (!isNaN(zCheck)) && (!isNaN(wCheck)) ){
           if ( parseFloat(xCheck) > 0  && parseFloat(yCheck) > 0 && parseFloat(zCheck) > 0 && parseFloat(wCheck) >= 0){
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
                            var status = mouse['generalInfo']['status'];
                            if (status == 'implanted' || status == 'ready for explant' || status == 'explantLite' || status == 'waste' || status == 'transferred'){
                                var mouseGroup = mouse['generalInfo']['group'];
                                if (document.getElementById('tableList').rows[0].cells.length == 0){
                                    groups[mouseGroup] = {};
                                    addToList(mouseGroup);
                                }else{
                                    var currGroup = jQuery('#tableList').attr('currGroup');
                                    if (currGroup != mouseGroup){
                                        //add group to list
                                        var newG = isNewGroup(mouseGroup);
                                        if (newG){
                                            if ( groups.hasOwnProperty(mouseGroup) == false ){
                                                groups[mouseGroup] = {};
                                                storageIt('quant', JSON.stringify(groups));
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
                                    addRow('measure', mouseGroup, status, mouse, xCheck, yCheck, zCheck, wCheck);
                                    barcodeSiteList.push(barcode + site);
                                }else
                                    alert("You've already measured this site of this mouse in the current session.");
                            }else{
                                alert('This mouse is ' + status + '. Only implanted mice and mice ready for explant (with or without sacrifice) can be measured');
                            }
                        }
                    }
                });
            }else
                alert("X, Y, Z and weight values must be positive numbers." );
        }else
            alert("X, Y, Z and weight values must be integer/decimal numbers.");
    }else{
        alert("You've inserted a blank barcode");
    }
}

//aggiunge una riga alla tabella prendendo i dati dall'input utente. Effettua vari controlli sull'input.
function addRow(tableID, mouseGroup,status, mouse, xCheck, yCheck, zCheck, wCheck) {
    var barcode = document.getElementById("id_barcode_of_mouse").value.toUpperCase();
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
    var y = parseFloat(yCheck);var x = parseFloat(xCheck); var weight = wCheck;var z = parseFloat(zCheck);

    var notes = document.getElementById("id_notes").value; var threshold = document.getElementById('threshold').value;
    var genID = "";var group = "";var volume = "";var explant = "";var scope = "";var scopeNotes = "";var treatment = "";var date = "";var time = "";var extra = "";
    var acute = "";var dateS = "";var duration = "";var counter_for_avg = 0;var continueFlag = Boolean(false);
    var counterH = getIndex(oTable) + 1;   var value = 0;  var oldW = ""; var oldWDate = "";
    value = (x/2)*(y/2)*(z/2)*4/3*Math.PI;
    volume = trunc(value, nDecimal);
    genID = mouse['generalInfo']['genID'];
    if (status == 'ready for explant'){
        explant = "ready for explant";
    }else{
        if (status == 'explantLite')
            explant = "explant without sacrifice";
        else
            explant = "not programmed for explant";
    }
    console.log(explant);
    console.log('STATUS: ' + status);
    scope = mouse['expl']['scope'];
    scopeNotes = mouse['expl']['scopeNotes'];
    dateS = mouse['treat']['start'];
    if (mouse['treat']['duration'] != "")
        duration = mouse['treat']['duration'] + ' [' + mouse['treat']['typeTime'] + ']';

    if (mouse['treat']['nameA'] != "")
        treatment = getName(mouse['treat']['nameP'], mouse['treat']['nameA']);
    extra = "actual";
    console.log(treatment);
    if (mouse['treat']['forces_explant'])
        acute = "true";
    else
        acute = "false";
    oldW = mouse['weight']['w'];
    oldWDate = mouse['weight']['dateW'];

    if (groups.hasOwnProperty(mouseGroup)){
        if (genID in groups[mouseGroup]){
            if (groups[mouseGroup][genID][9] != ""){ //info relative ad espianti
                explant = groups[mouseGroup][genID][9];
                scope = groups[mouseGroup][genID][11];
                scopeNotes = groups[mouseGroup][genID][13];
            }
            if ( (groups[mouseGroup][genID][14] != "") || ( groups[mouseGroup][genID][15] == "stop" ) ){
                //explant = groups[mouseGroup][genID][7];
                //scope = groups[mouseGroup][genID][8];
                //scopeNotes = groups[mouseGroup][genID][12];/*info expl per eventuali tratt acuti*/
                treatment = groups[mouseGroup][genID][14];
                extra = groups[mouseGroup][genID][15];
                dateS = groups[mouseGroup][genID][17];
                duration = groups[mouseGroup][genID][18];
            }
        }else{
            groups[mouseGroup][genID] = [];
        }
    }else{
        groups[mouseGroup] = {};
        groups[mouseGroup][genID] = [];
    }

    console.log([counterH,genID,x,y,volume,oldW,oldWDate,explant,scope,notes,barcode,weight,scopeNotes,treatment,extra,acute,dateS,duration]);
    groups[mouseGroup][genID] = [counterH,genID,x,y,z, volume,weight,oldW,oldWDate,explant,scope,notes,barcode,scopeNotes,treatment,extra,acute,dateS,duration];
    //console.log(groups);
    storageIt('quant', JSON.stringify(groups));
    storageIt('quantPhysBio', JSON.stringify(physBio));
    jQuery('#measure').dataTable().fnAddData( [counterH,genID,x,y,z, volume,weight,oldW,oldWDate,explant,scope,notes,barcode,scopeNotes,treatment,extra,acute,dateS,duration] );
    /* Add a click handler to the rows - this could be used as a callback */
    jQuery("#measure tr:last").click( function() {
        jQuery(this).toggleClass('row_selected');
        calcSelectedAvg();
    });
    if (volume > document.getElementById('threshold').value)
        jQuery("#measure tr:last").toggleClass('redR');
    calcAvg();
    document.getElementById('id_barcode_of_mouse').value = "";
    document.getElementById('id_x_measurement').focus();
    document.getElementById('id_x_measurement').value = "";
    document.getElementById('id_y_measurement').value = "";
    document.getElementById('id_notes').value = "";
    document.getElementById('id_weight').value = "";
    document.getElementById('id_x_measurement').value = "";
    //}else
    //    alert("Weight must be a positive integer/decimal number.");
}

function makeAction(msg){
    var nodes = oTable.fnGetNodes();
    var rows = fnGetSelected();
    if (rows.length > 0){
        var currG = jQuery('#tableList').attr('currgroup');
        for(var i = 0; i < nodes.length; i++) {
            var row = nodes[i];
            if (jQuery.inArray(row, rows) > -1){
                var barcode = oTable.fnGetData(i,12);
                var idGen = oTable.fnGetData(i,1);
                var scope = $("#id_scope_detail option:selected" ).text();
                var explNotes = document.getElementById('explNotes').value;
                if (msg == 'explant without sacrifice'){
                    var mouseGroup = currG;
                    if (groups.hasOwnProperty(mouseGroup)){
                        if (groups[mouseGroup].hasOwnProperty(idGen)){
                            //topo gia' inserito, da aggiornare
                            updateStruct(msg, mouseGroup, idGen, scope, explNotes);
                        }else{
                            //gruppo inserito, ma topo no
                            groups[mouseGroup][idGen] = ["",idGen,"", "", "","","","","",msg, scope,"",barcode,explNotes,"","","","","",""];
                        }
                    }else{
                        //topo e gruppo da inserire
                        groups[mouseGroup] = {};
                        groups[mouseGroup][idGen] = ["",idGen,"","","","","","","",msg, scope,"",barcode,explNotes,"","","","","",""];
                    }
                    if (mouseGroup == currG  && isInCurrentTable(idGen) == true ){
                        //aggiornare tabella
                        oTable.fnUpdate(msg, i, 9, false, false);
                        //togliere la selezione della riga
                        if (jQuery(row).hasClass('row_selected'))
                            jQuery(row).toggleClass('row_selected');
                        oTable.fnUpdate("", i, 10, false, false);
                        oTable.fnUpdate("", i, 13, false, false);
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
                                groups[mouseGroup][idGen] = ["",idGen,"","","","","","","",msg, scope,"",barcode,explNotes,"","","","","",""];
                            }
                        }else{
                            //topo e gruppo da inserire
                            groups[mouseGroup] = {};
                            groups[mouseGroup][idGen] = ["",idGen,"","","","","","","",msg, scope,"",barcode,explNotes,"","","","","",""];
                        }
                        if (mouseGroup == currG  && isInCurrentTable(idGen) == true ){
                            //aggiornare tabella
                            var row = getRow(idGen);
                            var index = oTable.fnGetPosition(row);
                            oTable.fnUpdate(msg, index, 9, false, false);
                            //togliere la selezione della riga
                            if (jQuery(row).hasClass('row_selected'))
                                jQuery(row).toggleClass('row_selected');
                            if (msg == "ready for explant"){
                                oTable.fnUpdate(scope, index, 10, false, false);
                                oTable.fnUpdate(explNotes, index, 13, false, false);
                            }else{
                                oTable.fnUpdate("", index, 10, false, false);
                                oTable.fnUpdate("", index, 13, false, false);
                            }
                            if (msg == 'sacrifice without explant'){
                                oTable.fnUpdate("", index, 14, false, false);
                                oTable.fnUpdate("", index, 15, false, false);
                                oTable.fnUpdate("", index, 16, false, false);
                                oTable.fnUpdate("", index, 17, false, false);
                                oTable.fnUpdate("", index, 18, false, false);
                            }
                        }
                    }
                }
                storageIt('quant', JSON.stringify(groups));
            }
        }
        document.getElementById('id_barcode_of_mouse').value = "";
        document.getElementById('id_weight').value = "";
        //document.getElementById('id_x_measurement').focus();
    }else
        alert("You have to select al least one row.");
}

//stoppa il trattamento dei topi selezionati
function stopTreat() {
    var nodes = oTable.fnGetNodes();
    var rows = fnGetSelected();
    if (rows.length > 0){
        for(var i = 0; i < nodes.length; i++) {
            var row = nodes[i];
            if (jQuery.inArray(row, rows) > -1){
                var barcode = oTable.fnGetData(i,12);
                var url = base_url + "/api.acute_treatment/" + oTable.fnGetData(i,14);
                var currG = jQuery('#tableList').attr('currgroup');
                var genID = oTable.fnGetData(i,1);
                checkTreat(url,currG,row,barcode, i);
            }
        }
    }
}

function checkTreat(url,currG,row,barcode, index){
    console.log('checkTreat');
    for (biomouse in physBio[barcode]){
        var genID = physBio[barcode][biomouse]['genID'];
        var mouseGroup = physBio[barcode][biomouse]['group'];
        if (groups.hasOwnProperty(mouseGroup)){
            console.log('1');
            if (groups[mouseGroup].hasOwnProperty(genID)){
                console.log('2');
                if (groups[mouseGroup][genID][15] == 'actual'){
                    console.log('3');
                    groups[mouseGroup][genID][16] = 'stop';
                    jQuery.ajax({
                        url:url,
                        async:false,
                        type:'get',
                        success: function(response){
                            if (response['forces_explant'] == true ){
                                groups[mouseGroup][genID][9] = 'ready for explant';
                                groups[mouseGroup][genID][10] = 'Archive (end of experiment)';
                                groups[mouseGroup][genID][16] = "true";
                            }
                        }
                    });
                }else{
                    groups[mouseGroup][genID][17] = '';
                }
                console.log('4')
                groups[mouseGroup][genID][14] = '';
                console.log(mouseGroup);
                console.log(genID);
                groups[mouseGroup][genID][15] = 'actual';
                groups[mouseGroup][genID][17] = '';
                groups[mouseGroup][genID][18] = ''; //HERE
                console.log(groups);
            }else{
                //gruppo inserito, ma topo no
                groups[mouseGroup][genID] = ["",genID,"","","","", "","","","", "","",barcode,"","","actual","", '', "",""];
            }
        }else{
            //topo e gruppo da inserire
            groups[mouseGroup] = {};
            groups[mouseGroup][genID] = ["",genID,"", "","","","","","","","","",barcode,"","","actual","", '', "",""];
        }
        if (mouseGroup == currG  && isInCurrentTable(genID) == true ){
            row = getRow(genID);
            index = oTable.fnGetPosition(row);
            if (groups[mouseGroup][genID][15] == 'actual'){
                if (oTable.fnGetData(index, 16) == "true"){
                    oTable.fnUpdate("ready for explant", index, 9, false, false);
                    oTable.fnUpdate("Archive (end of experiment)", index, 10, false, false);
                }
            }else{
                oTable.fnUpdate("", index, 17, false, false);
            }
            oTable.fnUpdate("", index, 14, false, false);
            oTable.fnUpdate("", index, 17, false, false);
            oTable.fnUpdate("", index, 18, false, false);
            if (jQuery(row).hasClass('row_selected'))
                jQuery(row).toggleClass('row_selected');

        }
        storageIt('quant', JSON.stringify(groups));
    }
}

//aggiorna e mostra la media per i topi checkati
function calcSelectedAvg() {
    try {
        var tot = 0; var counter_for_avg = 0; var avg = 0;
        var nodes = oTable.fnGetNodes();
        var rows = fnGetSelected();
        if (rows.length > 0){
            for(var i = 0; i < nodes.length; i++) {
                var row = nodes[i];
                if (jQuery.inArray(row, rows) > -1){
                    tot = tot + parseFloat(oTable.fnGetData(i, 5));
                    counter_for_avg++;
                }
            }
            console.log(tot + ' ' + counter_for_avg);
            var avg =  trunc( (tot/counter_for_avg), nDecimal);
            console.log(avg);
            document.getElementById('avgChecked').innerHTML ="Average volume of the selected mice: " + avg;
            if (avg > document.getElementById('threshold').value)
                document.getElementById('avgChecked').style.color='red';
            else
                document.getElementById('avgChecked').style.color='black';
        }else{
            document.getElementById('avgChecked').innerHTML ="Average volume of the selected mice: -"
            document.getElementById('avgChecked').style.color='black';
        }
        document.getElementById('id_x_measurement').focus();
    }catch(e) {
        alert(e);
    }
}

function refreshRows(){
    var avg = 0;
    var th = document.getElementById('threshold').value;
    for(var i = 0; i < oTable.fnGetNodes().length; i++) {
        var row = oTable.fnGetNodes()[i];
        if (oTable.fnGetData(i, 5) > th)
            addClass(row,'redR');
        else
            removeClass(row,'redR');
    }
}

function setTH(){
    calcAvg();
    calcSelectedAvg();
    refreshRows();
}

function addTreat(currG,barcode,nameP, nameA, date, duration,time,index ){
    console.log('start quant addTreat', barcode);
    for (biomouse in physBio[barcode]){
        var mouseGroup = physBio[barcode][biomouse]['group'];
        var genID = physBio[barcode][biomouse]['genID'];
        if (groups.hasOwnProperty(mouseGroup)){
            if (groups[mouseGroup].hasOwnProperty(genID)){
                console.log(mouseGroup, genID);
                //topo gia' inserito, da aggiornare
                groups[mouseGroup][genID][14] = getName(nameP, nameA);
                groups[mouseGroup][genID][15] = "new";
                groups[mouseGroup][genID][17] = date + ' ' + time;
                groups[mouseGroup][genID][18] = duration;
            }else{
                //gruppo inserito, ma topo no
                groups[mouseGroup][genID] = ["",genID,"","","","","","","","","","",barcode,"",getName(nameP, nameA),"new","",date + ' ' + time, duration,""];
            }
        }else{
            //topo e gruppo da inserire
            groups[mouseGroup] = {};
            groups[mouseGroup][genID] = ["",genID,"","","","","","","","","",barcode,"",getName(nameP, nameA),"new","",date + ' ' + time, duration,""];
        }
        if (mouseGroup == currG  && isInCurrentTable(genID) == true ){
            //aggiornare tabella
            row = getRow(genID);
            index = oTable.fnGetPosition(row);
            if (jQuery(row).hasClass('row_selected'))
                jQuery(row).toggleClass('row_selected');
            oTable.fnUpdate(getName(nameP, nameA), index, 14, false, false);
            oTable.fnUpdate("new", index, 15, false, false);
            oTable.fnUpdate(date + ' ' + time, index, 17, false, false);
            oTable.fnUpdate(duration, index, 18, false, false);
        }
    }
    storageIt('quant', JSON.stringify(groups));
}

function saveQuant (){
    jQuery("#save").attr("disabled",true);
    var currGroup = jQuery('#tableList').attr('currgroup');
    if (Object.size(groups) > 0){
	    jQuery.ajax({
		    url: base_url + '/measurement/quant',
		    type: 'POST',
		    data: {'obj':JSON.stringify(groups), 'lastG':currGroup},
		    dataType: 'text',
	    });
    }else{
        alert("You cannot save an empty measurement set.");
        jQuery("#save").attr("disabled",false);
    }
}

function wTox(evt){
    var charCode = (evt.which) ? evt.which : event.keyCode
    if ( charCode == 13 ) //codice ASCII del carattere carriage return (invio)
        $('#id_x_measurement').focus();
}


function xToY(evt){
    var charCode = (evt.which) ? evt.which : event.keyCode
    if ( charCode == 13 ) //codice ASCII del carattere carriage return (invio)
        document.getElementById('id_y_measurement').focus();
}

function yToB(evt){
    var charCode = (evt.which) ? evt.which : event.keyCode
    if ( charCode == 13 ) //codice ASCII del carattere carriage return (invio)
        document.getElementById('id_barcode_of_mouse').focus();
}

function checkKey(evt){
    var charCode = (evt.which) ? evt.which : event.keyCode
    if ( charCode == 13 ) //codice ASCII del carattere carriage return (invio)
        makeMeasure();
}


function wToBlank(evt){
    var charCode = (evt.which) ? evt.which : event.keyCode
    console.log(charCode)
    if ( charCode == 13) //codice ASCII del carattere carriage return (invio)
        if ($('#id_weight').val() == ''){
            $('#id_weight').focus();
        }
        else{
            if ($('#id_x_measurement').val() == ''){
                $('#id_x_measurement').focus();
            }
            else{
                if ($('#id_y_measurement').val() == ''){
                    $('#id_y_measurement').focus();
                }
                else{
                    if ($('#id_z_measurement').val() == ''){
                        $('#id_z_measurement').focus();
                    }
                    else{
                        if ($('#id_barcode_of_mouse').val() == ''){
                            $('#id_barcode_of_mouse').focus();
                        }
                        else{
                            makeMeasure();
                        }
                    }
                }
            }
        }
}
