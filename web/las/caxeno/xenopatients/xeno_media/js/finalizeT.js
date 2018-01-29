counter = 0;
function checkKey(evt){
    var charCode = (evt.which) ? evt.which : event.keyCode
    if ( charCode == 13 ) //codice ASCII del carattere carriage return (invio)
	    readMouse();
}

jQuery(document).ready(function () {
    oTableA = jQuery('#armList').dataTable( {
        "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        "iDisplayLength": -1,
        "aaSorting": [[1, 'asc']],
        "aoColumnDefs": [
            { "bVisible": false, "aTargets": [ 0 ] },
        ],
    });
    oTableM = jQuery('#miceList').dataTable( {
        "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        "iDisplayLength": -1,
        "aaSorting": [[0, 'asc']],
    });
    oTableG = jQuery('#groupList').dataTable( {
        "aLengthMenu": [[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]],
        "iDisplayLength": -1,
        "aoColumnDefs": [
            { "bVisible": false, "aTargets": [ 0 ] },
        ],
        "aaSorting": [[1, 'asc']]
    });
    var rows = oTableG.fnGetNodes();
    console.log(rows);
    for (var i = 0; i < rows.length; i++ ){
        var row = rows[i];
        console.log(row);
        jQuery(row).click( function() {
            loadArms(this);
        });
    }
});

function loadArms(row){
    console.log(row);
    jQuery("#armDiv").show();
    console.log(oTableG.fnGetData(oTableG.fnGetPosition(row), 1));
    jQuery("#hiddenGroup").text(oTableG.fnGetData(oTableG.fnGetPosition(row), 1));
    jQuery("#nameG").text(oTableG.fnGetData(oTableG.fnGetPosition(row), 1));
    jQuery.ajax({
        url: base_url + '/treatments/confirmTreatments',
        type: 'GET',
        data: {'groupSelected' : oTableG.fnGetData(oTableG.fnGetPosition(row), 0) },
        datatype: 'json',
        success: function(transport) {
            console.log(transport);
            for (j = 0; j <= oTableA.fnGetNodes().length; j++){ oTableA.fnDeleteRow(0); }
            var arms = JSON.parse(transport);
            for (index in arms){
                var arm = arms[index];
                oTableA.fnAddData([arm['longName'], arm['nameP'], arm['nameA'], arm['duration']]);
                jQuery( oTableA.fnGetNodes()[oTableA.fnGetNodes().length-1] ).click( function() {
                    loadMice(this);
                });
            }
        }
    });
}

function loadMice(row){
    console.log('test');
    jQuery("#hiddenPha").text(oTableA.fnGetData(oTableA.fnGetPosition(row), 0)) ;
    jQuery("#nameT").text(oTableA.fnGetData(oTableA.fnGetPosition(row), 0)) ;
    jQuery.ajax({
        url: base_url + '/treatments/confirmTreatments',
        type: 'GET',
        data: {'armSelected' : oTableA.fnGetData(oTableA.fnGetPosition(row), 0) },
        datatype: 'json',
        success: function(transport) {
            console.log(transport);
            var date = JSON.parse(transport)['date'];
            var time = JSON.parse(transport)['time'];
            var mice = JSON.parse(transport)['miceList'];
            console.log(mice);
            $("#date").val(date);
            $("#time").val(time);
            for (index in mice){
                var mouse = mice[index];
                oTableM.fnAddData([ mouse['genID'], mouse['barcode'], '' ]);
            }
            $("#date").datetimepicker({
                altField: "#time",
                dateFormat: "yy-mm-dd"
            });
            jQuery("#groupsArms").hide();
            jQuery("#passMice").show();
            document.getElementById('barcode').focus();
            
        }
    });
}

function writeMessage(info, background, textColor){
    console.log('writing');
    //jQuery("#outcomeDiv").css("background-color", background)
    jQuery("#outcome").html(info);
    //jQuery("#outcome").css("color",textColor);
    jQuery("#outcomeDiv").css('border-style','solid');
    jQuery("#outcomeDiv").css('border-width','2px');
    jQuery("#outcomeDiv").css('border-color',textColor);
}

function readMouse(){
    var barcode = document.getElementById("barcode").value.toUpperCase();
    var nameT = jQuery('#hiddenPha').text();
    var group = jQuery('#hiddenGroup').text();
    var url = base_url + "/api.mouseForTreat/" + barcode + "/" + group + "/" + nameT;
    var newMouse = true;
    if (jQuery('#' + barcode + '_img').length > 0){
        //topo gia' passato
        newMouse = false;                                         
    }
    if (newMouse){
        if (barcode != ""){
            console.log('pre');
            jQuery.ajax({
                url:url,
                method: 'get',
                datatype: 'json',
                async:false,
                success: function(transport) {
                    console.log('eeee');
                    console.log(transport);
                    transport = JSON.parse(transport);
                    console.log(transport);
                    console.log(transport['response']);
                    if (transport.response == 'bad'){
                        writeMessage(transport['message'], "#FF8080", 'red');
                    }else if (transport.response == 'ok'){
                        writeMessage(transport['message'], "LightGreen", 'green');
                        for (var i=0; i < transport['mice'].length; i++){
                            var genIDMouse = transport['mice'][i];
                            console.log(genIDMouse);    
                            for (var j = 0; j < oTableM.fnGetNodes().length; j++){
                                if (oTableM.fnGetData(j,0) == genIDMouse ){
                                    //oTableM.fnUpdate( '<img id = "' + barcode + '_img" src="' + base_url + '/xeno_media/img/admin/icon_success.gif"/>', j, 2);
                                    oTableM.fnUpdate( '<img id = "' + barcode + '_img" src="/xeno_media/img/admin/icon_success.gif"/>', j, 2);
                                    counter++;
                                }
                            }
                            
                        }
                    }
                }
            });
            var url = base_url + '/api.lastWeight/' + barcode;
            jQuery.ajax({
                datatype: "json",
                url:url,
                type: 'get',
                async:false,
                success:function(transport) {
                    console.log(transport.w);
                    if (transport.w != undefined)
                        jQuery("#lastw").text(transport.w + ' , the ' + transport.dateW);
                    else
                        jQuery("#lastw").text("-");
                }
            });
            $("#barcode").val("");
        }else{
            alert("You've inserted a blank barcode");
            
        }
    }else
        alert("You have already passed this mouse.");
}

function save(){
    jQuery("#save").attr("disabled",true);
    var lenM = oTableM.fnGetNodes().length;
    console.log(counter);
    if (lenM == counter){
        var group = jQuery('#hiddenGroup').text();
        var pha = jQuery('#hiddenPha').text();
        var date = jQuery('#date').val();
        var time = jQuery('#time').val();
        console.log(group);
        console.log(pha);
        console.log(date);
        console.log(time);
        jQuery.ajax({
	        url: base_url + '/treatments/confirmTreatments',
	        type: 'POST',
	        data: {'toSave':'True', 'group':group, 'pha':pha, 'date':date, 'time':time},
	        dataType: 'text',
        });
    }else{
        document.getElementById('barcode').focus();
        jQuery("#save").attr("disabled",false);
        alert("If you want to start and save this treatment, first you have to pass all mouse.");            
    }
}

function abort(){
    var response = confirm("If you confirm, the all the not finalized treatments of this group will be aborted.\nContinue?");
    if (response){
	    var group = jQuery('#hiddenGroup').text();
        jQuery.ajax({
	        url: base_url + '/treatments/confirmTreatments',
	        type: 'POST',
	        data: {'abort':'True', 'group':group},
	        dataType: 'text',
        });
    }
}
