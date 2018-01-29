var wWidth = $(window).width(); var dWidth = wWidth * 0.3;
var wHeight = $(window).height(); var dHeight = wHeight * 0.45;
var newTab2 = true; var newTab3 = true;
var selTab2 = false; var selTab3 = false;

newExpl = {}; newTreat = {}; cancData = {}; pendingData = {}; sacrificeData = {}; physBio = {};
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
// Set a callback to run when the Google Visualization API is loaded. Callback that creates and populates a data table, instantiates the chart, passes in the data and draws it.
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

//carica i dati per la tabella delle azioni pending e per la tabella con tutti i dati
function loadMeasure(nameG){
    var answer = true;
    jQuery("#save").attr("disabled",false);
    if (jQuery('#selGroup').text() != "" && (mod == true) )
        answer = confirm('Are you sure?\nUnsaved data will be lost. (first, click "Confirm all" to save your changes)');
    if (answer){
        if (jQuery('#selGroup').text() != ""){
            //creare tabella vuota
            var table = document.getElementById("measure");
            var totR = table.rows.length;
            for(var i = 1; i < totR; i++) {
                var row = table.rows[1];
                var index = oTable.fnGetPosition(row);
                oTable.fnDeleteRow(index);
            }
        }
        var table = document.getElementById('measureBody');
	    var url = base_url + '/api.checkGroup/' + nameG;
	    jQuery("body").addClass("loading");
        jQuery.ajax({
            url:url,
            type: 'get',
            //async:false,
            success:function(transport) {
			    var measures = eval('(' + transport.list_quant + ')');
			    var i = 0;var j = 0; var k = 0;
                jQuery("#avg").text("Group average volume (mm3): " + transport.avg);
                jQuery("#avgChecked").text("");
			    while(measures[i]){
				    var rowCount = table.rows.length;
				    var genID = measures[i]['id_mouse']; var barcode = measures[i]['barcode']; var dateM = measures[i]['dateM']; var value = measures[i]['value']; var notes = measures[i]['notes'];
				    var status = measures[i]['status']; var explant = measures[i]['scope']; var nameT = measures[i]['treatment']; var scopeNotes = measures[i]['scopeNotes'];
				    var dateS = measures[i]['dateS']; var duration = measures[i]['duration']; var idEvent = measures[i]['idEvent']; var comments = ""; var w = measures[i]['weight'];
                    var endDate = measures[i]['dateE']; var treatNotes = measures[i]['treatNotes'];                    
                    jQuery('#measure').dataTable().fnAddData( [genID, barcode, dateM, value, w, notes, status.substring(1,status.length), explant.substring(1,explant.length), scopeNotes, nameT.substring(1,nameT.length), dateS, duration, comments, endDate,treatNotes] );
                    var tr = oSettings.aoData[i].nTr;
                    jQuery(tr).attr('id_event',idEvent);
                    if (status.substring(1) != "explanted" && status.substring(1) != "sacrified" && status.substring(1) != "dead accidentally"){
                        /* Add a click handler to the rows - this could be used as a callback */
                        jQuery(tr).click( function() {
                            jQuery(this).toggleClass('row_selected');
                            calcSelectedAvg();
                        });
                        populatePhysBio(barcode);
                        jQuery(tr).attr('status','pending');    
                        
                        if (status.charAt(0) == "0"){
                            jQuery(tr).children("td:nth-child(7)").attr('status','pending');
                        }                            
                        if (explant.charAt(0) == "0"){
                            jQuery(tr).children("td:nth-child(8)").attr('status','pending');
                        }
                        if (nameT.charAt(0) == "0"){
                            jQuery(tr).children("td:nth-child(9)").attr('status','pending');
                            jQuery(tr).children("td:nth-child(10)").attr('status','pending');
                            jQuery(tr).children("td:nth-child(11)").attr('status','pending');
                        }
                    }else{
                        jQuery(tr).attr('status','not applicable');
                    }
				    i++;
		        }

                var i = 0; var j = 0; var k = 0;
                jQuery("#selGroup").text(nameG);
                var operators = eval('(' + transport.operators + ')');
                console.log(operators + ' '+ operators.length);
                var string = "Operator(s) who have worked with this group:";
                for (var i = 0; i < operators.length; i++){
                    console.log(operators[i]);
                    string += ' ' + operators[i] + ',';
                }
                string = string.substr(0, string.length-1) + '.';
                console.log(string);
                document.getElementById('whoWas').style.display = 'inline';
                document.getElementById('whoWas').innerHTML = string;
                drawChart(eval('(' + transport.groups + ')'), eval('(' + transport.graph + ')'), eval('(' + transport.dateList + ')'), nameG );
                
                /*jQuery("#measureLong").replaceWith( transport.table );
                jQuery("#allW").replaceWith( transport.wTable )
                console.log(transport.wTable);

                newTab2 = true;
                newTab3 = true;*/
                //if (selTab2 == true){
                    newTab2 = false;
                    try{
                        jQuery("#measureLong").dataTable().fnDestroy();
                        console.log('a1');
                        $('#measureLong_wrapper').empty();
                        console.log('a2');
                        $('#measureLong_wrapper').remove();
                    }catch(err){
                        console.log(err);
                    }
                    $("#tabs-2").html("<table id='measureLong'></table>");
                    jQuery("#measureLong").replaceWith( transport.table );
                    generate_result_table("#measureLong", 'measureHistory');
                //}
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
                jQuery("body").removeClass("loading");
            }
	    });
    }	    
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

function trunc(n, decimal){
    decimal++;
    n = n.toString();
    if(n.indexOf(".")>0)
        n = n.substring(0,n.indexOf(".")+decimal);
    n = parseFloat(n);
    return n;
}

//aggiorna e mostra la media per i topi checkati
function calcSelectedAvg() {
    try {
        var nDecimal = 3; //variabile usata per chiamare la funzione trunc, inviandolo come valore del paramentro decimal
        var tot = 0;var counter_for_avg = 0;
        var table = document.getElementById("measure");
        var rowCount = table.rows.length;
        var maxIndex = 0;var avg = 0;
        var rows = fnGetSelected(); //array con le righe selezionate
        if (rows.length > 0){
            for(var i = 1; i < table.rows.length; i++) {
                var row = table.rows[i];
                if (jQuery.inArray(row, rows) > -1){
                    var index = oTable.fnGetPosition(row);
                    tot = tot + parseFloat(oTable.fnGetData(index, 3));
                    counter_for_avg++;
                }
            }
            console.log(tot + ' ' + counter_for_avg);
            var avg =  trunc( (tot/counter_for_avg), nDecimal);
            console.log(avg);
            document.getElementById('avgChecked').innerHTML ="Average volume of the selected mice: " + avg;
            //if (avg > document.getElementById('threshold').value)
            //    document.getElementById('avgChecked').style.color='red';
            //else
            //    document.getElementById('avgChecked').style.color='black';
        }else{
            document.getElementById('avgChecked').innerHTML ="Average volume of the selected mice: -"
            document.getElementById('avgChecked').style.color='black';
        }
    }catch(e) {
        alert(e);
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
    var table = document.getElementById('measure'); 
    var rows = fnGetSelected(); //array con le righe selezionate
    for(var i = 0; i <= oTable.fnGetNodes().length; i++) {
        var row = table.rows[i];
        if (jQuery.inArray(row, rows) > -1){
            var index_temp = oTable.fnGetPosition(row);
            var barcode = oTable.fnGetData(index_temp, 1);
            if ( !barcodeList.hasOwnProperty(barcode) )
                barcodeList[barcode] = barcode;
        }
    }
    var message = "Do you confirm the selected actions? You can add some optional comments.";
    var first = true;
    var flag = false;
    for (barcode in barcodeList){
        console.log(barcode);
        flag = true;
        if (physBio[barcode].length > 1){
            for (biomouse in physBio[barcode]){
                if (first){
                    message = "Warning: the following mouse will be involved in the action selected.<br/>";
                    fisrt = false;
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
    var table = document.getElementById('measure'); 
    var rows = fnGetSelected(); //array con le righe selezionate

    if (rows.length > 0){
        checkSelectedMice();
        jQuery( "#dialog" ).dialog({
            //resizable: false,
            height:dHeight,
            width:dWidth,
            modal: true,
            draggable :false,
            buttons: {
                "Yes": function() {
                    var comments = jQuery('#checkNotes').val();
                    for(var i = 0; i <= oTable.fnGetNodes().length; i++) {
                        var row = table.rows[i];
                        if (jQuery.inArray(row, rows) > -1){
                            var scopeNotes = jQuery("#explNotes").val() ;
                            var index_temp = oTable.fnGetPosition(row);
                            var barcode = oTable.fnGetData(index_temp, 1);
                            var genID = oTable.fnGetData(index_temp, 0);
                            //alert(msg);
                            if (msg == "Explant without sacrifice"){
                                var index = isInCurrentTable(genID);
                                //alert(index);
                                if (index >= 0){
                                    oTable.fnUpdate('explantLite', index, 6, false, false);
                                    oTable.fnUpdate("", index, 8, false, false);
                                    oTable.fnUpdate(comments, index, 12, false, false);
                                }
                                if (jQuery(row).hasClass('row_selected'))
                                    jQuery(row).toggleClass('row_selected');
                            }else{
                                for (biomouse in physBio[barcode]){
                                    console.log(biomouse);
                                    
                                    console.log(genID);
                                    var k = isInCurrentTable(genID);
                                    console.log(k);
                                    var scope = jQuery("#id_scope_detail").find(":selected").text();
                                    if (k >= 0){
                                        //presente nella tabella
                                        var index = k;
                                        var tr = oSettings.aoData[index].nTr;
                                        console.log('indexxxxxx '+index);
                                        jQuery(tr).children("td:nth-child(8)").attr('status','new');
                                        jQuery(tr).attr('status','new');
                                        /*jQuery("#measureBody tr:nth-child("+child+") td:nth-child(6)").attr('status','new');
                                        jQuery("#measureBody tr:nth-child("+child+")").attr('status','new');*/
                                        oTable.fnUpdate(msg, index, 7, false, false);
                                        //togliere la selezione della riga
                                        if (jQuery(row).hasClass('row_selected'))
                                            jQuery(row).toggleClass('row_selected');
                                        if (msg == "ready for explant"){
                                            oTable.fnUpdate(scope, index, 7, false, false);
                                            oTable.fnUpdate(scopeNotes, index, 8, false, false);
                                            oTable.fnUpdate(comments, index, 12, false, false);
                                            oTable.fnUpdate(msg, index, 6, false, false);
                                        }else{
                                            oTable.fnUpdate('sacrifice', index, 6, false, false);
                                            oTable.fnUpdate("", index, 7, false, false);
                                            oTable.fnUpdate("", index, 8, false, false);
                                            oTable.fnUpdate("", index, 9, false, false);
                                            oTable.fnUpdate("", index, 10, false, false);
                                            oTable.fnUpdate("", index, 11, false, false);
                                            oTable.fnUpdate(comments, index, 12, false, false);

                                            jQuery(tr).children("td[status=pending]").attr('status','canc');
                                            jQuery(tr).children("td[status=pending]").text('Canceled');
                                            jQuery(tr).children("td[status=new]").attr('status','canc');
                                            jQuery(tr).children("td[status=new]").text('Canceled');
                                            jQuery(tr).children("td[status=sacr]").attr('status','canc');
                                            jQuery(tr).children("td[status=sacr]").text('Canceled');
                                            jQuery(tr).attr('status','sacr');
                                        }
                                    }else{
                                        //non presente nella tabella, segnarlo nella struttura dati
                                        console.log(msg);
                                        if (msg == "ready for explant"){
                                            newExpl[genID] = genID + "&" + scope + "&" + scopeNotes + "&" + msg + "&" + comments;
                                        }else if(msg =="Explant without sacrifice"){
                                            //newExpl[biomouse] = biomouse + '&explantLite&' + comments;
                                            //l'explantLite non si propaga ai fratelli!
                                            console.log('nothing to do here');
                                        }else{
                                            sacrificeData[genID] = genID + '&' + comments;
                                            cancData[genID]  = genID + '&' + comments;
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
    }else
        alert("You have to select at least one row.");
}


function insertComment() {
    firstUse();
    var table = document.getElementById('measure');
    jQuery( "#dialog" ).dialog({
        resizable: false,
        height:200,
        width:340,
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
                        var row = table.rows[i];
                        if (jQuery.inArray(row, rows) > -1){
                            console.log(i);
                            console.log(table.rows);
                            var index = oTable.fnGetPosition(row);
                            console.log(index);
                            var tr = oSettings.aoData[index].nTr;
                            var child = i + 1;
                            var index = oTable.fnGetPosition(row);
                            console.log('1111111 ' + notes);
                            oTable.fnUpdate(notes, index, 12, false, false);
                            jQuery(row).toggleClass('row_selected');
                            console.log(index + '-------' + oTable.fnGetData(index, 11));
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
                if (jQuery(tr).children("td:nth-child(9)").attr('status') == 'new' || jQuery(tr).children("td:nth-child(9)").text() == '' ){
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
                        var comments = jQuery('#checkNotes').val();
                        var rows = fnGetSelected(); //array con le righe selezionate
                        for(var i = 0; i <= oTable.fnGetNodes().length; i++) {
                            console.log(barcode);
                            var row = oTable.fnGetNodes()[i];
                            if (jQuery.inArray(row, rows) > -1){
                                var barcode = oTable.fnGetData(i, 1);    
                                for (biomouse in physBio[barcode]){
                                    var genID = physBio[barcode][biomouse]['genID'];
                                    var k = isInCurrentTable(genID);
                                    console.log(k);
                                    if (k < 0){
                                        var nameT = 'STOPPED';
                                        newTreat[genID]  = genID + '&' + nameT + '&&' + comments;
                                    }else{
                                        var index = k;
                                        console.log('indexxxxxx '+index);
                                        var tr = oSettings.aoData[index].nTr;
                                        jQuery(tr).children("td:nth-child(9)").attr('status','new');
                                        jQuery(tr).attr('status','new');
                                        oTable.fnUpdate("STOPPED", index, 9, false, false);
                                        var todayNow = new Date();
                                        oTable.fnUpdate(comments, index, 12, false, false);
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

function deleteAction(){
    var rows = fnGetSelected(); 
    if (rows.length > 0){
        checkSelectedMice();
        jQuery( "#dialog" ).dialog({
            resizable: false,
            height:200,
            width:340,
            modal: true,
            draggable :false,
            buttons: {
                "Yes": function() {
                    jQuery( this ).dialog( "close" );    
                    comments = jQuery('#checkNotes').val();
                    for(var i = 0; i <= oTable.fnGetNodes().length; i++) {
                        var row = oTable.fnGetNodes()[i];
                        if (jQuery.inArray(row, rows) > -1){
                            var index_temp = oTable.fnGetPosition(row);
                            var barcode = oTable.fnGetData(index_temp, 1);
                            for (biomouse in physBio[barcode]){
                                console.log(biomouse);
                                var genID = physBio[barcode][biomouse]['genID'];
                                var k = isInCurrentTable(genID);
                                console.log(k);
                                if (k < 0){
                                    newTreat[genID]  = "";
                                    newExpl[genID] = ""; 
                                    cancData[genID] = ""; 
                                    sacrificeData[genID] = "";
                                    cancData[genID]  = genID + '&' + comments;
                                }else{
                                    var index = k;
                                    var tr = oSettings.aoData[index].nTr;
                                    console.log('indexxxxxx '+index);
                                    if (jQuery(row).hasClass('row_selected'))
                                        jQuery(row).toggleClass('row_selected');
                                    oTable.fnUpdate(comments, index, 12, false, false);
                                    callDelete(index,genID, tr);
                                }
                            }
                        }
                    }
                },
                "No":function(){jQuery( this ).dialog( "close" );}
            }
        });    
    }else
        alert("You have to select at least one row.");
}

function callDelete(index, genID, tr){
    firstUse();
    var url = base_url + '/api.actionsMouse/' + genID;
    jQuery.ajax({
        url:url,
        type: 'get',
        async:'false',
        datatype:'json',
        success:function(transport) {
            var data = transport;
            deleteRowActions(index, data['status'],data['scope'],data['scopeNotes'],data['treatment'],data['dateS'],data['duration'], tr);
        }
    });
}

function deleteRowActions( index, status, explant, scopeNotes, nameT, start, end, tr){
    oTable.fnUpdate(status , index, 6, false, false);
    oTable.fnUpdate(explant , index, 7, false, false);
    oTable.fnUpdate(scopeNotes , index, 8, false, false);
    oTable.fnUpdate(nameT , index, 9, false, false);
    oTable.fnUpdate(start , index, 10, false, false);
    oTable.fnUpdate(end , index, 11, false, false);
    jQuery(tr).children("td[status=pending]").attr('status','canc');
    jQuery(tr).children("td[status=sacr]").attr('status','canc');
    jQuery(tr).children("td[status=new]").attr('status','canc');
    jQuery(tr).attr('status','canc');
}

function resetAction(){
    var rows = fnGetSelected(); //array con le righe selezionate
    if (rows.length > 0){
        for(var i = 0; i <= oTable.fnGetNodes().length; i++) {
            var row = oTable.fnGetNodes()[i];
            if (jQuery.inArray(row, rows) > -1){
                var index_temp = oTable.fnGetPosition(row);
                var barcode = oTable.fnGetData(index_temp, 1);
                for (biomouse in physBio[barcode]){
                    console.log(biomouse);
                    var genID = physBio[barcode][biomouse]['genID'];
                    var k = isInCurrentTable(genID);
                    console.log(k);
                    if (k < 0){
                        newTreat[genID]  = "";
                        newExpl[genID] = ""; 
                        cancData[genID] = ""; 
                        //pendingData[genID] = ""; 
                        sacrificeData[genID] = "";
                    }else{
                        var index = k
                        var tr = oSettings.aoData[index].nTr;
                        var idEvent = jQuery(tr).attr('id_event');
                        if (jQuery(row).hasClass('row_selected'))
                            jQuery(row).toggleClass('row_selected');
                        callReset(index, idEvent, tr);
                    }
                }
            }
        }
    }else
        alert("You have to select at least one row.");
}

function callReset( index, idEvent, tr){
    firstUse();
    console.log('ajaxing');
    jQuery.ajax({
        url: base_url + '/api.pendingMouse/' + idEvent,
        type: 'get',
        async: false,
        dataType:'json',
        success:function(transport) {
            console.log(transport);
            var data = transport;
            resetRowActions( index, data['status'],data['scope'],data['scopeNotes'],data['treatment'],data['dateS'],data['duration'], tr);
        }
    });
    console.log('end ajax');
}

function resetRowActions(index, status, explant, scopeNotes, nameT, start, end, tr){
    console.log('1');
    oTable.fnUpdate(status.substring(1,status.length), index, 6, false, false);
    oTable.fnUpdate(explant.substring(1,explant.length), index, 7, false, false);
    oTable.fnUpdate(scopeNotes, index, 8, false, false);
    oTable.fnUpdate(nameT.substring(1,nameT.length), index, 9, false, false);
    oTable.fnUpdate(start, index, 10, false, false);
    oTable.fnUpdate(end, index, 11, false, false);

    jQuery(tr).children("td[status=pending]").attr('status','');
    jQuery(tr).children("td[status=canc]").attr('status','');
    jQuery(tr).children("td[status=sacr]").attr('status','');
    jQuery(tr).children("td[status=new]").attr('status','');

    if (status.charAt(0) == "0"){
        jQuery(tr).children("td:nth-child(7)").attr('status','pending');
    }                            
    if (explant.charAt(0) == "0"){
        jQuery(tr).children("td:nth-child(8)").attr('status','pending');
    }
    if (nameT.charAt(0) == "0"){
        jQuery(tr).children("td:nth-child(9)").attr('status','pending');
        jQuery(tr).children("td:nth-child(10)").attr('status','pending');
        jQuery(tr).children("td:nth-child(11)").attr('status','pending');
    }

    jQuery(tr).attr('status', 'pending');
    console.log('2');
}

function confirmCheck(){
    jQuery("#save").attr("disabled",true);
    var canc = "";var news = "";var approved = "";var scopeExplant = "";var notesExplant = "";var comments = "";var status = "";var nameT = "";var startDate = ""; var idEvent = ""; 
    var newExplList = "";var newTreatList = "";var cancList = "";var pendingList = "";var sacrificeList = "";var groupName = jQuery("#selGroup").text();
    var notApplicableList = "";
    for(var i = 0; i < oTable.fnGetNodes().length; i++) {
        comments = oTable.fnGetData(i, 12);
        var tr = oSettings.aoData[i].nTr;
        idEvent = jQuery(tr).attr('id_event');
        if ( jQuery(tr).children("td:nth-child(8)").attr('status') == 'new' ){
            scopeExplant = oTable.fnGetData(i, 7);
            notesExplant = oTable.fnGetData(i, 8);//jQuery("#measureBody tr:nth-child("+child+") td:nth-child(7)").text();
            status = oTable.fnGetData(i, 6);
            if (newExplList != "")
                newExplList += "|" + idEvent + '&' + scopeExplant + '&' + notesExplant + '&' + status + '&' + comments;
            else
                newExplList = idEvent + '&' + scopeExplant + '&' + notesExplant + '&' + status + '&' + comments;
            for (genID in newExpl){
                if (newExpl[genID] != ""){
                    newExplList += "|" + newExpl[genID];
                }
            }
        }

        if ( jQuery(tr).children("td:nth-child(9)").attr('status') == 'new' ){
            nameT = oTable.fnGetData(i, 9);
            startDate = oTable.fnGetData(i, 10);
            console.log('nameT ' + nameT);
            if (newTreatList != "")
                newTreatList += "|" + idEvent + '&' + nameT + '&' + startDate + '&' + comments;
            else
                newTreatList = idEvent + '&' + nameT + '&' + startDate + '&' + comments;
            for (genID in newTreat){
                if (newTreat[genID] != "")
                    newTreatList += "|"  + newTreat[genID];
            }
            console.log(newTreatList);
        }

        if ( jQuery(tr).attr('status') == 'canc' ){
            if (cancList != "")
                cancList += "|" + idEvent + '&' + comments;
            else
                cancList = idEvent + '&' + comments;
            for (genID in cancData){
                if (cancData[genID] != "")
                    cancList += "|" + cancData[genID];
            }
        }

        if ( jQuery(tr).attr('status') == 'pending' ){
            if (pendingList != "")
                pendingList += "|" + idEvent + '&' + comments;
            else
                pendingList = idEvent + '&' + comments;
            /*for (genID in pendingData){
                pendingList += "|" + pendingData[genID];
            }*/
        }
console.log(jQuery(tr).attr('status'), idEvent);
        if ( jQuery(tr).attr('status') == 'not applicable' ){
            console.log('NA')
            if (notApplicableList != "")
                notApplicableList += "|" + idEvent;
            else
                notApplicableList = idEvent;
        }

        if (  jQuery(tr).attr('status') == 'sacr' ){
            if (sacrificeList != "")
                sacrificeList += "|" + idEvent + '&' + comments;
            else
                sacrificeList = idEvent + '&' + comments;
            for (genID in sacrificeData){
                if (sacrificeData[genID] != "")
                    sacrificeList += "|" + sacrificeData[genID];
            }
        }
    }
console.log(notApplicableList);
    console.log('group '+groupName+ '\nnewExplList '+newExplList+ '\nnewTreatList '+newTreatList+ '\ncancList '+cancList + '\npendingList '+pendingList+ '\nsacrificeList '+sacrificeList+ '\nnotApplicableList '+notApplicableList);
    jQuery.ajax({
        url: base_url + '/check/checking',
        type: 'POST',
        data: {'group':groupName,'newExplList':newExplList,'newTreatList':newTreatList,'cancList':cancList,'pendingList':pendingList,'sacrificeList':sacrificeList,'notApplicableList':notApplicableList},
        dataType: 'text',
    });
}        
