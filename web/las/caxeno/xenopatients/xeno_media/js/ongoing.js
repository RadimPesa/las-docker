var wWidth = $(window).width(); var dWidth = wWidth * 0.3;
var wHeight = $(window).height(); var dHeight = wHeight * 0.45;
var newTab2 = true; var newTab3 = true;
var selTab2 = false; var selTab3 = false;

actions = {}; physBio = {};
mod = false;
jQuery(document).ready(function() {
    $( "#tabs" ).tabs();
    jQuery('label[for=id_scope_detail]').remove();
    jQuery('#id_scope_detail').css("width",'90px');
    jQuery('#buttons p').css("width",'91px');
    jQuery('#buttons p').css("float",'left');
    jQuery('#2').css("width",'60px');
    jQuery('#2').css("float",'right');
    oTable = jQuery('#measure').dataTable( {
        "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        "iDisplayLength": -1,
        "aoColumnDefs": [
            { "bVisible": false, "aTargets": [ 8,12 ] },
        ],
        "aaSorting": [[2, 'asc']]
    });
    oSettings = oTable.fnSettings();
    jQuery("#save").attr("disabled",true);
});

function pad(n) { return ("0" + n).slice(-2); }

function generate_result_table(tableID, actionName){
    var d = new Date();
    var user = jQuery("#user_name").attr('user');   
    var filename = actionName + user + '_' + $.datepicker.formatDate('yy-mm-dd', d) + "--" + pad(d.getHours()) + "-" + pad(d.getMinutes()) + "-" + pad(d.getSeconds());
    console.log(tableID, actionName, filename);
    jQuery(tableID).dataTable( {
        "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        "iDisplayLength": -1,
        "sDom":'TRCH<\"clear\">lfrtip',
        "oTableTools": {
                "aButtons": [  //"copy",
                {
                    "sExtends": "las",
                    "sButtonText": "Las",
                    "sTitle": filename,
                    "mColumns": "visible"
                }, 
                {
                    "sExtends": "pdf",
                    "sButtonText": "Pdf",
                    "sPdfMessage": "Laboratory Assistant Suite - Xenopatients Management Module - " + user + " - " + $.datepicker.formatDate('yy/mm/dd', d) + " @ " + pad(d.getHours()) + ":" + pad(d.getMinutes()) + ":" + pad(d.getSeconds()),
                    "sTitle": filename,
                    "mColumns": "visible",
                    "sPdfSize": "tabloid"
                },
                {
                    "sExtends": "data",
                    "sButtonText": "Data",
                    "sTitle": filename,
                    "mColumns": "visible"
                },
                {
                    "sExtends": "xls",
                    "sButtonText": "Xls",
                    "sTitle": filename,
                    "mColumns": "visible"
                }, 
                "print" ],
                "sUrl": lasauth_url + "/generate_report/",          
                //"sSwfPath": base_url + "/xeno_media/js/DataTables-1.9.0/extras/TableTools/media/swf/copy_csv_xls_pdf.swf",
                "sSwfPath": "/xeno_media/js/DataTables-1.9.0/extras/TableTools/media/swf/copy_csv_xls_pdf.swf",
        }
    });
}

//Get the selected TR nodes from DataTables
function fnGetSelected(){
    var aReturn = new Array();
    var aTrs = oTable.fnGetNodes();
    for ( var i=0 ; i<aTrs.length ; i++ ){
        if ( jQuery(aTrs[i]).hasClass('row_selected') )
            aReturn.push( aTrs[i] );
    }
    return aReturn;
}

// Load the Visualization API and the chart package.
google.load('visualization', '1', {'packages':['corechart']});
// Set a callback to run when the Google Visualization API is loaded.
//google.setOnLoadCallback(drawChart);
// Callback that creates and populates a data table,
// instantiates the chart, passes in the data and draws it.
function drawChart(groups, graph, dates, nameG) {
    console.log(groups);
    console.log(graph);
    console.log(dates);
    console.log(nameG);
    var i = 0;
    // Create the data table.
    var data = new google.visualization.DataTable();
    var dataView = new google.visualization.DataView(data);
    //dataView.setColumns([0, 1, {sourceColumn: 2, role: 'interval'}]);
    data.addColumn('date', 'Date');
    var k = 0;
    if (groups.length > 0){
        for (k = 0; k < groups.length; k++){
            data.addColumn('number', groups[k]);
            //data.addColumn({type:'number', role:'interval'});  // interval role col.
            //data.addColumn({type:'number', role:'interval'});  // interval role col.
        }
    }else{
        data.addColumn('number', nameG);
        //data.addColumn({type:'number', role:'interval'});  // interval role col.
        //data.addColumn({type:'number', role:'interval'});  // interval role col.
        groups[0] = nameG;
    }
    //aggiungo una 'riga' per ogni data in cui e' stata effettuata una misurazione
    data.addRows(dates.length);
    var maxV = 2000.0;
    //per la data in questione, inserisco i valori relativi alle misure dei vari gruppi
    for (i = 0; i < dates.length; i++){
        if (i!=0){
            data.setValue( i, 0, new Date(dates[i]) ); 
            console.log(dates[i]);
            temp = graph[dates[i]];
            var j = 0;
            console.log('gg'+groups.length);
            if (temp){
                for (j = 0; j < groups.length; j++){
                    console.log(groups);
                    console.log(temp);
                    console.log('temp '+temp)
                    console.log('groups ' + groups[j]);
                    if ( groups[j] in temp){
                        var volume = parseFloat(temp[groups[j]]);
                        console.log(i + '  ' + j + '  ' + volume);
                        //dataView.setColumns([{sourceColumn: j+1, role: 'interval'}]);
                        data.setValue( i, j+1, volume);//, volume+100);
                        if (volume > maxV)
                            maxV = volume;
                        //data.setProperty(i, j+1, 'role:interval', 150)
                        //data.setRole( i, j+1, 'interval', 500 )
                        //console.log(i, j);
                        //data.setCell( i, j+1, 2,500 );
                        //data.setCell( i, j+1, 2,100 );
                    }
                }
            }
        }else{
            console.log('else');
            data.setValue( i, 0, new Date(dates[i]) ); 
            var j = 0;
            for (j = 0; j < groups.length; j++){
                console.log(groups[j]);
                console.log('inside');
                data.setValue( 0, j+1, 0 )
            }
        }
    }
    console.log(data);
    // Set chart options
    var options = {'title':nameG, 'width':600, 'height':400, 'pointSize':'4', 'interpolateNulls':true,
                    vAxis: { title: "Tumor Volume (mm3)", viewWindowMode:'explicit',viewWindow:{max:maxV,min:0.0},gridlines: {color:  '#FFFFFF' }},
                    hAxis: {gridlines: {color:  '#FFFFFF' }}
                     };
    // Instantiate and draw our chart, passing in some options.
    var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
    chart.draw(data, options);
}

function firstUse(){
    if (mod == false)
        mod = true;
}

function startLag(){
    console.log('START LAG');
    //jQuery("body").addClass("loading");
    timer = setTimeout(function(){jQuery("body").addClass("loading");}, 1000);    
    //console.log(timer);
}

function endLag(){
    console.log('ENDLAG');
    clearTimeout(timer);
    jQuery("body").removeClass("loading");
}

//carica i dati per la tabella delle azioni pending e per la tabella con tutti i dati
function loadMeasure(nameG){
    jQuery("#save").attr("disabled",false);
    if (jQuery('#selGroup').text() != ""){
        //creare tabella vuota
        var len = oTable.fnGetNodes().length;
        for(var i = 0; i < len; i++) {
            oTable.fnDeleteRow(0);
        }
    }
    var table = document.getElementById('measureBody');
    var url = base_url + '/api.miceOfGroup/' + nameG;
    console.log(url);
    //jQuery("body").addClass("loading");
    
    startLag();

    jQuery.ajax({
        url:url,
	    type: 'get',
        //async:false,
	    success:function(transport) {
            //jQuery("body").addClass("loading");
		    //var response = transport.responseJSON;
            //$("body").addClass("loading");        
		    var measures = eval('(' + transport.miceDict + ')');
		    var i = 0;var j = 0; var k = 0;
            jQuery("#avg").text("Group average volume (mm3): " + transport.avg);
		    while(measures[i]){
			    var rowCount = table.rows.length;
			    var genID = measures[i]['id_mouse']; var barcode = measures[i]['barcode']; var dateM = measures[i]['dateM']; var value = measures[i]['value']; var notes = measures[i]['notes'];
			    var status = measures[i]['status']; var explant = measures[i]['scope']; var nameT = measures[i]['treatment']; var scopeNotes = measures[i]['scopeNotes'];
			    var dateS = measures[i]['dateS']; var duration = measures[i]['duration']; /*var idEvent = measures[i]['idEvent'];*/ var comments = ""; var w = measures[i]['weight'];
                var dateE = measures[i]['dateE']; var treatNotes = measures[i]['treatNotes'];
                jQuery('#measure').dataTable().fnAddData( [genID, barcode, dateM, value, w, notes, status, explant, scopeNotes, nameT, dateS, duration, comments,dateE,treatNotes] );
                var tr = oSettings.aoData[i].nTr;
                /* Add a click handler to the rows - this could be used as a callback */
                if ( (status == 'implanted') || (status == 'ready for explant') || (status == 'waste') || (status == 'explantLite') || (status == 'toSacrifice')){
                    jQuery(tr).click( function() {
                        jQuery(this).toggleClass('row_selected');
                    });
                }
                populatePhysBio(barcode);
			    i++;
	        }

            var measures = eval('(' + transport.measure + ')');
            var i = 0; var j = 0; var k = 0;

            jQuery("#selGroup").text(nameG);
            var operators = eval('(' + transport.operators + ')');
            console.log(operators + ' '+ operators.length);
            var string = "Operator(s) who have worked with this group:";
            for (var i = 0; i < operators.length; i++){
                console.log(operators[i]);
                string += ' ' + operators[i] + ',';
            }
            console.log(string);
            console.log(string.substr(0, string.length-1));
            string = string.substr(0, string.length-1) + '.';
            console.log(string);
            document.getElementById('whoWas').style.display = 'inline';
            document.getElementById('whoWas').innerHTML = string;

            drawChart(eval('(' + transport.groups + ')'), eval('(' + transport.graph + ')'), eval('(' + transport.dateList + ')'), nameG );
            //jQuery("#measureLong").replaceWith( transport.table );
            //jQuery("#allW").replaceWith( transport.wTable );
            
            //jQuery("#measureLong").addClass( "report" );
            //jQuery("#allW").addClass( "report" );
            newTab2 = true;
            newTab3 = true;
            //if (selTab2 == true){
                newTab2 = false;
                try{
                    jQuery("#measureLong").dataTable().fnDestroy();
                    $('#measureLong_wrapper').empty();
                    $('#measureLong_wrapper').remove();
                }catch(err){
                    console.log(err);
                }
                $("#tabs-2").html("<table id='measureLong'></table>");
                jQuery("#measureLong").replaceWith( transport.table );
                generate_result_table("#measureLong", 'measureHistory');
            //}
            console.log('2');
            //if (selTab3 == true){
                newTab3 = false;
                try{
                    jQuery("#allW").dataTable().fnDestroy();
                    $('#allW_wrapper').empty();
                    $('#allW_wrapper').remove();
                }catch(err){
                    console.log(err);
                }
                $("#tabs-3").html("<table id='allW'></table>");
                jQuery("#allW").replaceWith( transport.wTable );
                generate_result_table("#allW", 'weightHistory');
            //}
            //jQuery("body").removeClass("loading");
            endLag()
        }
    });
    
}            

function initTab2(){
    selTab2 = true;
    selTab3 = false;
    if (newTab2 == true){
        newTab2 = false;
        generate_result_table("#measureLong", 'measureHistory');
    }
}

function initTab3(){
    selTab2 = false;
    selTab3 = true;
    if (newTab3 == true){
        newTab3 = false;
        generate_result_table("#allW", 'weightHistory');
    }
}

function isInCurrentTable(genID){
    console.log(genID);
    var nodes = oTable.fnGetNodes();
    //console.log(nodes);
    for (var i = 0; i < nodes.length; i++ ){
        if (genID == oTable.fnGetData( i, 0 ) )
            return i;
    }
    return -1;
}


function populatePhysBio(barcode){
    if (!physBio.hasOwnProperty(barcode)){
        var url = base_url + "/api.phystobio/" + barcode;
        console.log(url);
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
}

function checkSelectedMice(){
    var barcodeList = {};
    var rows = fnGetSelected(); //array con le righe selezionate
    for(var i = 0; i <= oTable.fnGetNodes().length; i++) {
        var row = oTable.fnGetNodes()[i];
        if (jQuery.inArray(row, rows) > -1){
            var barcode = oTable.fnGetData(i, 1);
            if ( !barcodeList.hasOwnProperty(barcode) )
                barcodeList[barcode] = barcode;
        }
    }
    var message = "Do you confirm the selected actions? You can add some optional comments.";
    var first = true;
    var flag = false;
    for (barcode in barcodeList){
        //console.log(barcode);
        flag = true;
        if (physBio[barcode].length > 1){
            for (biomouse in physBio[barcode]){
                //console.log(physBio[barcode][biomouse]['genID']);
                if (first){
                    //console.log('first');
                    message = "Warning: the following mouse will be involved in the action selected.<br/>";
                    first = false;
                }
                message += ' ' + physBio[barcode][biomouse]['genID'] + ', group: ' + physBio[barcode][biomouse]['group'] + '<br/>';
            }
            message += "<br/>Do you confirm the selected actions? You can add some optional comments."
        }
    }
    if (flag)
        $("#confirmAction").html(message);
    else
        $("#confirmAction").text("Do you confirm the selected actions? You can add some optional comments.");
}

function makeAction(msg){
    firstUse();
    var rows = fnGetSelected(); //array con le righe selezionate
    if (rows.length > 0){
        if (msg != 'Explant without sacrifice')
            checkSelectedMice();
        else
            $("#confirmAction").text("Do you confirm the selected actions? You can add some optional comments.");
        jQuery( "#dialog" ).dialog({
            //resizable: false,
            height:dHeight,
            width:dWidth,
            modal: true,
            draggable :false,
            buttons: {
                "Yes": function() {
                    var notes = jQuery('#checkNotes').val();
                    for(var i = 0; i <= oTable.fnGetNodes().length; i++) {
                        var row = oTable.fnGetNodes()[i];
                        if (jQuery.inArray(row, rows) > -1){
                            //var barcode = oTable.fnGetData(i,8);
                            var genID = oTable.fnGetData(i,0);
                            if (msg == 'Explant without sacrifice'){
                                if (actions.hasOwnProperty(genID)){
                                    if (notes != "")
                                        actions[genID]['comment'] = notes;
                                    actions[genID]['explant']['type'] = 'explLite';
                                }else{
                                    addKey(genID);
                                    if (notes != "")
                                        actions[genID]['comment'] = notes;
                                    actions[genID]['explant']['type'] = 'explLite';
                                }
                                var index = isInCurrentTable(genID);
                                if (index >= 0){
                                    oTable.fnUpdate('explantLite', index, 6, false, false);
                                    oTable.fnUpdate("", index, 8, false, false);
                                    oTable.fnUpdate(notes, index, 12, false, false);
                                }
                                if (jQuery(row).hasClass('row_selected'))
                                    jQuery(row).toggleClass('row_selected');
                            }else{
                                var index_temp = oTable.fnGetPosition(row);
                                var barcode = oTable.fnGetData(index_temp, 1);
                                var scopeNotes = jQuery("#explNotes").val() ;
                                for (biomouse in physBio[barcode]){
                                    var genID = physBio[barcode][biomouse]['genID'];
                                    var k = isInCurrentTable(genID);
                                    var scope = jQuery("#id_scope_detail").find(":selected").text();
                                    if (msg == "ready for explant"){
                                        if (actions.hasOwnProperty(genID)){
                                            if (notes != "")
                                                actions[genID]['comment'] = notes;
                                            actions[genID]['explant']['type'] = 'expl';
                                            actions[genID]['explant']['notes'] = scopeNotes;
                                            actions[genID]['explant']['scope'] = scope;
                                        }else{
                                            addKey(genID);
                                            if (notes != "")
                                                actions[genID]['comment'] = notes;
                                            actions[genID]['explant']['type'] = 'expl';
                                            actions[genID]['explant']['notes'] = scopeNotes;
                                            actions[genID]['explant']['scope'] = scope;
                                        }
                                    }else{
                                        jQuery(tr).children("td[status=pending]").attr('status','canc');
                                        jQuery(tr).children("td[status=pending]").text('Canceled');
                                        jQuery(tr).children("td[status=new]").attr('status','canc');
                                        jQuery(tr).children("td[status=new]").text('Canceled');
                                        jQuery(tr).children("td[status=sacr]").attr('status','canc');
                                        jQuery(tr).children("td[status=sacr]").text('Canceled');
                                        jQuery(tr).attr('status','sacr');
                                        if (actions.hasOwnProperty(genID)){
                                            if (notes != "")
                                                actions[genID]['comment'] = notes;
                                            actions[genID]['explant']['type'] = 'sacr';
                                        }else{
                                            addKey(genID);
                                            if (notes != "")
                                                actions[genID]['comment'] = notes;
                                            actions[genID]['explant']['type'] = 'sacr';
                                        }
                                    }
                                    if (k >= 0){
                                        //presente nella tabella
                                        var index = k;
                                        var tr = oSettings.aoData[index].nTr;
                                        jQuery(tr).children("td:nth-child(8)").attr('status','new');
                                        jQuery(tr).attr('status','new');
                                        oTable.fnUpdate(msg, index, 7, false, false);
                                        //togliere la selezione della riga
                                        if (jQuery(row).hasClass('row_selected'))
                                            jQuery(row).toggleClass('row_selected');
                                        if (msg == "ready for explant"){
                                            oTable.fnUpdate(scope, index, 7, false, false);
                                            oTable.fnUpdate(scopeNotes, index, 8, false, false);
                                            oTable.fnUpdate(notes, index, 12, false, false);
                                            oTable.fnUpdate(msg, index, 6, false, false);
                                        }else{
                                            oTable.fnUpdate('sacrifice', index, 6, false, false);
                                            oTable.fnUpdate("", index, 7, false, false);
                                            oTable.fnUpdate("", index, 8, false, false);
                                            oTable.fnUpdate("", index, 9, false, false);
                                            oTable.fnUpdate("", index, 10, false, false);
                                            oTable.fnUpdate("", index, 11, false, false);
                                            oTable.fnUpdate(notes, index, 12, false, false);
                                            jQuery(tr).children("td[status=pending]").attr('status','canc');
                                            jQuery(tr).children("td[status=pending]").text('Canceled');
                                            jQuery(tr).children("td[status=new]").attr('status','canc');
                                            jQuery(tr).children("td[status=new]").text('Canceled');
                                            jQuery(tr).children("td[status=sacr]").attr('status','canc');
                                            jQuery(tr).children("td[status=sacr]").text('Canceled');
                                            jQuery(tr).attr('status','sacr');
                                        }
                                    }
                                }
                            }
                        }
                    }
                    jQuery('#checkNotes').val("");
                    jQuery( this ).dialog( "close" );
                },
                "No":function(){jQuery( this ).dialog( "close" );}
            }
        });
    }
}

function insertComment() {
    firstUse();
    jQuery( "#dialog" ).dialog({
        //resizable: false,
        height:dHeight,
        width:dWidth,
        modal: true,
        draggable :false,
        buttons: {
            "Cancel": function() {
                jQuery( this ).dialog( "close" );
            },
            "Ok": function() {
                notes = jQuery('#checkNotes').val();
                var rows = fnGetSelected(); //array con le righe selezionate
                if (rows.length > 0){
                    for(var i = 0; i <= oTable.fnGetNodes().length; i++) {
                        var row = oTable.fnGetNodes()[i];
                        if (jQuery.inArray(row, rows) > -1){
                            var index = i;
                            var tr = oSettings.aoData[index].nTr;
                            var index = oTable.fnGetPosition(row);
                            oTable.fnUpdate(notes, index, 12, false, false);
                            jQuery(row).toggleClass('row_selected');
                            var genID = oTable.fnGetData(index, 0);
                            if (actions.hasOwnProperty(genID)){
                                actions[genID]['comment'] = notes;
                            }else{
                                addKey(genID);
                                actions[genID]['comment'] = notes;
                            }
                        }
                    }
                }
                jQuery('#checkNotes').val("");
                jQuery( this ).dialog( "close" );
            }
        }
    });    
}

function stopTreat(msg){
    firstUse();
    var k = 0;
    //permetto lo stop del trattamento solo se questo era stato precedentemente approvato
    cantStop = false;
    var rows = fnGetSelected(); //array con le righe selezionate
    if (rows.length > 0){
        checkSelectedMice();
        for(var i = 0; i <= oTable.fnGetNodes().length; i++) {
            var row = oTable.fnGetNodes()[i];
            if (jQuery.inArray(row, rows) > -1){
                var index = i;
                var tr = oSettings.aoData[index].nTr;
                if (jQuery(tr).children("td:nth-child(9)").attr('status') == 'new' || jQuery(tr).children("td:nth-child(9)").text() == '-' ){
                    cantStop = true;
                }
            }
        }
        if (cantStop){
            alert("You can't stop no confirmed treatment(s).");
        }else{
            jQuery( "#dialog" ).dialog({
                height:dHeight,
                width:dWidth,
                modal: true,
                draggable :false,
                buttons: {
                    "Yes": function() {
                        var notes = jQuery('#checkNotes').val();
                        var rows = fnGetSelected(); //array con le righe selezionate
                        for(var i = 0; i <= oTable.fnGetNodes().length; i++) {
                            console.log(barcode);
                            var row = oTable.fnGetNodes()[i];
                            if (jQuery.inArray(row, rows) > -1){
                                var barcode = oTable.fnGetData(i, 1);    
                                for (biomouse in physBio[barcode]){
                                    var genID = physBio[barcode][biomouse]['genID'];
                                    var k = isInCurrentTable(genID);
                                    if (actions.hasOwnProperty(genID)){
                                        if (notes != "")
                                            actions[genID]['comment'] = notes;
                                        actions[genID]['treatment']['action'] = 'stop';
                                    }else{
                                        addKey(genID);
                                        if (notes != "")
                                            actions[genID]['comment'] = notes;
                                        actions[genID]['treatment']['action'] = 'stop';
                                    }
                                    if (k > -1){
                                        var index = k;
                                        var tr = oSettings.aoData[index].nTr;
                                        jQuery(tr).children("td:nth-child(9)").attr('status','new');
                                        jQuery(tr).attr('status','new');
                                        oTable.fnUpdate("STOPPED", index, 9, false, false);
                                        var todayNow = new Date();
                                        oTable.fnUpdate(notes, index, 12, false, false);
                                        if (jQuery(row).hasClass('row_selected'))
                                            jQuery(row).toggleClass('row_selected');                                      
                                    }

                                }
                            }
                        }
                        jQuery( this ).dialog( "close" );
                    },
                    "No":function(){jQuery( this ).dialog( "close" );}
                }
            });
        }
    }else
        alert("You have to select at least one row.");
}

function resetAction(){
    var rows = fnGetSelected();
    if (rows.length > 0){
        for(var i = 0; i <= oTable.fnGetNodes().length; i++) {
            var row = oTable.fnGetNodes()[i];
            if (jQuery.inArray(row, rows) > -1){
                var index_temp = oTable.fnGetPosition(row);
                var barcode = oTable.fnGetData(index_temp, 1);
                for (biomouse in physBio[barcode]){
                    var genID = physBio[barcode][biomouse]['genID'];
                    var k = isInCurrentTable(genID);
                    if (k >= 0){
                        var tr = oSettings.aoData[k].nTr;
                        if (jQuery(row).hasClass('row_selected'))
                            jQuery(row).toggleClass('row_selected');
                        callReset(k, genID, tr);
                    }
                    if (actions.hasOwnProperty(genID)){
                        removeKey(genID);
                    }
                }
            }
        }
    }else
        alert("You have to select at least one row.");
}

function callReset( index, genID, tr){
    firstUse();
    var status = ""; var explant = ""; var scopeNotes = ""; var nameT = ""; var start = ""; var end = "";
    var url = base_url + '/api.actionsMouse/' + genID;
    console.log(url);
    jQuery.ajax({
        url:url,
        type: 'get',
        async:false,
        datatype:'json',
        success:function(transport) {
            //console.log(eval(transport));
            var data = transport;
            resetRowActions(index, data['status'],data['scope'],data['scopeNotes'],data['treatment'],data['dateS'],data['duration'], tr, genID);
        }
    });
}

function resetRowActions(index, status, explant, scopeNotes, nameT, start, end, tr, genID){
    oTable.fnUpdate(status , index, 6, false, false);
    oTable.fnUpdate(explant , index, 7, false, false);
    oTable.fnUpdate(scopeNotes , index, 8, false, false);
    oTable.fnUpdate(nameT , index, 9, false, false);
    oTable.fnUpdate(start , index, 10, false, false);
    oTable.fnUpdate(end , index, 11, false, false);

    jQuery(tr).children("td[status=pending]").attr('status','');
    jQuery(tr).children("td[status=canc]").attr('status','');
    jQuery(tr).children("td[status=sacr]").attr('status','');
    jQuery(tr).children("td[status=new]").attr('status','');
}

//funzione chiamata quando si deve inserire un nuovo valore nel dict, inserendone quindi la chiave relativa
function addKey(genID){
    actions[genID] = {};
    actions[genID]['explant'] = {}
    actions[genID]['explant']['type'] = "";
    actions[genID]['explant']['scope'] = "";
    actions[genID]['explant']['notes'] = "";
    actions[genID]['treatment'] = {};
    actions[genID]['treatment']['action'] = "";
    actions[genID]['treatment']['name'] = "";
    actions[genID]['treatment']['dateP'] = "";
    actions[genID]['comment'] = "";
}

function removeKey(genID){
    delete actions[genID];
}

function confirmCheck(){
    if (Object.size(actions) > 0){
        jQuery("#save").attr("disabled",true);
        console.log(actions);
        console.log('-');
        jQuery.ajax({
            url: base_url + '/experiments/ongoing',
            type: 'POST',
            data: {'actions':JSON.stringify(actions)},
            dataType: 'text',
        });
    }else{
        alert("Before you save, do at least one action!");
    }
}
