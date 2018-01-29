$(document).ready(function(){
	oTable = $('table#pending').dataTable( {
        "bProcessing": true,
        "bLengthChange": false, 
        "iDisplayLength": 5,
        "bAutoWidth": false ,
        "aaSorting": [[0, 'asc']],
        "aoColumnDefs": [
            { "bSortable": false, "aTargets": [ 3 ] },
            { "bVisible": false, "aTargets": [ 0 ] }
        ],
    });
	
	$("#pending span.ui-icon-trash").on('click', function(event){
		var selectedRow = event.target.parentNode.parentNode.parentNode;
		trashPlan(selectedRow);
	});
});

function getDetails(reqID){
	console.log('getDetails');
	var data = JSON.parse(pending[reqID]);
	var message = "Involved aliquots:\n"
	for (var i = 0; i < data.length; i++){
		message += data[i]['genid'] + "\n";
	}
	alert(message);
}

function select(reqID){
	console.log('select');
    if (typeOperation == 'Generation'){
        console.log('generation');
		window.location.assign(base_url + '/generation/aliquots/?reqid=' + reqID)
    }else if (typeOperation == 'Thawing'){
        console.log('thawing');
        window.location.assign(base_url + '/thawing/start/?reqid=' + reqID)
    }
}

function trashPlan(selectedRow){
	$('#trashdialog').dialog({
        autoOpen: false,
        modal: true,
        resizable: false,
        buttons:
        [
            {
                text: "Yes",
                click: function() {
                	var timer = setTimeout(function(){$("body").addClass("loading");},500);
                	var index = oTable.fnGetPosition(selectedRow);
                	var idplan= oTable.fnGetData( index, 0 );
                	$.ajax({
            	        url: base_url + "/delete/pending/",
            	        type: 'POST',
            	        data: {"delete":true,"idplan":idplan,"experiment":typeOperation},
            	        dataType: 'text',
            	        success: function(transport) {
            				if (transport=="ok"){
            					oTable.fnDeleteRow(selectedRow);
            				}
            				else{
            					alert("Error");
            				}
            				clearTimeout(timer);
        					$("body").removeClass("loading");
		                },
		                error: function(data) {
				            alert(data.responseText, 'Error');
				        }
            	    });                	
          	        $(this).dialog("close");
                }
            },
            {
                text: "No",
                click: function() {
                    $(this).dialog("close");
                }
            }
        ]
     }).dialog("open");
}
