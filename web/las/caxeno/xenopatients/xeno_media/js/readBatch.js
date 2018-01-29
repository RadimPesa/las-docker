$(document).ready(function () {
	console.log(data);
	
	for (var i = 0; i < data.length; i++){
	    console.log(data[i]);
	    if (i == 0){
	        //header
	        var string = "<tr id='" + data[i][0] + "'>";
	        var stringPopup = '<table>';
	        for (var j = 0; j < data[i].length; j++){
	            string += "<th>" + data[i][j] + "</th>";
	            stringPopup += '<tr><td><label for="' + data[i][j].replace(/ /g, '') + '">' + data[i][j] + '</label></td><td><input id="' + data[i][j].replace(/ /g, '') + '" type="text"></input></td></tr>';
	        }
	        string += '</tr>';
	        stringPopup += '</table>';
	        $("#fileData thead").append(string);
	        $("#dialog").append(stringPopup);
	        
	    }else{
	        var string = "<tr id='" + data[i][0] + "'>";
	        for (var j = 0; j < data[i].length; j++){
	            string += "<td>" + data[i][j] + "</td>";
	        }
	        string += '</tr>';
	        $("#fileData tbody").append(string);
	    }
	}
	$('#fileData tbody td').editable( function( sValue ) {
		var aPos = oTable.fnGetPosition( this );
        var aData = oTable.fnGetData( aPos[0] );
		aData[ aPos[1] ] = sValue;
		return sValue;
	}, { "onblur": 'submit' } );  
	oTable = $('#fileData').dataTable();

	$("#fileData_length").after('<input type="button" value="Save" style="float:left; margin-left:50px;" onclick="save();"></input>')
	$("#fileData_length").after('<input type="button" value="Add row" style="float:left; margin-left:50px;" onclick="addRow();"></input>')
});

function addRow(){
    $( "#dialog" ).dialog({
        resizable: false,
        modal: true,
        draggable :false,
        buttons: {
            "Cancel": function() {
                $(this).dialog( "close" );
            },
            "Ok": function() {
                var elements = $("#dialog input");
                var tmp = [];
                for (var i = 0; i < elements.length; i++){
                    tmp.push($(elements[i]).val());
                }
                console.log(tmp);
                oTable.fnAddData(tmp);
                //per rendere anche la nuova riga editabile
	            $('#fileData tbody td').editable( function( sValue ) {
		            var aPos = oTable.fnGetPosition( this );
                    var aData = oTable.fnGetData( aPos[0] );
		            aData[ aPos[1] ] = sValue;
		            return sValue;
	            }, { "onblur": 'submit' } );  
                $(this).dialog( "close" );
            },
        }
    });
}

function save(){
	timer = setTimeout(function(){jQuery("body").addClass("loading");}, 500);
    var recordsToSave = [];
    var aTrs = oTable.fnGetNodes();
    for ( var i = 0; i < aTrs.length; i++ ){
        var temp = {};
        var row = oTable.fnGetData(i);
        for ( var j = 0; j < row.length; j++ ){
            if (oTable.fnGetData(i, j) != 'Click to edit')
                temp[data[0][j]] = oTable.fnGetData(i, j);
            else
                temp[data[0][j]] = null;
        }
        recordsToSave.push(temp);
    }
    
    
    //send these data to server
    console.log(recordsToSave);
    console.log($('#action').text());
    console.log(JSON.stringify(recordsToSave));
    var url = base_url + "/batch/save";
    $.ajax({
        url: url,
        type: 'POST',
        data: { 'data':JSON.stringify(recordsToSave), 'action':$('#action').text() },
        dataType: 'text',
        success: function(transport) {
            console.log(transport);
            if (transport == 'ok'){
                $("#saveResponse").text('Data correctly saved.');                
                dialogSave();
            }else{
                $("#saveResponse").text(transport);
                dialogSave();
            }
            clearTimeout(timer);
            jQuery("body").removeClass("loading");
        }
    });
}

function dialogSave(){
    $( "#dialog2" ).dialog({
        resizable: false,
        modal: true,
        draggable :false,
        buttons: {
            "Ok": function() {
                document.location.href = startUrl;
                $(this).dialog( "close" );
            },
        }
    });
}
