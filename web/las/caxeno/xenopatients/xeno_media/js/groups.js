var tableSx = "#miceSx"; var tableDx = "#miceDx";
var groupSx = ""; var groupDx = ""; //gruppi attualmente selezionati rispettivamente a sx e a dx
var groupDict = {};
jQuery(document).ready(function(){
    oTableSx = generate_table_sx();
    oTableDx = generate_table_dx();
    jQuery("#divDx fieldset").attr("disabled", "disabled");
});

function generate_table_sx(){
    oTableSx = jQuery(tableSx).dataTable( {
	    "bProcessing": true,
	     "aoColumns": [
                { "sTitle": "Genealogy ID" },
                { "sTitle": "Barcode" },
                { "sTitle": "Status" },
                { "sTitle": "Treatment" },
                { "sTitle": "Start Date" },
                { "sTitle": "Duration" },
            ],
        "bAutoWidth": false ,
        "aaSorting": [[0, 'asc']],
        "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        "iDisplayLength": -1,
        "aoColumnDefs": [
          //{ "bVisible": false, "aTargets": [ 1 ] },
        ],
    });
    oSettingsSx = oTableSx.fnSettings();
    return oTableSx;
}

function generate_table_dx(){
    oTableDx = jQuery(tableDx).dataTable( {
	    "bProcessing": true,
	     "aoColumns": [
                { "sTitle": "Genealogy ID" },
                { "sTitle": "Barcode" },
                { "sTitle": "Status" },
                { "sTitle": "Treatment" },
                { "sTitle": "Start Date" },
                { "sTitle": "Duration" },
            ],
        "bAutoWidth": false ,
        "aaSorting": [[0, 'asc']],
        "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        "iDisplayLength": -1,
        "aoColumnDefs": [
          //{ "bVisible": false, "aTargets": [ 1 ] },
        ],
    });
    oSettingsDx = oTableDx.fnSettings();
    return oTableDx;
}

function writeBox(infoT, nameG, date, mice, protocol){
    if (protocol == '---------')
        protocol = "No protocol assigned to this group";
    document.getElementById(infoT).innerHTML = "Group's Properties:\n- name: "+nameG+";\n- creation date: "+date+";\n- number of assigned mice: " + mice + ";\n- expected protocol: " + protocol + ".";
}

function deleteRows(tableID){
    var tot = jQuery(tableID).dataTable().fnGetNodes().length;
    for(var i = 0; i < tot; i++) {
        jQuery(tableID).dataTable().fnDeleteRow(0);
    }
}

function loadFromStorage(infoT, nameG, tableID, oSettings){
    var i = 0;    
    if (groupDict.hasOwnProperty(nameG)){
        writeBox(infoT, nameG, groupDict[nameG]['properties']['date'], Object.size(groupDict[nameG]['mice']), groupDict[nameG]['properties']['protocol'])
        for (genID in groupDict[nameG]['mice']){
            jQuery(tableID).dataTable().fnAddData([ genID, groupDict[nameG]['mice'][genID]['barcode'], groupDict[nameG]['mice'][genID]['status'], groupDict[nameG]['mice'][genID]['treat'], groupDict[nameG]['mice'][genID]['dateS'], groupDict[nameG]['mice'][genID]['duration'] ]);
            jQuery(oSettings.aoData[i].nTr).click( function() {
                jQuery(this).toggleClass('row_selected');
            });
            i = i + 1;
        }
    }else{
        nameGroup = retrieveKey(nameG);
        writeBox(infoT, nameGroup, groupDict[nameGroup]['properties']['date'], Object.size(groupDict[nameGroup]['mice']), groupDict[nameGroup]['properties']['protocol'])
        for (genID in groupDict[nameGroup]['mice']){
            jQuery(tableID).dataTable().fnAddData([ genID, groupDict[nameGroup]['mice'][genID]['barcode'], groupDict[nameGroup]['mice'][genID]['status'], groupDict[nameGroup]['mice'][genID]['treat'], groupDict[nameGroup]['mice'][genID]['dateS'], groupDict[nameGroup]['mice'][genID]['duration'] ]);
            jQuery(oSettings.aoData[i].nTr).click( function() {
                jQuery(this).toggleClass('row_selected');
            });
            i = i + 1;
        }
    }
}

function startLag(){
    /*jQuery("#sf button,#rna button,#vital button,#ffpe button,#oct button,#cb button").attr("disabled", true );
    jQuery("#sf button[sel='s'],#rna button[sel='s'],#vital button[sel='s']").attr("disabled", true );
    jQuery("#confirm_all").attr("disabled", true );
    jQuery("#nextMouse").attr("disabled", true );*/
    timer = setTimeout(function(){jQuery("body").addClass("loading");}, 2000);    
}

function endLag(){
    clearTimeout(timer);
    /*jQuery("#sf button,#rna button,#vital button,#ffpe button,#oct button,#cb button").attr("disabled", false );
    jQuery("#sf button[sel='s'],#rna button[sel='s'],#vital button[sel='s'],#ffpe button[sel='s'],#oct button[sel='s'],#cb button[sel='s']").attr("disabled", true );
    jQuery("#rna button:contains('X'),#sf button:contains('X')").attr("disabled", true );
    jQuery("#confirm_all").attr("disabled", false );
    jQuery("#nextMouse").attr("disabled", false );*/
    jQuery("body").removeClass("loading");
}

function loadMice(g, sourceT){
    if (sourceT == 'sx'){
        var infoT = 'infoTL';
        groupSx = g;
        var tableID = "#miceSx";
        var oTable = oTableSx;
        var oSettings = oSettingsSx;
    }else if (sourceT == 'dx'){
        var infoT = 'infoTR';
        groupDx = g;
        var tableID = "#miceDx";
        var oTable = oTableDx;
        var oSettings = oSettingsDx;
    }
    //API per avere le info generali sul gruppo
    url = base_url+'/api.infoGroup/' + g;
    jQuery.getJSON(url,function(info){
        var date = info['date'];
        var protocol = info['protocol'];
        var nameG = info['name'];
        var mice = info['mice'];
        //cancellare righe gia' presenti nella tabella selezionata
        deleteRows(tableID);
        //check se esiste gia' il gruppo nel dict (cioe' se era gia' stato usato in questa sessione)
        if (groupDict.hasOwnProperty(nameG)){
            //gruppo gia' usato
            loadFromStorage(infoT, nameG, tableID, oSettings);
        }else{
            //gruppo nuovo
            writeBox(infoT, nameG, date, mice, protocol);
            groupDict[nameG] = {};
            groupDict[nameG]['mice'] = {};
            groupDict[nameG]['properties'] = {};
            groupDict[nameG]['properties']['date'] = date;
            groupDict[nameG]['properties']['protocol'] = protocol;
            groupDict[nameG]['properties']['name'] = nameG;
            groupDict[nameG]['properties']['type'] = 'loaded';
            //API per avere tutti i topi di quel gruppo (dati: genID, barcode, status, info sul treat.) 
            var url = base_url + '/api.miceOfGroup/' + g;
            startLag();
            console.log(url);
            jQuery.ajax({
                url: url,
	            type: 'get',
	            success: function(transport) {
                    miceList = JSON.parse(transport['miceDict']);
                    console.log(miceList);
                    //popolare tabella topi
                    for (key in miceList){
                        //console.log(miceList[key]);
                        jQuery(tableID).dataTable().fnAddData( [miceList[key]['id_mouse'], miceList[key]['barcode'], miceList[key]['status'], miceList[key]['treatment'], miceList[key]['dateS'], miceList[key]['duration'] ] );
                        groupDict[nameG]['mice'][miceList[key]['id_mouse']] = {};
                        groupDict[nameG]['mice'][miceList[key]['id_mouse']]['new'] = false;
                        groupDict[nameG]['mice'][miceList[key]['id_mouse']]['barcode'] = miceList[key]['barcode']
                        groupDict[nameG]['mice'][miceList[key]['id_mouse']]['status'] = miceList[key]['status']
                        groupDict[nameG]['mice'][miceList[key]['id_mouse']]['treat'] = miceList[key]['treatment']
                        groupDict[nameG]['mice'][miceList[key]['id_mouse']]['dateS'] = miceList[key]['dateS']
                        groupDict[nameG]['mice'][miceList[key]['id_mouse']]['duration'] = miceList[key]['duration']
                        //console.log(key);   
                        //aggiungere azione di selezione righe
                        jQuery(oSettings.aoData[key].nTr).click( function() {
                            jQuery(this).toggleClass('row_selected');
                        });
                    }
                    jQuery("#divDx fieldset").removeAttr("disabled"); //abilita la parte destra della schermata
                    endLag();
	            }
            });
        }
    });
}

function newGroup(sourceT){
    jQuery( "#dialog" ).dialog({
        resizable: false,
        height:300,
        width:340,
        modal: true,
        draggable :false,
        buttons: {
            "Cancel": function() {
                jQuery(this).dialog( "close" );
            },
            "Ok": function() {
                var nameG = jQuery("#id_name").val();
                var protocol = jQuery("#id_protocol option:selected").text()
                if (nameG != ""){
                    if (sourceT == 'sx'){
                        var infoT = 'infoTL';
                        var tableID = "#miceSx";
                    }else if (sourceT == 'dx'){
                        var infoT = 'infoTR';
                        var tableID = "#miceDx";
                    }
                    //cancellare righe gia' presenti nella tabella selezionata
                    deleteRows(tableID);
                    var popup = this;
		            jQuery.ajax({
			            url: base_url + '/api.countGroupName/'+nameG,
			            type: 'GET',
			            dataType: 'text',
			            success: function(count){
                            nameG = nameG + '.' + count;
                            if (sourceT == 'sx'){
                                groupSx = nameG;
                            }else if (sourceT == 'dx'){
                                groupDx = nameG;
                            }
                            writeBox(infoT, nameG, 'today', 0, protocol);
                            groupDict[nameG] = {};
                            groupDict[nameG]['properties'] = {};
                            groupDict[nameG]['properties']['date'] = "today";
                            groupDict[nameG]['properties']['protocol'] = protocol;
                            groupDict[nameG]['properties']['name'] = nameG;
                            groupDict[nameG]['mice'] = {};
                            groupDict[nameG]['properties']['type'] = 'new';
                            jQuery("#divDx fieldset").removeAttr("disabled"); //abilita la parte destra della schermata
                            jQuery(popup).dialog( "close" );
		                }
		            }); 
                }
            }
        }
    });
}

function editGroup(sourceT){
    jQuery("#id_name").val("");
    jQuery("#id_protocol").val(0);
    if (sourceT == 'sx'){
        if (groupSx == ""){
            alert("First, select the group. Then, you can edit it.");
            return;
        }
        var g = groupSx;
    }else if (sourceT == 'dx'){
        if (groupDx == ""){
            alert("First, select the group. Then, you can edit it.");
            return;
        }
        var g = groupDx;
    }
    jQuery("#id_name").val(g);
    jQuery( "#dialog" ).dialog({
        resizable: false,
        height:300,
        width:340,
        modal: true,
        draggable :false,
        buttons: {
            "Cancel": function() {
                jQuery(this).dialog( "close" );
            },
            "Ok": function() {
                var nameG = jQuery("#id_name").val();
                var protocol = jQuery("#id_protocol option:selected").text()
                if (nameG != ""){
                    if (sourceT == 'sx'){
                        var infoT = 'infoTL';
                        var g = groupSx;
                    }else if (sourceT == 'dx'){
                        var infoT = 'infoTR';
                        var g = groupDx;
                    }
                    var popup = this;
		            jQuery.ajax({
			            url: base_url + '/api.countGroupName/'+nameG,
			            type: 'GET',
			            dataType: 'text',
			            success: function(count){
                            nameG = nameG + '.' + count;
                            if (sourceT == 'sx'){
                                groupSx = nameG;
                            }else if (sourceT == 'dx'){
                                groupDx = nameG;
                            }
                            if (groupDict.hasOwnProperty(g)){
                                writeBox(infoT, nameG, groupDict[g]['properties']['date'], Object.size(groupDict[g]['mice']) , protocol);
                                groupDict[g]['properties']['name'] = nameG;
                                groupDict[g]['properties']['protocol'] = protocol;
                                if (groupDict[g]['properties']['type'] != 'new')
                                    groupDict[g]['properties']['type'] = 'mod';
                            }else{
                                nameGroup = retriveKey(nameG)

                                writeBox(infoT, nameG, groupDict[nameGroup]['properties']['date'], Object.size(groupDict[g]['mice']) , protocol);
                                groupDict[nameGroup]['properties']['name'] = nameG;
                                groupDict[nameGroup]['properties']['protocol'] = protocol;
                                if (groupDict[nameGroup]['properties']['type'] != 'new')
                                    groupDict[nameGroup]['properties']['type'] = 'mod';
                            }
                            jQuery("#save").css('display','block');
                            jQuery(popup).dialog( "close" );
		                }
		            }); 
                }
            }
        }
    });
}

function retrieveKey(nameG){
    for (nameGroup in groupDict){
        if (groupDict[nameGroup]['properties']['name'] == nameG){
            return nameGroup
        }
    }
}

//Get the selected TR nodes from DataTables
function fnGetSelectedSx(){
    var aReturn = new Array();
    var aTrs = oTableSx.fnGetNodes();
    for ( var i=0 ; i<aTrs.length ; i++ ){
        if ( jQuery(aTrs[i]).hasClass('row_selected') )
	        aReturn.push( aTrs[i] );
    }
    return aReturn;
}

//Get the selected TR nodes from DataTables
function fnGetSelectedDx(){
    var aReturn = new Array();
    var aTrs = oTableDx.fnGetNodes();
    for ( var i=0 ; i<aTrs.length ; i++ ){
        if ( jQuery(aTrs[i]).hasClass('row_selected') )
	        aReturn.push( aTrs[i] );
    }
    return aReturn;
}

function moveTo(direction){
    if ((groupDx != "") && (groupSx != "")){
        if (direction == 'dx'){
            var destinationTable = "#miceDx"; var sourceTable = "#miceSx"; var sourceRows = fnGetSelectedSx(); var oTableSource = oTableSx; var oTableDestination = oTableDx; 
            var oSettingsDestination = oSettingsDx; var sourceGroup = groupSx; var destinationGroup = groupDx;
        }else if (direction == 'sx'){
            var destinationTable = "#miceSx"; var sourceTable = "#miceDx"; var sourceRows = fnGetSelectedDx(); var oTableSource = oTableDx; var oTableDestination = oTableSx;
            var oSettingsDestination = oSettingsSx; var sourceGroup = groupDx; var destinationGroup = groupSx;
        }
        if (sourceRows.length > 0){
            var startRows = oTableDestination.fnGetNodes().length;
            for (var i = 0; i < sourceRows.length; i++){
                jQuery(destinationTable).dataTable().fnAddData( oTableSource.fnGetData(sourceRows[i]) );
                var genID = oTableSource.fnGetData(sourceRows[i],0);    
                if (groupDict.hasOwnProperty(sourceGroup)){
                    var temp = groupDict[sourceGroup]['mice'][genID];                    
                    delete groupDict[sourceGroup]['mice'][genID];
                }else{
                    var nameGroup = retrieveKey(sourceGroup);
                    var temp = groupDict[nameGroup]['mice'][genID];
                    delete groupDict[nameGroup]['mice'][genID];
                }
                temp['new'] = true;
                console.log(temp);
                if (groupDict.hasOwnProperty(destinationGroup)){
                    console.log("if");
                    groupDict[destinationGroup]['mice'][genID] = {};
                    groupDict[destinationGroup]['mice'][genID] = temp;
                }else{
                    console.log('else');
                    var nameGroup = retrieveKey(destinationGroup);
                    console.log(nameGroup);
                    groupDict[nameGroup]['mice'][genID] = {};
                    groupDict[nameGroup]['mice'][genID] = temp;                   
                }
                jQuery(oSettingsDestination.aoData[startRows+i].nTr).click( function() {
                    jQuery(this).toggleClass('row_selected');
                });
            }
            for (var i = 0; i < sourceRows.length; i++){
                var index = oTableSource.fnGetPosition( sourceRows[i]);
                oTableSource.fnDeleteRow(index);
            }
            //console.log(groupDict);
            if (direction == 'dx'){
                if (groupDict.hasOwnProperty(sourceGroup))
                    writeBox('infoTL', sourceGroup, groupDict[sourceGroup]['properties']['date'], Object.size(groupDict[sourceGroup]['mice']), groupDict[sourceGroup]['properties']['protocol']);
                else{
                    nameGroup = retrieveKey(sourceGroup);
                    writeBox('infoTL', sourceGroup, groupDict[nameGroup]['properties']['date'], Object.size(groupDict[nameGroup]['mice']), groupDict[nameGroup]['properties']['protocol']);
                }
                if (groupDict.hasOwnProperty(destinationGroup))
                    writeBox('infoTR', destinationGroup, groupDict[destinationGroup]['properties']['date'],Object.size(groupDict[destinationGroup]['mice']), groupDict[destinationGroup]['properties']['protocol']);
                else{
                    nameGroup = retrieveKey(destinationGroup);
                    writeBox('infoTR', destinationGroup, groupDict[nameGroup]['properties']['date'],Object.size(groupDict[nameGroup]['mice']), groupDict[nameGroup]['properties']['protocol']);
                }                    
            }else if (direction == 'sx'){
                if (groupDict.hasOwnProperty(sourceGroup)){
                    writeBox('infoTR', sourceGroup, groupDict[sourceGroup]['properties']['date'], Object.size(groupDict[sourceGroup]['mice']), groupDict[sourceGroup]['properties']['protocol']);
                }else{
                    nameGroup = retrieveKey(sourceGroup);
                    writeBox('infoTR', sourceGroup, groupDict[nameGroup]['properties']['date'], Object.size(groupDict[nameGroup]['mice']), groupDict[nameGroup]['properties']['protocol']);
                }                    
                if (groupDict.hasOwnProperty(destinationGroup)){
                    writeBox('infoTL', destinationGroup, groupDict[destinationGroup]['properties']['date'],Object.size(groupDict[destinationGroup]['mice']), groupDict[destinationGroup]['properties']['protocol']);               
                }else{
                    nameGroup = retrieveKey(destinationGroup);
                    writeBox('infoTL', destinationGroup, groupDict[nameGroup]['properties']['date'],Object.size(groupDict[nameGroup]['mice']), groupDict[nameGroup]['properties']['protocol']);
                }                    
            }
            jQuery("#save").css('display','block');   
        }
    }else
        alert("First, select two experimental groups.");
}

function recentGroup(sourceT){
    jQuery("#recentList").empty();
    for (key in groupDict){
        console.log(key);
        var nameG = groupDict[key]['properties']['name'];
        var radioBtn = $('<input type="radio" name="recentGroups" value="'+nameG+'"/>' + nameG + '<br>');
        radioBtn.appendTo('#recentList');
    }
    if (sourceT == 'sx'){
        var infoT = 'infoTL';
        var tableID = "#miceSx";
        var oTable = oTableSx;
        var oSettings = oSettingsSx;
    }else if (sourceT == 'dx'){
        var infoT = 'infoTR';
        var tableID = "#miceDx";
        var oTable = oTableDx;
        var oSettings = oSettingsDx;
    }
    jQuery( "#recentDialog" ).dialog({
        resizable: false,
        height:300,
        width:340,
        modal: true,
        draggable :false,
        buttons: {
            "Cancel": function() {
                jQuery(this).dialog( "close" );
            },
            "Ok": function() {
                if (jQuery('#recentList input:checked').length > 0){
                    var nameG = jQuery('#recentList input:checked')[0].value;
                    if (sourceT == 'sx'){
                        if (groupDx == nameG){
                            alert("You've already loaded this group. Check your selected groups.");
                            return;
                        }
                        groupSx = nameG;
                    }else if (sourceT == 'dx'){
                        if (groupSx == nameG){
                            alert("You've already loaded this group. Check your selected groups.");
                            return;
                        }
                        groupDx = nameG;
                    }
                    deleteRows(tableID);
                    loadFromStorage(infoT, nameG, tableID, oSettings);
                    jQuery(this).dialog( "close" );
                }
            }
        }
    });
}

function saveAll(){
    console.log(JSON.stringify(groupDict));
    jQuery.ajax({
        url: base_url + '/groups/manage',
        type: 'POST',
        data: {'actions':JSON.stringify(groupDict)},
        dataType: 'text',
    });
}