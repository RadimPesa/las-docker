//restituisce la lunghezza della tabella datatable
function getIndex(oTable){
    //return oTable.fnGetData().length;
    var rows = oTable.fnGetNodes();
    var max = 0;
    for(var i=0; i<rows.length; i++){
        if (max < oTable.fnGetData( i, 0 ))
            max = oTable.fnGetData( i, 0 );
    }
    return max;
}

//per evidenziare i gruppi dopo uno swap
function lightGroup(mouseGroup){
    var table = document.getElementById('tableList');
    for (var i = 0; i < table.rows[0].cells.length; i++){
        //table.rows[0].cells[i].style.backgroundColor = 'white';
        table.rows[0].cells[i].className = "";
    }
    //document.getElementById(mouseGroup).style.backgroundColor = '#6C91DA';
    document.getElementById(mouseGroup).className = "selectedGroup";
}

//apre la finestra per assegnare i trattamenti
function openTreat(url) {
    var table = document.getElementById("measure");
    var rows = fnGetSelected(); //array con le righe selezionate
    if (rows.length > 0)
        window.open(url,"_blank",'width=900,height=600,left=100,top=100,screenX=100,screenY=100');
}

function getRow(genID){
    var nodes = oTable.fnGetNodes();
    for (var i = 0; i < nodes.length; i++ ){
        if (genID == oTable.fnGetData( i, 1 ) )
            return nodes[i];
    }
    return 'err';
}

//cancella l'i-esima riga della tabella
function deleteRow(type) {
    try {
        var nodes = oTable.fnGetNodes();
        var rows = fnGetSelected();
        if (rows.length > 0){
            for(var i = nodes.length; i >= 0 ; i--) {
                var row = nodes[i];
                if (jQuery.inArray(row, rows) > -1){
                    var currG = jQuery('#tableList').attr('currgroup');
                    var genID = oTable.fnGetData(i,1);
                    console.log(typeMeasure);
                    console.log(oTable.fnGetData(i,11), oTable.fnGetData(i,12))
                    if (typeMeasure == 'qual'){
                        var barcode = oTable.fnGetData(i,10);
                    }else if (typeMeasure == 'quant'){
                        var barcode = oTable.fnGetData(i,12);
                    }
                    console.log('splicing');
                    console.log(oTable.fnGetData(i))
                    console.log(barcode + genID.substr(17,3));
                    console.log(barcodeSiteList)
                    var j = barcodeSiteList.indexOf(barcode + genID.substr(17,3));
                    console.log(j, barcodeSiteList);
                    barcodeSiteList.splice(j, 1);
                    console.log(barcodeSiteList, currG, genID, groups[currG][genID]);
                    delete groups[currG][genID];
                    console.log(groups);
                    oTable.fnDeleteRow(i);
                }
            }
        }
        if (oTable.fnGetNodes( ).length == 0){
            var currG = jQuery("#tableList").attr("currgroup");
            console.log('curggg'+currG);
            removeElement('row1',currG);
            delete groups[currG];
            objTR = document.getElementById('row1');
            if (objTR.cells.length > 0){ //se ci sono altri gruppi misurati in questa sessione
                var g = objTR.cells[0].innerHTML;
                console.log('g'+g);
                swapTable(g, 'afterDelete');
            }
        }
        storageIt(type, JSON.stringify(groups));
        try{
            document.getElementById('id_barcode').focus();
        }
        catch(err){
            document.getElementById('id_x_measurement').focus();
        }
    }catch(e) {
        alert(e);
    }
}

//swap della tabella delle misure
function swapTable(nextGroup, onlySave){
    //creare tabella vuota
    //
    var totR = oTable.fnGetNodes().length;
    if (onlySave != "afterDelete"){
        for(var i = 0; i < totR; i++) {
            oTable.fnDeleteRow(0);
        }
    }
    if (onlySave != 'true'){
        for (var k in groups[nextGroup]){
            //console.log('kkkk'+k);
            jQuery('#measure').dataTable().fnAddData( groups[nextGroup][k] );
        }
        try{
            setTH();
        }
        catch(err){}
    }
    try{
       jQuery("#measure tbody tr").click( function() {
           jQuery(this).toggleClass('row_selected');
           calcSelectedAvg();
       });
    }
    catch(err){
        jQuery("#measure tbody tr").click( function() {
            jQuery(this).toggleClass('row_selected');
        });
    }
    jQuery('#tableList').attr('currGroup', nextGroup);
    lightGroup(nextGroup);
}

function addToList(mouseGroup){
    //add group to list (--> add column to table)
    var row = document.getElementById('row1');
    var td = document.createElement("td");
    td.setAttribute("align","center");
    td.setAttribute("id",mouseGroup);
    td.setAttribute("onclick","swap('" + mouseGroup + "')");
    td.innerHTML = mouseGroup;
    row.appendChild(td);
    lightGroup(mouseGroup);
}

function swap(genID){
    if (genID != jQuery('#tableList').attr('currgroup')){
        swapTable(genID, 'false');
        jQuery('#tableList').attr('currGroup', genID);
    }
}

function isNewGroup(mouseGroup){
    var table = document.getElementById('tableList');
    for (var i = 0; i < table.rows[0].cells.length; i++){
        console.log(mouseGroup + ' ' + table.rows[0].cells[i].innerHTML);
        if (mouseGroup == table.rows[0].cells[i].innerHTML){
            return false;
        }
    }
    return true;
}

function setGroups(data){
    groups = data;
}

function isNumber(n) {
    return !isNaN(parseFloat(n)) && isFinite(n);
}

function restoreData(listKey, oTable, typeM){
    var groups = JSON.parse(localStorage.getItem(listKey[0]));
    physBio = JSON.parse(localStorage.getItem(listKey[0] + 'PhysBio') );
    var user = localStorage.getItem(listKey[0] + 'user');
    var timestamp = localStorage.getItem(listKey[0] + 'timestamp');
    setGroups(groups);
    for (g in groups){
        jQuery('#tableList').attr('currgroup', g);
        console.log(groups[g]);
        addToList(g);
        //cancello eventuali altre righe
        var totR = oTable.fnGetNodes().length;
        for(var i = 0; i < totR; i++) {  oTable.fnDeleteRow(0); }
        if (typeM == 'quant'){
            for (mouse in groups[g]){
                console.log(groups[g][mouse]);
                var volume = groups[g][mouse][5];
                if (volume != ""){
                    if (isNumber(volume)){
                        if (volume > document.getElementById('threshold').value)
                            jQuery("#measure tr:last").toggleClass('redR');
                            jQuery('#measure').dataTable().fnAddData( [ groups[g][mouse] ] );
                            jQuery("#measure tr:last").click( function() {
                                jQuery(this).toggleClass('row_selected');
                            });
                    }
                }
            }
        }else if(typeM == 'qual'){
            for (mouse in groups[g]){
                var value = groups[g][mouse][2];
                if (value != ""){
                    jQuery('#measure').dataTable().fnAddData( [ groups[g][mouse] ] );
                    jQuery("#measure tr:last").click( function() {
                        jQuery(this).toggleClass('row_selected');
                    });
                }
            }
        }
    }
}
